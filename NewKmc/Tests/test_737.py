import os
import subprocess
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
    Practi_TestSet_ID = '1991'
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
            
            self.logi = reporter2.Reporter2('TEST737')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()   
            self.entriesName = "smalljpg"
            
        except Exception as Exp:
            print(Exp)
            pass    
        
    def test_737(self):
        
        global testStatus
        self.logi.initMsg('test 737')
        
        try:  
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
              
            self.logi.appendMsg("INFO - going to upload different kind of files")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
            try:
                uploadFromDesktop =  self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            except:
                self.logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
                self.logi.reportTest('fail',self.sendto)
                assert False
            
            time.sleep(1)      
            uploadFromDesktop.click()
            time.sleep(5)
            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            pthstr = str(os.path.abspath(os.path.join(pth, '01.wav')))
            uploadfuncs.windows_upload_dialog(self, pthstr)
            #
            #
            #
            #
            #
            uploadFilesNames = ['smalljpg.jpg', 'smallmp4.mp4']
            for filename in uploadFilesNames:
                time.sleep(2)
                pthstr = str(os.path.abspath(os.path.join(pth, filename)))
                self.Wd.find_element_by_xpath(DOM.UPLOAD_ADD_FILE).click()
                time.sleep(2)
                uploadfuncs.windows_upload_dialog(self, pthstr)
            self.logi.appendMsg("INFO- going to verify files data appear in \"Upload Settings\" window")
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            uploadSettingsRow = uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
            dictFilename = {1:"01",
                            2:"smalljpg",
                            3:"smallmp4"}
            
             
            i=1
              
            for row in(uploadSettingsRow[1:]):
                  
                fline = str(row.text)
                farr = fline.split("\n")
                if dictFilename[i]!= farr[0]:
                    self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, in line " + str(i) + " for file name = " + dictFilename[i] + " and actual value = " +  farr[0])
                    testStatus = False
                
                i+=1
                       
            if testStatus:
                    self.logi.appendMsg("PASS - all 3 rows appear in upload settings window")
                    
            # close the upload settings window without uploading any of the entries
            self.logi.appendMsg("INFO- going to close the upload settings window without uploading any entry")
            closeButton = self.BasicFuncs.selectOneOfInvisibleSameObjects(self.Wd, DOM.UPLOAD_SETTINGS_CLOSE)
            closeButton.click() 
            
            # open upload from desktop widow again and verify no files already appears there
            self.logi.appendMsg("INFO- going to open upload from desktop widow again and verify no files already appears there")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
            try:
                uploadFromDesktop =  self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            except:
                self.logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
                self.logi.reportTest('fail',self.sendto)
                assert False
            
            uploadFromDesktop.click()
            time.sleep(2)   
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            try:
                uploadSettingsWin.find_element_by_xpath("//h1[text()='No files to upload']")
                self.logi.appendMsg("PASS - the upload settings window popped empty as expected")
                
                
            except:
                self.logi.appendMsg("FAIL - the upload settings window popped not expected")
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
            self.practitest.post(Practi_TestSet_ID, '737','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '737','0')
            assert True         

    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_737.py', '-s'])
    #===========================================================================
 
