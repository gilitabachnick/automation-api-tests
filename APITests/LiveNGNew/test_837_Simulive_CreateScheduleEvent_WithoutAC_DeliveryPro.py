'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro.py
 @desc : this test check E2E test of  test_837_Simulive_CreateScheduleEvent - Create simulive event by kaltura client API and then play the entry on LIVE logic platform
 without Access control_delivery Profile
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
        self.logi = reporter2.Reporter2('test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro')
        self.logi.initMsg('test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro')

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
            self.PublisherID = self.inifile.RetIniVal(self.section, 'SIMULIVE_PublisherID')  # QA 6814 / PROD 4281553
            self.UserSecret = self.inifile.RetIniVal(self.section, 'SIMULIVE_UserSecret')
        #Simulive params
        self.conversionProfileID = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SIMULIVE_conversionProfileID')#"30162"
        self.kwebcastProfileId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SIMULIVE_kwebcastProfileId')#"18242"
        self.vodId = self.inifile.RetIniVal('Simulive_Partner_' + self.PublisherID, 'SIMULIVE_vodId')#"0_wc1hww4e" -> File 1:12 hour VOD AUTOMATION900_Ron_vodId.mp4

        self.sendto = "moran.cohen@kaltura.com;"           
        #***** Playback config
        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        #self.practitest = Practitest.practitest('1327')#set project BE API
        self.practitest = Practitest.practitest('18742')  # set project LIVENG
        self.Wdobj = MySelenium.seleniumWebDrive()         
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")                   
        #self.logi = reporter2.Reporter2('test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro')
        #self.logi.initMsg('test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
    
    
    def test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
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
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
            # Create Simulive object with current player
            self.SimuliveObj = Simulive.Simulivecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)

            # Create Simulive Webcast event by Kaltura API
            self.logi.appendMsg('INFO - Going to perform Simulive_Add:Create SIMULIVE ENTRY')
            sessionTitle='AUTOMATION-Simulive_NoACNoDP' + str(datetime.datetime.now())
            #sessionTitle = '"' + sessionTitle + '"'
            rc, LiveEntryId = self.SimuliveObj.Simulive_Add(client=self.client,UserSecret=self.UserSecret,partner_id=self.PublisherID, entry_name=sessionTitle, entry_conversionProfileId=self.conversionProfileID,metadata_profile_id=self.kwebcastProfileId,schedule_event_sourceEntryId=self.vodId,schedule_event_summary=sessionTitle,sessionEndOffset=20)
            if rc == True:
                print("Pass " + LiveEntryId)
                self.logi.appendMsg('PASS - Simulive_Add LiveEntryId: ' + LiveEntryId)
            else:
                self.logi.appendMsg('FAIL - Simulive_Add')
                                  
            time.sleep(2)
            
            self.entrieslst = []
            self.entryId = str(LiveEntryId)
            Entryobj = self.client.baseEntry.get(LiveEntryId)
            self.entrieslst.append(Entryobj)
            #self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entryId) + '\')')
            
            # Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:
                    time.sleep(2)
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True
                                        
            self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))  
                      
            print("Delete entry")
            self.logi.appendMsg("INFO - Delete entry =  " + str(self.entryId))
            result = self.client.baseEntry.delete(self.entryId)

                           
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
        print(' Tear down - Wd.quit')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass        
        
        try:
            time.sleep(5)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '837','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '837','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True


    #===========================================================================
    #pytest.main('test_837_Simulive_CreateScheduleEvent_WithoutAC_DeliveryPro.py -s')
    #===========================================================================
        
        
        