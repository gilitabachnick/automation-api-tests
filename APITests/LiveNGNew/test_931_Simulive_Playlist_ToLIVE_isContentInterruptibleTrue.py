'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_931_Simulive_Playlist_ToLIVE_isContentInterruptibleTrue.py
  @desc : this test check E2E test of  test_931_Simulive_Playlist_ToLIVE - Create simulive event by kaltura API and then play the entry on LIVE logic platform
 without Access control_delivery Profile
 1) Create manual playlist by API
 * Precondition to upload those 3 files to QA env and PROD env
 PlaylistItem1 =  3 minutes duration mainForDual_Item1_3min.mp4
 PlaylistItem2 =  3 minutes duration mainForDual_Item2_3min.mp4
 PlaylistItem3 =  4 minutes duration mainForDual_Item3_4min.mp4
 2)Update scheduling event by API with following fields:
 schedule_event.sourceEntryId = self.MainEntryId # PlaylistId
 Play the Simulive with all parts duration -> PlaylistItem1,PlaylistItem2,PlaylistItem3
 3) Start streaming the simulive entry on the playlist(MAIN) areas:
  Verify that after arriving to MAIN/PLAYLIST area(isContentInterruptible = True) -> The live entry content is played on the simulive entry instead of playlist items.
 Verify playback of the live streaming on the simulive entry
 Verify sniffer_fitler_VOD_Simulive='klive-stg;s32.ts'
 SIMULIVE: /hlsm/
 LIVE: /hls/

https://kaltura.atlassian.net/wiki/spaces/LiveTeam/pages/2089326382/Simulive+-+how+to+configure
Create files for playlist - 3 items:
ffmpeg -ss 00:00:00 -i mainForDual.mp4 -to 00:03:00 -c copy mainForDual_Item1_3min.mp4
ffmpeg -ss 00:03:00 -i mainForDual.mp4 -to 00:03:00 -c copy mainForDual_Item2_3min.mp4
ffmpeg -ss 00:06:00 -i mainForDual.mp4 -to 00:04:00 -c copy mainForDual_Item3_4min.mp4
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
import Entry
import live
import Simulive

