# ==================================================================================================================
#  @Author: Zeev Shulman 28/11/21
#
#  Replaces the following tests in Reach manual regression/post production:
#  3705 - Dashboard - Requests number behavior
#
# ===================================================================================================================

import os
import sys
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
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
        global testStatus

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
                self.reachProfile_name = "1111" #"delete"
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')
                self.Partner_ID = 6265
                self.KMCAccountName = "MAIN Template"
                self.reachProfile_name = "Marketing"

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
            self.logi = reporter2.Reporter2('test_3705_Reach_dashboard_requests')

        except Exception as Exp:
            print(Exp)

    def test_3705_Reach_dashboard_requests(self):
        global testStatus

        try:
            self.logi.initMsg('test_3705_Reach_dashboard_requests')
            self.logi.appendMsg("INFO - login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL -  FAILED to login to KMC")
                return
            time.sleep(1)
            self.logi.appendMsg("PASS - login to KMC")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL -  FAILED to login to KMC")
            return

        try:
            self.logi.appendMsg("INFO - going to navigate to SERVICES DASHBOARD")
            self.Wd.find_element_by_xpath(RDOM.SERVICES_DASHBOARD).click()
            time.sleep(1)
            self.logi.appendMsg("PASS - navigate to SERVICES DASHBOARD")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL -  FAILED to navigate to SERVICES DASHBOARD")
            return

        try:
            # "//iframe" is generic waiting for any iframe
            rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)
            self.Wd.switch_to.frame(0)
            time.sleep(5)

            self.logi.appendMsg("INFO - going to set Unit to REACH Profile Name")
            element = self.Wd.find_element_by_xpath(RDOM.SERVICES_UNIT)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys(self.reachProfile_name)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(3)

            self.logi.appendMsg("INFO - going to check for requests")
            requests_string = self.Wd.find_element_by_xpath(RDOM.SERVICES_REQUEST_NUM).text
            for word in requests_string.split():
                if word.isdigit():
                    requests_number = (int(word))
                    break

            if requests_number > 0:
                self.logi.appendMsg("PASS - Requests found")
                try:
                    cost = self.Wd.find_element_by_xpath(RDOM.SERVICES_FIRST_COST).text
                except:
                    # this is not a fail but a precaution
                    cost = self.Wd.find_element_by_xpath(RDOM.SERVICES_FIRST_COST_OLD).text
            else:
                self.logi.appendMsg("FAIL -  FAILED to find requests")
                testStatus = False
                return

            self.Wd.find_element_by_xpath(RDOM.SERVICES_DETAILS_BTN).click()
            time.sleep(1)

            num_requests_list = self.Wd.find_elements_by_xpath(RDOM.SERVICES_DETAILS_PARTIAL)
            sum = 0
            for n in range(3, len(num_requests_list)):
                sum += int(num_requests_list[n].text)
            if sum == int(self.Wd.find_element_by_xpath(RDOM.SERVICES_DETAILS_TOTAL).text):
                self.logi.appendMsg("PASS - request detailed categories == total, " + str(sum))
            else:
                self.logi.appendMsg("FAIL - request categories = " + str(sum) + " total = " + self.Wd.find_element_by_xpath(RDOM.SERVICES_DETAILS_TOTAL).text)
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL -  FAILED to navigate to SERVICES DASHBOARD")
            return

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
                self.practitest.post(Practi_TestSet_ID, '3705', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '3705', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)
    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_3705_Reach_dashboard_requests.py', '-s'])
    # ===========================================================================
