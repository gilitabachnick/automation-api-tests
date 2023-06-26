'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_x915_SimuliveToLiveMAIN_isContentInterruptibleTrue.py
  @desc : this test check E2E test of  test_915_SimuliveToLiveMAIN_isContentInterruptibleTrue - Create simulive event by ASSAF PHP script and then play the entry on LIVE logic platform
 without Access control_delivery Profile
 1)Update scheduling event by API with following fields(make sure that all the entries with same flavors converted):
 preStartEntryId.mp4 --> duration 1
 MainEntryId.mp4     --> duration 10
 postEndEntryId.mp4  --> duration 5
 * Precondition to upload those 3 files to QA env and PROD env
 Play the Simulive with all parts duration - preStartEntryId + MainEntryId + postEndEntryId
 Set isContentInterruptible = True
 Verification playback during the startDate / Pre + Verify sniffer_fitler_VOD_Simulive = 'qa-aws-vod;-v1-a1.ts'
 2) Start streaming the simulive entry on the MAIN areas:
  Verify that after arriving to MAIN area(isContentInterruptible = True) -> The live entry content is played on the simulive entry.
 Verify playback of the live streaming on the simulive entry
 Verify sniffer_fitler_VOD_Simulive='klive-stg;s32.ts'
 SIMULIVE: /hlsm/
 LIVE: /hls/
 ffmpeg -ss 00:01:00 -i input.mp4 -to 00:02:00 -c copy output.mp4

 https://kaltura.atlassian.net/wiki/spaces/LiveTeam/pages/2089326382/Simulive+-+how+to+configure
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

from KalturaClient.Plugins.Core import *

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter2
import Config
import Practitest
import uiconf
import tearDownclass
import MySelenium

import live
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
import threading
import queue
import ast
import LiveDashboard
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
#Set Jenkins parameters
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
IsSRT = os.getenv('IsSRT')
if str(IsSRT) == 'true':
    IsSRT = True
