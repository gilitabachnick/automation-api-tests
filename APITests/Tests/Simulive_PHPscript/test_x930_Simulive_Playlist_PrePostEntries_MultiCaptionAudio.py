'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

 @test_name: test_x930_Simulive_Playlist_PrePostEntries_MultiCaptionAudio.py
  @desc : this test check E2E test of  test_930_Simulive_Playlist_PrePostEntries - Create simulive event by ASSAF PHP script and then play the entry on LIVE logic platform
 without Access control_delivery Profile

Precondition upload file with multi audio and multi caption, for example(entryid=0_we6l5ftx-auto,0_xw44h4sk-alex):
1)Upload file - Sintel,_the_Durian_Open_Movie_Project_(Source).mp4
with conversionProfile:
Basic/Small - WEB/MBL (H264/400)
Basic/Small - WEB/MBL (H264/600)
SD/Small - WEB/MBL (H264/900)
Audio-only ENG - (AAC)
Audio-only SPA - (AAC)
origin entry"0_we6l5ftx" QA env duration 14:47  (PROD 1_p7521yuw)
2)Go to KMC drilldown->caption tab->Upload:
Sintel_English_American.srt
Sintel_Spanish.srt
3)Create clip by KMC - **** You can upload playlist items from simulivePlaylistItems folder(linux /home/kaltura/entries) ****:
preStartEntryId = "0_nwuqpww7" # duration 1 LongCloDvRec_Pre (Source).mp4
CLIP1:PlaylistItem1 ="0_ozkr3qqn" --> Create clip of first part duration 4 minutes ->"AUTOMATION PlaylistITEM1_Clip of Sintel,_the_Durian_Open_Movie_Project_(Source).mp4"
CLIP2:PlaylistItem2 = "0_bxinlt68"--> Create clip of second part duration 4 minutes ->"AUTOMATION PlaylistITEM2_Sintel,_the_Durian_Open_Movie_Project_(Source) ITEM_2.mp4"
postEndEntryId = "0_mjm6yg64"# duration 2 minutes LongCloDvRec_Post.mp4
* Verify that all captions(English and Spanish) are played on each vod entry.
4)Add to clips multi audio flavors:
Audio-only ENG - (AAC)
Audio-only SPA - (AAC)
CLIP1:PlaylistItem1 ="0_ozkr3qqn"
CLIP2:PlaylistItem2 = "0_bxinlt68"
* Verify that the multi audio flavors are played on each vod entry.
5)Update scheduling event by API with following fields:
schedule_event.sourceEntryId = self.MainEntryId # PlaylistId
6)Play the Simulive with all parts duration -> preStartEntryId,PlaylistItem1,PlaylistItem2,postEndEntryId
7)Verification playback duration by QRlogic during the startDate / End Date --> preStart + PlaylistItems + postEnd
8)Verify multi captions and audio selection on the player v3


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
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Schedule import *
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

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

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
            #self.MainEntryId = "1_hlx558mn"  # $argv[11]; // $config[$env]['vodId'];
            self.preStartEntryId = "1_b2x73t0y"  # duration 1 minutes
            self.PlaylistItem1 = "1_x994jzqf"  # duration 4 minutes -CLIP1 including multi audio+caption (origin entry"0_we6l5ftx" )
            self.PlaylistItem2 = "1_ci436pbj"  # duration 4 minutes -CLIP2 including multi audio+caption(origin entry"0_we6l5ftx" )
            self.postEndEntryId = "1_qa9xteqo"  # duration 2 minutes
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
            #self.MainEntryId = "0_t3ahjz17"#"0_u68a15b0"# 3 minutes duration
            self.preStartEntryId = "0_nwuqpww7" # duration 1 minutes
            self.PlaylistItem1 = "0_ozkr3qqn"# duration 4 minutes -CLIP1 including multi audio+caption (origin entry"0_we6l5ftx" )
            self.PlaylistItem2 = "0_bxinlt68"# duration 4 minutes -CLIP2 including multi audio+caption(origin entry"0_we6l5ftx" )
            self.postEndEntryId = "0_mjm6yg64"# duration 2 minutes
        #***** SSH streaming server - Assaf PHP script location    
        self.SimulivePHPscript_host=""
        self.SimulivePHPscript_user=""
        self.SimulivePHPscript_pwd=""
                     
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        self.SchedulerEvent_sessionEndOffset = 11 #Total Duration of the SchedulerEvent_sessionEndOffset playback = preEntryId.duration + mainEntry.duration + postEntry.duration
        self.preStartEntryId_duration = 1  # preEntryid.Duration  0 minute -->Zero Meaning no preStartEntryId
        self.SchedulerEvent_MainEntryId_duration = 8 # duration of self.MainEntryId - Playlist items

        self.SchedulerEvent_AddMinToStartTime=3 #Time to add for startTime
        self.languageList = "Español;English"  # mMlti audio player selections
        self.languageList_Caption = "Spanish;English"  # Multi captions player selections
        self.sleepUntil_PlaybackVerifications = self.preStartEntryId_duration * 60 #- 15  # Wait Time(until passing the PreEntry) until arriving to the multi audio/captions + playback on the playlist items ,reduce 15 sec for start streaming/playing time
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_930_Simulive_Playlist_PrePostEntries_MultiCaptionAudio')
        self.logi.initMsg('test_930_Simulive_Playlist_PrePostEntries_MultiCaptionAudio')
    
    def test_930_Simulive_Playlist_PrePostEntries_MultiCaptionAudio(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - Start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(5)

            # Create manual playlist by API
            self.logi.appendMsg('INFO - Going to create manual playlist.')
            playlistName = "AUTOMATION-Simulive_Playlist_PrePost_MultiAudioCaption" + '_' + str(datetime.datetime.now())
            Entryobj = Entry.Entry(client=self.client, entryName=playlistName, entryDesc="", entryTags="", entryAdminTag="", entryCategory="", intentryType=KalturaPlaylist())
            playlistContent = self.PlaylistItem1 + "," + self.PlaylistItem2
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
            self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')    
            
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
            
            # Create Simulive Webcast event by Assaf script PHP 
            self.logi.appendMsg('INFO - Going to CreateSimuliveWecastByPHPscript:Create SIMULIVE ENTRY ,host=' + self.SimulivePHPscript_host + ' ,user = ' + self.SimulivePHPscript_user + ' , pwd =  ' + self.SimulivePHPscript_pwd)
            sessionTitle='AUTOMATION-SimulivePlaylist_PrePost_MultiAudioCaption' + str(datetime.datetime.now())
            sessionTitle = '"' + sessionTitle + '"'
            startTime= time.time() + (self.SchedulerEvent_AddMinToStartTime*60)
            startTime_WithPreEntryIdDuration = startTime - self.preStartEntryId_duration*60 #reduction preStartEntryId_duration from the start_time of the scheduling event
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            print("startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            rc, LiveEntryId = self.liveObj.CreateSimuliveWecastByPHPscript(self.SimulivePHPscript_host,self.SimulivePHPscript_user,self.SimulivePHPscript_pwd,self.configInI_ForPHPscript_Env,sessionEndOffset=self.SchedulerEvent_MainEntryId_duration,startTime=startTime, sessionTitle=sessionTitle,env=self.env, PublisherID=self.PublisherID,UserSecret=self.UserSecret, url=self.ServerURL,conversionProfileID=self.conversionProfileID,kwebcastProfileId=self.kwebcastProfileId,eventsProfileId=self.eventsProfileId,vodId=self.MainEntryId)
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
            schedule_event_KalturaLiveStreamScheduleEvent = self.client.schedule.scheduleEvent.update(schedule_event_id,schedule_event)
            print("schedule_event_KalturaLiveStreamScheduleEvent.preStartEntryId = " + str(schedule_event_KalturaLiveStreamScheduleEvent.preStartEntryId))
            print("schedule_event_KalturaLiveStreamScheduleEvent.postEndEntryId = " + str(schedule_event_KalturaLiveStreamScheduleEvent.postEndEntryId))
            print("schedule_event_KalturaLiveStreamScheduleEvent.id = " + str(schedule_event_KalturaLiveStreamScheduleEvent.id))
            print("schedule_event_KalturaLiveStreamScheduleEvent.startDate = " + str(datetime.datetime.fromtimestamp(schedule_event_KalturaLiveStreamScheduleEvent.startDate).strftime('%Y-%m-%d %H:%M:%S')))
            print("schedule_event_KalturaLiveStreamScheduleEvent.endDate = " + str(datetime.datetime.fromtimestamp(schedule_event_KalturaLiveStreamScheduleEvent.endDate).strftime('%Y-%m-%d %H:%M:%S')))

            # Playback verification of Simulive entries - boolShouldPlay=false->NO play until arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to NOT play SIMULIVE(boolShouldPlay=False) - before arriving to schedule_startTime " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            if startTime_WithPreEntryIdDuration > time.time():
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll==False:
                        time.sleep(1)
                        rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst,boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
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
            #time.sleep(5)
            while startTime_WithPreEntryIdDuration > time.time():
               time.sleep(5)
            # Playback verification of Simulive entries - boolShouldPlay=True->Play when arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to play SIMULIVE PLAYLIST (after arriving to startTime_WithPreEntryIdDuration) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , TimeNow = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                #reduction of MinToPlayEntry with 2 min because of playing time + caption/audio verifications + sleepUntil_PlaybackVerifications
                time.sleep(5)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst,boolShouldPlay=True, MinToPlayEntry=(self.SchedulerEvent_sessionEndOffset-2),PlayerVersion=self.PlayerVersion,ClosedCaption=True,languageList_Caption=self.languageList_Caption,MultiAudio=True,languageList=self.languageList,sleepUntil_PlaybackVerifications=self.sleepUntil_PlaybackVerifications)  # remove 2.5 min because of staring playing time + caption/audio verifications + sleepUntil_PlaybackVerifications(waiting to preEntry to finish)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Playback of SIMULIVE " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(30)#Time to arriving to endTime
            # Playback verification of Simulive entries - boolShouldPlay=false->NO play because arriving to end time of scheduling event
            self.logi.appendMsg("INFO - SCHEDULING_EVENT arrived to EndTime: Going to NOT play SIMULIVE(boolShouldPlay=False) " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(2)
                #rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entryList=self.entrieslst,boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    self.logi.appendMsg("FAIL - SCHEDULING_EVENT arrived to EndTime:SIMULIVE" + str(self.entryId) + " live entry played despite of boolShouldPlay=false(expected NO playback state) , End time = " + str(datetime.datetime.now()))
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - SCHEDULING_EVENT arrived to EndTime:NO Playback (boolShouldPlay=false) of SIMULIVE" + str(self.entryId) + " live entries on preview&embed page , End time = " + str(datetime.datetime.now()))


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
           self.practitest.post(Practi_TestSet_ID, '930','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '930','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x930_Simulive_Playlist_PrePostEntries_MultiCaptionAudio.py -s')
    #===========================================================================
        
