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
            self.reach_profile_name = ' test-boolean23 '

            self.logi = reporter2.Reporter2('test_1903_reach_profiles_input_validation')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_1903_reach_profiles_input_validation(self):

        global testStatus
        self.logi.initMsg('test_1903_reach_profiles_input_validation')

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

            self.logi.appendMsg("INFO - step 3: Going to open reach profile")
            if self.settingsfuncs.select_reach_profile(self.reach_profile_name) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to open reach profile")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            self.logi.appendMsg("INFO - step 4: Going to going to change reach profile name")
            if self.settingsfuncs.clear_reach_profile_name_for_validation(num_of_errors=1) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to going to change reach profile name")
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to clear max characters_for_validation")
            if self.settingsfuncs.clear_reach_max_characters_for_validation(num_of_errors=2) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to clear max characters_for_validation")
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to exit without saving")
            if self.settingsfuncs.exit_without_saving(exitWithoutSaving=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to exit without saving")
                return
            else:
                self.logi.appendMsg("Pass - step 6")

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

        # ADD TRY AND EXCEPT IF NEEDED

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1903', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1903', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    #pytest.main(args=['test_1903_reach_profiles_input_validation.py','-s'])
    #===========================================================================
