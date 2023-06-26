'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_265_SESSION_Recording_TransHD_Backup_kubernetes.py
 @desc : this test check E2E test of new LiveNG entries Transcoding HD + SESSION recording with RTMP streaming from backup by new logic function - host access run ffmpeg cmd
 verification of create new entries ,API,start/check ps/stop streaming, QRCODE Playback and liveDashboard Analyzer - alerts tab and channels
 LIVE entry playback by QRCODE
 Verify VOD/RECORDED entry is created.
 Check kubernetes only on QA env:
     controllers get pods
     Run backup content script by kubernetes
     flavorAssets status (mp4 flavor upload) by API
     VOD/RECORDED entry playback after mp4 flavor uploaded by checking sniffer verification from aws/cfvod/qa-nginx-vod
     Verify DURATION for the first recording - by API VS streaming start/stop times

 Step to run the backup script:
 aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1
 kubectl exec -i controllers-85959d65d5-9qqtt  -- curl -i -d '{"0_mzg2ranx" : "0_k2qr67ma", "recordedEntryId" : "0_ytpssjic", "sessionType" : 1, "clusterId" : "cluster-1-b.live.nvq1"}' -H "Content-Type: application/json" -X POST  http://localhost:8084/restorerecord
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter2
import Config
import Practitest
import Entry
import uiconf
import tearDownclass
import MySelenium

import live
import LiveDashboard
import Transcoding
import QrcodeReader
from KalturaClient.Plugins.Core import *
import re
import Kubernetes
import ast
import Kubernetes_k8sConnect
import StaticMethods
### Jenkins params ###
#===============================================================================
# cnfgCls = Config.ConfigFile("stam")
# #Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# Practi_TestSet_ID,isProd = 11,"false"
# if str(isProd) == 'true':
#     isProd = True
# else:
#     isProd = False
# 
# isProd = False # LiveNG is just supported on testing
#==========================PublisherID=====================================================
testStatus = True


