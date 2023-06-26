import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import KmcBasicFuncs
import reporter2
from uploadFuncs import uploadfuncs
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
                
                self.logi = reporter2.Reporter2('TEST746')
                
                self.Wdobj = MySelenium.seleniumWebDrive()
                self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome") 
                if self.Wdobj.RUN_REMOTE:
                    self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                    self.AWD =  self.autoitwebdriver.retautoWebDriver()  

        except:
            pass
        
    def test_746(self):
        
        global testStatus
        self.logi.initMsg('test 746')
        
        try:  
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
              
            self.logi.appendMsg("INFO - going to upload a file with special characters in the name of it")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
            try:
                uploadFromDesktop =  self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            except:
                self.logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
                self.logi.reportTest('fail',self.sendto)
                assert False
                  
            uploadFromDesktop.click()
            time.sleep(5)
            
            
            time.sleep(3)
            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
            pthstr = str(os.path.abspath(os.path.join(pth, 'smalljpg.jpg')))
            uploadfuncs.windows_upload_dialog(self, pthstr)

            self.logi.appendMsg("INFO- going to delete the image name and try to upload")
            mouse = webdriver.ActionChains(self.Wd)
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            uploadSettingsRow = uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
            row = uploadSettingsRow[1]
            dd= row.find_elements_by_xpath(".//td")
            mouse.move_to_element(dd[1]).perform()
            row.find_element_by_xpath(DOM.UPLOAD_SETTINGS_EDIT).click()
            time.sleep(1)
            uploadSettingsWin.find_element_by_xpath(DOM.UPLOAD_SETTIGS_EDIT_FILENAME).send_keys(Keys.CONTROL,'a',Keys.DELETE)
            self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()                                  
            time.sleep(1)
            
            try:
                row.find_element_by_xpath(DOM.UPLOAD_SETTINGS_ERROR) 
                self.logi.appendMsg("PASS - The file was not uploaded with empty name, the error icon appeared in upload settings window")
            except:
                self.logi.appendMsg("FAIL - the error icon did not appear in upload settings window")
                testStatus = False
        
        except:
            testStatus = False
            pass              
      
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        
        global testStatus
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '746','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '746','0')
            assert True         
        
            
        
            
        
    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_746.py', '-s'])
    #===========================================================================
 
