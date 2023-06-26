
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_984_LiveNG_PreviewModeRecordingSESSION_Trans_RestartGoLiveWaitToMp4_redirectEntry.py
 
 @desc : This test check E2E test of new LiveNG entries Passthrough + PREVIEWMODE ON + Recording SESSION by Creating new live entry with explicitLive=1 enable  and start streaming and then
 Playback with/out USER KS and ADMIN KS
 Updating GO LIVE preview mode -> Verify live entry playback by refreshing/opening new browser
 Verify that recorded1 entry is created only after GO LIVE.
 Verify that the recorded1 entry is played ok.
 Verify that the recorded1 entry stopped recording after END LIVE and then mp4 flavours are uploaed.
 Verify duration of the recording1 entry.
 Updating GO LIVE preview mode -> Verify live entry playback by refreshing/opening new browser
 Verify that the recorded2 entry is played ok.
 Verify that the recorded2 entry stopped recording after END LIVE and then mp4 flavours are uploaed.
 Verify duration of the recording2 entry.
 Verify that redirectEntryId is set with recording2 entryId.
 Verify that redirectEntryId plays after stopping streaming of the live entry.

Open issue-redirect entry empty:
https://kaltura.atlassian.net/browse/LIV-1102
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time
import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
#sys.path.insert(1,pth)

from KalturaClient.Plugins.Core import *
import QrcodeReader
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
import ast
import StaticMethods

