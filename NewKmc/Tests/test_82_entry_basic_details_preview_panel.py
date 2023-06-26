import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import DOM
import MySelenium
import KmcBasicFuncs
import reporter2

import datetime
import uploadFuncs
import Config
import Practitest
import autoitWebDriver
import Entrypage


### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True


#================================================================================================================================
#  @Author: Erez Bouskila
# Test description:
#================================================================================================================================


class TestClass:

    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userName5')
            self.pwd = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')

            self.logi = reporter2.Reporter2('test_82_entry_basic_details_preview_panel')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entryName = 'test 82'
            self.medialess_entry_name = 'test 82 medialess'
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_82_entry_basic_details_preview_panel(self):

        global testStatus
        self.logi.initMsg('test_82_entry_basic_details_preview_panel')

        try:
            # Invoke and login
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return

            time.sleep(1)

            try:
                self.basicFuncs.deleteEntries(self.Wd, self.entryName)
                self.logi.appendMsg("INFO - entries deleted")
            except:
                pass

            self.logi.appendMsg("INFO - step 2: Going to bulk upload entries")

            self.logi.appendMsg("INFO - going to do bulk upload")
            self.logi.appendMsg("INFO - going to upload csv file - test939.csv")
            the_time = str(datetime.datetime.time(datetime.datetime.now()))[:5]

            self.uploadfuncs.bulkUpload("entry", 'kaltura_batch_upload_test_82.xml')

            self.logi.appendMsg(
                "INFO - going to verify the bulk upload message window appear with the correct text in it")
            rc = self.uploadfuncs.bulkMessageAndStatus("Finished successfully", the_time)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to bulk upload entries")
                return
            else:
                self.logi.appendMsg("INFO - going to entries tab")
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to open first entry")
            rc = self.basicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL step 3 - could not find the entry- " + self.entryName + " in entries table")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(2)

            self.logi.appendMsg("INFO - step 4: Going to verify audio elements")
            if self.entryPage.verify_entry_preview_details() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to verify audio elements")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4.1: Going to navigate to next entry")
            if self.entryPage.navigate_entries('previous') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4.1: FAILED to navigate to next entry")
                return
            else:
                self.logi.appendMsg("Pass - step 4.1")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to verify image elements")
            if self.entryPage.verify_entry_preview_details() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to verify image elements")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5.1: Going to navigate to next entry")
            if self.entryPage.navigate_entries('next') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5.1: FAILED to navigate to next entry")
                return
            else:
                self.logi.appendMsg("Pass - step 5.1")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to verify video elements")
            if self.entryPage.verify_entry_preview_details() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to verify video elements")
                return
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(5)

            self.logi.appendMsg("INFO - step 6.1: Going to navigate to entries page")
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()

            time.sleep(5)

            self.logi.appendMsg("INFO - step 7: Going to prepare an empty video entry")
            if self.uploadfuncs.prepare_entry(entry_type='video', entry_name=self.medialess_entry_name) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to prepare an empty video entry")
                return
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(5)

            self.logi.appendMsg("INFO - step 8: Going to open media less entry")
            rc = self.basicFuncs.selectEntryfromtbl(self.Wd, self.medialess_entry_name, True)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL step 8 - could not find the entry- " + self.medialess_entry_name + " in entries table")
                return
            else:
                self.logi.appendMsg("Pass - step 8")

            time.sleep(5)

            self.logi.appendMsg("INFO - step 9: Going to verify media less entry elements")
            if self.entryPage.verify_entry_preview_details(medialess=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 9: FAILED to verify media less entry elements")
                return
            else:
                self.logi.appendMsg("Pass - step 9")

            time.sleep(1)

        except Exception as e:
            self.logi.appendMsg(e)
            testStatus = False
            pass

    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):

        global testStatus

        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            self.basicFuncs.deleteEntries(self.Wd, self.entryName)
            self.logi.appendMsg("INFO - entries deleted")
        except:
            pass

        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '82', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '82', '0')
            assert True

    #===========================================================================
    # pytest.main('test_82_entry_basic_details_preview_panel.py -s')
    #===========================================================================
