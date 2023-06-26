'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_Simulive_preStartEntryId_postEndEntryId_RedirectScheduleEvent.py
  @desc : this test check E2E test of  test_837_Simulive_CreateScheduleEvent - Create simulive event by kaltura client API and then play the entry on LIVE logic platform
 without Access control_delivery Profile
 1)Update scheduling event by API with following fields:
 preStartEntryId.mp4 --> duration 1
 MainEntryId.mp4     --> duration 3
 postEndEntryId.mp4  --> duration 2
 * Precondition to upload those 3 files to QA env and PROD env
 Play the Simulive with all parts duration - preStartEntryId + MainEntryId + postEndEntryId
 Verification playback duration by QRlogic during the startDate / End Date
 2) Add scheduling event TYPE KalturaLiveRedirectScheduleEvent
 Add with Redirect entryId MainEntryId.mp4     --> duration 3
 Verification playback duration by QRlogic during the startDate / End Date
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
            self.MainEntryId = "1_hlx558mn"  # $argv[11]; // $config[$env]['vodId'];
            self.preStartEntryId = "1_b2x73t0y"
            self.postEndEntryId = "1_qa9xteqo"
            
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
            self.MainEntryId = "0_t3ahjz17"#"0_u68a15b0"# 3 minutes duration
            self.preStartEntryId = "0_nwuqpww7"#"0_xmd2egoo"# 1 minutes duration
            self.postEndEntryId = "0_l81xhd9y" #"0_mjm6yg64"# 2 minutes duration
                     
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        self.SchedulerEvent_sessionEndOffset = 6 #Total Duration of the SchedulerEvent_sessionEndOffset playback = preEntryId.duration + mainEntry.duration + postEntry.duration
        self.preStartEntryId_duration = 1  # preEntryid.Duration  1 minute
        self.SchedulerEvent_MainEntryId_duration = 3 # 3 minutes duration of self.MainEntryId

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_847_Simulive_preStartEntryId_postEndEntryId_RedirectScheduleEvent')
        self.logi.initMsg('test_847_Simulive_preStartEntryId_postEndEntryId_RedirectScheduleEvent')
    
    def test_847_Simulive_preStartEntryId_postEndEntryId_RedirectScheduleEvent(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - Start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(5)
            
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

            # Create Simulive object with current player
            self.SimuliveObj = Simulive.Simulivecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID,self.playerId)
            
            # Create Simulive Webcast event by Assaf script PHP 
            self.logi.appendMsg('INFO - Going to perform Simulive_Add:Create SIMULIVE ENTRY')
            sessionTitle='AUTOMATION-Simulive_PreMainPost' + str(datetime.datetime.now())
            sessionTitle = '"' + sessionTitle + '"'
            startTime= time.time() + (self.SchedulerEvent_sessionEndOffset+1)*60 #add 7minutes to startTime of the scheduling event(add another 1 minutes for the expected starttime of scheduling)
            startTime_WithPreEntryIdDuration = startTime - self.preStartEntryId_duration*60 #reduction preStartEntryId_duration from the start_time of the scheduling event
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            print("startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            #rc, LiveEntryId = self.liveObj.CreateSimuliveWecastByPHPscript(self.SimulivePHPscript_host,self.SimulivePHPscript_user,self.SimulivePHPscript_pwd,self.configInI_ForPHPscript_Env,sessionEndOffset=self.SchedulerEvent_MainEntryId_duration,startTime=startTime, sessionTitle=sessionTitle,env=self.env, PublisherID=self.PublisherID,UserSecret=self.UserSecret, url=self.ServerURL,conversionProfileID=self.conversionProfileID,kwebcastProfileId=self.kwebcastProfileId,eventsProfileId=self.eventsProfileId,vodId=self.MainEntryId)
            rc, LiveEntryId = self.SimuliveObj.Simulive_Add(client=self.client, UserSecret=self.UserSecret,
                                                        partner_id=self.PublisherID, entry_name=sessionTitle,
                                                        entry_conversionProfileId=self.conversionProfileID,
                                                        metadata_profile_id=self.kwebcastProfileId,
                                                        schedule_event_sourceEntryId=self.MainEntryId,
                                                        schedule_event_summary=sessionTitle,schedule_event_startDate=startTime, sessionEndOffset=self.SchedulerEvent_MainEntryId_duration,preStartEntryId=self.preStartEntryId,postEndEntryId=self.postEndEntryId)
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

            '''
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
            '''
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
            # Playback verification of Simulive entries - boolShouldPlay=True->Play when arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to play SIMULIVE (after arriving to startTime_WithPreEntryIdDuration) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , TimeNow = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(5)
                #reduction of MinToPlayEntry with 0.5 because of waiting function until playing
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=True,MinToPlayEntry=(self.SchedulerEvent_sessionEndOffset-1.5), PlayerVersion=self.PlayerVersion)#remove 0.5
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Playback of SIMULIVE " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(30)
            # Playback verification of Simulive entries - boolShouldPlay=false->NO play because arriving to end time of scheduling event
            self.logi.appendMsg("INFO - SCHEDULING_EVENT arrived to EndTime: Going to NOT play SIMULIVE(boolShouldPlay=False) " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(2)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    self.logi.appendMsg("FAIL - SCHEDULING_EVENT arrived to EndTime:SIMULIVE" + str(self.entryId) + " live entry played despite of boolShouldPlay=false(expected NO playback state) , End time = " + str(datetime.datetime.now()))
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - SCHEDULING_EVENT arrived to EndTime:NO Playback (boolShouldPlay=false) of SIMULIVE" + str(self.entryId) + " live entries on preview&embed page , End time = " + str(datetime.datetime.now()))

            time.sleep(10) # Wait for the previous scheduling event to finish
            self.logi.appendMsg('INFO - KalturaLiveRedirectScheduleEvent:Going to add scheduler event TYPE KalturaLiveRedirectScheduleEvent by API.templateEntryId =' + str(self.entryId))
            schedule_event = KalturaLiveRedirectScheduleEvent()
            schedule_event.summary = "Summary" + str(datetime.datetime.now())
            schedule_event.recurrenceType = KalturaScheduleEventRecurrenceType.NONE
            schedule_event.templateEntryId = self.entryId
            schedule_event.startDate = time.time() + (self.SchedulerEvent_MainEntryId_duration)*60
            schedule_event.endDate = schedule_event.startDate + (self.SchedulerEvent_MainEntryId_duration+1)*60 # add 1 min to the endDate
            schedule_event.redirectEntryId = self.MainEntryId

            schedule_event_KalturaLiveRedirectScheduleEvent = self.client.schedule.scheduleEvent.add(schedule_event)
            print("schedule_event_KalturaLiveRedirectScheduleEvent.id= " + str(schedule_event_KalturaLiveRedirectScheduleEvent.id))
            print("schedule_event_KalturaLiveRedirectScheduleEvent.startDate = " + str(datetime.datetime.fromtimestamp(schedule_event_KalturaLiveRedirectScheduleEvent.startDate).strftime('%Y-%m-%d %H:%M:%S')))
            print("schedule_event_KalturaLiveRedirectScheduleEvent.endDate = " + str(datetime.datetime.fromtimestamp(schedule_event_KalturaLiveRedirectScheduleEvent.endDate).strftime('%Y-%m-%d %H:%M:%S')))

           # Playback verification of Simulive entries - boolShouldPlay=false->NO play until arriving to start time of scheduling event
            self.logi.appendMsg("INFO - KalturaLiveRedirectScheduleEvent:Going to NOT play SIMULIVE(boolShouldPlay=False) - before arriving to schedule_event_KalturaLiveRedirectScheduleEvent.startDate " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(schedule_event_KalturaLiveRedirectScheduleEvent.startDate)).strftime('%Y-%m-%d %H:%M:%S')))
            if schedule_event_KalturaLiveRedirectScheduleEvent.startDate > time.time():
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    time.sleep(2)
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        self.logi.appendMsg("FAIL - KalturaLiveRedirectScheduleEvent:SIMULIVE" + str(self.entryId) + " live entry played despite of boolShouldPlay=false(expected NO playback state) - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True
            else:
                testStatus = False
                self.logi.appendMsg('FAIL - KalturaLiveRedirectScheduleEvent:Passed time for SIMULIVE(boolShouldPlay=False) verification because schedule_event_KalturaLiveRedirectScheduleEvent.startDate < currentTime LiveEntryId: ' + LiveEntryId + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(schedule_event_KalturaLiveRedirectScheduleEvent.startDate)).strftime('%Y-%m-%d %H:%M:%S')) + " , CurrentTime = " + str(datetime.datetime.now()))

            self.logi.appendMsg("PASS - KalturaLiveRedirectScheduleEvent:NO Playback (boolShouldPlay=false) of SIMULIVE" + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            self.logi.appendMsg("INFO - Going to wait for arriving to schedule_event_KalturaLiveRedirectScheduleEvent.startDate= " + str(datetime.datetime.fromtimestamp(int(schedule_event_KalturaLiveRedirectScheduleEvent.startDate)).strftime('%Y-%m-%d %H:%M:%S')))
            while schedule_event_KalturaLiveRedirectScheduleEvent.startDate > time.time():
                time.sleep(5)
            # Playback verification of KalturaLiveRedirectScheduleEvent.Simulive entries - boolShouldPlay=True->Play when arriving to start time of scheduling event
            self.logi.appendMsg("INFO - KalturaLiveRedirectScheduleEvent:Going to play SIMULIVE (after arriving to schedule_event_KalturaLiveRedirectScheduleEvent.startDate) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_MainEntryId_duration)=" + str(self.SchedulerEvent_MainEntryId_duration) + " , TimeNow = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(2)
                # reduction of MinToPlayEntry with 0.5 because of waiting function until playing
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=True,MinToPlayEntry=(self.SchedulerEvent_MainEntryId_duration - 1),PlayerVersion=self.PlayerVersion)#was -0.5
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - KalturaLiveRedirectScheduleEvent:Playback of SIMULIVE " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay(SchedulerEvent_MainEntryId_duration)=" + str(self.SchedulerEvent_MainEntryId_duration) + " , End time = " + str(datetime.datetime.now()))

            self.logi.appendMsg("INFO - KalturaLiveRedirectScheduleEvent:Going to wait for arriving to schedule_event_KalturaLiveRedirectScheduleEvent.EndDate= " + str(datetime.datetime.fromtimestamp(int(schedule_event_KalturaLiveRedirectScheduleEvent.endDate)).strftime('%Y-%m-%d %H:%M:%S')))
            while schedule_event_KalturaLiveRedirectScheduleEvent.endDate > time.time():
                time.sleep(5)
            # Playback verification of KalturaLiveRedirectScheduleEvent.Simulive entries - boolShouldPlay=false->NO play because arriving to end time of KalturaLiveRedirectScheduleEvent scheduling event
            self.logi.appendMsg("INFO - KalturaLiveRedirectScheduleEvent:SCHEDULING_EVENT arrived to EndTime: Going to NOT play SIMULIVE(boolShouldPlay=False) " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(2)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False,PlayerVersion=self.PlayerVersion)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    self.logi.appendMsg("FAIL - KalturaLiveRedirectScheduleEvent:SCHEDULING_EVENT arrived to EndTime:SIMULIVE" + str(self.entryId) + " live entry played despite of boolShouldPlay=false(expected NO playback state) - MinToPlay=" + str(self.SchedulerEvent_MainEntryId_duration) + " , End time = " + str(datetime.datetime.now()))
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - KalturaLiveRedirectScheduleEvent:SCHEDULING_EVENT arrived to EndTime:NO Playback (boolShouldPlay=false) of SIMULIVE" + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.SchedulerEvent_MainEntryId_duration) + " , End time = " + str(datetime.datetime.now()))

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
           self.practitest.post(Practi_TestSet_ID, '847','1')
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '847','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_Simulive_preStartEntryId_postEndEntryId_RedirectScheduleEvent.py -s')
    #===========================================================================
        
