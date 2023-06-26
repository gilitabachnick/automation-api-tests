import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import uploadFuncs
import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs
import Entrypage
import DOM

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
                self.old_name = 'Kaltura'
                self.old_last_name = 'K'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                self.old_name = 'KMC'
                self.old_last_name = 'Kaltura Automation'
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userName5')
            self.pwd = inifile.RetIniVal(section, 'pass5')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1143_my_user_settings_input_validation')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.new_name = 'Grizzly'
            self.new_last_name = 'Bouskila'
            self.input_error_list = [DOM.EDIT_USER_NAME_INPUT_ERROR_PASSWORD]


            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_1143_my_user_settings_input_validation(self):

        global testStatus
        self.logi.initMsg('test_1143_my_user_settings_input_validation')

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

            self.logi.appendMsg("INFO - step 2: Going to open my user settings menu")
            if self.settingsFuncs.input_my_user_settings_details() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to open my user settings menu")
                return
            else:
                self.logi.appendMsg("PASS - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to open my user settings menu")
            if self.settingsFuncs.verify_valid_user_info_input(input_error_list=self.input_error_list, num_of_errors=1) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to open my user settings menu")
                return
            else:
                self.logi.appendMsg("PASS - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to open my user settings menu")
            if self.settingsFuncs.input_my_user_settings_details(firstName=self.new_name, lastName=self.new_last_name, password=self.pwd, save_changes=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to open my user settings menu")
                return
            else:
                self.logi.appendMsg("PASS - step 4")

            time.sleep(1)

        except:
            testStatus = False
            pass

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus

        try:
            self.logi.appendMsg("INFO - Going to change my user first and last name back")
            self.settingsFuncs.input_my_user_settings_details(firstName=self.old_name, lastName=self.old_last_name,
                                                              password=self.pwd, save_changes=True)
            self.logi.appendMsg("PASS - First and last name changed")
        except:
            self.logi.appendMsg("FAIL - First and last name did not changed")
            pass

        time.sleep(5)

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1143', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1143', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    # pytest.main('test_1143_my_user_settings_input_validation.py -s')
