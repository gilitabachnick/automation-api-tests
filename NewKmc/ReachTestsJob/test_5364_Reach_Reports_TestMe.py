# ==================================================================================================================
#  @Author: Zeev Shulman 12/10/21
#  @description : Inspect Reach USAGE and BILLING report via testMe
#
#  Replaces the following tests in Reach manual regression/post production:
#  5364 Reports - As a customer I would like to have service usage and billing report
#   -   manual test was production only, in testing gets an unpopulated report
#
# ===================================================================================================================

import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import MySelenium
import KmcBasicFuncs
import reporter2
import Config
import Practitest
import RDOM
import ClienSession

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
                self.Partner_ID = "1788671"
                self.KMCAccountName = "Kaltura internal - Ella Lidich"
                self.AdminSecret     = inifile.RetIniVal(section, 'AdminSecretMR')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')
                self.Partner_ID = "6265"
                self.KMCAccountName = "MAIN Template"
                self.AdminSecret     = inifile.RetIniVal(section, 'AdminSecretReach')

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
            self.logi = reporter2.Reporter2('test_5364_Reach_Reports_TestMe')

            # ==================================================================
            # generate KS for Partner_ID
            # ==================================================================
            self.ServerURL = inifile.RetIniVal(section, "ServerURL")
            mySess = ClienSession.clientSession(self.Partner_ID, self.ServerURL, self.AdminSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
            myKS = mySess.GetKs()
            self.KS = str(myKS[2])

        except Exception as Exp:
            print(Exp)
            testStatus = False

    def test_5364_Reach_Reports_TestMe(self):

        global testStatus
        # Invoke login - admin console
        try:
            self.logi.initMsg('test_5364_Reach_Reports_TestMe')
            self.logi.appendMsg(
                "INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                        'zeev.shulman@kaltura.com', self.env)
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
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - Going to navigate to testMe")
            self.Wd.find_element_by_xpath(RDOM.TESTME_TAB).click()
            time.sleep(1)
            rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)

            self.Wd.switch_to.frame(0)
            self.logi.appendMsg("PASS - Reached testMe")

            self.logi.appendMsg("INFO - Going to fill KS and select: service, action")
            self.Wd.find_element_by_xpath(RDOM.TESTME_KS_BOX).click()
            self.Wd.find_element_by_xpath(RDOM.TESTME_KS).send_keys(self.KS)
            self.Wd.find_element_by_xpath(RDOM.TESTME_SERVICE_REPORT).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.TESTME_ACTION_GETTOTAL).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.TESTME_REPORT_TYPE_BOX).click()
            self.Wd.find_element_by_xpath(RDOM.TESTME_REPORT_TYPE_USAGE).click()
            self.logi.appendMsg("PASS - Report, getTotal,REACH_USAGE selected")

            self.logi.appendMsg("INFO - Going to edit filter for 90 days back and Send")
            edits_list = self.Wd.find_elements_by_xpath(RDOM.TESTME_EDIT)
            edits_list[0].click()
            time.sleep(1)
            # now = unixtime, 90 days = 7776000 seconds
            now = int(time.time())
            self.Wd.find_element_by_xpath(RDOM.TESTME_FILTER_FROMD_BOX).click()
            self.Wd.find_element_by_xpath(RDOM.TESTME_FILTER_FROMD).send_keys(str(now - 7776000)) # 1624706959
            self.Wd.find_element_by_xpath(RDOM.TESTME_FILTER_TOD_BOX).click()
            self.Wd.find_element_by_xpath(RDOM.TESTME_FILTER_TOD).send_keys(str(now)) # 1632666559
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.TESTME_SEND).click()
            self.logi.appendMsg("PASS - request sent")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to produce the Report")
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - Going to inspect the Report")
            time.sleep(3)
            self.Wd.switch_to.frame(0)
            data = self.Wd.find_element_by_xpath(RDOM.TESTME_REACH_USAGE_DATA).text
            self.logi.appendMsg("PASS - found unique_videos, price: " + data)
            time.sleep(1)
        except Exception as Exp:
            if isProd:
                print(Exp)
                self.logi.appendMsg("FAIL - FAILED no data for 'unique_videos, price' in the last 90 days")
                testStatus = False
            else:
                self.logi.appendMsg("PASS - No Reach Usage in QA env")

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
                self.practitest.post(Practi_TestSet_ID, '5364', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '5364', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)
    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_5364_Reach_Reports_TestMe.py', '-s'])
    # ===========================================================================
