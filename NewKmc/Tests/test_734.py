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

import Config
import Practitest
import autoitWebDriver
from uploadFuncs import uploadfuncs

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
            
            self.logi = reporter2.Reporter2('TEST734')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            if self.Wdobj.RUN_REMOTE:  
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver() 
                self.entriesName = "@#]%"
            else:
                self.entriesName = "@#&%"
                
            
        except:
            pass
        
        
    def test_734(self):
        
        global testStatus
        self.logi.initMsg('test 734')
        
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
                return
                  
            uploadFromDesktop.click()
            time.sleep(5)

            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            fname = '@#&%.jpg'
            pthstr = str(os.path.abspath(os.path.join(pth, fname)))
            uploadfuncs.windows_upload_dialog(self, pthstr)

            time.sleep(3)
            self.logi.appendMsg("INFO- going to verify files data are correct in \"Upload Settings\" window")
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            uploadSettingsRow = uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
            
            mtype = "Image"
            fsize = "497.64 KB"
                  
            fline = str(uploadSettingsRow[1].text)
            farr = fline.split("\n")
            if fname[:4]!= farr[0]:
                self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, file name = " + fname + " and actual value = " +  farr[0])
                testStatus = False
            if mtype!= farr[1]:
                self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, file type = " + mtype + " and actual value = " +  farr[1])
                testStatus  = False
            if fsize!= farr[2]:
                self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, file size = " + fsize + " and actual value = " + farr[2])
                testStatus  = False
               
              
            self.logi.appendMsg("INFO- going to upload the file")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)
              
            self.logi.appendMsg("INFO- going to wait that the entry would be in status Ready")
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,fname[:4])
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \""  + fname + "\" status was not changed to Ready after 5 minutes, this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \""  + fname + "\" uploaded successfully")
            
                  
            self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
            time.sleep(3)
        
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
        except Exception as Exp:
            print(Exp)
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '734','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '734','0')
            assert True         
        
            
        
            
        
    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_734.py', '-s'])
    #===========================================================================
 
