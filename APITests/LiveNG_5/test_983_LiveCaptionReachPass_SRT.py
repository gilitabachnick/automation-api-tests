'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_983_LiveCaptionReachPass_SRT.py
 @desc : this test check E2E test of new LiveNG entries Passthrough with SRT streaming by new logic function - host access run ffmpeg cmd
Test case:
Create live entry
Create schedulingEvent
Create Kaltura EntryVendorTask
Start streaming - until https://kaltura.atlassian.net/wiki/spaces/LiveTeam/pages/3778773251/Feature+Manager+-+technical+design  until manager feature is ready ->YOU MUST TO Start streaming after arriving to scheduleEvent.startTime AND  EntryVendorTaskId.status=3 processing
Verify Playback VTT
End streaming

 https://kaltura.atlassian.net/wiki/spaces/LiveTeam/pages/3754033425/Live+captions+testme+explanation
 interface EntryVendorTaskStatus extends BaseEnum
{
   const PENDING           = 1;
   const READY             = 2;     get ready status after arriving to endTime(verbit) or stop streaming
   const PROCESSING         = 3;    will update for sure just after arriving to startTime and start stream for 10sec
   const PENDING_MODERATION   = 4;
   const REJECTED              = 5;
   const ERROR             = 6;
   const ABORTED           = 7;
   const PENDING_ENTRY_READY  = 8;
   const SCHEDULED          = 9;
}
Scenario:
1)Create live entry
2)Create scheduleEvent:
scheduleEvent.add
scheduleEvent (KalturaScheduleEvent):kalturaLiveStreamScheduleEvent
recurrenceType (int):NONE
templateEntryId:0_rjrjo1jv
summary:
startDate:Now+5min
endDate


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
import ast
import re
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
        # LIVE CAPTION config profile
        self.reachProfileId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'reachProfileId')  # QA 310 #PROD 206622
        self.catalogItemId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'catalogItemId')  # QA 374 #PROD 14652
        # lowlatency access control
        #self.access_control_id_lowlatency = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'access_control_id_lowlatency')  # QA 29293#Prod 5982132

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3

        # Live caption parameters
        self.SchedulerEvent_AddMinToStartTime = 5  # Time to add for startTime - minutes
        self.SchedulerEvent_sessionEndTimeOffset = 30  # Time to add for EndTime from startTime  - minutes
        self.sniffer_fitler = '.vtt'

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_983_LiveCaptionReachPass_SRT')
        self.logi.initMsg('test_983_LiveCaptionReachPass_SRT')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)

    def test_983_LiveCaptionReachPass_SRT(self):
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveEntry_LiveCaptionReach_Pass_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

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

                self.logi.appendMsg("INFO - Wait for arriving to startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            while startTime > time.time():#Wait until SchedulerEvent.startTime
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
                self.logi.appendMsg("INFO - ****************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                if self.IsSRT == True:
                    ffmpegCmdLine, Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath,str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)

            ######### Start streaming - until https://kaltura.atlassian.net/wiki/spaces/LiveTeam/pages/3778773251/Feature+Manager+-+technical+design manager feature is ready - YOU MUST TO Start streaming after scheduleEvent.startTime and  EntryVendorTaskId.status=3 processing
            rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID, env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
            if rc == False:
                self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
            # ******* CHECK CPU usage of streaming machine
            self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " + self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))
            cmdLine = "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"
            rc, CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass,cmdLine)
            if rc == True:
                self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
            else:
                self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                testStatus = False
                return
            time.sleep(1)
            # ****** Livedashboard - Channels tab
            self.logi.appendMsg("INFO  - Going to verify live dashboard")
            self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
            rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId, self.PublisherID,self.ServerURL, self.UserSecret, self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
            if rc == True:
                self.logi.appendMsg("PASS  - Verify_LiveDashboard")
            else:
                self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                testStatus = False
            time.sleep(3)
            ########################Caption verification on playback
            self.logi.appendMsg("INFO - ************** Going to play live entries with Live caption on PlayerVersion= " + str(self.PlayerVersion) + "  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
            while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 2:  # Change condition
                # BUG Protocol="https" - Need to user https for playing caption on VOD entry
                ##################***** Because of the bug I changed it from sniffer_fitler_After_Mp4flavorsUpload to sniffer_fitler_Before_Mp4flavorsUpload
                rc_MatchValue = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst, boolShouldPlay=True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,sniffer_fitler=self.sniffer_fitler,Protocol="http", MatchValue=True,ServerURL=self.ServerURL)
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
            #Verify vtt url from playback
            self.logi.appendMsg("INFO -  Going to verify LiveCaption_VerifyPlaybackVTT MatchValue vtt url = " + str(rc_MatchValue))
            rc=self.liveObj.LiveCaption_VerifyPlaybackVTT(rc_MatchValue)
            if rc == False:
                self.logi.appendMsg("FAIL -  LiveCaption_VerifyPlaybackVTT")
                testStatus = False
            else:
                self.logi.appendMsg("PASS -  LiveCaption_VerifyPlaybackVTT")


            #kill ffmpeg ps   
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return    
           
                           
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
           self.practitest.post(self.Practi_TestSet_ID, '983','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '983','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_983_LiveCaptionReachPass_SRT.py -s')
    #===========================================================================
        
        
        