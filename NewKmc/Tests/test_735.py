import os
import sys
import time

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
            
            self.logi = reporter2.Reporter2('TEST735')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            if self.Wdobj.RUN_REMOTE:   
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            self.entriesName = "smalljpg"
            
        except Exception as exp:
            pass
        
        
    def test_735(self):
        
        global testStatus
        self.logi.initMsg('test 735')
        
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

            pthstr = str(os.path.abspath(os.path.join(pth, 'smalljpg.jpg')))
            uploadfuncs.windows_upload_dialog(self, pthstr)
            time.sleep(3)               
            self.logi.appendMsg("INFO- going to replace the file type to Video instead of Image")
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_MTYPE_FATHER)[1].click()
            self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_TYPE_VIDEO).click()
            time.sleep(3)                     
            self.logi.appendMsg("INFO- going to upload the file")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)
              
            self.logi.appendMsg("INFO- going to wait that the entry would be in status Ready")
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"smalljpg")
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \"smalljpg\" status was not changed to Ready after 5 minutes, this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \"smalljpg\" uploaded successfully")
            
            
            self.logi.appendMsg("INFO- going to verify that the media type is Video as set")
            mediaType = self.BasicFuncs.retEntryMediaType(self.Wd)
            try:
                if mediaType!= "video":
                    self.logi.appendMsg("FAIL - the media type of the entry should have been Video and it is actually - " + mediaType)
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - the media type of the entry is Video as expected")
                
            except:
                self.logi.appendMsg("FAIL - the media type of the entry should have been Video and it is actually have no media type showed or could not retreive it from the page")
                testStatus = False
                  
            self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
            time.sleep(3)
        
        except Exception as Exp:
            testStatus = False
            pass  
            
      
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName)
        except Exception as Exp:
            print(Exp)
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '735','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '735','0')
            assert True         
        

    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_735.py', '-s'])
    #===========================================================================
 
