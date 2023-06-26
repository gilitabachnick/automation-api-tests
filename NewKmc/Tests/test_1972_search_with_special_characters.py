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
from selenium.webdriver.common.keys import Keys

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

            self.logi = reporter2.Reporter2('test_1972_search_with_special_characters')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entry_underscore = '1000_'
            self.entry_unit = 'unit_'
            self.entry_virtual = 'virtual 19'
            self.entry_virtual = 'SPED08316!'


            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_1972_search_with_special_characters(self):

        global testStatus
        self.logi.initMsg('test_1972_search_with_special_characters')

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
                self.basicFuncs.deleteEntries(self.Wd, "test 1000_;unit_;virtual 19;SPED08316!", entriesSeparator=";")
                self.logi.appendMsg("INFO - entries deleted")
            except:
                pass

            self.logi.appendMsg("INFO - step 2: Going to bulk upload entries")

            self.logi.appendMsg("INFO - going to do bulk upload")
            self.logi.appendMsg("INFO - going to upload csv file - test939.csv")
            the_time = str(datetime.datetime.time(datetime.datetime.now()))[:5]

            self.uploadfuncs.bulkUpload("entry", 'test_1972.csv')

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

            self.logi.appendMsg("INFO - step 3 : Going to search for entry with _ ")
            try:
                self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
                self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(self.entry_underscore + Keys.RETURN)

                time.sleep(1)

                num_of_entries = self.Wd.find_element_by_xpath(
                    "//span[@class='kSelectedEntriesNum ng-star-inserted']").text

                if num_of_entries > 0:
                    self.logi.appendMsg("Pass - step 3 ")
            except:
                self.logi.appendMsg("FAIL - step 3 : FAILED to search for entry with _ ")
                testStatus = False


            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to search for entry unit_ ")
            try:
                self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
                self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(self.entry_unit + Keys.RETURN)

                time.sleep(1)

                num_of_entries = self.Wd.find_element_by_xpath(
                    "//span[@class='kSelectedEntriesNum ng-star-inserted']").text

                if num_of_entries > 0:
                    self.logi.appendMsg("Pass - step 4")
            except:
                self.logi.appendMsg("FAIL - step 4: FAILED to search for entry unit_ ")
                testStatus = False

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to search for entry with virtual 19")
            try:
                self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
                self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(self.entry_virtual + Keys.RETURN)

                time.sleep(1)

                num_of_entries = self.Wd.find_element_by_xpath(
                    "//span[@class='kSelectedEntriesNum ng-star-inserted']").text

                if num_of_entries > 0:
                    self.logi.appendMsg("Pass - step 4")
            except:
                self.logi.appendMsg("FAIL - step 4: FAILED to search for entry virtual 19")
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
            self.basicFuncs.deleteEntries(self.Wd,"test 1000_;unit_;virtual 19;SPED08316!",entriesSeparator=";")
            self.logi.appendMsg("INFO - entries deleted")
        except:
            pass

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1972', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1972', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_1972_search_with_special_characters.py -s')
    #===========================================================================