##########
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
        #self.PartnerID ="231"
        #self.ServerURL ="https://api.nvd1.ovp.kaltura.com"
        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')

        # Recording after mp4 files are uploaded
        self.sniffer_fitler_After_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_After_Mp4flavorsUpload')  # QA 'qa-aws-vod'  # PROD 'cfvod'
        self.sniffer_fitler_Before_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_Before_Mp4flavorsUpload')  # QA and Prod klive->regular DP (cflive ->DP CF)

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

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')
        self.sendto = "moran.cohen@kaltura.com;"
        # Streamer connection - Local/remote
        self.LocalCheckpointKey = None#inifile.RetIniVal('NewLive', 'LocalCheckpointKey')
        #self.SSH_CONNECTION = "KEY_SSH"  # "KEY_SSH"#"LINADMIN_SSH"
        #***** SSH streaming server - AWS LINUX
        # Jenkis run LIVENGRecording
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENG_Recording')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENG_Recording')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4" 

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.RestartDowntime = 60
        self.PlayerVersion = 3 # Set player version 2 or 3
        #self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_984_LiveNG_PreviewModeRecordingSESSION_Trans_RestartGoLiveWaitToMp4_redirectEntry')
        self.logi.initMsg('test_984_LiveNG_PreviewModeRecordingSESSION_Trans_RestartGoLiveWaitToMp4_redirectEntry')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_984_LiveNG_PreviewModeRecordingSESSION_Trans_RestartGoLiveWaitToMp4_redirectEntry(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
           # Create Admin ks
            self.logi.appendMsg('INFO - Going to created admin KS by API.session.start')
            user_id = "AdminKS_USER_ID" + str(datetime.datetime.now())
            k_type = KalturaSessionType.ADMIN
            expiry = None
            privileges = ""
            ksAdmin = str(self.client.session.start(self.UserSecret, user_id, k_type, self.PublisherID, expiry, privileges))
            self.logi.appendMsg('INFO - Created admin KS by API.ksAdmin = ' + ksAdmin)

            ''' RETRIEVE TRANSCODING ID AND CREATE cloud transcode IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Cloud transcode')
            Transobj = Transcoding.Transcoding(self.client, 'Cloud transcode')
            self.CloudtranscodeId = Transobj.CreateConversionProfileFlavors(self.client, 'Cloud transcode', '32,33,34,35')
            if isinstance(self.CloudtranscodeId, bool):
                testStatus = False
                return
                    
            # Create player of latest version -  Create V2/3 Player
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveEntry_PEVIEWMODE_SESSION_DVR_Trans_Restart_Redirect' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(None, None,dvrStatus=1,explicitLive=1,recordStatus=2)  # 2 : KalturaRecordStatus.PER_SESSION,  # 1 : explicitLive enable # 1 :dvrStatus enable
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                if self.IsSRT == True:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primarySrtBroadcastingUrl
                    primarySrtStreamId = self.streamUrl[i].primarySrtStreamId
                    self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
                else:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primaryBroadcastingUrl
                if self.env == 'testing':
                    if self.Live_Change_Cluster == True:
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))

                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                start_streaming = datetime.datetime.now().timestamp()
                #rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True,SSH_CONNECTION=self.SSH_CONNECTION,LocalCheckpointKey=self.LocalCheckpointKey)
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
                #******* CHECK CPU usage of streaming machine
                #cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
                self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))           
                cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"                
                #rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine,SSH_CONNECTION=self.SSH_CONNECTION,LocalCheckpointKey=self.LocalCheckpointKey)
                rc, CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user,self.remote_pass, cmdLine)
                if rc == True:
                    self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
                else:
                    self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                    testStatus = False
                    return

                ####### Verify that there is NO recordedEntryId before GO LIVE state - Try to Get recordedEntryId from the live entry by API
                self.logi.appendMsg("INFO - Going to verify that recordedEntryId is not created of LIVE ENTRY = " + self.entryId + "before GO LIVE STATE.")
                entryLiveStream = self.client.liveStream.get(self.entryId)
                FirstRecording_EntryID = entryLiveStream.recordedEntryId
                if FirstRecording_EntryID != "":
                    self.logi.appendMsg("FAIL - Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")
                else:
                    self.logi.appendMsg("PASS - NOT Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")

                time.sleep(5)
                # ****** Livedashboard - Channels tab
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False

                time.sleep(10)

                # Playback verification when explicitLive=1 enable of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False --> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=False -> Meaning the entry should not play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, False, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) of " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(15)#Add wait for start playing
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + " with ADMIN KS when explicitLive=1 enable - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,flashvars=flashvars,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " with ADMIN KS explicitLive=1 enable -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                ################################ SET GO LIVE
                self.logi.appendMsg("INFO - Going to perform GO LIVE viewMode = 1 to entryId= " + str(self.entryId) + " time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 1 #Go live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)
                GO_LIVE_time = datetime.datetime.now().timestamp()

                time.sleep(30)  # Wait for GO LIVE backend cache
                ####### Get recordedEntryId from the live entry by API after GO LIVE STATE
                self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + str(self.entryId) + " after GO LIVE STATE.")
                entryLiveStream = self.client.liveStream.get(self.entryId)
                recorded_entry = KalturaBaseEntry()
                recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
                FirstRecording_EntryID = entryLiveStream.recordedEntryId
                if FirstRecording_EntryID == "":
                    self.logi.appendMsg("FAIL - NOT Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId + " after GO LIVE STATE.")
                    testStatus = False
                    return
                self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(FirstRecording_EntryID) + '\')')
                self.recorded_entrieslst = []
                self.recorded_entrieslst.append(recorded_entry)
                self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)

                # Playback verification of all LIVE entries
                self.logi.appendMsg("INFO - Going to verify playback on LIVE entry After updating GO LIVE viewMode = 1 , boolShouldPlay=True --> Going to PLAY " + str(self.entryId) + "  live entry on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=True -> Meaning the entry should play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst_GoLive, True, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback(boolShouldPlay=True) of Live entry " + str(entryGoLiveState.id) + " After updating GO LIVE viewMode = 1 - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                # Waiting about 1.5 until recording entry is playable from klive
                #self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                #time.sleep(90)
                # RECORDED ENTRY - Playback verification of all entries
                self.logi.appendMsg("INFO - AFTER GO LIVE:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                ################################ SET END LIVE
                self.logi.appendMsg("INFO - Going to perform END LIVE viewMode = 0 to entryId= " + str(self.entryId) + "  time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 0  # END live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)
                END_LIVE_time = datetime.datetime.now().timestamp()  # Save END LIVE time of stream

                # Playback verification of all entries
                time.sleep(30)  # Wait for GO LIVE backend cache

                ##################################

                # Playback verification when viewMode=0 END LIVE of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False viewMode=0 END LIVE for LIVE entry--> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=False -> Meaning the entry should not play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) and viewMode=0 END LIVE of LIVE entry " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(10)
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play LIVE entry " + str(self.entryId) + " with ADMIN KS when viewMode=0 END LIVE - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,flashvars=flashvars,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback of LIVE entry " + str(self.entryId) + " with ADMIN KS and viewMode=0 END LIVE -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                #####################################*********** Verify first RECORDING after END LIVE
                rc=self.liveObj.PLAY_RECORDING_After_END_LIVE(client=self.client, recorded_entrieslst=self.recorded_entrieslst, Recording_EntryID=FirstRecording_EntryID, recorded_entry=recorded_entry, GO_LIVE_time=GO_LIVE_time, END_LIVE_time=END_LIVE_time,PlayerVersion=self.PlayerVersion, env=self.env, testTeardownclass=self.testTeardownclass, sniffer_fitler_After_Mp4flavorsUpload=self.sniffer_fitler_After_Mp4flavorsUpload, MinToPlay=self.MinToPlay,seenAll_justOnce_flag=self.seenAll_justOnce_flag,expectedFlavors_totalCount=4)
                if rc == False:
                    self.logi.appendMsg("FAIL - PLAY_RECORDING_After_END_LIVE.  FirstRecording_EntryID=" + FirstRecording_EntryID)
                    testStatus = False
                    return
                ################################### Restart GO LIVE streaming - Working on
                # Restart time
                deltaTime = datetime.datetime.now().timestamp() - END_LIVE_time
                deltaTime = int(deltaTime)
                if deltaTime <= self.RestartDowntime:
                    deltaTime = self.RestartDowntime - deltaTime
                    time.sleep(deltaTime)
                # Restart GO LIVE
                ################################ Re-SET GO LIVE
                self.logi.appendMsg("INFO - Restart GO LIVE:Going to perform GO LIVE viewMode = 1 to entryId= " + str(self.entryId) + " time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 1  # Go live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)
                GO_LIVE_time2 = datetime.datetime.now().timestamp()

                time.sleep(30)  # Wait for GO LIVE backend cache
                ####### Get recordedEntryId from the live entry by API after GO LIVE STATE
                self.logi.appendMsg("INFO - Restart GO LIVE:Going to take second recordedEntryId of LIVE ENTRY = " + str(self.entryId) + " after GO LIVE STATE.")
                entryLiveStream = self.client.liveStream.get(self.entryId)
                recorded_entry = KalturaBaseEntry()
                recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
                SecondRecording_EntryID = entryLiveStream.recordedEntryId
                if SecondRecording_EntryID == "":
                    self.logi.appendMsg("FAIL - Restart GO LIVE:NOT Found second recordedEntryId = " + str(SecondRecording_EntryID) + " of LIVE ENTRY = " + self.entryId + " after GO LIVE STATE.")
                    testStatus = False
                    return
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(SecondRecording_EntryID) + '\')')
                self.recorded_entrieslst = []
                self.recorded_entrieslst.append(recorded_entry)
                self.logi.appendMsg("PASS - Restart GO LIVE:Found  SecondRecording_EntryID = " + str(SecondRecording_EntryID) + " of LIVE ENTRY = " + self.entryId)
                ######################
                # Playback verification of all LIVE entries
                self.logi.appendMsg("INFO - Restart GO LIVE:Going to verify playback on LIVE entry After updating GO LIVE viewMode = 1 , boolShouldPlay=True --> Going to PLAY " + str(self.entryId) + "  live entry on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=True -> Meaning the entry should play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst_GoLive, True,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Restart GO LIVE:Playback(boolShouldPlay=True) of Live entry " + str(entryGoLiveState.id) + " After updating GO LIVE viewMode = 1 - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                # Waiting about 1.5 until recording entry is playable from klive
                # self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                # time.sleep(90)
                # RECORDED ENTRY - Playback verification of all entries
                self.logi.appendMsg("INFO - Restart GO LIVE:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Restart GO LIVE:RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                ################################ SET END LIVE
                self.logi.appendMsg("INFO - Restart GO LIVE:Going to perform END LIVE viewMode = 0 to entryId= " + str(
                    self.entryId) + "  time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 0  # END live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)
                END_LIVE_time2 = datetime.datetime.now().timestamp()  # Save END LIVE time of stream

                # Playback verification of all entries
                time.sleep(30)  # Wait for GO LIVE backend cache

                #####################################*********** Verify Second RECORDING after END LIVE
                rc = self.liveObj.PLAY_RECORDING_After_END_LIVE(client=self.client,recorded_entrieslst=self.recorded_entrieslst,Recording_EntryID=SecondRecording_EntryID,recorded_entry=recorded_entry,GO_LIVE_time=GO_LIVE_time2, END_LIVE_time=END_LIVE_time2,PlayerVersion=self.PlayerVersion, env=self.env,testTeardownclass=self.testTeardownclass,sniffer_fitler_After_Mp4flavorsUpload=self.sniffer_fitler_After_Mp4flavorsUpload,MinToPlay=self.MinToPlay,seenAll_justOnce_flag=self.seenAll_justOnce_flag,expectedFlavors_totalCount=4)
                if rc == False:
                    self.logi.appendMsg("FAIL - Restart GO LIVE:PLAY_RECORDING_After_END_LIVE.  SecondRecording_EntryID=" + SecondRecording_EntryID)
                    testStatus = False
                    return

                #kill ffmpeg ps
                self.logi.appendMsg("INFO - Restart GO LIVE:Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
                #rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString,SSH_CONNECTION=self.SSH_CONNECTION,LocalCheckpointKey=self.LocalCheckpointKey)
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass,self.entryId, self.PublisherID,FoundByProcessId=ffmpegOutputString)
                if rc != False:
                    self.logi.appendMsg("PASS - Restart GO LIVE:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                else:
                    self.logi.appendMsg("FAIL - Restart GO LIVE:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return

                if str(FirstRecording_EntryID) != str(SecondRecording_EntryID):
                    self.logi.appendMsg("PASS - Restart GO LIVE:FirstRecording_EntryID = " + str(FirstRecording_EntryID) + " is different from SecondRecording_EntryID = " + str(SecondRecording_EntryID))
                else:
                    self.logi.appendMsg("FAIL - Restart GO LIVE:FirstRecording_EntryID = " + str(FirstRecording_EntryID) + " is equal to SecondRecording_EntryID = " + str(SecondRecording_EntryID))
                    testStatus = False
                    return

        except Exception as Exp:
               print(Exp)
               testStatus = False
               pass

        
    #=============================================================================
    # TEARDOWN   
    #=============================================================================
    
    def teardown_class(self):
        
        global testStatus
        
        print('#############')
        print(' Tear down')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        
        try:
            print('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '984','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '984','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
        
        
            
    #===========================================================================
    #pytest.main(['test_984_LiveNG_PreviewModeRecordingSESSION_Trans_RestartGoLiveWaitToMp4_redirectEntry.py', '-s'])
    #===========================================================================
        
        
        