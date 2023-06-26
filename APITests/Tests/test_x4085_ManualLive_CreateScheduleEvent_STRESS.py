'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_x4085_ManualLive_CreateScheduleEvent.py
 @desc : this test check E2E test of  test_4085_ManualLive_CreateScheduleEvent - Create Manual event by ASSAF PHP script with Primary+Backup and then play the entry on LIVE logic platform 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import os
import sys
import time
import datetime
import pytest
import multiprocessing
import re

from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from KalturaClient import *
from KalturaClient.Plugins.Core import *
from test.test_sax import start

 
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)


import DOM
import ClienSession
import reporter2
import Config
import Practitest
import Entry
import uiconf
import strclass
import tearDownclass
import MySelenium
import KmcBasicFuncs
import Entrypage

from selenium.webdriver.common.action_chains import ActionChains
import subprocess
import live
import LiveDashboard
import Transcoding
import QrcodeReader
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
#For now the script is just running PRODUCTION until the reinvent    
isProd = True
class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            # Streaming details
            self.url= "www.kaltura.com"
            #self.playerId = "46022611"# v3 player
            self.PublisherID = "2095431"
            self.ServerURL = "https://www.kaltura.com"#inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.access_control_id_SIMULIVE="3629423" #Simulive access control
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.configFile = "config.ini" #set the KMS config in Production
            #self.playerId = "44686701" # KMS player with-> {"versions":{"kaltura-ovp-player":"{latest}","playkit-kava":"{latest}","playkit-live-fallback":"1.0.2"},"langs":["en"]}
            print ('PRODUCTION ENVIRONMENT')
            
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            #self.playerId = "15225574"##"15224080" v3 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')#"6611"
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')  
            self.access_control_id_SIMULIVE="20327" #Simulive access control  
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.configFile = "TestingConfig.ini" #set the KMS config in testing.qa
            print ('TESTING ENVIRONMENT')
        #***** SSH streaming server - Assaf PHP script location    
        self.SimulivePHPscript_host="qa-apache-php7.dev.kaltura.com"
        self.SimulivePHPscript_user="root"
        self.SimulivePHPscript_pwd="testingqa"
        
        self.isSimulive=0 # Manual live: true-1(simulive)/false-0(manual)
        self.manualLiveHlsUrl="https://klive.kaltura.com/dc-1/m/ny-live-publish111/live/legacy/p/931702/e/1_oorxcge2/sd/10000/t/FbLuRSy3lvSO0lua7RBuvg/master-s34-s33-s32-s35.m3u8"#"https://d16gdga1b4l4j4.cloudfront.net/out/v1/7d4290572e3446bbbcc4291c26ce5a33/index.m3u8"
        self.manualLiveBackupHlsUrl="https://klive.kaltura.com/dc-1/m/ny-live-publish111/live/legacy/p/931702/e/1_oorxcge2/sd/10000/t/FbLuRSy3lvSO0lua7RBuvg/master-s34-s33-s32-s35.m3u8"#"https://d16gdga1b4l4j4.cloudfront.net/out/v1/7d4290572e3446bbbcc4291c26ce5a33/index.m3u8"
                     
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.NumOfEntries = 2000
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('1327')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()         
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")                   
        self.logi = reporter2.Reporter2('test_4085_ManualLive_CreateScheduleEvent_STRESS')
        self.logi.initMsg('test_4085_ManualLive_CreateScheduleEvent_STRESS')     
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
    
    
    def test_4085_ManualLive_CreateScheduleEvent_STRESS(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - Start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(5)
            
            #===================================================================
            # # Create player of latest version -  Create V2/3 Player
            # self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion)  + ' player')
            # myplayer = uiconf.uiconf(self.client, 'livePlayer')
            # if self.PlayerVersion == 2:
            #     self.player = myplayer.addPlayer(None,self.env,False, False) # Create latest player v2
            # elif self.PlayerVersion == 3:    
            #     self.player = myplayer.addPlayer(None,self.env,False, False,"v3") # Create latest player v3
            # else: 
            #     self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
            # if isinstance(self.player,bool):
            #     testStatus = False
            #     return
            # else:
            #     self.playerId = self.player.id
            # self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))       
            # self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')    
            self.playerId="46665613" 
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
            
            #for i in range(0, self.NumOfEntries):
            # Create Simulive Webcast event by Assaf script PHP 
            #self.logi.appendMsg('INFO - Going to CreateSimuliveWecastByPHPscript- Create MANUAL LIVE ' + str(i) + ', host=' + self.SimulivePHPscript_host + ' ,user = ' + self.SimulivePHPscript_user + ' , pwd =  ' + self.SimulivePHPscript_pwd)
            #sessionTitle='AUTOMATION-BECore_MANUAL_LIVE_' +  str(i) + "_" + str(datetime.datetime.now()) 
            sessionTitle='AUTOMATION-BECore_MANUAL_LIVE_' + str(datetime.datetime.now())
            #rc,LiveEntryId = self.liveObj.CreateSimuliveWecastByPHPscript(self.SimulivePHPscript_host,self.SimulivePHPscript_user, self.SimulivePHPscript_pwd,self.configFile,self.isSimulive,self.manualLiveHlsUrl,self.manualLiveBackupHlsUrl,sessionEndOffset=20,sessionTitle=sessionTitle)
            rc = self.liveObj.CreateSimuliveWecastByPHPscriptSTRESS(self.SimulivePHPscript_host,self.SimulivePHPscript_user, self.SimulivePHPscript_pwd,self.configFile,self.isSimulive,self.manualLiveHlsUrl,self.manualLiveBackupHlsUrl,sessionEndOffset=20,sessionTitle=sessionTitle,NumOfEntries=self.NumOfEntries)   
            if rc == True:
                #print ("Pass " + str(LiveEntry.Id))
                self.logi.appendMsg('PASS - CreateSimuliveWecastByPHPscriptSTRESS ')
            else:
                self.logi.appendMsg('FAIL - CreateSimuliveWecastByPHPscriptSTRESS')
                     
            
            #===================================================================
            # time.sleep(2)
            # 
            # self.entrieslst = []
            # self.entryId = str(LiveEntryId)
            # Entryobj = self.client.baseEntry.get(LiveEntryId) #fails KalturaException: Entry id "01_rgxoiozo" not found (ENTRY_ID_NOT_FOUND)
            # self.entrieslst.append(Entryobj)
            # #self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entryId) + '\')')
            # 
            # # Playback verification of all entries
            # self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            # limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            # seenAll = False
            # while datetime.datetime.now() <= limitTimeout and seenAll==False:   
            #         #rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion)
            #         rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True,PlayerVersion=self.PlayerVersion)
            #         time.sleep(5)
            #         if not rc:
            #             testStatus = False
            #             return
            #         if self.seenAll_justOnce_flag ==True:
            #             seenAll = True
            #                             
            # self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))  
            #           
            # print "Delete entry"
            # self.logi.appendMsg("INFO - Delete entry =  " + str(self.entryId))
            # result = self.client.baseEntry.delete(self.entryId)
            #===================================================================
                           
        except Exception as e:
            print (e)
            testStatus = False
            pass
             
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    
    def teardown_class(self):
        
        global testStatus
        
        print ('#############')
        print (' Tear down - Wd.quit')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print (Exp)
            pass      
        
        try:
            time.sleep(5)
            #self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print (Exp)
           pass
        print ('#############')
        if testStatus == False:
           print ("fail")
           self.practitest.post(Practi_TestSet_ID, '4085','1') 
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print ("pass")
           self.practitest.post(Practi_TestSet_ID, '4085','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main(args=['test_x4085_ManualLive_CreateScheduleEvent_STRESS.py', '-s'])
    #===========================================================================
        
        
        