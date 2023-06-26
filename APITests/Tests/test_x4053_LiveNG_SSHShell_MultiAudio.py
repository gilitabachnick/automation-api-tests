'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_4055_ExistLiveNG_SSHShell_MultiAudio.py
 
 @desc : this test check exist LiveNG entry  with RTMP streaming by SSH shellscript
 verification of Playback and liveDashboard Analyzer  

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter2
import Config
import Practitest
import Entry
import tearDownclass
import MySelenium

import live
import LiveDashboard
import Transcoding

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
isProd =  os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

isProd = True#for now it's just working on Production old live partner(1794961)
#For now also It's not supported on liveNG therefore failed live dashboard tests
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
             # Streaming details
            self.url= "www.kaltura.com"
            self.playerId = "32845731"
            self.PublisherID = "1794961"
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            #self.cmdLine ="" #No parameters script 
            print('PRODUCTION ENVIRONMENT')

            
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            self.url= "qa-apache-php7.dev.kaltura.com"
            # Streaming details
            self.playerId = "15227406"#"v2 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')#"6611"
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            #self.cmdLine_parametners ="" #No parametners script          
            print('TESTING ENVIRONMENT') 
        
        self.filePath = "/home/kaltura/tests/LIVENG_ma_stream_prod_AUTOMATION.sh"    
        self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')    
        self.sendto = "moran.cohen@kaltura.com;"        
        #***** SSH streaming server - liveng-core3-automation.kaltura.com
        self.remote_host = "liveng-core3-automation.kaltura.com"
        self.remote_user = "root"
        self.remote_pass = "testingqa"  
        
        self.PlayerVersion = 2 # Player version 2 or 3
        self.NumOfEntries = 1

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('1327')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()                            
        self.logi = reporter2.Reporter2('test_4053_LiveNG_SSHShell_MultiAudio')
        self.logi.initMsg('test_4053_LiveNG_SSHShell_MultiAudio')     
        
        # Live objects
        self.Wd = None
        self.LiveDashboard = None
        self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
        #=======================================================================
        # # create client session
        # self.logi.appendMsg('INFO - start create session for partner: ' + self.PublisherID)
        # mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        # self.client = mySess.OpenSession()
        # time.sleep(2)
        # version = -1
        # self.entry = self.client.baseEntry.get(self.entryId)
        # self.entrieslst = []
        # self.entrieslst.append(self.entry)
        #=======================================================================
        # create client session
        self.logi.appendMsg('INFO - start create session for partner: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
                  
        ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
        Transobj = Transcoding.Transcoding(self.client,'Eng+SPA partner 0 profile')
        self.Eng_SPA_ProfileID = Transobj.getTranscodingProfileIDByName('Eng+SPA partner 0 profile')
        if self.Eng_SPA_ProfileID==None:
            if self.env == "prod":
                self.Eng_SPA_ProfileID = Transobj.addTranscodingProfile(1,'32,100,101')
            else:
                self.Eng_SPA_ProfileID = Transobj.addTranscodingProfile(1,'32,583728,583734')
            if isinstance(self.passtrhroughId,bool):
                testStatus = False
                return
            
        # Create self.NumOfEntries live entries
        self.entrieslst = []
        self.streamUrl = []
        for i in range(0, self.NumOfEntries):
            Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_LINUX_LiveEntry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.Eng_SPA_ProfileID)
            self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
            self.entrieslst.append(self.entry)
            self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
            streamUrl = self.client.liveStream.get(self.entry.id)
            self.streamUrl.append(streamUrl)
            #self.cmdLine_parametners = str(self.Eng_SPA_ProfileID) + " " + str(self.PublisherID) + " " + str(self.entry.id) + " " + str(self.streamUrl[i].primaryBroadcastingUrl) + " " + str(self.playerId)
            self.cmdLine_parametners = str(self.Eng_SPA_ProfileID) + " " + str(self.PublisherID) + " " + str(self.entry.id) + " " + str(self.playerId) + " " + str(self.url) + " " + str(self.streamUrl[i].primaryBroadcastingUrl)
    def test_4053_LiveNG_SSHShell_MultiAudio(self):
        global testStatus
        try:            
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id) 
                #****** ssh streaming entry
                self.logi.appendMsg("INFO - Going to stream EXIST entry by file ssh streamEntryByShellScript." + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + self.playerId + " , " + self.url + ", primaryBroadcastingUrl=" + str(self.streamUrl[i].primaryBroadcastingUrl))
                rc,resultData = self.liveObj.streamEntryByShellScript(self.remote_host, self.remote_user, self.remote_pass,self.filePath, self.entryId,self.entrieslst,self.PublisherID, self.playerId,self.url,PlayerVersion=self.PlayerVersion,cmdLine=self.cmdLine_parametners,QRcode=False,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
                if rc != False:
                    self.logi.appendMsg("INFO - Going to verify the result of streamEntryByShellScript")
                    rc = self.liveObj.VerifyResultFromStreamEntryByShellScript(resultData)
                    if rc != False:
                        self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + self.playerId + " , " + self.url)
                    else:
                        self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + self.playerId + " , " + self.url)
                else:
                    print("******** Fail - Return result from streamEntryByShellScript")
                    self.logi.appendMsg("FAIL - streamEntryByShellScript resultData=" + str(resultData) + ". streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return
                #******* CHECK CPU usage of streaming machine
                    self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))           
                    cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"                
                    rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine)
                    if rc == True:
                        self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
                    else:
                        self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                        testStatus = False
                        return                
                #**** Login LiveDashboard
                self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
                self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
                time.sleep(5)
                self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
                rc = self.LiveDashboard.invokeLiveDashboardLogin(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL)
                if(rc):
                    self.logi.appendMsg("PASS - LiveDashboard login.")
                else:       
                    self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                    testStatus = False
                    return
                time.sleep(5)
                #****** Channels tab     
                navigateTo= "Channels"
                rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo)
                if(rc):
                    self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                else:       
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                    testStatus = False
                    return
                self.logi.appendMsg("INFO - Waiting to status Stopped - 30 sec")
                time.sleep(20)#wait for status to Stopped 
                #Return row data from Channels
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
                rowsNum=len(RowData)
                i=1
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Channels of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,"Stopped")
                    if(rc):
                        self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        testStatus = False    
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
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                    testStatus = False
                    return
               
                 # Return row data from Alerts
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo)
                    if(rc):
                        self.logi.appendMsg("PASS -VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        testStatus = False    
                else:       
                    self.logi.appendMsg("FAIL -ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
         
            #===================================================================
            # try:
            #     self.logi.appendMsg("INFO - Going to close browser")
            #     self.Wd.quit()
            # except Exception as Exp:
            #     print Exp
            #     pass
            #===================================================================
                           
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
        print('Tear down')
        try:
            print('Tear down - Wd.quit')
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        print('#############')
        try:
            print('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '4053','1') 
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '4053','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x4053_LiveNG_SSHShell_MultiAudio.py -s')
    #===========================================================================
        
        
        