class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):

        StaticMethods.before_run(self)

        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')

        # Environment BE server URL
        if self.ServerURL is None:
            self.ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')
        print("ServerURL = " + self.ServerURL)
        # LiveNG config partner:
        if self.PartnerID != None:
            self.PublisherID = self.PartnerID
            self.UserSecret = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'LIVENG_UserSecret')
        else:
            self.PublisherID = self.inifile.RetIniVal(self.section, 'LIVENG_PublisherID')  # QA 6611/ PROD 2930571
            self.UserSecret = self.inifile.RetIniVal(self.section, 'LIVENG_UserSecret')

        # Recording after mp4 files are uploaded
        self.sniffer_fitler_After_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_After_Mp4flavorsUpload')  # QA 'qa-aws-vod'  # PROD 'cfvod'
        self.sniffer_fitler_Before_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_Before_Mp4flavorsUpload')  # QA and Prod klive->regular DP (cflive ->DP CF)

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = '1-b'
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENG_Kubernetes')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENG_Kubernetes')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

        self.expectedFlavors_totalCount = 6  # Flavor count on Recording entry

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_265_SESSION_Recording_TransHD_Backup_kubernetes')
        self.logi.initMsg('test_265_SESSION_Recording_TransHD_Backup_kubernetes')
        self.KubernetesObj = Kubernetes_k8sConnect.Kubernetes_Live(None, self.logi, self.isProd, self.PublisherID)

    def test_265_SESSION_Recording_TransHD_Backup_kubernetes(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE transcoding HD IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = AUTO Transcoding HD')
            Transobj = Transcoding.Transcoding(self.client, 'AUTO Transcoding HD')
            self.CloudtranscodeId = Transobj.CreateConversionProfileFlavors(self.client, 'AUTO Transcoding HD','32,33,34,35,42,43')
            if isinstance(self.CloudtranscodeId, bool):
                testStatus = False
                return
                    
            #Create player of latest version -  Create V2/3 Player
            self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion)  + ' player')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            if self.PlayerVersion == 2:
               self.player = myplayer.addPlayer(None,self.env,False, False) # Create latest player v2
            elif self.PlayerVersion == 3:
               self.player = myplayer.addPlayer(None,self.env,False, False,"v3") # Create latest player v3
            else:
               self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
            if isinstance(self.player,bool):
               testStatus = False
               return
            else:
               self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')

            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-BACKUP_STREAM_RECORDING_SESSION_TransHD_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(recordStatus=2) # 2 : KalturaRecordStatus.PER_SESSION
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
            
            time.sleep(2)

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                if self.IsSRT == True:
                    Current_secondaryBroadcastingUrl = self.streamUrl[i].secondarySrtBroadcastingUrl
                    secondarySrtStreamId = self.streamUrl[i].secondarySrtStreamId
                    self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
                else:
                    Current_secondaryBroadcastingUrl = self.streamUrl[i].secondaryBroadcastingUrl
                if self.env == 'testing':
                    if self.Live_Change_Cluster == True:
                        Current_secondaryBroadcastingUrl = Current_secondaryBroadcastingUrl.replace("1-b",self.Live_Cluster_Backup)
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd from BACKUP only.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + Current_secondaryBroadcastingUrl)
                if self.IsSRT == True:
                    ffmpegCmdLine,Current_secondaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_secondaryBroadcastingUrl),secondarySrtStreamId)
                else:
                    ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(Current_secondaryBroadcastingUrl), self.streamUrl[i].streamName)
                start_streaming = datetime.datetime.now().timestamp()
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_secondaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript secondaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + str(Current_secondaryBroadcastingUrl))
                    testStatus = False
                    return
                # ******* CHECK CPU usage of streaming machine
                #cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
                self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))           
                cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"                
                rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine)
                if rc == True:
                    self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
                else:
                    self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                    testStatus = False
                    return
            time.sleep(1)
            # live dashboard verification
            self.logi.appendMsg("INFO  - Going to verify live dashboard")
            self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
            rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId, self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Backup,ServersStreaming="Only_Backup")
            if rc == True:
                self.logi.appendMsg("PASS  - Verify_LiveDashboard")
            else:
                self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                testStatus = False
        
            # LIVE ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play LIVE ENTRY " + str(self.entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True

            self.logi.appendMsg("PASS - LIVE ENTRY Playback of " + str(self.entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### Get recordedEntryId from the live entry by API
            self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            FirstRecording_EntryID = entryLiveStream.recordedEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(entryLiveStream.recordedEntryId) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)

            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to NOT play(boolShouldPlay=False) RECORDED ENTRY  for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst,boolShouldPlay=False,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True
            self.logi.appendMsg("PASS - RECORDED ENTRY NO Playback((boolShouldPlay=False)) for recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            #kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
            stop_time = datetime.datetime.now().timestamp()  # Save stop time of stream
            if self.env == 'testing': #Check kubernetes only on QA env
                #Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
                self.logi.appendMsg("INFO - Wait about 1.5 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                time.sleep(90)
                time.sleep(5)  # added
                if self.ConfigId!="":#Do if multi regional setting
                    self.ConfigId=self.ConfigId + "-"
                self.logi.appendMsg("PASS - Going to run backupScript execRestoreRecording on recordedEntryId=" + str(entryLiveStream.recordedEntryId) + ",LIVEentryId=" + str(self.entryId) + ",Live_Cluster_Backup= " + str(self.Live_Cluster_Backup) + ", datetime = " + str(datetime.datetime.now()))
                rc = self.KubernetesObj.execRestoreRecording(self.Live_Cluster_Backup,self.ConfigId + self.entryId, entryLiveStream.recordedEntryId, '1')#was '0'
                if rc == False:
                    self.logi.appendMsg("FAIL - Kubernetes_RunBackupContentScript - execRestoreRecording , datetime = " + str(datetime.datetime.now()))
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - Kubernetes_RunBackupContentScript - execRestoreRecording , datetime = " + str(datetime.datetime.now()))
                time.sleep(5)  # added
                # Recording verification
                rc = self.liveObj.FirstRecordingVerification(client=self.client,recordedEntryId=entryLiveStream.recordedEntryId,recorded_entry=recorded_entry,expectedFlavors_totalCount=self.expectedFlavors_totalCount,start_streaming=start_streaming, stop_time=stop_time,FirstRecording_EntryID=FirstRecording_EntryID,recorded_entrieslst=self.recorded_entrieslst,sniffer_fitler_After_Mp4flavorsUpload=self.sniffer_fitler_After_Mp4flavorsUpload,MinToPlay=self.MinToPlay, env=self.env,seenAll_justOnce_flag=self.seenAll_justOnce_flag,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                if rc == False:
                    self.logi.appendMsg("FAIL - FirstRecordingVerification. recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - FirstRecordingVerification. recordedEntryId = " + entryLiveStream.recordedEntryId)

                # #####################################################
                # Create new player of latest version -  Create V2/3 Player because of cache isse
                self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion) + ' player')
                myplayer = uiconf.uiconf(self.client, 'livePlayer')
                if self.PlayerVersion == 2:
                    self.player = myplayer.addPlayer(None, self.env, False, False)  # Create latest player v2
                elif self.PlayerVersion == 3:
                    self.player = myplayer.addPlayer(None, self.env, False, False, "v3")  # Create latest player v3
                else:
                    self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
                if isinstance(self.player, bool):
                    testStatus = False
                    return
                else:
                    self.playerId = self.player.id
                self.logi.appendMsg('INFO - Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
                self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
                self.liveObj.playerId = self.playerId
                # #####################################################

                # RECORDED ENTRY - Playback verification of all entries
                self.logi.appendMsg("INFO - Going to play(boolShouldPlay=True) RECORDED ENTRY  for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst,boolShouldPlay=True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - RECORDED ENTRY  Playback(boolShouldPlay=True) for recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

        except Exception as e:
            print(e)
            testStatus = False
            pass
             
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    
    def teardown_class(self):
        
        global testStatus
        
        print('#############')
        print(' Tear down')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        print('Tear down - testTeardownclass')
        
        try:
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '265','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '265','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_265_SESSION_Recording_TransHD_Backup_kubernetes.py -s')
    #===========================================================================
        
        
        
