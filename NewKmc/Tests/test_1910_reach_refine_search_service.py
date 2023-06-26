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
                self.user = inifile.RetIniVal(section, 'userElla')
                self.pwd = inifile.RetIniVal(section, 'passElla')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

            self.logi = reporter2.Reporter2('test_1910_reach_refine_search_service')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.human = ' Human '
            self.machine = ' Machine '
            self.active_filter_list = ['Human', 'Machine']

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_1910_reach_refine_search_service(self):

        global testStatus
        self.logi.initMsg('test_1911_reach_refine_filter_turn_around_time')

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

            self.logi.appendMsg("INFO - step 2: Going to navigate to reach settings tab")
            if self.settingsfuncs.open_reach_menu() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to navigate to reach settings tab")
                return
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(5)
            self.Wd.execute_script("window.scrollTo(0, 1080)")

            num_of_services_before = self.Wd.find_elements_by_xpath(DOM.PROFILE_COUNT)[1].text

            self.logi.appendMsg("INFO - step 3: Going to open refine search dropdown")
            # open refine filter and verify Custom metadata filters appear
            self.logi.appendMsg("INFO - going to open refine filter and verify Custom metadata filters appear")
            try:
                self.Wd.find_element_by_xpath(DOM.REFINE_BUTTON).click()
                self.settingsfuncs.open_refine_expand_menu()
                self.logi.appendMsg("Pass - step 3")
            except:
                self.logi.appendMsg("FAIL - step 3: FAILED to open refine search dropdown")
                self.logi.appendMsg("FAIL - could not find the Refine Filter button, can not continue the test")
                return False

            self.logi.appendMsg("INFO - step 4: Going to select human")
            if self.settingsfuncs.select_refine_filter_option(self.human) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to select human")
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            num_of_services_after = self.Wd.find_elements_by_xpath(DOM.PROFILE_COUNT)[1].text

            if num_of_services_before != num_of_services_after:
                self.logi.appendMsg("Pass - the services number changed")
            else:
                self.logi.appendMsg("FAIL = the services number did not change")

            self.logi.appendMsg("INFO - step 5: Going to verify active filter")
            if self.basicFuncs.verify_entrires_active_filter_selected(self.Wd, self.logi, self.active_filter_list) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to verify active filter")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to select machine")
            if self.settingsfuncs.select_refine_filter_option(self.machine) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to select machine")
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(1)

            num_of_services_after = self.Wd.find_elements_by_xpath(DOM.PROFILE_COUNT)[1].text

            if num_of_services_before == num_of_services_after:
                self.logi.appendMsg("Pass - the services number changed")
            else:
                self.logi.appendMsg("FAIL = the services number did not change")

        except:
            testStatus = False
            pass

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus

        # ADD TRY AND EXCEPT IF NEEDED

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1910', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1910', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    #pytest.main(args=['test_1910_reach_refine_search_service.py','-s'])
    #===========================================================================