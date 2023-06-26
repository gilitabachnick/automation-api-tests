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

            self.logi = reporter2.Reporter2('TEST732')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entriesName = "01;smalljpg;smallmp4"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
        except Exception as e:
            print(e)
        
    def test_732(self):
        
        global testStatus
        try:
            self.logi.initMsg('test 732')

            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            self.logi.appendMsg("INFO - going to upload different kind of files")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
            try:
                uploadFromDesktop =  self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            except Exception as Exp:

                self.logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
                self.logi.reportTest('fail',self.sendto)
                assert False

            uploadFromDesktop.click()  # Upload first file
            time.sleep(3)
            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
            pthstr = str(os.path.abspath(os.path.join(pth, '01.wav')))
            uploadfuncs.windows_upload_dialog(self, pthstr)

            uploadFilesNames = ['smalljpg.jpg', 'smallmp4.mp4']

            for filename in uploadFilesNames:
                time.sleep(2)
                pthstr = str(os.path.abspath(os.path.join(pth, filename)))
                self.Wd.find_element_by_xpath(DOM.UPLOAD_ADD_FILE).click()
                time.sleep(2)
                uploadfuncs.windows_upload_dialog(self, pthstr)

            time.sleep(3)
            self.logi.appendMsg("INFO- going to verify files data are correct in \"Upload Settings\" window")
            uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
            uploadSettingsRow = uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
            dictFilename = {1:"01",
                            2:"smalljpg",
                            3:"smallmp4"}
            dictMediaType = {1:"Audio",
                             2:"Image",
                             3:"Video"}
            dictSize    = {1:"1.94 MB",
                           2:"50.75 KB",
                           3:"160.96 KB"}

            i=1

            for row in(uploadSettingsRow[1:]):

                fline = str(row.text)
                farr = fline.split("\n")
                if dictFilename[i]!= farr[0]:
                    self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, in line " + str(i) + " for file name = " + dictFilename[i] + " and actual value = " +  farr[0])
                    testStatus = False
                if dictMediaType[i]!= farr[1]:
                    self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, in line " + str(i) + " for file type = " + dictMediaType[i] + " and actual value = " +  farr[1])
                    testStatus  = False
                if dictSize[i]!= farr[2]:
                    self.logi.appendMsg("FAIL - Expected in \"UPLOAD SETTINGS\" window, in line " + str(i) + " for file size = " + dictSize[i] + " and actual value = " + farr[2])
                    testStatus  = False
                i+=1

            self.logi.appendMsg("INFO- going to upload the files")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)

            self.logi.appendMsg("INFO- going to wait that the entries would be in status Ready")
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"01",600)
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \"01\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \"01\" uploaded successfully")
            time.sleep(1)
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"smallmp4",300)
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \"smallmp4\" status was not changed to Ready after 5 minutes, this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - the entry \"smallmp4\" uploaded successfully")
            time.sleep(1)
            entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,"smalljpg",300)
            if not entryStatus:
                self.logi.appendMsg("FAIL - the entry \"smalljpg\" status was not changed to Ready after 5 minutes, this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                self.logi.appendMsg("PASS - the entry \"smalljpg\" uploaded successfully")

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
                self.practitest.post(Practi_TestSet_ID, '732', '1')
                self.logi.reportTest('fail',self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '732', '0')
                self.logi.reportTest('pass',self.sendto)
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_732.py', '-s'])
    # ===========================================================================
