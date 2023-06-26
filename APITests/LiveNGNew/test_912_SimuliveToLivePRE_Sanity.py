'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_912_SimuliveToLivePRE_Sanity.py
  @desc : this test check E2E test of  test_912_SimuliveToLivePRE_Sanity - Create simulive event by kaltura API and then play the entry on LIVE logic platform
 without Access control_delivery Profile
 1)Update scheduling event by API with following fields(make sure that all the entries with same flavors converted):
 preStartEntryId.mp4 --> duration 1
 MainEntryId.mp4     --> duration 3
 postEndEntryId.mp4  --> duration 2
 * Precondition to upload those 3 files to QA env and PROD env
 Play the Simulive with all parts duration - preStartEntryId + MainEntryId + postEndEntryId
 * You can find files on /home/kaltura/entries/Simulive_To_Live_Files (named mainForDual)
 Verification playback during the startDate / Pre + Verify sniffer_fitler_VOD_Simulive = 'qa-aws-vod;-v1-a1.ts'
 2) Start streaming the simulive entry on the PRE areas:
 Verify playback of the live streaming on the simulive entry
 Verify sniffer_fitler_VOD_Simulive='klive-stg;-s32.ts'
 SIMULIVE: /hlsm/
 LIVE: /hls/
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
import Simulive
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
import threading
import queue
import ast
import LiveDashboard
import StaticMethods
### Jenkins params ###
#===============================================================================
# cnfgCls = Config.ConfigFile("stam")
# #self.Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# self.Practi_TestSet_ID,isProd = 11,"false"
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

        self.logi = reporter2.Reporter2('test_912_SimuliveToLivePRE_Sanity')
        self.logi.initMsg('test_912_SimuliveToLivePRE_Sanity')

        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')

        # Environment BE server URL
        if self.ServerURL is None:
            self.ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')
        print("ServerURL = " + self.ServerURL)

        # LiveNG config partner:
        if self.PartnerID != None:
            self.PublisherID = self.PartnerID
            self.UserSecret = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'SIMULIVE_Partner_UserSecret')
        else:
            self.PublisherID = self.inifile.RetIniVal(self.section, 'SIMULIVE_PublisherID')  #QA 6814 #PROD 4281553
            self.UserSecret = self.inifile.RetIniVal(self.section, 'SIMULIVE_UserSecret')
        #Simulive params
        self.conversionProfileID = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SIMULIVE_conversionProfileID')  #QA "30162"  #PROD "17469513"
        self.kwebcastProfileId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SIMULIVE_kwebcastProfileId')  #QA "18242"  #PROD "16890803"
        self.MainEntryId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SimuliveToLivePRE_MainEntryId')#QA "0_1vlw5w0o" #PROD "1_njw9gegj"#10 min duration - File AUTOMATIONmainForDual_10min.mp4
        self.preStartEntryId =self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SimuliveToLivePRE_preStartEntryId')#QA "0_tvf86gsi" #PROD "1_reogx2ap" #10 min duration - File AUTOMATIONmainForDual_10min.mp4
        self.postEndEntryId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SimuliveToLivePRE_postEndEntryId')#QA "0_m8f9f3cy"  #PROD"1_mbm0aeve" #10 min duration - File AUTOMATIONmainForDual_10min.mp4

        #Simulive playback
        self.sniffer_fitler_SimuliveVOD = '/hlsm/'#'qa-aws-vod'
        self.sniffer_fitler_SimuliveToLIVE = '/hls/'  # ts search for each flavor on flavorList - Delivery profile 1033:Live packager hls -redirect
        self.PlayerV7_confVars = self.inifile.RetIniVal(self.section, 'PlayerV7_confVars')#'{"versions":{"kaltura-ovp-player":"{latest}", "playkit-kaltura-live":"2.2.5"},"langs":["en"]}'

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sleepUntilCloseBrowser=180#240(seconds) for waiting to close the browser after playback verification
        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        #self.filePath = "/home/kaltura/entries/disney_ma.mp4"

        #***** Playback config
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
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

        #Simulive params:
        self.SchedulerEvent_sessionEndOffset = 30  # Total Duration of the SchedulerEvent_sessionEndOffset playback = preEntryId.duration + mainEntry.duration + postEntry.duration
        self.reduceMinutesFromStartTime = 14
        self.preStartEntryId_duration = 10  # preEntryid.Duration  1 minute
        self.SchedulerEvent_MainEntryId_duration = 10  # 3 minutes duration of self.MainEntryId
        self.SchedulerEvent_TotalSimulivePlaybackDuration=15#Total Duration of the SchedulerEvent_sessionEndOffset playback = preEntryId.duration + mainEntry.duration + postEntry.duration
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.logi = reporter2.Reporter2('test_912_SimuliveToLivePRE_Sanity')
        #self.logi.initMsg('test_912_SimuliveToLivePRE_Sanity')
    
    def test_912_SimuliveToLivePRE_Sanity(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
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
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)
            # Create Simulive object with current player
            self.SimuliveObj = Simulive.Simulivecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)
            
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
            
            # Create Simulive Webcast event by Kaltura API
            self.logi.appendMsg('INFO - Going to perform Simulive_Add:Create SIMULIVE ENTRY')
            sessionTitle='AUTOMATION-SimuliveToLive_PRE' + str(datetime.datetime.now())
            #sessionTitle = '"' + sessionTitle + '"'
            startTime = time.time() + (self.SchedulerEvent_sessionEndOffset-self.reduceMinutesFromStartTime) * 60  #Expected startTime - reduce 14 minutes
            startTime_WithPreEntryIdDuration = startTime - self.preStartEntryId_duration*60 #reduction preStartEntryId_duration from the start_time of the scheduling event
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            print("startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            rc, LiveEntryId = self.SimuliveObj.Simulive_Add(client=self.client, UserSecret=self.UserSecret,
                                                            partner_id=self.PublisherID, entry_name=sessionTitle,
                                                            entry_conversionProfileId=self.conversionProfileID,
                                                            metadata_profile_id=self.kwebcastProfileId,
                                                            schedule_event_sourceEntryId=self.MainEntryId,
                                                            schedule_event_summary=sessionTitle,
                                                            schedule_event_startDate=startTime,
                                                            sessionEndOffset=self.SchedulerEvent_MainEntryId_duration,
                                                            preStartEntryId=self.preStartEntryId,
                                                            postEndEntryId=self.postEndEntryId)
            if rc == True:
                print("Pass " + LiveEntryId)
                self.logi.appendMsg('PASS - CreateSimuliveWecastByPHPscript LiveEntryId: ' + LiveEntryId + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')) + " , CurrentTime = " + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
            else:
                self.logi.appendMsg('FAIL - CreateSimuliveWecastByPHPscript')
                                  

            self.entrieslst = []
            self.entryId = str(LiveEntryId)
            Entryobj = self.client.baseEntry.get(LiveEntryId)
            self.entrieslst.append(Entryobj)
            self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entryId) + '\')')

            # Playback verification of Simulive entries - boolShouldPlay=false->NO play until arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to NOT play SIMULIVE(boolShouldPlay=False) - before arriving to schedule_startTime " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            if startTime_WithPreEntryIdDuration > time.time():
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll==False:
                        time.sleep(2)
                        rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst,boolShouldPlay=False,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
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

            #self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True, 1, self.PlayerVersion,self.sniffer_fitler_SimuliveVOD,self.sleepUntilCloseBrowser, self.ServerURL)

            self.logi.appendMsg("INFO - Going to wait for arriving to startTime_WithPreEntryIdDuration= " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            while startTime_WithPreEntryIdDuration > time.time():
               time.sleep(5)
            self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True,1,self.PlayerVersion,self.sniffer_fitler_SimuliveVOD,self.sleepUntilCloseBrowser,self.ServerURL)
            # Running as thread function Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode
            self.logi.appendMsg("INFO - Main : Before creating thread - Going to play SIMULIVE (after arriving to startTime_WithPreEntryIdDuration) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , TimeNow = " + str(datetime.datetime.now()))
            que = queue.Queue()
            x = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4, arg5, arg6, arg7: q.put(self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(arg1, arg2, arg3, arg4, arg5, arg6, arg7)), args=(que, self.entrieslst, True,1,self.PlayerVersion,self.sniffer_fitler_SimuliveVOD,self.sleepUntilCloseBrowser,self.ServerURL))  # reduce -16 mintes for the total 30-->TO 14 playback

            self.logi.appendMsg("INFO - Main : Before running thread - verifyAllEntriesPlayOrNoBbyOnlyPlayback -  " + str(datetime.datetime.now()))
            x.start()
            self.logi.appendMsg("INFO - Main : Wait for the thread to start playing the entry - entryId = " + str(self.entryId) + " , CurrentTime = " + str(datetime.datetime.now()))
            # x.join()
            time.sleep(60)  # Wait for the thread to start playing the entry

            # Get primaryBroadcastingUrl from the SIMULIVE entry
            streamUrl= self.client.liveStream.get(self.entryId)
            if self.IsSRT == True:
                Current_primaryBroadcastingUrl = streamUrl.primarySrtBroadcastingUrl
                primarySrtStreamId = streamUrl.primarySrtStreamId
                self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
            else:
                Current_primaryBroadcastingUrl = streamUrl.primaryBroadcastingUrl
            if self.env == 'testing':
                if self.Live_Change_Cluster == True:
                    Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
            self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** SIMULIVE ENTRY# , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , primaryBroadcastingUrl = " + str(Current_primaryBroadcastingUrl))
            if self.IsSRT == True:
                ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
            else:
                ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),streamUrl.streamName)
            # start ffmpeg by FoundByProcessId
            rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
            if rc == False:
                self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
            #########################SIMULIVE Playback with live streaming
            time.sleep(40)  #Wait for the stream to start playing on the simulive entry

            PlayBrowser = None
            self.logi.appendMsg("INFO - *************** SIMULIVE TO LIVE Playback(after start streaming - klive): " + str(self.entryId) + " , TimeNow = " + str(datetime.datetime.now()))
            rc_SimuliveToLive = self.liveObj.verifyLiveisPlayingOverTime_Sniffer(PlayBrowser=PlayBrowser,entryList=self.entrieslst,boolShouldPlay=True,MinToPlayEntry=1,sniffer_fitler=self.sniffer_fitler_SimuliveToLIVE,QRCode=True,verifyPlayback=True)
            if rc_SimuliveToLive == True:
                self.logi.appendMsg("PASS  - verifyLiveisPlayingOverTime_Sniffer")
            else:
                self.logi.appendMsg("FAIL - verifyLiveisPlayingOverTime_Sniffer")
                testStatus = False
            ########################
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
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId))
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
           self.practitest.post(self.Practi_TestSet_ID, '912','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '912','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_912_SimuliveToLivePRE_Sanity.py -s')
    #===========================================================================
        
