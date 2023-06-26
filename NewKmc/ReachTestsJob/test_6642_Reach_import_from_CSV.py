# ===============================================================================================================
#  @Author: Zeev Shulman 05/12/21
#
#  @description:Admin>Reach>catalog Items
#       choose file csv1 import, copy num, get result find already exist -conf danish machine resubmision
#       check human/machine + resubmision import csv2 change resubmision + price
#
#  Replaces the following tests in Reach manual regression/post production:
#      6642 - Import catalog items from csv - import button on Admin Console
#      7417 - Add/Update/Delete allow_resubmission from a catalog items
#
# ===============================================================================================================

import os
import sys
import time
import subprocess
# ========================================================================
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
# ========================================================================

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import DOM
import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs
import Config
import Practitest
import autoitWebDriver
import RDOM

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '1328'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()
    if str(isProd) == 'true':
        isProd = True
    else:
        isProd = False

if isProd:
    isProd = False
    print("FAIL - This is a QA only test, DOESN'T RUN ON PROD")
testStatus = True

class TestClass:
    # ===========================================================================
    # SETUP
    # ===========================================================================
    def setup_class(self):
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.user = inifile.RetIniVal(section, 'userElla')
                self.pwd = inifile.RetIniVal(section, 'passElla')
                self.Partner_ID = 1788671
                self.KMCAccountName = "Kaltura internal - Ella Lidich"

            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')
                self.Partner_ID = 6265
                self.KMCAccountName = "MAIN Template"

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('1328')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome", SaveToC=True)

            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_6642_Reach_import_from_CSV')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)

    def test_6642_Reach_import_from_CSV(self):
        global testStatus
        # Invoke login - admin console
        try:
            self.logi.initMsg('test_6642_Reach_import_from_CSV')
            self.logi.appendMsg(
                "INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass, self.user,
                                                        self.env)
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd, self.Wdobj, self.logi, self.admin_url, self.user, self.pwd,
                                                    ks)
            if (rc):
                self.logi.appendMsg("PASS - Admin Console login")
            else:
                self.logi.appendMsg(
                    "FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                testStatus = False
                return
            self.Wd.maximize_window()
        except Exception as Exp:
            print(Exp)
            return

        try:
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_TAB).click()
            time.sleep(3)
            rc = self.import_csv("test_1932_1.csv")
            if not rc:
                testStatus = False
                return
            self.logi.appendMsg("INFO - Find already exists err in the log")
            time.sleep(10)
            self.Wd.find_element_by_xpath(RDOM.REACH_IMPORT_RESULT).click()
            time.sleep(1)
            import_log = self.Wd.find_element_by_xpath(RDOM.REACH_IMPORT_LOG).text
            if "already exists" in import_log:
                self.logi.appendMsg("PASS - already exists found")
            else:
                self.logi.appendMsg("FAIL - already exists NOT found")
                testStatus = False
                return
            self.Wd.find_element_by_xpath(RDOM.REACH_CLOSE).click()
            time.sleep(3)
            self.logi.appendMsg("INFO - Filtered: Danish, CAPTIONS, BEST_EFFORT")
            self.Wd.find_element_by_xpath(RDOM.REACH_SERVICE_FEATURE_DD).send_keys("CAPTIONS")
            self.Wd.find_element_by_xpath(RDOM.REACH_TURN_AROUND_DD).send_keys("BEST_EFFORT")
            self.Wd.find_element_by_xpath(RDOM.REACH_SERVICE_SOURCE_LANG_DD).send_keys("Danish")
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
            time.sleep(3)
            self.logi.appendMsg("PASS - Filtered: Danish, CAPTIONS, BEST_EFFORT")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - filter Danish, CAPTIONS, BEST_EFFORT")
            return

        try:
            self.logi.appendMsg("INFO - Configure Item 326")
            rows = self.Wd.find_elements_by_xpath(RDOM.REACH_ITEMS_TABLE)
            for i, e in enumerate(rows, start=1):
                if "326" in e.text:
                    break
            time.sleep(1)
            configure_dd = RDOM.REACH_ITEM_ID.replace('tr[*]', 'tr[' + str(i) + ']')
            self.Wd.find_element_by_xpath(configure_dd).send_keys("Configure")
            time.sleep(1)

            self.Wd.find_element_by_xpath(RDOM.REACH_ITEM_CONFIG_RESUBMISION).send_keys("TRUE")
            self.Wd.find_element_by_xpath(DOM.SAVE_BTN).click()
            only_machine_xpath = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE",
                                                                   "Only machine service type is allowed for resubmission")
            if "Only machine" in self.Wd.find_element_by_xpath(only_machine_xpath).text:
                self.logi.appendMsg("PASS - Human resubmission blocked as expected")
            time.sleep(1)
            self.logi.appendMsg("INFO - set service type = MACHINE")
            self.Wd.find_element_by_xpath(RDOM.REACH_CLOSE).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(configure_dd).send_keys("Configure")
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.REACH_ITEM_CONFIG_TYPE).send_keys("MACHINE")
            self.Wd.find_element_by_xpath(DOM.SAVE_BTN).click()
            self.logi.appendMsg("PASS - set service type = MACHINE")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - Configure Item 326")
            return

        try:
            time.sleep(3)
            rc = self.import_csv("test_1932_2.csv")
            if not rc:
                testStatus = False
                return
            time.sleep(10)
            self.Wd.find_element_by_xpath(configure_dd).send_keys("Configure")
            time.sleep(3)
            self.logi.appendMsg("INFO - Validate price and resubmission changes")
            valid = False
            if "TRUE" in self.Wd.find_element_by_xpath(RDOM.REACH_ITEM_CONFIG_RESUBMISION).text:
                valid = True
            if self.Wd.find_element_by_xpath(RDOM.ITEM_UNIT_PRICE) and valid:
                self.logi.appendMsg("PASS - Price, Resubmission, change Validated")
            else:
                self.logi.appendMsg("FAIL - failed to Validate Price, Resubmission changes")
                testStatus = False
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - failed to Validate Price, Resubmission changes")

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus
        print("---------- Teardown ---------")
        try:
            self.Wd.quit()
        except Exception as Exp:
            print("Teardown quit() Exception")
            print(Exp)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '6642', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '6642', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    # import_csv sequence used several times in the test
    # ===========================================================================
    def import_csv(self, file_name):
        global testStatus
        try:
            self.logi.appendMsg("INFO - Reach>Catalog Items, Import " + file_name)
            element = self.Wd.find_element_by_xpath(RDOM.REACH_IMPORT_CSV)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(3)
            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                pth2 = pth + r'\test_1932_1.csv'
                self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe',
                                        pth2.replace("test_1932_1.csv", file_name))
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                subprocess.call([pth2 + "\\openFile.exe", pth + "\\" + file_name])
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.REACH_IMPORT_BTN).click()
            time.sleep(10)
            import_str = self.Wd.find_element_by_xpath(RDOM.IMP_NUM).text
            self.Wd.find_element_by_xpath(RDOM.REACH_CLOSE).click()
            self.logi.appendMsg("PASS - Imported " + file_name)
            time.sleep(1)
            # import_str is in the Admin form. It can be used: ..REACH_IMPORT_RESULT).click() - or not
            self.Wd.find_element_by_xpath(RDOM.REACH_IMPORT_INPUT).send_keys(import_str)
            return True
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to Import " + file_name)
            return False

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_6642_Reach_import_from_CSV', '-s'])
    # ===========================================================================



