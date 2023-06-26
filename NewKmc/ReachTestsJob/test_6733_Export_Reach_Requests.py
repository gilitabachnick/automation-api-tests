#================================================================================================================================
#  @Author: Zeev Shulman 5/9/21
#  @description :
#
#  Replaces the following tests in Reach manual regression/post production:
#  6733 - Export "Reach Requests" in admin console
#
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

#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
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
            # ===================================================================================
            # CSVpth = the folder CSV will be downloaded to and uploaded from
            # Its the Chrome default_directory setting - set in mySelenium
            #   using RetWebDriverLocalOrRemote("chrome", SaveToC=True)
            # ====================================================================================
            CSVpth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))

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
                self.Partner_ID = 6611
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

            self.CSVpthFull = os.path.join(CSVpth, 'export.csv')

            self.logi = reporter2.Reporter2('test_6733_Export_Reach_Requests')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)

    def test_6733_Export_Reach_Requests(self):

        global testStatus
        # Invoke login - admin console
        try:

            self.logi.initMsg('test_6733_Export_Reach_Requests')
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
            self.logi.appendMsg("INFO - Going to navigate to Reach>Reach Requests")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_TAB).click()
            self.Wd.find_element_by_xpath(RDOM.REACH_REQUESTS_TAB).click()
            self.logi.appendMsg("PASS - navigated to Reach>Reach Requests")
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to navigate to Reach>Reach Requests")
            return

        # ===============================================================
        # We are at the right place, now: Find, export, load, validate
        # ===============================================================
        try:
            self.logi.appendMsg("INFO - Going to filter the requests data")
            self.Wd.find_element_by_xpath(RDOM.REACH_REQUESTS_FILTER).send_keys("P")

            self.Wd.find_element_by_xpath(RDOM.REACH_FILTER_BY_PID).send_keys(self.Partner_ID)
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
            time.sleep(1)

            # ===========================================================================
            # create validation data from the requests table
            # validation_data_str = the first entry's columns converted into a string
            # ===========================================================================
            validation_data_str = ""
            for i in range(1, 11):
                xp = RDOM.REACH_REQUEST_ROW_1_FIELDS.replace("TEXTTOREPLACE", str(i))
                box = self.Wd.find_element_by_xpath(xp).text
                validation_data_str = validation_data_str + box + ","
            self.logi.appendMsg("PASS - requests data found")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - couldn't find the requests data for " + str(self.Partner_ID))
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - Going to Export CSV")
            # ===========================================================================
            # if old export.csv exists remove it before export
            # this should only happen if teardown failed in the past
            # ===========================================================================
            if os.path.exists(self.CSVpthFull):
                os.remove(self.CSVpthFull)
                self.logi.appendMsg("INFO - old 'export.csv' deleted")
                time.sleep(1)

            # PROCESSING filter is useful in Production - empty in testing
            if isProd:
                self.Wd.find_element_by_xpath(RDOM.REACH_STATUS_FILTER).send_keys("PROCESSING")
                self.Wd.find_element_by_xpath(RDOM.ENTRY_ID_SEARCH).click()
                time.sleep(1)

            self.Wd.find_element_by_xpath(RDOM.REACH_EXPORT_CSV).click()
            self.Wd.find_element_by_xpath(RDOM.REACH_EXPORT_LINK).click()
            time.sleep(5)
            self.logi.appendMsg("PASS - CSV Exported")

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to Export CSV file")
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - Going to open Exported CSV")
            CSVfile = open(self.CSVpthFull, mode='r')
            CSVdata = CSVfile.read()
            time.sleep(1)
            CSVfile.close()
            self.logi.appendMsg("PASS - CSV Opened")

            self.logi.appendMsg("INFO - Going to Validate Exported data")
            # If validation_data_str extracted form admin console is part of the CSVdata its validated
            if CSVdata.find(validation_data_str):
                self.logi.appendMsg("PASS - Exported data Validated")
            else:
                self.logi.appendMsg("FAIL - FAILED to Validate Exported data")
                testStatus = False

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to Validate Exported data")
            testStatus = False

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus
        self.logi.appendMsg("TEARDOWN - Going to quit")
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)

        try:
            self.logi.appendMsg("TEARDOWN - Going to Delete 'export.csv'")
            os.remove(self.CSVpthFull)
            time.sleep(1)
            if os.path.exists(self.CSVpthFull):
                testStatus = False
                self.logi.appendMsg("TEARDOWN - FAILED to to Delete 'export.csv'")
            else:
                self.logi.appendMsg("TEARDOWN - PASS, 'export.csv' Deleted")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("TEARDOWN - FAILED to to Delete 'export.csv'")

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '6733', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '6733', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_6733_Export_Reach_Requests.py', '-s'])
    # ===========================================================================
