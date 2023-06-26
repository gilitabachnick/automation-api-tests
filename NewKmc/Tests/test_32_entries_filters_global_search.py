import os
import sys
import time

import pytest

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

            self.logi = reporter2.Reporter2('test_32_Entries_Filters_global_search')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entryName1 = 'hello world'
            self.entryName2 = 'world ! hello'
            self.entryName3 = 'hello, world'
            self.entryName4 = '"Hello World"'
            self.tag = 'creative'
            self.description = 'Homepage'
            self.error_rule = '!'
            self.error_msg = "Search engine query failed"

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_32_entries_filters_global_search(self):

        global testStatus
        self.logi.initMsg('test_32_Entries_Filters_global_search')

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
                self.basicFuncs.deleteEntries(self.Wd, self.entryName3)
                self.logi.appendMsg("INFO - entries deleted")
            except:
                pass

            self.logi.appendMsg("INFO - step 2: Going to bulk upload entries")

            self.logi.appendMsg("INFO - going to do bulk upload")
            self.logi.appendMsg("INFO - going to upload csv file - kaltura_batch_upload_test_32.csv")
            the_time = str(datetime.datetime.time(datetime.datetime.now()))[:5]

            self.uploadfuncs.bulkUpload("entry", 'kaltura_batch_upload_test_32.csv')

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

            self.logi.appendMsg("INFO - step 3: Going to search by tag")
            rc = self.basicFuncs.searchEntrySimpleSearch(self.Wd, self.tag)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL step 3 - could not find the entry- " + self.entryName1 + " in entries table")
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(2)

            self.logi.appendMsg("INFO - step 4: Going to verify search by tag")
            if self.basicFuncs.verify_entry_search_result(self.Wd, self.logi, self.tag) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to veriy search by tag")
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to search by description")
            rc = self.basicFuncs.searchEntrySimpleSearch(self.Wd, self.description)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL step 5 - could not find the entry- " + self.entryName1 + " in entries table")
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(2)

            self.logi.appendMsg("INFO - step 6: Going to verify search by description")
            if self.basicFuncs.verify_entry_search_result(self.Wd, self.logi, self.description) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to verify search by description")
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to search by owner")
            rc = self.basicFuncs.searchEntrySimpleSearch(self.Wd, self.user)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL step 7 - could not find the entry- " + self.entryName1 + " in entries table")
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(2)

            # searcing by owner will return more then 1, this is expected
            self.logi.appendMsg("INFO - step 8: Going to verify search by owner - FAIL IS EXPECTED IN THIS CASE")
            if self.basicFuncs.verify_entry_search_result(self.Wd, self.logi, self.user) == False:
                self.logi.appendMsg("Pass - step 8")
            else:
                testStatus = False
                self.logi.appendMsg("FAIL - step 8: FAILED to verify search by owner")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 9-12: Going to search using search rules")
            search_rules = [self.entryName1, self.entryName2, self.entryName3, self.entryName4]
            for rule in search_rules:
                rc = self.basicFuncs.searchEntrySimpleSearch(self.Wd, rule)
                if not rc:
                    testStatus = False
                    self.logi.appendMsg("FAIL step 9-12 - could not find the entry- " + rule + " in entries table")
                else:
                    self.logi.appendMsg("Pass - step 9-12")

                time.sleep(2)

                # searcing by owner will return more then 1, this is expected
                self.logi.appendMsg("INFO - step 9-12: Going to verify search by rule")
                if self.basicFuncs.verify_entry_search_result(self.Wd, self.logi, rule) == False:
                    # Expected fail with search rule OR - ','
                    if rule == self.entryName3:
                        self.logi.appendMsg("Pass - step 9-12")

                    testStatus = False
                    self.logi.appendMsg("FAIL - step 9-12: FAILED to verify search by rule")
                    return
                else:
                    self.logi.appendMsg("Pass - step 9-12")

            self.logi.appendMsg("INFO - step 13: Going to search by tag")
            self.basicFuncs.searchEntrySimpleSearch(self.Wd, self.error_rule)

            self.logi.appendMsg("INFO - step 13 - Verifying correct error message after trying to use an invalid search rule")
            popupMessageText = self.Wd.find_element_by_xpath(DOM.GLOBAL_ERROR_POPUP_MSG_TEXT).text
            if popupMessageText.find(self.error_msg) >= 0:
                self.logi.appendMsg("PASS - the pop-up message contains the expected text: '"+ popupMessageText+"'")
                self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_TAG_CLOSE).click()
                self.logi.appendMsg("Pass - step 13")
            else:
                self.logi.appendMsg("FAIL - step 13 - the pop-up message is not the expected one, the actual message was: '" + popupMessageText+"'")
                testStatus = False

            time.sleep(1)



        except Exception as e:
            print(e)
            testStatus = False
            pass

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus

        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            self.basicFuncs.deleteEntries(self.Wd, self.entryName3)
            self.logi.appendMsg("INFO - entries deleted")
        except:
            pass

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '32', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '32', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main(['test_32_entries_filters_global_search.py','-s'])
    #===========================================================================
