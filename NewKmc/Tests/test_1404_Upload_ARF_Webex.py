import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import MySelenium
import KmcBasicFuncs
import reporter2
import uploadFuncs
import Config
import Practitest
import autoitWebDriver

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    Practi_TestSet_ID = '1418'
else:
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
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userName6')
            self.pwd    = inifile.RetIniVal(section, 'pass6')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST1404_Upload_ARF_Webex')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entriesName = "webex-1min"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
        
        except:
            pass
            
    def test_1404_Upload_ARF_Webex(self):
        
        global testStatus
        self.logi.initMsg('test 1404_Upload_ARF_Webex')
         
        try:  
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
              
            self.logi.appendMsg("INFO - going to upload ARF file")
            # except:
            #     assert False
            #
            #
            #
            #
            #
            self.uploadfuncs.uploadFromDesktop('webex-1min.arf')
            time.sleep(3)
              
            self.logi.appendMsg("INFO- going to wait until the entry will be in status Ready")
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"webex-1min",600)
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \"webex-1min\" status was not changed to Ready after 10 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \"webex-1min\" uploaded successfully")
        
        except:
            testStatus = False
            pass
      
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName)           
        except:
            pass
        
            
            
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1404','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1404','0')
            assert True         
        

    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_1404_Upload_ARF_Webex.py', '-s'])
    #===========================================================================
 
        