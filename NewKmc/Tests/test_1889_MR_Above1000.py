'''
@author: Moran.Cohen
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@test_name: test_1889_MR_Above1000
 
 @desc : This test check mediaRepurposing dry run url log on case of above 1000 items  
 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''



import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import KmcBasicFuncs
import reporter2

import Config
import Practitest
import autoitWebDriver
import MediaRepurposingFuncs
import time

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

class TestClass:
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        try:       
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.user   = inifile.RetIniVal(section,'userElla')
                self.pwd    = inifile.RetIniVal(section,'passElla')
                self.Partner_ID = inifile.RetIniVal(section, 'partnerElla')
                self.MediaRepurposingID = "4131" #> 1000
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user   = inifile.RetIniVal(section,'AdminConsoleUser')
                self.pwd    = inifile.RetIniVal(section,'AdminConsolePwd')
                self.Partner_ID = inifile.RetIniVal(section, 'partnerId4770')
                self.MediaRepurposingID = "1237" #> 1000
                
            self.url    = inifile.RetIniVal(section,'admin_url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')
            self.admin_user = inifile.RetIniVal('admin_console_access', 'session_user')
            self.env = inifile.RetIniVal('admin_console_access', 'environment')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()            
            self.practitest = Practitest.practitest()
            self.logi = reporter2.Reporter2('test_1889_MR_Above1000')
            self.practitest = Practitest.practitest('4586')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.MediaRepurposingFuncs = MediaRepurposingFuncs.MediaRepurposingFuncs(self.Wd, self.logi)
            self.ExpectedMediaRepurposingAlertResult = "Dry run for MR profile id [" + self.MediaRepurposingID + "] has been Assign. This could take couple of minutes. Results will be save to file."
             
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()         
        except:
            pass   
        
    def test_1889_MR_Above1000(self):
        
        global testStatus
        self.logi.initMsg('test_1889_MR_Above1000')       
        
        try:
            try:  
                self.logi.appendMsg("INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                if "nv" not in self.url:  # Bypass NVD console user/pass login
                    ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                                self.admin_user, self.env)
                else:
                    ks = False
                rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.url,self.user,self.pwd,ks)
                if(rc):
                    self.logi.appendMsg("PASS - Admin Console login.")
                else:       
                    self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                    testStatus = False
                    return
            except:
                pass     
                    
            time.sleep(2)
            
            self.Wd.maximize_window()
        
            self.logi.appendMsg("INFO - Going to Navigate to MediaRepurposing screen. Partner_ID: " + self.Partner_ID)
            rc= self.MediaRepurposingFuncs.AdminConsole_Navigate_MediaRepurposing(self.Partner_ID)
            if not rc:
                self.logi.appendMsg("FAIL - Navigate to MR profile screen, Partner_ID: " + self.Partner_ID)
                testStatus = False
                return
            
            time.sleep(4)
                     
            # Select MediaRepurposing profile id
            self.logi.appendMsg("INFO - Going to perform dry run by:Media Repurposing ID = " + self.MediaRepurposingID)
            rc = self.MediaRepurposingFuncs.MediaRepurposing_DryRun(self.MediaRepurposingID)
            if not rc:
                self.logi.appendMsg("FAIL - Could NOT perform dry run by - Media Repurposing ID= " + self.MediaRepurposingID)
                testStatus = False
                return
            time.sleep(3)
            
            # Verify MediaRepurposing alert and return job id
            self.logi.appendMsg("INFO - Going to verify Alert result of dry run:Media Repurposing ID = " + self.MediaRepurposingID)
            rc,ActualbatchJobId = self.MediaRepurposingFuncs.MediaRepurposing_VerfiyAlertDryRun(self.MediaRepurposingID,self.ExpectedMediaRepurposingAlertResult)
            if not rc:
                self.logi.appendMsg("FAIL - Verify dry run of - Media Repurposing ID= " + self.MediaRepurposingID )
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS - Dry run of - Media Repurposing ID= " + self.MediaRepurposingID + " ,ActualbatchJobId = " + ActualbatchJobId )
            time.sleep(3)                     
            # Perform MediaRepurposing Dry Run Identification
            self.logi.appendMsg("INFO - Going to Perform MediaRepurposing Dry Run Identification: ActualbatchJobId = " + ActualbatchJobId)
            rc = self.MediaRepurposingFuncs.MediaRepurposing_DryRunIdentificationResultAbove1000(ActualbatchJobId)
            if not rc:
                self.logi.appendMsg("FAIL - MediaRepurposing Dry Run Identification - ActualbatchJobId = " + ActualbatchJobId )
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS - MediaRepurposing Dry Run Identification - Media Repurposing ID= " + self.MediaRepurposingID + " ,ActualbatchJobId = " + ActualbatchJobId )    
          
       
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - MediaRepurposing |Login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            pass           
   
   
   
   
    def teardown_class(self):
         
        global testStatus
         
         
        self.Wd.quit()
         
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1889','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1889','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
                            
    #===========================================================================
    # pytest.main(args=['test_1889_MR_Above1000.py','-s'])
    # pytest.main('test_1889_MR_Above1000.py -s')    
    #===========================================================================
