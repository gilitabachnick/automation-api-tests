import os
import sys

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
            self.user   = inifile.RetIniVal(section, 'userUpload')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST1308')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entriesName = "AVI_8"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
        except:
            pass
        
    def test_1308(self):
        
        global testStatus
        self.logi.initMsg('test 1308')
        
        try:  
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
              
            self.logi.appendMsg("INFO - going to upload AVI file")
            # except:
            #     assert False
            #
            #
            #
            #
            #
            self.uploadfuncs.uploadFromDesktop('AVI_8.avi')
            self.logi.appendMsg("INFO- going to wait until the entry will be in status Ready")
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"AVI_8")
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \"AVI_8\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \"AVI_8\" uploaded successfully")
            
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
            self.practitest.post(Practi_TestSet_ID, '1308', '1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1308', '0')
            self.logi.reportTest('pass',self.sendto)
            assert True

    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_1308.py', '-s'])
    #===========================================================================
 
        