import threading
import queue
import ast
import LiveDashboard
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
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
            self.PublisherID = self.inifile.RetIniVal(self.section, 'SIMULIVE_PublisherID')  # QA 6814 #PROD 4281553
            self.UserSecret = self.inifile.RetIniVal(self.section, 'SIMULIVE_UserSecret')
        # Simulive params
        self.conversionProfileID = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'SIMULIVE_conversionProfileID')  # QA "30162"  #PROD "17469513"
        self.kwebcastProfileId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'SIMULIVE_kwebcastProfileId')  # QA "18242"  #PROD "16890803"
        self.PlaylistItem1 = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'Simulive_Playlist_ToLIVE_isContentInterruptibleTrue_PlaylistItem1_Dual3min')  # QA "0_vwe2lkvf" #PROD "1_bbr2bbzi" # 3 minutes duration mainForDual_Item1_3min.mp4
        self.PlaylistItem2 =self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'Simulive_Playlist_ToLIVE_isContentInterruptibleTrue_PlaylistItem2_Dual3min')  # QA "0_763bvu61" #PROD "1_jdgsfsyu" # 3 minutes duration mainForDual_Item2_3min.mp4
        self.PlaylistItem3 = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'Simulive_Playlist_ToLIVE_isContentInterruptibleTrue_PlaylistItem3_Dual4min')  # QA "0_1b6rcwjq"  #PROD"1_6yfzq62d" # 4 minutes duration mainForDual_Item3_4min.mp4

        # Simulive playback
        self.sniffer_fitler_SimuliveVOD = '/hlsm/'  # 'qa-aws-vod'
        self.sniffer_fitler_SimuliveToLIVE = '/hls/'  # ts search for each flavor on flavorList - Delivery profile 1033:Live packager hls -redirect
        #self.sniffer_fitler_SimuliveToLIVE = '/hls/;-s32'  # ts search for each flavor on flavorList - Delivery profile 1033:Live packager hls -redirect
        self.PlayerV7_confVars = self.inifile.RetIniVal(self.section,'PlayerV7_confVars')  # '{"versions":{"kaltura-ovp-player":"{latest}", "playkit-kaltura-live":"2.2.5"},"langs":["en"]}'

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

        # Playback config
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        self.SchedulerEvent_sessionEndOffset = 10 #Total Duration of the SchedulerEvent_sessionEndOffset playback -> Playlist all items duration(PlaylistItem1+PlaylistItem2+PlaylistItem3)
        self.sleepUntilCloseBrowser = 300  # 5min -(seconds) for waiting to close the browser after playback verification
        self.MinToPlay_BeforeStartStreaming = 1
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
        #Simulive Config
        self.SchedulerEvent_AddMinToStartTime=2 #Time to add for startTime
        self.isContentInterruptible = True

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_931_Simulive_Playlist_ToLIVE_isContentInterruptibleTrue')
        self.logi.initMsg('test_931_Simulive_Playlist_ToLIVE_isContentInterruptibleTrue')
    
    def test_931_Simulive_Playlist_ToLIVE_isContentInterruptibleTrue(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(5)

            # Create manual playlist by API
            self.logi.appendMsg('INFO - Going to create manual playlist.')
            playlistName = "AUTOMATION-Simulive_Playlist_BasicFlow" + '_' + str(datetime.datetime.now())
            Entryobj = Entry.Entry(client=self.client, entryName=playlistName, entryDesc="", entryTags="", entryAdminTag="", entryCategory="", intentryType=KalturaPlaylist())
            playlistContent = self.PlaylistItem1 + "," + self.PlaylistItem2 + "," + self.PlaylistItem3
            rc,PlaylistManualId = Entryobj.CreatePlaylistManual(playlistContent)
            if rc==False:
                self.logi.appendMsg('FAIL - CreatePlaylistManual.')
                testStatus = False
                return
            self.logi.appendMsg('PASS - CreatePlaylistManual.PlaylistManualId =' + str(PlaylistManualId))
            self.MainEntryId=PlaylistManualId #Set playlist as MainEntryId/sourceEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(PlaylistManualId) + '\')')
            
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
                # Update the config with live-plugin of the new player v3/7
                id = int(self.player.id)
                ui_conf = KalturaUiConf()
                ui_conf.confVars = self.PlayerV7_confVars
                ui_conf.config = self.PlayerV7_config
                result = self.client.uiConf.update(id, ui_conf)

            self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')    
            
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
           # Create Simulive object with current player
            self.SimuliveObj = Simulive.Simulivecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)

            # Create Simulive Webcast event by kaltura API
            self.logi.appendMsg('INFO - Going to perform Simulive_Add:Create SIMULIVE ENTRY')
            sessionTitle = 'AUTOMATION-Simulive_Playlist_ToLIVE' + str(datetime.datetime.now())
            #sessionTitle = '"' + sessionTitle + '"'
            startTime = time.time() + (self.SchedulerEvent_AddMinToStartTime) * 60
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            #rc, LiveEntryId = self.liveObj.CreateSimuliveWecastByPHPscript(self.SimulivePHPscript_host,self.SimulivePHPscript_user,self.SimulivePHPscript_pwd,self.configInI_ForPHPscript_Env,sessionEndOffset=self.SchedulerEvent_sessionEndOffset,startTime=startTime, sessionTitle=sessionTitle,env=self.env, PublisherID=self.PublisherID,UserSecret=self.UserSecret, url=self.ServerURL,conversionProfileID=self.conversionProfileID,kwebcastProfileId=self.kwebcastProfileId,eventsProfileId=self.eventsProfileId,vodId=self.MainEntryId)
            rc, LiveEntryId = self.SimuliveObj.Simulive_Add(client=self.client, UserSecret=self.UserSecret,
                                                        partner_id=self.PublisherID, entry_name=sessionTitle,
                                                        entry_conversionProfileId=self.conversionProfileID,
                                                        metadata_profile_id=self.kwebcastProfileId,
                                                        schedule_event_sourceEntryId=self.MainEntryId,
                                                        schedule_event_summary=sessionTitle,
                                                        schedule_event_startDate=startTime,
                                                        sessionEndOffset=self.SchedulerEvent_sessionEndOffset,
                                                        isContentInterruptible=self.isContentInterruptible)
            if rc == True:
                print("Pass " + LiveEntryId)
                self.logi.appendMsg('PASS - CreateSimuliveWecastByPHPscript LiveEntryId: ' + LiveEntryId + " , startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')) + " , CurrentTime = " + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
            else:
                self.logi.appendMsg('FAIL - CreateSimuliveWecastByPHPscript')

            self.entrieslst = []
            self.entryId = str(LiveEntryId)
            Entryobj = self.client.baseEntry.get(LiveEntryId)
            self.entrieslst.append(Entryobj)
            self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entryId) + '\')')

            # Playback verification of Simulive entries - boolShouldPlay=false->NO play until arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to NOT play SIMULIVE(boolShouldPlay=False) - before arriving to schedule_startTime " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            if startTime > time.time():
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
                self.logi.appendMsg('FAIL - Passed time for SIMULIVE(boolShouldPlay=False) verification because startTime < currentTime LiveEntryId: ' + LiveEntryId + " , startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')) + " , CurrentTime = " + str(datetime.datetime.now()))

            self.logi.appendMsg("PASS - NO Playback (boolShouldPlay=false) of SIMULIVE" + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            self.logi.appendMsg("INFO - Going to wait for arriving to startTime= " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            while startTime > time.time():
                time.sleep(5)
            # Running as thread function Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode
            self.logi.appendMsg("INFO - Main : Before creating thread - Going to play SIMULIVE (after arriving to startTime_WithPreEntryIdDuration) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , TimeNow = " + str(datetime.datetime.now()))
            que = queue.Queue()
            x = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4, arg5, arg6, arg7: q.put(self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(arg1, arg2, arg3, arg4, arg5, arg6, arg7)), args=(que, self.entrieslst, True, self.MinToPlay_BeforeStartStreaming, self.PlayerVersion,self.sniffer_fitler_SimuliveVOD,self.sleepUntilCloseBrowser,self.ServerURL))  # reduce -16 mintes for the total 30-->TO 14 playback
            self.logi.appendMsg("INFO - Main : Before running thread - verifyAllEntriesPlayOrNoBbyOnlyPlayback -  " + str(datetime.datetime.now()))
            x.start()
            # startTime_SimulivePlayback=time.time()
            self.logi.appendMsg("INFO - Main : Wait for the thread to start playing the entry - entryId = " + str(self.entryId) + " , CurrentTime = " + str(datetime.datetime.now()))
            # x.join()
            self.logi.appendMsg("INFO - Waiting MinToPlay_BeforeStartStreaming = " + str(self.MinToPlay_BeforeStartStreaming) + " minutes")
            time.sleep(60 * (self.MinToPlay_BeforeStartStreaming + 1))  # Wait for the thread to start playing the entry - 2 minutes
            # Get primaryBroadcastingUrl from the SIMULIVE entry
            streamUrl = self.client.liveStream.get(self.entryId)
            # Current_primaryBroadcastingUrl = streamUrl.primaryBroadcastingUrl
            if self.IsSRT == True:
                Current_primaryBroadcastingUrl = streamUrl.primarySrtBroadcastingUrl
                primarySrtStreamId = streamUrl.primarySrtStreamId
                self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
            else:
                Current_primaryBroadcastingUrl = streamUrl.primaryBroadcastingUrl
            if self.env == 'testing':
                if self.Live_Change_Cluster == True:
                    Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
            self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** SIMULIVE ENTRY# , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId)  + " , primaryBroadcastingUrl = " + str(Current_primaryBroadcastingUrl))
            if self.IsSRT == True:
                ffmpegCmdLine, Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath,str(Current_primaryBroadcastingUrl),primarySrtStreamId)
            else:
                ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),streamUrl.streamName)
            # start ffmpeg by FoundByProcessId
            rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID, env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
            if rc == False:
                self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
            #########################SIMULIVE Playback with live streaming
            time.sleep(40)  # Wait for the stream to start playing on the simulive entry

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
            rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId, self.PublisherID,self.ServerURL, self.UserSecret, self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
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
           self.practitest.post(self.Practi_TestSet_ID, '931','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '931','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_931_Simulive_Playlist_ToLIVE_isContentInterruptibleTrue.py -s')
    #===========================================================================
        
