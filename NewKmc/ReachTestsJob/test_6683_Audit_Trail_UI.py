#================================================================================================================================
#  @Author: Zeev Shulman 19/8/21
#  @description : Tests search & Add/Delete catalog items in - Admin Console>Reach>Partner Catalog Items
#
#  Replaces the following tests in Reach manual regression/post production:
#  6683 - Audit trail UI
#  clone profile, edit profile, audit trail, remove profile
#================================================================================================================================

import os
import sys
import time
import random
from selenium.webdriver.common.keys import Keys

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


#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    Practi_TestSet_ID = '14368'
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
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_6683_Audit_Trail_UI')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)


    def test_6683_Audit_Trail_UI(self):
        global testStatus
        # Clone_ID needs to be global for teardown delete
        global Clone_ID
        try:
            # Invoke login - admin console
            self.logi.initMsg('test_6683_Audit_Trail_UI')
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
            return

        try:
            self.logi.appendMsg("INFO - Going to navigate to Reach>Partner Catalog Items")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_TAB).click()
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_PROFILES).click()
            self.logi.appendMsg("PASS - navigated to Reach>Partner Catalog Items")
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to navigate to Reach>Partner Catalog Items")
            return

        try:
            self.logi.appendMsg("INFO - Going to clone an existing profile")
            self.Wd.find_element_by_xpath(RDOM.REACH_FILTER_BY_PID).send_keys(self.Partner_ID)
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()

            Profile_ID = self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_ID).text
            Profile_Name = self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_NAME).text
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_ID_INPUT).send_keys(Profile_ID)
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.REACH_CLONE_PROFILE_BTN).click()
            time.sleep(3)

            self.Wd.switch_to.alert.accept()
            time.sleep(3)
            self.Wd.switch_to.alert.accept()
            time.sleep(3)

            Clone_ID = self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_ID).text
            Clone_Name = self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_NAME).text

            # A clone name should include the original name and have a new number
            if (Profile_Name in Clone_Name) and (Profile_ID != Clone_ID):
                self.logi.appendMsg("PASS - PID " + str(self.Partner_ID) + " profile " + Clone_ID +" clone of "+ Profile_ID+ " was created")
            else:
                self.logi.appendMsg("FAIL - Failed to clone a profile")
                return
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - Failed to clone a profile")
            return

        try:
            self.logi.appendMsg("INFO - Going to configure profile")
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_DD).send_keys("Configure")
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CONFIG_CREDIT).send_keys(Keys.CONTROL, 'a')
            credit = str(random.randrange(1, 999))
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CONFIG_CREDIT).send_keys(credit)
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CONFIG_TO_DATE).send_keys(Keys.CONTROL, 'a')
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CONFIG_TO_DATE).send_keys("2040.01.01")
            time.sleep(2)
            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()
            self.logi.appendMsg("PASS - configured profile")
            time.sleep(3)

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - Failed to configure profile")
            return

        try:
            self.logi.appendMsg("INFO - Going to inspect the cloned profile Audit Trail")
            self.Wd.find_element_by_xpath(RDOM.ADMINCONSOLE_CONFIGURATION_TAB).click()
            self.Wd.find_element_by_xpath(RDOM.ADMINCONSOLE_AUDIT_TAB).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.ADMINCONSOLE_AUDIT_TYPE).send_keys("REACH_PROFILE")
            self.Wd.find_element_by_xpath(RDOM.ADMINCONSOLE_AUDIT_OBJECT_ID).send_keys(Clone_ID)
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
            Ditails_Text = self.Wd.find_element_by_xpath(RDOM.AUDIT_ROW1_DETAILS).text
            time.sleep(3)
            #=================================================================================
            # Verifying the changes to the profile are Auditable:
            # - Creation of a new profile already verified
            # - Details should retain changes to Credit and To Date (2040.01.01 in Unix time)
            #====================================================================================
            if ('"toDate":2209075199' in Ditails_Text) and ('"credit":' + credit in Ditails_Text):
                self.logi.appendMsg("PASS - Audit Trail of the changes to Reach Profile found")

            else:
                self.logi.appendMsg("FAIL - Audit Trail of the changes not found")

            time.sleep(1)
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - Failed to audit the trail of changes to the cloned profile")
            return


    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus
        try:
            self.logi.appendMsg("TEARDOWN - Going to Delete cloned profile")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_TAB).click()
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_PROFILES).click()
            self.Wd.find_element_by_xpath(RDOM.REACH_FILTER_BY_PID).send_keys(self.Partner_ID)
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
            if Clone_ID == self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_ID).text:
                self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_TABLE_1_DD).send_keys("Remove")
                time.sleep(3)
                self.Wd.switch_to.alert.accept()
                time.sleep(3)
                self.Wd.switch_to.alert.accept()
                time.sleep(1)
                self.logi.appendMsg("TEARDOWN - PASS - Deleted cloned profile")
            else:
                self.logi.appendMsg("TEARDOWN - FAIL - cloned profile NOT deleted")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("TEARDOWN - FAIL - cloned profile NOT deleted")
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '6683', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '6683', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_6683_Audit_Trail_UI.py', '-s'])
    # ===========================================================================
