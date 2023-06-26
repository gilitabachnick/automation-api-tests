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
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userName5')
            self.pwd = inifile.RetIniVal(section, 'pass5')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1147_my_user_settings_edit_password')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.new_pass = 'Passme!1!2'
            self.input_error_list = [DOM.CHANGE_USER_PASSWORD_ERROR_CURRENT, DOM.CHANGE_USER_PASSWORD_ERROR_CURRENT, DOM.CHANGE_USER_PASSWORD_ERROR_CURRENT]

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_1147_my_user_settings_edit_password(self):

        global testStatus
        self.logi.initMsg('test_1147_my_user_settings_edit_password')

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

            self.logi.appendMsg("INFO - step 2: Going to click edit password")
            if self.settingsFuncs.input_my_user_password_details() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to click edit password")
                return
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to verify invalid input")
            if self.settingsFuncs.verify_valid_user_info_input(input_error_list=self.input_error_list, num_of_errors=3) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to verify invalid input")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to edit password")
            if self.settingsFuncs.input_my_user_password_details(current_password=self.pwd, new_password=self.new_pass, re_type_new_password=self.new_pass, save_changes=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to click edit password")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to edit password")
            if self.settingsFuncs.input_my_user_password_details(current_password=self.new_pass, new_password=self.pwd,
                                                                 re_type_new_password=self.pwd,
                                                                 save_changes=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to click edit password")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

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
            self.settingsFuncs.input_my_user_password_details(current_password=self.new_pass, new_password=self.pwd, re_type_new_password=self.pwd, save_changes=True)
        except:
            pass

            time.sleep(5)

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1147', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1147', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    # pytest.main(['test_1147_my_user_settings_edit_password.py -s'])
