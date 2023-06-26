'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_x4113_LiveNG_Passthrough_DVR_PlayerV3.py - WOKRING ON ADD SUPPORT TO V3 player + DVR
 @desc : this test check E2E test of new LiveNG entries Passthrough with DVR with player v3 - host access run ffmpeg cmd 
 verification of create new entries ,API,start/check ps/stop streaming, Playback and liveDashboard Analyzer - alerts tab and channels
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
import clsPlayerV2
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
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            # Streaming details
            self.url= "www.kaltura.com"
            #self.playerId = "46022611"# v3 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            print ('PRODUCTION ENVIRONMENT')
            
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            #self.playerId = "15225574"##"15224080" v3 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            print ('TESTING ENVIRONMENT')
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.remote_host = "34.201.96.171"  # "liveng-core3-automation.kaltura.com"
        self.remote_user = "root"
        self.remote_pass = "Vc9Qvx%J5PJNxG%$Wo@ad9xZAHJEg?P9"  # "testingqa"
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        #**** SSH streaming computer - Ilia computer
        #self.remote_host = "192.168.162.176"
        #self.remote_user = "root"
        #self.remote_pass = "Kaltura12#"
        #self.filePath = "/home/kaltura/tests/stream_liveNG_custom_entry_AUTOMATION.sh"
        #***** SSH streaming computer - dev-backend4
        #self.remote_host = "dev-backend4.dev.kaltura.com"
        #self.remote_user = "root"
        #self.remote_pass = "1q2w3e4R"  
        #self.filePath = "/root/LiveNG/ffmpeg_data/entries/LongCloDvRec.mp4"
        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('1327')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()         
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")                   
        self.logi = reporter2.Reporter2('test_4113_LiveNG_Passthrough_DVR_PlayerV3')
        self.logi.initMsg('test_4113_LiveNG_Passthrough_DVR_PlayerV3')     
        self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
        
  

    def test_4113_LiveNG_Passthrough_DVR_PlayerV3(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
                      
            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            Transobj = Transcoding.Transcoding(self.client,'Passthrough')
            self.passtrhroughId = Transobj.getTranscodingProfileIDByName('Passthrough')
            if self.passtrhroughId==None:
                self.passtrhroughId = Transobj.addTranscodingProfile(1,'32,36,37')
                if isinstance(self.passtrhroughId,bool):
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
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveEntry_DVR_PASSTHROUGH_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                #Add stream entry    # recordStatus - send 0 for disable, 1 for append, 2 for per_session # dvrStatus - send 0 for disable, 1 for enable
                self.entry = Entryobj.AddEntryLiveStream(None, None, recordStatus=0, dvrStatus=1)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
            
            time.sleep(2)
            #**** Login LiveDashboard 
            self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
            rc = self.LiveDashboard.invokeLiveDashboardLogin(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL)
            if(rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:       
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                testStatus = False
                return
            time.sleep(5)
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id) 
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)    
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByffmpegCmd.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return
                # ******* CHECK CPU usage of streaming machine
                #cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
                self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))           
                cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"                
                rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine)
                if rc == True:
                    self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
                else:
                    self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                    testStatus = False
                    return
                         
                #****** Livedashboard - Channels tab     
                navigateTo= "Channels"
                self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo = " + navigateTo)
                rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo)
                if(rc):
                    self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                else:       
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                    testStatus = False
                    return
                # Return row data from Channels
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Channels of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,env="prod")
                    if(rc):
                        self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        testStatus = False   
                        return 
                else:       
                    self.logi.appendMsg("FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
                # LiveDashboard - Alerts tab
                navigateTo= "Alerts"
                self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo= " + navigateTo)
                rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd,navigateTo)
                if(rc):
                    self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                else:       
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo + ",  entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
             
                 # Return row data from Alerts
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,env="prod")
                    if(rc):
                        self.logi.appendMsg("PASS -VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        testStatus = False
                        return    
                else:       
                    self.logi.appendMsg("FAIL -ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
                
            #Close LiveDashboard window
            try:
                self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                self.Wd.quit()
                time.sleep(2)
            except Exception as Exp:
                print (Exp)
                pass
        
            ''' read QR code for 2 minutes of play'''
            self.logi.appendMsg("Going to read QR code for 2 minutes of play")
            ''' ----- first play 2 minutes -------'''
            # Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:   
                    rc,self.PlayBrowserDriver = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode_DVR(self.entrieslst, True,MinToPlayEntry=2,PlayerVersion=self.PlayerVersion,CloseBrowser=False)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True
                                         
            self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))  
            if testStatus == True:
                self.logi.appendMsg("PASS - First 2 minutes played video OK. EntryId = " + str(self.entryId))
            else:
                self.logi.appendMsg("FAIL - First 2 minutes did NOT play the video ok. EntryId = " + str(self.entryId))
                return
                 
            ''' Going to scroll to start point - REWIND '''            
            self.logi.appendMsg("INFO - Going to scroll to start point - REWIND. EntryId = " + str(self.entryId))  
            self.kaltplayer = clsPlayerV2.playerV("kaltura_player_1418811966",self.PlayerVersion)
            self.kaltplayer.returnLocators(3)
            rc = self.kaltplayer.clickOnSlider(self.PlayBrowserDriver, 0)
            if (not rc):
                testStatus = False
                self.logi.appendMsg("FAIL - Scroll to start point - REWIND. EntryId = " + str(self.entryId))
                return
            else:   
                self.logi.appendMsg("PASS - Scroll to start point - REWIND. EntryId = " + str(self.entryId))

                
            ''' ----- second play 1 minutes -------'''
            self.logi.appendMsg("INFO - Going to read QR code for 1 minute of play - after Rewind to start point. EntryId = " + str(self.entryId))
            MinToPlayEntry = 1 # 1 minutes playback
            isPlaying = self.liveObj.verifyLiveisPlayingOverTime(self.PlayBrowserDriver, MinToPlayEntry=MinToPlayEntry)
            if (not isPlaying):
                testStatus = False
                self.logi.appendMsg("FAIL - 1 minute of played video after Rewind to start point, did NOT play the video OK. Details:Entry = "+ str(self.entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                return
            else:
                self.logi.appendMsg("PASS - 1 minute of played video after Rewind to start point, played OK.Details:Entry = "+ str(self.entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))                       
            if testStatus == True:
                self.logi.appendMsg("PASS - 1 minute of played video after Rewind to start point, played OK.EntryId = " + str(self.entryId))
            else:
                self.logi.appendMsg("FAIL - 1 minute of played video after Rewind to start point, did NOT play the video OK.EntryId = " + str(self.entryId))
                 
            ''' ----- Going to scroll to middle point - Forward -------'''            
            self.logi.appendMsg("INFO - Going to scroll to middle point - Forward to start point. EntryId = " + str(self.entryId))
            self.kaltplayer.clickOnSlider(self.PlayBrowserDriver, 50)
                
            ''' ----- third play 1 minutes -------'''
            self.logi.appendMsg("INFO - Going to read QR code for 1 minute of play - after Rewind to middle point. EntryId = " + str(self.entryId))
            MinToPlayEntry = 1 # 1 minutes playback
            isPlaying = self.liveObj.verifyLiveisPlayingOverTime(self.PlayBrowserDriver, MinToPlayEntry=MinToPlayEntry)
            if (not isPlaying):
                testStatus = False
                self.logi.appendMsg("FAIL - 1 minute of played video after Rewind to middle point, did NOT play the video OK. Details:Entry = "+ str(self.entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                return
            else:
                self.logi.appendMsg("PASS - 1 minute of played video after Rewind to middle point, played OK.Details:Entry = "+ str(self.entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                            
            if testStatus == True:
                self.logi.appendMsg("PASS - 1 minute of played video after Forward to middle point, played OK. EntryId = " + str(self.entryId))  
            else:
                self.logi.appendMsg("FAIL - 1 minute of played video after Forward to middle point did NOT play the video OK. EntryId = " + str(self.entryId))   
            
            ''' Going to perform BACK TO LIVE '''    
            self.logi.appendMsg("INFO - Going to Press the BACK TO LIVE button. EntryId = " + str(self.entryId))
            self.kaltplayer.clickLiveIconBackToLive(self.PlayBrowserDriver)
            reTimer = self.kaltplayer.getCurrentTimeLabel(self.PlayBrowserDriver) # WORKING ON 
            print ("reTimer = " + str(reTimer))
                
            ''' check scroll is at the end of it'''                
            ''' ----- forth play 1 minutes -------'''
            self.logi.appendMsg("INFO - Going to read QR code for 1 minute of play - after BACK TO LIVE. EntryId = " + str(self.entryId))
            MinToPlayEntry = 1 # 1 minutes playback
            isPlaying = self.liveObj.verifyLiveisPlayingOverTime(self.PlayBrowserDriver, MinToPlayEntry=MinToPlayEntry)
            if (not isPlaying):
                testStatus = False
                self.logi.appendMsg("FAIL - 1 minute of played video after BACK TO LIVE, did NOT play the video OK. Details:Entry = "+ str(self.entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                return
            else:
                self.logi.appendMsg("PASS - 1 minute of played video after BACK TO LIVE, played OK.Details:Entry = "+ str(self.entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))            
            if testStatus == True:
                self.logi.appendMsg("PASS - 1 minute of played video after BACK TO LIVE, played OK.EntryId = " + str(self.entryId))
            else:
                self.logi.appendMsg("FAIL - 1 minute of played video after BACK TO LIVE, did NOT play the video OK.EntryId = " + str(self.entryId))    
                      
            #Stop streaming - kill ffmpeg ps   
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                testStatus = False
                return    
            
                           
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
        print (' Tear down')

        try:
            self.PlayBrowserDriver
        except Exception as Exp:
            print (Exp)
            pass

        try:
            self.Wd.quit()
        except Exception as Exp:
            print (Exp)
            pass
        print ('Tear down - testTeardownclass')
        
        try:
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print (Exp)
           pass
        print ('#############')
        if testStatus == False:
           print ("fail")
           self.practitest.post(Practi_TestSet_ID, '4113','1') 
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print ("pass")
           self.practitest.post(Practi_TestSet_ID, '4113','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x4113_LiveNG_Passthrough_DVR_PlayerV3.py -s')
    #===========================================================================
        
        
        