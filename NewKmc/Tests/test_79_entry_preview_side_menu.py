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

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
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


#================================================================================================================================
#  @Author: Erez Bouskila
#  Updated: Zeev Shulman 21.10.2021
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

            self.logi = reporter2.Reporter2('test_79_entry_preview_side_menu')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entryName = 'test 82'

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as e:
            print(e)

    def test_79_entry_preview_side_menu(self):

        global testStatus
        self.logi.initMsg('test_79_entry_preview_side_menu')

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

            self.logi.appendMsg("INFO - step 2: Going to bulk upload entries")

            self.logi.appendMsg("INFO - going to do bulk upload")
            self.logi.appendMsg("INFO - going to upload csv file - test939.csv")
            self.uploadfuncs.bulkUpload("entry", 'kaltura_batch_upload_test_82.xml')
            self.logi.appendMsg(
                "INFO - going to verify the bulk upload message window appear with the correct text in it")

            the_time = str(datetime.datetime.time(datetime.datetime.now()))[:5]

            rc = self.uploadfuncs.bulkMessageAndStatus("Finished successfully", the_time, 900)
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

            self.logi.appendMsg("INFO - step 4: Going to verify entry preview side menu")
            if self.entryPage.verify_entry_side_preview_menu(self.env) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to verify entry preview side menu")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4.1: Going to cycle through side menu")
            if self.entryPage.cycle_through_side_menu(self.env) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4.1: FAILED to cycle through side menu")
                return
            else:
                self.logi.appendMsg("Pass - step 4.1")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to navigate to next entry")
            if self.entryPage.navigate_entries('next') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to navigate to next entry")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to verify entry preview side menu")
            if self.entryPage.verify_entry_side_preview_menu(self.env) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to verify entry preview side menu")
                return
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6.1: Going to cycle through side menu")
            if self.entryPage.cycle_through_side_menu(self.env) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6.1: FAILED to cycle through side menu")
                return
            else:
                self.logi.appendMsg("Pass - step 6.1")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to navigate to next entry")
            if self.entryPage.navigate_entries('next') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to navigate to next entry")
                return
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 8: Going to verify entry preview side menu")
            if self.entryPage.verify_entry_side_preview_menu(self.env) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 8: FAILED to verify entry preview side menu")
                return
            else:
                self.logi.appendMsg("Pass - step 8")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 8.1: Going to cycle through side menu")
            if self.entryPage.cycle_through_side_menu(self.env) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 8.1: FAILED to cycle through side menu")
            else:
                self.logi.appendMsg("Pass - step 8.1")

            time.sleep(1)

        except Exception as e:
            print(e)
            testStatus = False

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):
        global testStatus
        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(1)
            self.basicFuncs.deleteEntries(self.Wd, self.entryName)
            self.logi.appendMsg("Pass - Teardown entries deleted")
        except Exception as e:
            print(e)
            self.logi.appendMsg("Fail - Teardown Failed to delete entries")
            testStatus = False

        try:
            self.Wd.quit()
        except Exception as e:
            print(e)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '79', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '79', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as e:
            print(e)
    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_79_entry_preview_side_menu', '-s'])
    # ===========================================================================