else:
    IsSRT = False

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):

        os.system("taskkill /IM chromedriver.exe /F")
        os.system("taskkill /IM chrome.exe /F")
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            # Streaming details
            self.url= "www.kaltura.com"
            #self.playerId = "46022611"# v3 player
            self.PublisherID = inifile.RetIniVal(section, 'SIMULIVE_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'SIMULIVE_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.configInI_ForPHPscript_Env = "config.ini" #set the KMS config in Production
            print('PRODUCTION ENVIRONMENT')
            #########SIMULIVE CONFIG
            self.conversionProfileID = "17469513"#$argv[8]; // $config[$env]['transcodingProfile'];
            self.kwebcastProfileId = "16890803"#$argv[9]; // $config[$env]['entryMetadataProfileId'];
            self.eventsProfileId = "16890813"#$argv[10]; // $config[$env]['eventsProfileId'];
            #self.vodId = "1_7tn8q9y5"#$argv[11]; // $config[$env]['vodId'];
            self.MainEntryId = "1_mbm0aeve"#10 min duration# $argv[11]; // $config[$env]['vodId'];
            self.preStartEntryId = "1_b2x73t0y"# 1 minutes duration
            self.postEndEntryId = "1_n6mie47o"#5 min duration
            self.sniffer_fitler_SimuliveVOD = '/hlsm/'#'qa-aws-vod'
            self.sniffer_fitler_SimuliveToLIVE ='/hls/'##s32.ts'#'klive-stg;-s32.ts'
            self.PlayerV7_confVars = inifile.RetIniVal(section, 'PlayerV7_confVars')#'{"versions": {"kaltura-ovp-player": "{latest}", "playkit-kaltura-live": "{latest}"}, "langs": ["en"]}'
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            #self.playerId = "15225574"##"15224080" v3 player
            self.PublisherID = inifile.RetIniVal(section, 'SIMULIVE_PublisherID')#""
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'SIMULIVE_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.configInI_ForPHPscript_Env ="TestingConfig.ini"#"TestingConfig_SimuliveWithoutAC.ini" # #set the KMS config in testing.qa
            print('TESTING ENVIRONMENT')
            #########SIMULIVE CONFIG
            self.conversionProfileID = "30162"#$argv[8]; // $config[$env]['transcodingProfile'];
            self.kwebcastProfileId = "18242"#$argv[9]; // $config[$env]['entryMetadataProfileId'];
            self.eventsProfileId = "18243"#$argv[10]; // $config[$env]['eventsProfileId'];
            self.MainEntryId = "0_m8f9f3cy"#10 min duration
            self.preStartEntryId ="0_nwuqpww7" # 1 minutes duration
            self.postEndEntryId = "0_m5aia7c7"#5 min duration
            #self.sniffer_fitler_SimuliveVOD = 'qa-aws-vod;-v1-a1.ts'
            #self.sniffer_fitler_SimuliveToLIVE = 'klive-stg;-s32.ts'
            self.sniffer_fitler_SimuliveVOD = '/hlsm/'#'qa-aws-vod'
            self.sniffer_fitler_SimuliveToLIVE = '/hls/'#;s32.ts'#'klive-stg;-s32.ts'
            self.PlayerV7_confVars = inifile.RetIniVal(section, 'PlayerV7_confVars')#'{"versions":{"kaltura-ovp-player":"{latest}", "playkit-kaltura-live":"{canary}"},"langs":["en"]}'

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(inifile.RetIniVal(section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = inifile.RetIniVal(section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = inifile.RetIniVal(section, 'Live_Cluster_Backup')

        #***** SSH streaming server - Assaf PHP script location    
        self.SimulivePHPscript_host=""
        self.SimulivePHPscript_user=""
        self.SimulivePHPscript_pwd=""
        self.sleepUntilCloseBrowser=300#5min -(seconds) for waiting to close the browser after playback verification
        self.MinToPlay_BeforeStartStreaming=1
                     
        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        #self.filePath = "/home/kaltura/entries/disney_ma.mp4"

        #***** SSH streaming server - AWS LINUX
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        self.SchedulerEvent_sessionEndOffset = 16  # Total Duration of the SchedulerEvent_sessionEndOffset playback = preEntryId.duration + mainEntry.duration + postEntry.duration
        self.reduceMinutesFromStartTime = 11
        self.preStartEntryId_duration = 1  # preEntryid.Duration  1 minute
        self.SchedulerEvent_MainEntryId_duration = 5  # 3 minutes duration of self.MainEntryId
        self.SchedulerEvent_TotalSimulivePlaybackDuration=16#Total Duration of the SchedulerEvent_sessionEndOffset playback = preEntryId.duration + mainEntry.duration + postEntry.duration
        self.isContentInterruptible = True

        self.PlayerV7_config = '{\
          "disableUserCache": false,\
          "plugins": {\
           "kaltura-live": {}\
           },\
          "playback": {},\
          "provider": {\
            "env": {}\
          }\
        }'

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        #self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_915_SimuliveToLiveMAIN_isContentInterruptibleTrue')
        self.logi.initMsg('test_915_SimuliveToLiveMAIN_isContentInterruptibleTrue')
    
    def test_915_SimuliveToLiveMAIN_isContentInterruptibleTrue(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - Start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(5)
            
            # Create player of latest version -  Create V2/3 Player
            self.logi.appendMsg('INFO - Going to create latest V3')
            myplayer3 = uiconf.uiconf(self.client, 'livePlayer')
            self.player_v3 = myplayer3.addPlayer(None, self.env, False, False, "v3")  # Create latest player v3
            if isinstance(self.player_v3, bool):
                testStatus = False
                return
            else:
                self.playerId = self.player_v3.id
                # Update the config with closed caption of the new player v3/7
                id = int(self.player_v3.id)
                ui_conf = KalturaUiConf()
                ui_conf.confVars=self.PlayerV7_confVars
                ui_conf.config = self.PlayerV7_config
                result = self.client.uiConf.update(id, ui_conf)

            # Create live object with current player_v3
            self.logi.appendMsg('INFO - Created latest player V3 ' + str(self.player_v3))
            self.testTeardownclass.addTearCommand(myplayer3, 'deletePlayer(' + str(self.player_v3.id) + ')')
            # Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID,self.playerId)
            #self.playerId=15258466 # player dash on testing.qa env
            
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
            
            # Create Simulive Webcast event by Assaf script PHP 
            self.logi.appendMsg('INFO - Going to CreateSimuliveWecastByPHPscript:Create SIMULIVE ENTRY ,host=' + self.SimulivePHPscript_host + ' ,user = ' + self.SimulivePHPscript_user + ' , pwd =  ' + self.SimulivePHPscript_pwd)
            sessionTitle='AUTOMATION-SimuliveToLive_MAIN' + str(datetime.datetime.now())
            sessionTitle = '"' + sessionTitle + '"'
            #startTime= time.time() + (self.SchedulerEvent_sessionEndOffset+1)*60 #add 7minutes to startTime of the scheduling event(add another 1 minutes for the expected starttime of scheduling)
            startTime = time.time() + (self.SchedulerEvent_sessionEndOffset-self.reduceMinutesFromStartTime) * 60  #Expected startTime - reduce 14 minutes
            startTime_WithPreEntryIdDuration = startTime - self.preStartEntryId_duration*60 #reduction preStartEntryId_duration from the start_time of the scheduling event
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            print("startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            rc, LiveEntryId = self.liveObj.CreateSimuliveWecastByPHPscript(self.SimulivePHPscript_host,self.SimulivePHPscript_user,self.SimulivePHPscript_pwd,self.configInI_ForPHPscript_Env,sessionEndOffset=self.SchedulerEvent_MainEntryId_duration,startTime=startTime, sessionTitle=sessionTitle,env=self.env, PublisherID=self.PublisherID,UserSecret=self.UserSecret, url=self.ServerURL,conversionProfileID=self.conversionProfileID,kwebcastProfileId=self.kwebcastProfileId,eventsProfileId=self.eventsProfileId,vodId=self.MainEntryId)
            if rc == True:
                print("Pass " + LiveEntryId)
                self.logi.appendMsg('PASS - CreateSimuliveWecastByPHPscript LiveEntryId: ' + LiveEntryId + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')) + " , CurrentTime = " + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
            else:
                self.logi.appendMsg('FAIL - CreateSimuliveWecastByPHPscript')
                                  
            #time.sleep(2)
            self.entrieslst = []
            self.entryId = str(LiveEntryId)
            Entryobj = self.client.baseEntry.get(LiveEntryId)
            self.entrieslst.append(Entryobj)
            self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entryId) + '\')')

            self.logi.appendMsg('INFO - Going to get scheduler event ID by scheduleEvent.list.self.templateEntryId =' + str(self.entryId))
            # **** Get scheduler event ID *******:
            filter = KalturaLiveStreamScheduleEventFilter()
            filter.templateEntryIdEqual = self.entryId
            pager = KalturaFilterPager()
            scheduleEventOftemplateEntryId = self.client.schedule.scheduleEvent.list(filter, pager)
            schedule_event_id = scheduleEventOftemplateEntryId.objects[0].id
            schedule_event = KalturaLiveStreamScheduleEvent()
            # **** Update scheduler event *******:
            schedule_event.sourceEntryId = self.MainEntryId
            schedule_event.preStartEntryId = self.preStartEntryId
            schedule_event.postEndEntryId = self.postEndEntryId
            schedule_event.isContentInterruptible = self.isContentInterruptible
            schedule_event_KalturaLiveStreamScheduleEvent = self.client.schedule.scheduleEvent.update(schedule_event_id,schedule_event)
            print("schedule_event_KalturaLiveStreamScheduleEvent.preStartEntryId = " + str(schedule_event_KalturaLiveStreamScheduleEvent.preStartEntryId))
            print("schedule_event_KalturaLiveStreamScheduleEvent.postEndEntryId = " + str(schedule_event_KalturaLiveStreamScheduleEvent.postEndEntryId))
            print("schedule_event_KalturaLiveStreamScheduleEvent.id = " + str(schedule_event_KalturaLiveStreamScheduleEvent.id))
            print("schedule_event_KalturaLiveStreamScheduleEvent.startDate = " + str(datetime.datetime.fromtimestamp(schedule_event_KalturaLiveStreamScheduleEvent.startDate).strftime('%Y-%m-%d %H:%M:%S')))
            print("schedule_event_KalturaLiveStreamScheduleEvent.endDate = " + str(datetime.datetime.fromtimestamp(schedule_event_KalturaLiveStreamScheduleEvent.endDate).strftime('%Y-%m-%d %H:%M:%S')))
            print("schedule_event_KalturaLiveStreamScheduleEvent.isContentInterruptible = " + str(schedule_event_KalturaLiveStreamScheduleEvent.isContentInterruptible))

            # Playback verification of Simulive entries - boolShouldPlay=false->NO play until arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to NOT play SIMULIVE(boolShouldPlay=False) - before arriving to schedule_startTime " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            if startTime_WithPreEntryIdDuration > time.time():
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll==False:
                        time.sleep(2)
                        rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst,boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
                        time.sleep(5)
                        if not rc:
                            testStatus = False
                            self.logi.appendMsg("FAIL - SIMULIVE" + str(self.entryId) + " live entry played despite of boolShouldPlay=false(expected NO playback state) - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                            return
                        if self.seenAll_justOnce_flag ==True:
                            seenAll = True
            else:
                testStatus = False
                self.logi.appendMsg('FAIL - Passed time for SIMULIVE(boolShouldPlay=False) verification because startTime_WithPreEntryIdDuration < currentTime LiveEntryId: ' + LiveEntryId + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')) + " , CurrentTime = " + str(datetime.datetime.now()))

            self.logi.appendMsg("PASS - NO Playback (boolShouldPlay=false) of SIMULIVE" + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            self.logi.appendMsg("INFO - Going to wait for arriving to startTime_WithPreEntryIdDuration= " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            while startTime_WithPreEntryIdDuration > time.time():
               time.sleep(5)
            # Running as thread function Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode
            self.logi.appendMsg("INFO - Main : Before creating thread - Going to play SIMULIVE (after arriving to startTime_WithPreEntryIdDuration) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , TimeNow = " + str(datetime.datetime.now()))
            que = queue.Queue()
            x = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4, arg5, arg6: q.put(self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(arg1, arg2, arg3, arg4, arg5, arg6)), args=(que, self.entrieslst, True,self.MinToPlay_BeforeStartStreaming,self.PlayerVersion,self.sniffer_fitler_SimuliveVOD,self.sleepUntilCloseBrowser))  # reduce -16 mintes for the total 30-->TO 14 playback
            self.logi.appendMsg("INFO - Main : Before running thread - verifyAllEntriesPlayOrNoBbyOnlyPlayback -  " + str(datetime.datetime.now()))
            x.start()
            #startTime_SimulivePlayback=time.time()
            self.logi.appendMsg("INFO - Main : Wait for the thread to start playing the entry - entryId = " + str(self.entryId) + " , CurrentTime = " + str(datetime.datetime.now()))
            # x.join()
            self.logi.appendMsg("INFO - Waiting MinToPlay_BeforeStartStreaming = " + str(self.MinToPlay_BeforeStartStreaming) + " minutes")
            time.sleep(60*(self.MinToPlay_BeforeStartStreaming+1))  # Wait for the thread to start playing the entry - 2 minutes

            # Get primaryBroadcastingUrl from the SIMULIVE entry
            streamUrl= self.client.liveStream.get(self.entryId)
            #Current_primaryBroadcastingUrl = streamUrl.primaryBroadcastingUrl
            if IsSRT == True:
                Current_primaryBroadcastingUrl = streamUrl.primarySrtBroadcastingUrl
                primarySrtStreamId = streamUrl.primarySrtStreamId
                self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
            else:
                Current_primaryBroadcastingUrl = streamUrl.primaryBroadcastingUrl
            if self.env == 'testing':
                if self.Live_Change_Cluster == True:
                    Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
            self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** SIMULIVE ENTRY# , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , primaryBroadcastingUrl = " + str(Current_primaryBroadcastingUrl))
            if IsSRT == True:
                ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
            else:
                ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.entryId)
            # start ffmpeg by FoundByProcessId
            rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
            if rc == False:
                self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                testStatus = False
            #########################SIMULIVE Playback with live streaming
            time.sleep(40)  #Wait for the stream to start playing on the simulive entry

            PlayBrowser = None
            if self.env == 'prod':
                time.sleep(20)
            self.logi.appendMsg("INFO - *************** Verify playback of SIMULIVE TO LIVE Playback on Main entry area(after start streaming - klive): " + str(self.entryId) + " , TimeNow = " + str(datetime.datetime.now()))
            rc_SimuliveToLive = self.liveObj.verifyLiveisPlayingOverTime_Sniffer(PlayBrowser=PlayBrowser,entryList=self.entrieslst,boolShouldPlay=True, MinToPlayEntry=1,sniffer_fitler=self.sniffer_fitler_SimuliveToLIVE,QRCode=True, verifyPlayback=True)
            if rc_SimuliveToLive == True:
                self.logi.appendMsg("PASS  - verifyLiveisPlayingOverTime_Sniffer")
            else:
                self.logi.appendMsg("FAIL - verifyLiveisPlayingOverTime_Sniffer")
                testStatus = False

            self.logi.appendMsg("INFO  - Main: Wait for the thread to finish - verifyAllEntriesPlayOrNoBbyOnlyPlayback")
            x.join()
            rc = que.get()
            if rc == True:
                self.logi.appendMsg("PASS  - Main: thread return result verifyAllEntriesPlayOrNoBbyOnlyPlayback")
            else:
                self.logi.appendMsg("FAIL -  Main: thread verifyAllEntriesPlayOrNoBbyOnlyPlayback")
                testStatus = False

            # ****** Livedashboard verification
            self.logi.appendMsg("INFO  - Going to verify live dashboard")
            self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
            rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId, self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
            if rc == True:
                self.logi.appendMsg("PASS  - Verify_LiveDashboard")
            else:
                self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                testStatus = False
            # kill ffmpeg ps by FoundByProcessId
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID, FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId) + " , url= " + self.url)
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId) + " , url= " + self.url)
                testStatus = False
                return

        except Exception as e:
            print("ERROR.Exception = " + str(e))
            testStatus = False
            pass
             
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    
    def teardown_class(self):
        
        global testStatus
        
        print('#############')
        print(' Tear down - Wd.quit')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass        
        
        try:
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '915','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '915','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x915_SimuliveToLiveMAIN_isContentInterruptibleTrue.py -s')
    #===========================================================================
        
