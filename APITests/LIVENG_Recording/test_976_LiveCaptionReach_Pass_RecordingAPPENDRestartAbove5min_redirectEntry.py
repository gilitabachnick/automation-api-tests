'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_976_LiveCaptionReach_Pass_RecordingAPPENDRestartAbove5min_redirectEntry.py
 @desc : this test check E2E test of new LiveNG entries passthrough + APPEND recording with RTMP streaming by new logic function - host access run ffmpeg cmd


    Must to set adminTags = "createvodcaption"  or use CreateStreamContainer function from live caption created on VOD entry.

    User case:
    1.Create live entry with passthrough + APPEND recording.
    2.Create live caption:
    Create scheduling event
    Create EntryVandorTask
    3.Start streaming when arriving to startTime of the scheduling event.
    4.Play the Live entry with live caption(vtt verification).
    5.Verify that recording entry is created.
    6.Play the Recording entry with live caption - before stop streaming (klive) and after stop streaming(aws) mp4 files are uploaded.
    7.After above 5min start the streaming.
    8.Verify that new recording entry is not created - same recording entry id gets the new recording content as APPEND
    9.Play the Recording entry with live caption - before stop streaming (klive) and after stop streaming(aws) mp4 files are uploaded.
    10.Verify redirect entry.


 Remark:
 Set accessControl with delivery profile for DP 1113(HLS short segment-Simulive-AWS)- Playback issue with VOD entry after mp4files are uploaded bug https://kaltura.atlassian.net/browse/LIV-1032


 Remark:
 Add multi/two options on sniffer_fitler
 check vtt on recording entry and another sniffer filter(aws/klive)
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

        # live caption config partner
        self.reachProfileId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'reachProfileId')  # QA 310 #PROD 206622
        self.catalogItemId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'catalogItemId')  # QA 374 #PROD 14652
        if self.env == 'testing':
            self.access_control_id_Default = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'access_control_id_Default')
            #self.access_control_id_Default = inifile.RetIniVal(section,'access_control_id_Default')  # 19690 #default access control ->It's needed for playing recording entry on klive mode(before mp4 files are uploaded)
        self.access_control_id_DP_FOR_VODentry = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'access_control_id_DP_FOR_VODentry')  # QA 374 #PROD 14652
        # self.access_control_id_DP_FOR_VODentry = 36000 #QA 36000 #Set accessControl with delivery profile for DP 1113(HLS short segment-Simulive-AWS)- Playback issue with VOD entry after mp4files are uploaded bug https://kaltura.atlassian.net/browse/LIV-1032
        # self.access_control_id_DP_FOR_VODentry = ""  # need to add Live access control to PROD - Don't have this one in PROD# Set accessControl with delivery profile for DP 1113(HLS short segment-Simulive-AWS)- Playback issue with VOD entry after mp4files are uploaded bug https://kaltura.atlassian.net/browse/LIV-1032

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        # Jenkis run LIVENGRecording
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENG_Recording')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENG_Recording')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        #self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
        self.RestartDowntime = 300 # 5 minutes

        # Live caption parameters
        self.SchedulerEvent_AddMinToStartTime = 5  # Time to add for startTime - minutes
        self.SchedulerEvent_sessionEndTimeOffset = 30  # Time to add for EndTime from startTime  - minutes
        self.sniffer_fitler = '.vtt'
        # Caption assets
        self.KalturaStreamContainerArray = [["SERVICE1", "closedCaptions", "eng", "English"]]
        self.ASSET_STATUS_READY = 2  # status ready of captionAsset
        self.CntOfCaptions = 1

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_976_LiveCaptionReach_Pass_RecordingAPPENDRestartAbove5min_redirectEntry')
        self.logi.initMsg('test_976_LiveCaptionReach_Pass_RecordingAPPENDRestartAbove5min_redirectEntry')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)


    def test_976_LiveCaptionReach_Pass_RecordingAPPENDRestartAbove5min_redirectEntry(self):
        global testStatus
        try:

           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Passthrough')
            Transobj = Transcoding.Transcoding(self.client, 'Passthrough')
            self.passtrhroughId = Transobj.CreateConversionProfileFlavors(self.client, 'Passthrough', '32,36,37')
            if isinstance(self.passtrhroughId, bool):
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveCaptionReach_RECORDING_APPEND_RESTART_5_pass_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(recordStatus=1) # 1 : KalturaRecordStatus.APPENDED
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
                ######## ADD adminTag and Containers to liveStream entry - It is required for VOD captions
                # entry_id = self.entry.id
                rc = self.liveObj.CreateStreamContainer(self.client, self.KalturaStreamContainerArray, self.entry.id)
                if rc == False:
                    self.logi.appendMsg("FAIL - Update StreamContainer.EntryID = " + str(self.entry.id))

            time.sleep(5)

            # Create live caption
            self.logi.appendMsg('INFO - Going to create live caption')
            startTime = time.time() + (self.SchedulerEvent_AddMinToStartTime) * 60
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            endTime = startTime + self.SchedulerEvent_sessionEndTimeOffset * 60
            print("endTime = " + str(datetime.datetime.fromtimestamp(int(endTime)).strftime('%Y-%m-%d %H:%M:%S')))
            self.logi.appendMsg("INFO - Going to add KalturaLiveStreamScheduleEvent.Details: entryid=" + str(self.entry.id) + " , startTime INT= " + str(startTime) + " , endTime INT= " + str(endTime) + " , current time= " + str(datetime.datetime.now()))
            self.logi.appendMsg("INFO - startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')) + " , endTime = " + str(datetime.datetime.fromtimestamp(int(endTime)).strftime('%Y-%m-%d %H:%M:%S')))
            rc, EntryVendorTaskId = self.liveObj.LiveCaption_Create(client=self.client, startTime=startTime,endTime=endTime, entryId=self.entry.id,catalogItemId=self.catalogItemId,reachProfileId=self.reachProfileId)
            if rc != True:
                self.logi.appendMsg('FAIL - LiveCaption_Create')
                testStatus = False
                return

            # Wait to scheduling event startTime
            self.logi.appendMsg("INFO - Wait for arriving to startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            while startTime > time.time():  # Wait until SchedulerEvent.startTime
                time.sleep(5)
            # Verify VendorTask Status - 3 processing after arriving to startTime --> will update for sure just after arriving to startTime and start stream for 10sec
            rc = self.liveObj.Create_KalturaEntryVendorTask_VerifyStatus(client=self.client, id=EntryVendorTaskId,Expected_STATUS=3)  # entryVendorTask.status - first 1 scheduled , 3 processing
            if rc == False:
                self.logi.appendMsg("FAIL - After arriving to startTime:Create_KalturaEntryVendorTask_VerifyStatus.Details: entryid=" + self.entry.id + " , EntryVendorTaskId= " + str(EntryVendorTaskId) + " , catalogItemId= " + str(self.catalogItemId) + " , Expected_STATUS= 3 processing")
                testStatus = False
                return
            self.logi.appendMsg("PASS - Create_KalturaEntryVendorTask_VerifyStatus.Details: entryid=" + self.entry.id + " , EntryVendorTaskId= " + str(EntryVendorTaskId) + " , catalogItemId= " + str(self.catalogItemId) + " , Expected_STATUS= 3 processing")
            time.sleep(2)


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

            ########################Caption verification on playback
            self.logi.appendMsg("INFO - ************** Going to play live entries with Live caption on PlayerVersion= " + str(self.PlayerVersion) + "  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
            while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 2:  # Change condition
                # BUG Protocol="https" - Need to user https for playing caption on VOD entry
                ##################***** Because of the bug I changed it from sniffer_fitler_After_Mp4flavorsUpload to sniffer_fitler_Before_Mp4flavorsUpload
                rc_MatchValue = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst,boolShouldPlay=True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,sniffer_fitler=self.sniffer_fitler,Protocol="http", MatchValue=True,ServerURL=self.ServerURL)
                time.sleep(5)
                timeout = timeout + 1
                if rc_MatchValue == False and timeout < 2:
                    self.logi.appendMsg("INFO - ****** Going to play AGAIN after player CACHE ISSUE (No caption ICONF on the PLAYER)   - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                    time.sleep(60)  # Time for player cache issue
                if not rc_MatchValue and timeout >= 2:  # Change condition
                    print("FAIL - Going to play LIVE ENTRY with caption - Retry count:timeout = " + str(timeout))
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True and rc_MatchValue != False:  # Change condition
                    seenAll = True
                    break
                self.logi.appendMsg("PASS - Playback of PlayerVersion= " + str(self.PlayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### Get recordedEntryId from the live entry by API
            self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            #durationFirstRecording= int(self.client.baseEntry.get(recorded_entry.id).duration)
            FirstRecording_EntryID=entryLiveStream.recordedEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(FirstRecording_EntryID) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)

           # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # RECORDED ENTRY - Playback verification of all entries ########### NEED TO ADD VTT VERIFICATION on VOD entry
            self.logi.appendMsg("INFO - AFTER GO LIVE:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.recorded_entrieslst,boolShouldPlay=True,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,PlayerVersion=self.PlayerVersion,ClosedCaption=True, Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True
            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


            #####################################
            time.sleep(5)
            # ****** Livedashboard - Channels tab
            self.logi.appendMsg("INFO  - Going to verify live dashboard before first stop streaming")
            self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
            rc = self.LiveDashboard.Verify_LiveDashboard(logi=self.logi, LiveDashboardURL=self.LiveDashboardURL,
                                                         entryId=self.entryId, PublisherID=self.PublisherID,
                                                         ServerURL=self.ServerURL, UserSecret=self.UserSecret, env=self.env,
                                                         Flag_Transcoding=False,
                                                         Live_Cluster_Primary=self.Live_Cluster_Primary,
                                                         First_navigateTo="Recordings")
            if rc == True:
                self.logi.appendMsg("PASS  - Verify_LiveDashboard")
            else:
                self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                testStatus = False

            #####################################

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
            self.logi.appendMsg("INFO - AFTER FIRST STOP STREAMING:Wait about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # *********************************************
            # Get redirectEntryId from API
            entryLiveStream = self.client.liveStream.get(self.entryId)
            FirstRecording_redirectEntryId = str(entryLiveStream.redirectEntryId)  # Save the first recording redirectEntryID
            if str(entryLiveStream.recordedEntryId) == str(FirstRecording_redirectEntryId):
                self.logi.appendMsg("PASS - AFTER FIRST STOP STREAMING:recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is equal to redirectEntryId = " + str(FirstRecording_redirectEntryId))
            else:
                self.logi.appendMsg("FAIL - AFTER FIRST STOP STREAMING:recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is different from redirectEntryId = " + str(FirstRecording_redirectEntryId))
                testStatus = False
                return

            # Play LIVE ENTRY after stop streaming - > Expected redirectEntryId playback
            self.logi.appendMsg("INFO - AFTER FIRST STOP STREAMING:(before mp4 uploaded)-redirectEntryId:Going to play LIVE ENTRY " + str(self.entryId) + " Expected redirectEntryId playback - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()) + " , redirectEntryId = " + str(FirstRecording_redirectEntryId))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst, boolShouldPlay=True, PlayerVersion=self.PlayerVersion,sniffer_fitler=str(FirstRecording_redirectEntryId),ClosedCaption=True,Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - AFTER FIRST STOP STREAMING:before mp4 uploaded)-redirectEntryId:LIVE ENTRY Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


            # ***********************************
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client,entryLiveStream.recordedEntryId, recorded_entry,expectedFlavors_totalCount=1) # expectedFlavors_totalCount=1 is for passthrough
            if rc == True:
                self.logi.appendMsg("PASS - AFTER FIRST STOP STREAMING:Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + entryLiveStream.recordedEntryId)
                durationFirstRecording = int(self.client.baseEntry.get(recorded_entry.id).duration)#Save the duration of the recording entry after mp4 flavors uploaded
            else:
                self.logi.appendMsg("FAIL - AFTER FIRST STOP STREAMING:MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                testStatus = False
                return

            #######################CAPTION ASSETS ON VOD entry
            self.logi.appendMsg("INFO -  AFTER FIRST STOP STREAMING::Going to verify captionAssetList_result on recordedEntryId = " + entryLiveStream.recordedEntryId)
            rc = self.liveObj.captionAssetOnVODentry(self.client, self.KalturaStreamContainerArray,entryLiveStream.recordedEntryId,CntOfCaptions=self.CntOfCaptions)
            if rc != True:
                self.logi.appendMsg("FAIL -  AFTER FIRST STOP STREAMING::VOD entry captionAssetList_result verification.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                testStatus = False
                return
            self.logi.appendMsg("PASS -  AFTER FIRST STOP STREAMING::VOD entry captionAssetList_result verification.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            #######################
            ######## Get conversion version of VOD entry
            #entry_id = entryLiveStream.recordedEntryId
            context_data_params = KalturaEntryContextDataParams()
            First_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
            timeout=0
            while First_RecordedEntry_Version == None:
                time.sleep(20)
                First_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId, context_data_params).flavorAssets[0].version
                timeout = timeout + 1
                if timeout >= 30: # 10 minutes timout for waiting to version update
                    self.logi.appendMsg("FAIL - TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return

            ########## Verify DURATION for the first recording
            recordingTime1 = int(stop_time - start_streaming)
            self.logi.appendMsg("INFO - Going to verify DURATION for the first recording. recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            if (0 <= recordingTime1 % durationFirstRecording <= 40) or (0 <= durationFirstRecording % recordingTime1 <= 40):  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                self.logi.appendMsg("PASS - AFTER FIRST STOP STREAMING::VOD entry:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER FIRST STOP STREAMING::VOD entry:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                testStatus = False
                return
            ############################################MORAN$$$$$$$$$$$$$$$$$$$$$
            # Waiting about 1 minutes before playing the record entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
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


            # ##################################################### BUG LIV-1032 on QA env
            if self.env == 'testing':
                # Set accessControl with delivery profile for DP 1113(HLS short segment-Simulive-AWS)- Playback issue with VOD entry after mp4files are uploaded bug https://kaltura.atlassian.net/browse/LIV-1032
                self.logi.appendMsg('INFO - AFTER FIRST STOP STREAMING:Going to set AccessControl id after mp4 files are uploaded to Recording entry with HLS short segment-Simulive-AWS + str(self.access_control_id_DP_FOR_VODentry) +' + str(self.access_control_id_DP_FOR_VODentry) + ', Recording_EntryID =' + str(FirstRecording_EntryID))
                base_entry = KalturaBaseEntry()
                base_entry.accessControlId = self.access_control_id_DP_FOR_VODentry
                result = self.client.baseEntry.update(FirstRecording_EntryID, base_entry)

            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER FIRST STOP STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 2:
               # added sleepUntil_PlaybackVerifications=10sec for starting caption on recording entry(delay)
               time.sleep(5)
               rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.recorded_entrieslst, boolShouldPlay=True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,ClosedCaption=True,Protocol="http",sleepUntil_PlaybackVerifications=20,ServerURL=self.ServerURL)
               time.sleep(5)
               timeout = timeout + 1
               if rc == False and timeout < 2:
                   self.logi.appendMsg("INFO - ****** AFTER FIRST STOP STREAMING:Going to play AGAIN after player CACHE ISSUE (No caption ICONF on the PLAYER)RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                   time.sleep(60)  # Time for player cache issue
               if not rc and timeout >= 2:  # Change condition
                   print("FAIL - AFTER FIRST STOP STREAMING:Going to play RECORDED ENTRY with caption after mp4 conversion - Retry count:timeout = " + str(timeout))
                   testStatus = False
                   return
               if self.seenAll_justOnce_flag == True and rc != False:  # Change condition
                   seenAll = True
                   break

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ############### Wait RestartDowntime=5 minutes until restart streaming
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



            #HERE - WORKING ON playback failed due to no caption on player after restart need to check
            ######################## RESTART streaming - Caption verification on playback
            self.logi.appendMsg("INFO - ************** RESTART:Going to play live entries with Live caption on PlayerVersion= " + str(self.PlayerVersion) + "  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
            while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 2:  # Change condition
                # BUG Protocol="https" - Need to user https for playing caption on VOD entry
                ##################***** Because of the bug I changed it from sniffer_fitler_After_Mp4flavorsUpload to sniffer_fitler_Before_Mp4flavorsUpload
                rc_MatchValue = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst,boolShouldPlay=True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,sniffer_fitler=self.sniffer_fitler,Protocol="http", MatchValue=True,ServerURL=self.ServerURL)
#                 time.sleep(5)
                timeout = timeout + 1
                if rc_MatchValue == False and timeout < 2:
                    self.logi.appendMsg("INFO - ****** Going to play AGAIN after player CACHE ISSUE (No caption ICONF on the PLAYER)   - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                    time.sleep(60)  # Time for player cache issue
                if not rc_MatchValue and timeout >= 2:  # Change condition
                    print("FAIL - Going to play LIVE ENTRY with caption - Retry count:timeout = " + str(timeout))
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True and rc_MatchValue != False:  # Change condition
                    seenAll = True
                    break
                self.logi.appendMsg("PASS - Playback of PlayerVersion= " + str(self.PlayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### AFTER RESTART STREAMING:Get recordedEntryId from the live entry by API --->>>>>>>>>>HERE
            OLD_Recording_entryId= str(recorded_entry.id) # Save the previous vod/recording entry id
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to take NEW recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            SecondRecording_EntryID = entryLiveStream.recordedEntryId
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Verify that the same vod entry stays (No creation of new entry)
            if FirstRecording_EntryID != SecondRecording_EntryID:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING-APPEND:VOD entry ID is different from the first one.FirstRecording_EntryID  = " + FirstRecording_EntryID + ", SecondRecording_EntryID = " + str(SecondRecording_EntryID) + ", LIVE ENTRY = " + self.entryId)
                testStatus = False
                return
            self.logi.appendMsg("PASS - AFTER RESTART STREAMING-APPEND:VOD entry ID stays the same.FirstRecording_EntryID  = " + FirstRecording_EntryID + ", SecondRecording_EntryID = " + str(SecondRecording_EntryID) + ", LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            ############
            #Create new player of latest version -  Create V2/3 Player because of cache issues
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
            ############
            # ##################################################### BUG LIV-1032 on QA env
            if self.env == 'testing':
                # Set accessControl with delivery profile for DP 1113(HLS short segment-Simulive-AWS)- Playback issue with VOD entry after mp4files are uploaded bug https://kaltura.atlassian.net/browse/LIV-1032
                self.logi.appendMsg('INFO - AFTER RESTART STREAMING:Going to re-set back default AccessControl id before mp4 files are uploaded(klive) to Recording entry with HLS short segment-Simulive-AWS + str(self.access_control_id_Default) +' + str(self.access_control_id_Default) + ', Recording_EntryID =' + str(FirstRecording_EntryID))
                base_entry = KalturaBaseEntry()
                base_entry.accessControlId = self.access_control_id_Default
                result = self.client.baseEntry.update(SecondRecording_EntryID, base_entry)
            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload +  " for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.recorded_entrieslst, boolShouldPlay=True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,ClosedCaption=True, Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            time.sleep(5)
            # ****** Livedashboard - Channels tab
            self.logi.appendMsg("INFO  - AFTER RESTART STREAMING:Going to verify live dashboard")
            self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
            rc = self.LiveDashboard.Verify_LiveDashboard(logi=self.logi, LiveDashboardURL=self.LiveDashboardURL,
                                                         entryId=self.entryId, PublisherID=self.PublisherID,
                                                         ServerURL=self.ServerURL, UserSecret=self.UserSecret, env=self.env,
                                                         Flag_Transcoding=False,
                                                         Live_Cluster_Primary=self.Live_Cluster_Primary,
                                                         First_navigateTo="Recordings")
            if rc == True:
                self.logi.appendMsg("PASS  - Verify_LiveDashboard")
            else:
                self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                testStatus = False


            #kill ffmpeg ps
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to END streams by kill FoundByProcessId=" + str(ffmpegOutputString) + " , Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
            stop_time2 = datetime.datetime.now().timestamp() # Save stop time of stream

            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Wait about 1.5 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # *********************************************
            # Get redirectEntryId from API
            entryLiveStream = self.client.liveStream.get(self.entryId)
            SecondRecording_redirectEntryId = str(entryLiveStream.redirectEntryId)  # Save the second recording redirectEntryID
            if SecondRecording_redirectEntryId != FirstRecording_redirectEntryId:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:APPEND-SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId) + " is different from FirstRecording_redirectEntryId = " + str(FirstRecording_redirectEntryId))
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:APPEND-SecondRecording_redirectEntryId = " + str(SecondRecording_redirectEntryId) + " is equal to FirstRecording_redirectEntryId = " + str(FirstRecording_redirectEntryId))

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
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst, boolShouldPlay=True, PlayerVersion=self.PlayerVersion,sniffer_fitler=str(SecondRecording_redirectEntryId),ClosedCaption=True,Protocol="http",ServerURL=self.ServerURL)
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
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client, SecondRecording_EntryID, recorded_entry,expectedFlavors_totalCount=1) # 1 expectedFlavors_totalCount is passthrough
            if rc == True:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + entryLiveStream.recordedEntryId)
                durationSecondRecording = int(self.client.baseEntry.get(recorded_entry.id).duration)  # Save the duration of the second recorded entry id after mp4 flaovrs uploaded
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                testStatus = False
                return

            ######## Get version of the second recording on the Vod entry id
            # entry_id = entryLiveStream.recordedEntryId
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to verify APPENED-REPLACED of the flavors.recordedEntryId = " + entryLiveStream.recordedEntryId)
            context_data_params = KalturaEntryContextDataParams()
            Second_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
            timeout=0
            while Second_RecordedEntry_Version == None:
                time.sleep(20)
                Second_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                timeout = timeout + 1
                if timeout >= 30: # 10 minutes timout for waiting to version update
                    self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return
            timeout=0
            while int(First_RecordedEntry_Version) == Second_RecordedEntry_Version:
                time.sleep(60)
                Second_RecordedEntry_Version = int(self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).version)
                timeout=timeout+1
                if timeout >=15:# timeout after 15 mintues
                    self.logi.appendMsg("FAIL - AFTER RESTART STREAMING-TIMEOUT:APPENED-REPLACED of the flavors was NOT done after waiting 15 minutes.recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return
            self.logi.appendMsg("PASSED - AFTER RESTART STREAMING:APPENED-REPLACED of the flavors was done.recordedEntryId = " + entryLiveStream.recordedEntryId + " , First_RecordedEntry_Version" + str(First_RecordedEntry_Version) + ", Second_RecordedEntry_Version" + str(Second_RecordedEntry_Version))


            #######################CAPTION ASSETS ON VOD entry
            self.logi.appendMsg("INFO -  AFTER RESTART STREAMING:Going to verify captionAssetList_result on recordedEntryId = " + entryLiveStream.recordedEntryId)
            rc = self.liveObj.captionAssetOnVODentry(self.client, self.KalturaStreamContainerArray, entryLiveStream.recordedEntryId, CntOfCaptions=self.CntOfCaptions)
            if rc != True:
                self.logi.appendMsg("FAIL -  AFTER RESTART STREAMING:VOD entry captionAssetList_result verification.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                testStatus = False
                return
            self.logi.appendMsg("PASS -  AFTER RESTART STREAMING:VOD entry captionAssetList_result verification.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            #######################

            # Waiting about 1 minutes before playing the recorded entry after mp4 flavors uploaded with ready status-->Total need 2 minutes becuase the livedashboard verification , reduce it to 1min
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Wait antoher 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)

            #Create new player of latest version -  Create V2/3 Player because of cache issues
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

            # ##################################################### BUG LIV-1032 on QA env
            if self.env == 'testing':
                # Set accessControl with delivery profile for DP 1113(HLS short segment-Simulive-AWS)- Playback issue with VOD entry after mp4files are uploaded bug https://kaltura.atlassian.net/browse/LIV-1032
                self.logi.appendMsg('INFO - AFTER RESTART STREAMING:Going to set AccessControl id after mp4 files are uploaded to Recording entry with HLS short segment-Simulive-AWS + str(self.access_control_id_DP_FOR_VODentry) +' + str(self.access_control_id_DP_FOR_VODentry) + ', Recording_EntryID =' + str(FirstRecording_EntryID))
                base_entry = KalturaBaseEntry()
                base_entry.accessControlId = self.access_control_id_DP_FOR_VODentry
                result = self.client.baseEntry.update(FirstRecording_EntryID, base_entry)
            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon or sniffer_fitler_After_Mp4flavorsUpload
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 2:
                # added sleepUntil_PlaybackVerifications=10sec for starting caption on recording entry(delay)
                time.sleep(5)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.recorded_entrieslst,boolShouldPlay=True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,ClosedCaption=True,Protocol="http",sleepUntil_PlaybackVerifications=20,ServerURL=self.ServerURL)
                time.sleep(5)
                timeout = timeout + 1
                if rc == False and timeout < 2:
                    self.logi.appendMsg("INFO - ****** AFTER RESTART STREAMING:Going to play AGAIN after player CACHE ISSUE (No caption ICONF on the PLAYER)RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                    time.sleep(60)  # Time for player cache issue
                if not rc and timeout >= 2:  # Change condition
                    print("FAIL -AFTER RESTART STREAMING:Going to play RECORDED ENTRY with caption after mp4 conversion - Retry count:timeout = " + str(timeout))
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True and rc != False:  # Change condition
                    seenAll = True
                    break

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            # Cal recording duration after mp4 flavors are uploaded for the second recording after restart
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING-APPEND:Going to verify DURATION of vod entry after the second recording.Recording_EntryID = " + str(FirstRecording_EntryID))
            #recordingTime1=stop_time-start_streaming
            recordingTime2=int(stop_time2-start_streaming2)
            Expected_TotalRecordingTime=int(recordingTime1 + recordingTime2) # Expected total duration of the two vod entries
            Actual_TotalRecordingTime=int(durationSecondRecording) # Actual total duration of the two vod entries is the second recording duration in case of append
            #Compare total duration of the vod entry after two recording
            if (0 <= Expected_TotalRecordingTime % Actual_TotalRecordingTime <= 40) or (0 <= Actual_TotalRecordingTime % Expected_TotalRecordingTime <= 40):#Until 40 seconds of delay between expected to actual duration
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING-APPEND:TOTAL recording duration is OK for VOD entry. Actual_TotalRecordingTime=" + str(Actual_TotalRecordingTime) + " , Expected_TotalRecordingTime = " + str(Expected_TotalRecordingTime) + " , FirstRecording_EntryID = " + str(FirstRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING-APPEND:TOTAL recording duration is NOT as expected for VOD entry. Actual_TotalRecordingTime=" + str(Actual_TotalRecordingTime) + " , Expected_TotalRecordingTime = " + str(Expected_TotalRecordingTime) + " , FirstRecording_EntryID = " + str(FirstRecording_EntryID))
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
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst,boolShouldPlay=True,PlayerVersion=self.PlayerVersion,sniffer_fitler=str(SecondRecording_redirectEntryId_AfterMP4files),ClosedCaption=True,Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Second STOP STREAMING(after mp4 uploaded)-redirectEntryId:LIVE ENTRY Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

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
           self.practitest.post(self.Practi_TestSet_ID,'976','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID,'976','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_976_LiveCaptionReach_Pass_RecordingAPPENDRestartAbove5min_redirectEntry.py -s')
    #===========================================================================
        
        
        