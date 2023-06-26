'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_929_Simulive_Playlist_BasicFlow.py
  @desc : this test check E2E test of  test_929_Simulive_Playlist_BasicFlow - Create simulive event by Kaltura API and then play the entry on LIVE logic platform
 without Access control_delivery Profile
 1) Create manual playlist by API
 * Precondition to upload those 3 files to QA env and PROD env
 PlaylistItem1 = "0_nwuqpww7" --> 1 minutes duration
 PlaylistItem2 = "0_t3ahjz17" --> 3 minutes duration
 PlaylistItem3 = "0_l81xhd9y" --> 2 minutes duration
 2)Update scheduling event by API with following fields:
 schedule_event.sourceEntryId = self.MainEntryId # PlaylistId
 Play the Simulive with all parts duration -> PlaylistItem1,PlaylistItem2,PlaylistItem3
 3)Verification playback duration by QRlogic during the startDate / End Date

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
        self.conversionProfileID = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'SIMULIVE_conversionProfileID')  # QA "30162"  # PROD "17469513"
        self.kwebcastProfileId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'SIMULIVE_kwebcastProfileId')  # QA "18242" #PROD "16890803"
        self.PlaylistItem1 = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'Simulive_Playlist_BasicFlow_PlaylistItem1_Ron1min')  # QA "0_nwuqpww7"# #PROD "1_b2x73t0y" #1 minutes duration - File LongCloDvRec_Pre_1min.mp4
        self.PlaylistItem2 = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'Simulive_Playlist_BasicFlow_PlaylistItem2_Ron3min')  # QA "0_t3ahjz17"#PROD "1_hlx558mn"#3 minutes duration  - File LongCloDvRec_Main_3min_1until4.mp4
        self.PlaylistItem3 = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID,'Simulive_Playlist_BasicFlow_PlaylistItem3_Ron2min')  # QA "0_l81xhd9y" #PROD "1_qa9xteqo"  #2 minutes duration - File LongCloDvRec_Post_2min_4until6.mp4

        self.sendto = "moran.cohen@kaltura.com;"           
        #***** Playback cofing
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        # Simulive params
        self.SchedulerEvent_sessionEndOffset = 6 #Total Duration of the SchedulerEvent_sessionEndOffset playback -> Playlist all items duration(PlaylistItem1+PlaylistItem2+PlaylistItem3)
        self.SchedulerEvent_AddMinToStartTime=2 #Time to add for startTime

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_929_Simulive_Playlist_BasicFlow')
        self.logi.initMsg('test_929_Simulive_Playlist_BasicFlow')
    
    def test_929_Simulive_Playlist_BasicFlow(self):
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
            self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')    
            
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
            # Create Simulive object with current player
            self.SimuliveObj = Simulive.Simulivecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)

            # Create Simulive Webcast event by kaltura API
            self.logi.appendMsg('INFO - Going to perform Simulive_Add:Create SIMULIVE ENTRY')
            sessionTitle='AUTOMATION-Simulive_Playlist_BasicFlow' + str(datetime.datetime.now())
            #sessionTitle = '"' + sessionTitle + '"'
            startTime= time.time() + (self.SchedulerEvent_AddMinToStartTime)*60
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            rc, LiveEntryId = self.SimuliveObj.Simulive_Add(client=self.client, UserSecret=self.UserSecret,
                                                        partner_id=self.PublisherID, entry_name=sessionTitle,
                                                        entry_conversionProfileId=self.conversionProfileID,
                                                        metadata_profile_id=self.kwebcastProfileId,
                                                        schedule_event_sourceEntryId=self.MainEntryId,
                                                        schedule_event_summary=sessionTitle,
                                                        schedule_event_startDate=startTime,
                                                        sessionEndOffset=self.SchedulerEvent_sessionEndOffset)
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
            # Playback verification of Simulive entries - boolShouldPlay=True->Play when arriving to start time of scheduling event
            self.logi.appendMsg("INFO - Going to play SIMULIVE (after arriving to startTime) " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlayEntry(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , TimeNow = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(5)
                #reduction of MinToPlayEntry with 0.5 because of waiting function until playing
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=True,MinToPlayEntry=(self.SchedulerEvent_sessionEndOffset-1.2), PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)#remove 0.5
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Playback of SIMULIVE " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay(SchedulerEvent_sessionEndOffset)=" + str(self.SchedulerEvent_sessionEndOffset) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(20)#Time to arriving to endTime
            # Playback verification of Simulive entries - boolShouldPlay=false->NO play because arriving to end time of scheduling event
            self.logi.appendMsg("INFO - SCHEDULING_EVENT arrived to EndTime: Going to NOT play SIMULIVE(boolShouldPlay=False) " + str(self.entryId) + "  live entries on preview&embed page., currentTime = " + str(datetime.datetime.now()) + " , startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(2)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
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
           self.practitest.post(self.Practi_TestSet_ID, '929','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '929','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_929_Simulive_Playlist_BasicFlow.py -s')
    #===========================================================================
        
