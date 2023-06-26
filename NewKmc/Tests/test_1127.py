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
import Entrypage
import AdministrationFuncs

import DOM
import Config
import Practitest

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
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
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userName5')
            self.userB = inifile.RetIniVal(section, 'userName4')
            self.pwd = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('TEST1127')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.adminFuncs = AdministrationFuncs.adminFuncs(self.Wd, self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd)
            self.userEmail = 'First.Last1127@kaltura.com'
            self.invalidUserEmail = 'First.Last'
            self.firstName = 'First1127'
            self.lastName = 'Last1127'
            self.userID = 'userID_1127'
            self.input_error_list = [DOM.USER_INPUT_ERROR_EMAIL, DOM.USER_INPUT_ERROR_FIRST_NAME, DOM.USER_INPUT_ERROR_LAST_NAME]


        except:
            pass

    def test_1127(self):

        global testStatus
        self.logi.initMsg('Test 1127: Administration > Personal details validation ')

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

            self.logi.appendMsg("INFO - step 2: Going to check required input field")
            if self.adminFuncs.inputUserDetails() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to check required input field")
                return
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to verify 3 expected input errors")
            num_of_expected_errors = self.adminFuncs.verify_valid_user_info_input(self.input_error_list, num_of_errors=3)

            if num_of_expected_errors == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to verify 3 expected input errors")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to check required input field")
            if self.adminFuncs.inputUserDetails(self.userEmail, self.firstName, self.lastName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to check required input field")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to verify zero expected input errors")
            num_of_expected_errors = self.adminFuncs.verify_valid_user_info_input(self.input_error_list, num_of_errors=0)

            if num_of_expected_errors == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to verify zero expected input errors")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to check required input field")
            if self.adminFuncs.inputUserDetails(self.invalidUserEmail, self.firstName, self.lastName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to check required input field")
                return
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to verify 1 expected input errors")
            num_of_expected_errors = self.adminFuncs.verify_valid_user_info_input(self.input_error_list, num_of_errors=1)

            if num_of_expected_errors == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to verify 1 expected input errors")
                return
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(1)

        except Exception as e:
            print(e)
            testStatus = False
            pass

    def teardown_class(self):

        global testStatus

        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1127', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1127', '0')
            assert True

    #===========================================================================
    # pytest.main('test_1127.py -s')
    #===========================================================================

