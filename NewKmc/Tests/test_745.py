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
            self.user   = inifile.RetIniVal(section, 'userUpload')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST745')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")   
            self.entriesName = "Autotest_File"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()

        except Exception as e:
            print(e)
        
    def test_745(self):
        
        global testStatus
        self.logi.initMsg('test 745')
        
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
            
            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            pthstr = str(os.path.abspath(os.path.join(pth, '01.wav')))
            uploadfuncs.windows_upload_dialog(self, pthstr)
            
            time.sleep(3)   
            
            self.logi.appendMsg("INFO- going to Edit the image name to Autotest_File")
            mouse = webdriver.ActionChains(self.Wd)
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            uploadSettingsRow = uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
            row = uploadSettingsRow[1]
            dd= row.find_elements_by_xpath(".//td")
            mouse.move_to_element(dd[1]).perform()
            time.sleep(1)
            row.find_element_by_xpath(DOM.UPLOAD_SETTINGS_EDIT).click()
            time.sleep(1)

            uploadSettingsWin.find_element_by_xpath(DOM.UPLOAD_SETTIGS_EDIT_FILENAME).send_keys(Keys.CONTROL,"a")
            uploadSettingsWin.find_element_by_xpath(DOM.UPLOAD_SETTIGS_EDIT_FILENAME).send_keys("Autotest_File")
                                       
            self.logi.appendMsg("INFO- going to upload the file")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)
              
            self.logi.appendMsg("INFO- going to verify the entry is uploading and with its new name")
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"Autotest_File", 600)
            if not entryStatus:
                if lineText=="NoEntry":
                    self.logi.appendMsg("FAIL - new entry with the name \"Autotest_File\" was not created")
                else:
                    self.logi.appendMsg("FAIL - the entry \"Autotest_File\" created but its status was not changed to Ready after 10 minutes, this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \"Autotest_File\" uploaded successfully with its new name")
                   
            self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
            time.sleep(3)

        except Exception as e:
            print(e)
            testStatus = False

            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName)
        except Exception as e:
            self.logi.appendMsg("Teardown - failed to delete entries")
            print(e)
        
        try:
            self.Wd.quit()
        except Exception as e:
            print(e)

        try:
            if testStatus == False:
                self.logi.reportTest('fail',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '745','1')
                assert False
            else:
                self.logi.reportTest('pass',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '745','0')
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_745.py', '-s'])
    # ===========================================================================
