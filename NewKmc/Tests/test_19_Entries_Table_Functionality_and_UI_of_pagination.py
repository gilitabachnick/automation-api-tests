import os
import sys
import time

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import MySelenium
import KmcBasicFuncs

import reporter2

import Config
import Practitest
import autoitWebDriver
import KmcCheckUI



## Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False


testStatus = True
isProd = False

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
                inifile  = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.pwd = inifile.RetIniVal(section, 'passBulkUpload')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.pwd = inifile.RetIniVal(section, 'passBulkUploadTesting')

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userBulkUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_19_Entries_Table_Functionality_and_UI_of_pagination')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.UI = KmcCheckUI.CheckUI(self.Wd, self.logi)


            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_19_Entries_Table_Functionality_and_UI_of_pagination(self):

        global testStatus
        self.logi.initMsg('test_19_Entries_Table_Functionality_and_UI_of_pagination')

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

            self.logi.appendMsg("INFO - step 2: Going to verify pagination buttons")
            if self.UI.verify_pagination_buttons(number_of_pages=5) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to verify pagination buttons")
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to verify number of entry per page options")
            if self.UI.verify_show_rows_menu_items() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to verify number of entry per page options")
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to verify disabled page navigation buttons")
            if self.UI.verify_disabled_page_navigation_buttons() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to verify disabled page navigation buttons")
            else:
                self.logi.appendMsg("Pass - step 4")

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

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '19', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '19', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    pytest.main(['test_19_Entries_Table_Functionality_and_UI_of_pagination.py','-s'])
    #===========================================================================
 
        