#================================================================================================================================
#  @Author: Zeev Shulman 18/8/21
#  @description : Tests search & Add/Delete catalog items in - Admin Console>Reach>Partner Catalog Items
#
#  Replaces the following tests in Reach manual regression/post production:
#  5296 - Add/Delete catalogs to Partner Catalog Items
#  5295 - Search Partner Catalog Items
#================================================================================================================================

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

testStatus = True

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
                self.user = inifile.RetIniVal(section, 'userElla')
                self.pwd = inifile.RetIniVal(section, 'passElla')
                self.Partner_ID = 1788671
                self.KMCAccountName = "Kaltura internal - Ella Lidich"
                self.Item_ID_Xpath = RDOM.REACH_CHECK_ITEM.replace("TEXTTOREPLACE", "6291")
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')
                self.Partner_ID = 6265
                self.KMCAccountName = "MAIN Template"
                self.Item_ID_Xpath = RDOM.REACH_CHECK_ITEM.replace("TEXTTOREPLACE", "228")

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('1328')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_5295_Reach_add_delete_catalogs')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)


    def test_5295_Reach_add_delete_catalogs(self):
        global testStatus
        try:
            # Invoke login - admin console
            self.logi.initMsg('test_5295_Reach_add_delete_catalogs')
            self.logi.appendMsg("INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                        'zeev.shulman@kaltura.com', self.env)
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.admin_url,self.user,self.pwd,ks)
            if(rc):
                self.logi.appendMsg("PASS - Admin Console login")
            else:
                self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                testStatus = False
                return
            self.Wd.maximize_window()
        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - Going to navigate to Reach>Partner Catalog Items")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_TAB).click()
            self.Wd.find_element_by_xpath(RDOM.REACH_PARTNER_CATALOG_ITEMS).click()
            self.logi.appendMsg("PASS - navigated to Reach>Partner Catalog Items")
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to navigate to Reach>Partner Catalog Items")
            return

        try:
            # setting search parameters
            self.logi.appendMsg("INFO - Going to search for a catalog item and check its box")
            self.Wd.find_element_by_xpath(RDOM.REACH_FILTER_BY_PID).send_keys(self.Partner_ID)
            self.Wd.find_element_by_xpath(RDOM.REACH_SERVICE_FEATURE_DD).send_keys("CAPTIONS")
            self.Wd.find_element_by_xpath(RDOM.REACH_SERVICE_TYPE_DD).send_keys("MACHINE")
            self.Wd.find_element_by_xpath(RDOM.REACH_TURN_AROUND_DD).send_keys("BEST_EFFORT")
            self.Wd.find_element_by_xpath(RDOM.REACH_SERVICE_SOURCE_LANG_DD).send_keys("English")
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()

            try:
                ### if item not found - posible result of old fail - try adding it in the Exception
                self.Wd.find_element_by_xpath(self.Item_ID_Xpath).click()
            except Exception as e:
                if "no such element" in str(e):
                    self.logi.appendMsg("INFO - item not found First Try - going to add the item")
                    self.Wd.find_element_by_xpath(RDOM.REACH_CATALOG_ITEM_CONFIG).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(self.Item_ID_Xpath).click()
                    self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(self.Item_ID_Xpath).click()

            self.logi.appendMsg("PASS - Item found its box checked")
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to find an item and check its box")
            return

        try:
            self.logi.appendMsg("INFO - Going to delete checked item")
            self.Wd.find_element_by_xpath(RDOM.REACH_BULK_DELETE).click()
            time.sleep(3)
            self.Wd.switch_to.alert.accept()
            time.sleep(3)
            self.Wd.switch_to.alert.accept()
            time.sleep(1)
            try:
                #Looking for a deleted item - exception is a Pass next line is a Fail
                self.Wd.find_element_by_xpath(self.Item_ID_Xpath)
                testStatus = False
                self.logi.appendMsg("FAIL - FAILED to delete checked item")
                return
            except:
                self.logi.appendMsg("PASS - Item deleted")

        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to delete checked item")
            return

        try:
            self.logi.appendMsg("INFO - Going to add back the deleted item")
            self.Wd.find_element_by_xpath(RDOM.REACH_CATALOG_ITEM_CONFIG).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(self.Item_ID_Xpath).click()
            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(self.Item_ID_Xpath)
            self.logi.appendMsg("PASS - item added and found")
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to to add back the deleted item")


    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '5295', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '5295', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_5295_Reach_add_delete_catalogs.py', '-s'])
    # ===========================================================================
