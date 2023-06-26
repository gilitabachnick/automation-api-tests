'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_x921_SimuliveEventShorterThanSourcesDuration.py
  @desc : this test check E2E test of  test_921_SimuliveEventShorterThanSourcesDuration  - Create simulive event by ASSAF PHP script and then play the entry on LIVE logic platform
 without Access control_delivery Profile
 1)Update scheduling event by API with following fields:
 preStartEntryId.mp4 --> duration 1
 MainEntryId.mp4     --> duration 3
 postEndEntryId.mp4  --> duration 2
 * Precondition to upload those 3 files to QA env and PROD env
 2)Perform case#3 in https://kaltura.atlassian.net/browse/LIV-932
     scheduling duration=2min
     preStartEntryId=1min --> Uploaded Uploaded LongCloDvRec_Pre.mp4(QRcode)
     postEndEntryId=2min  --> Uploaded Prince_POST2min.mp4(No QRcode on the file, therefore should get error on QRcodePlayback if will play)
     MainEntryId=5min  --> Uploaded LongCloDvRec_Main5min.mp4 (Qrcode)

    Expected Result:
    5min playback of pre1(1min) and then main(4min)
    Verify that the post is not played.

  Another option:
  create entry with dvr
  search for hls m3u8 with end list and then 1 discontinuities
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
            self.PublisherID = inifile.RetIniVal(section, 'SIMULIVE_PublisherID')#
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
            self.MainEntryId = "1_uroulseo"  # 5min duration $argv[11]; // $config[$env]['vodId'];
            self.preStartEntryId = "1_b2x73t0y" #1min duration
            self.postEndEntryId = "1_qkpe1qvt"#"1_yvk058l1" # 2min duration
            
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
            self.MainEntryId = "0_534rftzr"# 5 minutes duration - Uploaded LongCloDvRec_Main5min.mp4
            self.preStartEntryId = "0_nwuqpww7"#1 minutes duration - Uploaded LongCloDvRec_Pre (Source).mp4
            self.postEndEntryId = "0_uqcn3emq"#"0_j67dpdvx" # 2 minutes duration - Uploaded Prince_POST2min.mp4(No QR code)
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
        self.SchedulerEvent_Duration = 2 #SchedulerEvent duration (minutes)
        self.preStartEntryId_duration = 1 # preEntryid.Duration  1 minute
        self.postEndEntryId_duration = 2  # postEndEntryId.Duration  2 minute
        self.MainEntryId_duration = 5
        #self.SchedulerEvent_MainEntryId_duration = 3 # 3 minutes duration of self.MainEntryId

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_921_SimuliveEventShorterThanSourcesDuration')
        self.logi.initMsg('test_921_SimuliveEventShorterThanSourcesDuration')
    
    def test_921_SimuliveEventShorterThanSourcesDuration(self):
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
            
            # Create Simulive Webcast event by Assaf script PHP 
            self.logi.appendMsg('INFO - Going to CreateSimuliveWecastByPHPscript:Create SIMULIVE ENTRY ,host=' + self.SimulivePHPscript_host + ' ,user = ' + self.SimulivePHPscript_user + ' , pwd =  ' + self.SimulivePHPscript_pwd)
            sessionTitle='AUTOMATION-Simulive_PreMainPost' + str(datetime.datetime.now())
            sessionTitle = '"' + sessionTitle + '"'
            startTime= time.time() + (self.SchedulerEvent_Duration+1)*60 #add another 1 minutes for the expected starttime of scheduling
            startTime_WithPreEntryIdDuration = startTime - self.preStartEntryId_duration*60 #reduction preStartEntryId_duration from the start_time of the scheduling event
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            print("startTime_WithPreEntryIdDuration = " + str(datetime.datetime.fromtimestamp(int(startTime_WithPreEntryIdDuration)).strftime('%Y-%m-%d %H:%M:%S')))
            rc, LiveEntryId = self.liveObj.CreateSimuliveWecastByPHPscript(self.SimulivePHPscript_host,self.SimulivePHPscript_user,self.SimulivePHPscript_pwd,self.configInI_ForPHPscript_Env,sessionEndOffset=self.SchedulerEvent_Duration,startTime=startTime, sessionTitle=sessionTitle,env=self.env, PublisherID=self.PublisherID,UserSecret=self.UserSecret, url=self.ServerURL,conversionProfileID=self.conversionProfileID,kwebcastProfileId=self.kwebcastProfileId,eventsProfileId=self.eventsProfileId,vodId=self.MainEntryId)
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
            self.logi.appendMsg("INFO - Going to play SIMULIVE (after arriving to startTime_WithPreEntryIdDuration) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_Duration)=" + str(self.SchedulerEvent_Duration) + " , TimeNow = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(5)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=True,MinToPlayEntry=(self.preStartEntryId_duration + self.MainEntryId_duration - self.SchedulerEvent_Duration-0.2),PlayerVersion=self.PlayerVersion)  # Expected result:5min playback of pre1(1min) and then main(4min) - Verify that post entry is not played
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Playback of SIMULIVE " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay(SchedulerEvent_Duration)=" + str(self.SchedulerEvent_Duration) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(40)#Add to the end 40sec
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
           self.practitest.post(Practi_TestSet_ID, '921','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '921','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x921_SimuliveEventShorterThanSourcesDuration.py -s')
    #===========================================================================
        
