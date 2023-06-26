'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_816_SESSION_Recording_Trans_RestartAbove5min_redirectEntry.py
 @desc : this test check E2E test of new LiveNG entries transcoding + SESSION recording with RTMP streaming by new logic function - host access run ffmpeg cmd
 verification of create new entries ,API,start/check ps/stop streaming, QRCODE Playback and liveDashboard Analyzer - alerts tab and channels
 LIVE entry playback by QRCODE
 VOD/RECORDED entry playback on the fly from klive sniffer verification
 Verify redirectEntry playback after stop streaming before mp4 upload files
 flavorAssets status (mp4 flavor upload) by API
  VOD/RECORDED entry1 playback after mp4 flavor uploaded by checking sniffer verification from aws/cfvod/qa-nginx-vod
  Restart streaming above 5 minutes
  Verify redirectEntry playback after stop streaming before mp4 upload files
  VOD/RECORDED entry2 playback after mp4 flavor uploaded by checking sniffer verification from aws/cfvod/qa-nginx-vod
 Compare duration - Cal recording duration after mp4 flavors are uploaded
 Verify redirectEntry playback after stop streaming after mp4 upload files
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
import ast
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
        #***** SSH streaming server - AWS LINUX
        # Jenkis run LIVENGRecording1
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGRecording1')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENGRecording1')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"      

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        #self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
        self.RestartDowntime = 300 # 5 minutes
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_816_SESSION_Recording_Trans_RestartAbove5min_redirectEntry')
        self.logi.initMsg('test_816_SESSION_Recording_Trans_RestartAbove5min_redirectEntry')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)


    def test_816_SESSION_Recording_Trans_RestartAbove5min_redirectEntry(self):
        global testStatus
        try:

           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE cloud transcode IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Cloud transcode')
            Transobj = Transcoding.Transcoding(self.client, 'Cloud transcode')
            self.CloudtranscodeId = Transobj.CreateConversionProfileFlavors(self.client, 'Cloud transcode', '32,33,34,35')
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-RECORDING_SESSION_RESTART_5_trans_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(recordStatus=2) # 2 : KalturaRecordStatus.PER_SESSION
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            time.sleep(5)
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
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
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

                # ****** Livedashboard - Channels tab
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
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
            FirstRecording_EntryID=entryLiveStream.recordedEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(FirstRecording_EntryID) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload +  " for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(5)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload, Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    #return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


            #kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
            stop_time = datetime.datetime.now().timestamp() # Save stop time of stream
            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - Wait about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            #*********************************************
            # Get redirectEntryId from API
            entryLiveStream = self.client.liveStream.get(self.entryId)
            FirstRecording_redirectEntryId=str(entryLiveStream.redirectEntryId) # Save the first recording redirectEntryID
            if str(entryLiveStream.recordedEntryId) == str(FirstRecording_redirectEntryId):
                self.logi.appendMsg("PASS - recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is equal to redirectEntryId = " + str(FirstRecording_redirectEntryId))
            else:
                self.logi.appendMsg("FAIL - recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is different from redirectEntryId = " + str(FirstRecording_redirectEntryId))
                testStatus = False
                return
            # Play LIVE ENTRY after stop streaming - > Expected redirectEntryId playback
            self.logi.appendMsg("INFO - STOP STREAMING(before mp4 uploaded)-redirectEntryId:Going to play LIVE ENTRY " + str(self.entryId) + " Expected redirectEntryId playback - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()) + " , redirectEntryId = " + str(FirstRecording_redirectEntryId))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=str(FirstRecording_redirectEntryId),Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - STOP STREAMING(before mp4 uploaded)-redirectEntryId:LIVE ENTRY Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            #***********************************
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client,FirstRecording_EntryID, recorded_entry,expectedFlavors_totalCount=4) # 4 expectedFlavors_totalCount is transcoding
            if rc == True:
                self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + entryLiveStream.recordedEntryId)
                ################
                ######## Get conversion version of VOD entry
                # entry_id = entryLiveStream.recordedEntryId
                context_data_params = KalturaEntryContextDataParams()
                First_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                timeout = 0
                while First_RecordedEntry_Version == None or First_RecordedEntry_Version == 0:
                    time.sleep(20)
                    First_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                    timeout = timeout + 1
                    if timeout >= 30:  # 10 minutes timeout for waiting to version update
                        self.logi.appendMsg("FAIL - TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId)
                        testStatus = False
                        return
                ################
                durationFirstRecording = int(self.client.baseEntry.get(FirstRecording_EntryID).duration)#Save the duration of the recording entry after mp4 flavors uploaded
                self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - First_RecordedEntry_Version = " + str(First_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
            else:
                self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                testStatus = False
                return

            # Waiting about 1 minutes before playing the recored entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # #####################################################
            #Create new player of latest version -  Create V2/3 Player because of cache isse
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
            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ###############################################################
            deltaTime = datetime.datetime.now().timestamp() - stop_time
            deltaTime = int(deltaTime)
            if deltaTime <= self.RestartDowntime:
                deltaTime = self.RestartDowntime - deltaTime
                time.sleep(deltaTime)

            # Get entryId and start streaming primaryBroadcastingUrl live entries
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
                self.logi.appendMsg("INFO - ************** AFTER RESTART STREAMING above " + str(self.RestartDowntime) + " seconds - Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                start_streaming2 = datetime.datetime.now().timestamp()
                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host,self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
            ######################################## START
            # LIVE ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING: Going to play LIVE ENTRY " + str(self.entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
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

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:LIVE ENTRY Playback of " + str(self.entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### AFTER RESTART STREAMING:Get recordedEntryId from the live entry by API
            OLD_Recording_entryId= str(recorded_entry.id) # Save the previous vod/recording entry id
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to take NEW recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            SecondRecording_EntryID = entryLiveStream.recordedEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(SecondRecording_EntryID) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Waiting 1.5 minutes until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            # Compare old vod entry to new vod entry
            if OLD_Recording_entryId == str(recorded_entry.id):
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:New recordedEntryId is NOT created.OLD_Recording_entryId = " + OLD_Recording_entryId + ", New recording entryId = " + str(recorded_entry.id) + ", LIVE ENTRY = " + self.entryId)
                testStatus = False
            else:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:New recordedEntryId is created.OLD_Recording_entryId = " + OLD_Recording_entryId + ", New recording entryId = " + str(recorded_entry.id) + ", LIVE ENTRY = " + self.entryId)
            time.sleep(90)
            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload +  " for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload, Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


            #kill ffmpeg ps
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
            stop_time2 = datetime.datetime.now().timestamp() # Save stop time of stream

            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - Wait about 1.5 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # *********************************************
            # Get redirectEntryId from API
            entryLiveStream = self.client.liveStream.get(self.entryId)
            SecondRecording_redirectEntryId = str(entryLiveStream.redirectEntryId)  # Save the second recording redirectEntryID
            if SecondRecording_redirectEntryId == FirstRecording_redirectEntryId:
                self.logi.appendMsg("FAIL - SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId) + " is equal to FirstRecording_redirectEntryId = " + str(FirstRecording_redirectEntryId))
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS - SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId) + " is different from FirstRecording_redirectEntryId = " + str(FirstRecording_redirectEntryId))

            if str(entryLiveStream.recordedEntryId) == str(SecondRecording_redirectEntryId):
                self.logi.appendMsg("PASS - recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is equal to SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId))
            else:
                self.logi.appendMsg("FAIL - recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is different from SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId))
                testStatus = False
                return
            # Play LIVE ENTRY after stop streaming - > Expected redirectEntryId playback
            self.logi.appendMsg("INFO - STOP STREAMING(before mp4 uploaded)-redirectEntryId:Going to play LIVE ENTRY " + str(self.entryId) + " Expected redirectEntryId playback - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()) + " , SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True, PlayerVersion=self.PlayerVersion,sniffer_fitler=str(SecondRecording_redirectEntryId),Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - STOP STREAMING(before mp4 uploaded)-redirectEntryId:LIVE ENTRY Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(60)
            # ***********************************
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("INFO - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client,entryLiveStream.recordedEntryId, recorded_entry,expectedFlavors_totalCount=4) # expectedFlavors_totalCount=4 is for transcoding
            if rc == True:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + entryLiveStream.recordedEntryId)
                ################
                ######## Get conversion version of VOD entry
                # entry_id = entryLiveStream.recordedEntryId
                context_data_params = KalturaEntryContextDataParams()
                Second_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId, context_data_params).flavorAssets[0].version
                timeout = 0
                while Second_RecordedEntry_Version == None or Second_RecordedEntry_Version == 0:
                    time.sleep(20)
                    Second_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                    timeout = timeout + 1
                    if timeout >= 30:  # 10 minutes timeout for waiting to version update
                        self.logi.appendMsg("FAIL - TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId + ", Second_RecordedEntry_Version = " + str(Second_RecordedEntry_Version))
                        testStatus = False
                        return
                ################
                durationSecondRecording = int(self.client.baseEntry.get(SecondRecording_EntryID).duration)#Save the duration of the second recorded entry id after mp4 flaovrs uploaded
                timeout = 0
                while durationSecondRecording == 0:
                    time.sleep(30)
                    durationSecondRecording = int(self.client.baseEntry.get(SecondRecording_EntryID).duration)#Save the duration of the second recorded entry id after mp4 flaovrs uploaded
                    timeout = timeout + 1
                    if timeout >= 10:  # 5 minutes timeout for waiting to version update
                        self.logi.appendMsg("FAIL - TIMEOUT - Duration of Second Recording is not updated on baseEntry.get.duration after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId + " , durationSecondRecording" + str(durationSecondRecording))
                        testStatus = False
                        return
                self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - Second_RecordedEntry_Version = " + str(Second_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                testStatus = False
                return

            # Waiting about 1 minutes before playing the recored entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # #####################################################
            #Create new player of latest version -  Create V2/3 Player because of cache isse
            self.logi.appendMsg('INFO - AFTER RESTART STREAMING:Going to create latest V' + str(self.PlayerVersion) + ' player')
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
            self.logi.appendMsg('INFO - AFTER RESTART STREAMING:Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
            self.liveObj.playerId = self.playerId
            # #####################################################
            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            # Cal recording duration after mp4 flavors are uploaded
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to verify DURATION of both recorded entries.FirstRecording_EntryID = " + str(FirstRecording_EntryID) + " , SecondRecording_EntryID = " + str(SecondRecording_EntryID))
            recordingTime1=int(stop_time-start_streaming)
            recordingTime2=int(stop_time2-start_streaming2)
            Expected_TotalRecordingTime=int(recordingTime1 + recordingTime2) # Expected total duration of the two vod entries
            Actual_TotalRecordingTime=int(durationFirstRecording + durationSecondRecording) # Actual total duration of the two vod entries
            if 0 <= int(recordingTime1) % int(durationFirstRecording) <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:VOD entry1:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:VOD entry1:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                testStatus = False
            if 0 <= int(recordingTime2) % int(durationSecondRecording) <= 40:  # Until 40 seconds of delay between expected to actual duration of the second vod entry2
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:VOD entry2:durationSecondRecording duration is ok Actual_durationSecondRecording=" + str(durationSecondRecording) + " , Expected_recordingTime1 = " + str(recordingTime2) + ", SecondRecording_EntryID = " + str(SecondRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:VOD entry2:durationSecondRecording is NOT as expected -  Actual_durationSecondRecording=" + str(durationSecondRecording)) + " , Expected_recordingTime1 = " + str(recordingTime2) + ", SecondRecording_EntryID = " + str(SecondRecording_EntryID)
                testStatus = False
            #Compare total duration of the two vod entries
            if 0 <= int(Expected_TotalRecordingTime) % int(Actual_TotalRecordingTime) <= 80:#Until 80 seconds of delay between expected to actual duration
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:TOTAL recording duration is OK for two VOD entries. Actual_TotalRecordingTime=" + str(Actual_TotalRecordingTime) + " , Expected_TotalRecordingTime = " + str(Expected_TotalRecordingTime))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:TOTAL recording duration is NOT as expected for two VOD entries. Actual_TotalRecordingTime=" + str(Actual_TotalRecordingTime) + " , Expected_TotalRecordingTime = " + str(Expected_TotalRecordingTime))
                testStatus = False

            # *********************************************
            # Get redirectEntryId from API
            entryLiveStream = self.client.liveStream.get(self.entryId)
            SecondRecording_redirectEntryId_AfterMP4files = str(entryLiveStream.redirectEntryId)  # Save the second recording after mp4 uploaded file redirectEntryID
            if SecondRecording_redirectEntryId != SecondRecording_redirectEntryId_AfterMP4files:
                self.logi.appendMsg("FAIL - Second STOP STREAMING(after mp4 uploaded):SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId) + " different from SecondRecording_redirectEntryId_AfterMP4files = " + str(SecondRecording_redirectEntryId_AfterMP4files))
                testStatus = False
                return
            # Play LIVE ENTRY after stop streaming the second time and mp4 uploaded files- > Expected redirectEntryId playback
            self.logi.appendMsg("INFO - Second STOP STREAMING(after mp4 uploaded)-redirectEntryId:Going to play LIVE ENTRY " + str(self.entryId) + " Expected redirectEntryId playback - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()) + " , SecondRecording_redirectEntryId_AfterMP4files = " + str(SecondRecording_redirectEntryId_AfterMP4files))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=str(SecondRecording_redirectEntryId_AfterMP4files),Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Second STOP STREAMING(after mp4 uploaded)-redirectEntryId:LIVE ENTRY Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            # ***********************************

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
           self.practitest.post(self.Practi_TestSet_ID,'816','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID,'816','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_816_SESSION_Recording_Trans_RestartAbove5min_redirectEntry.py -s')
    #===========================================================================
        
        
        