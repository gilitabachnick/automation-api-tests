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
import Entrypage
import settingsFuncs

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
            self.pwd = inifile.RetIniVal(section, 'pass5')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()

            self.logi = reporter2.Reporter2('test_1174_access_control_bulk_action')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entrypagefuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.accessControls = ["autotest basic", "autotest basic",
                                   "autotest domain", "autotest domain",
                                   "autotest country allow", "autotest country allow",
                                   "autotest country block", "autotest country block"]


        except:
            pass

    def test_1174_access_control_bulk_action(self):

        global testStatus

        try:
            self.logi.initMsg('test_1174_access_control_bulk_action')

            # Invoke and login
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - Step 2: Going to create 4 access controls")
            # adding access control
            # create 8 access controls: basic, domain, country allow, and country block
            j = 0
            for i in (self.accessControls):

                if i == "autotest basic":
                    rc = self.settingsfuncs.addAccessControlProfile(i, "basic description")
                elif i == "autotest domain":
                    rc = self.settingsfuncs.addAccessControlProfile(i, "domain description", "selected", "google.com")
                elif i == "autotest country allow":
                    rc = self.settingsfuncs.addAccessControlProfile(i, "country allow description",
                                                                   authorizedCountries="selected",
                                                                   theCountries="Australia")
                else:
                    rc = self.settingsfuncs.addAccessControlProfile(i, "country block description",
                                                                   authorizedCountries="blocked", theCountries="Israel")
                if not rc:
                    self.logi.appendMsg("FAIL - Step 2: Going to create 4 access controls")
                    testStatus = False
                    return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to select 2 profiles")
            self.entrypagefuncs.selectEntries("2,5")

            selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
            if selectedEntriesNum == 3:
                self.logi.appendMsg('PASS - step 3: the number of selected entries is 2 as expected')
            else:
                self.logi.appendMsg(
                    'FAIL -  step 3: the number of selected profiles should have been 2 and actually it is: ' + str(
                        selectedEntriesNum))
                testStatus = False

            self.entrypagefuncs.cancel_selected()

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to select 2 profiles")
            try:
                self.entrypagefuncs.selectEntries("2,4")
                time.sleep(1)
            except Exception as e:
                print(e)
                testStatus = False
                return

            selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
            if selectedEntriesNum == 2:
                self.logi.appendMsg(
                    'PASS - the number of selected entries is: ' + str(selectedEntriesNum) + ' as expected')
            else:
                self.logi.appendMsg('FAIL - step 4: the number of selected entries is: ' + str(
                    selectedEntriesNum) + ' and should have been 2')
                testStatus = False

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to delete access profiles")
            if self.entrypagefuncs.bulk_delete_selected(confirm_delete=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to delete access profiles")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to select 3 profiles")

            try:
                self.entrypagefuncs.selectEntries("2,5")
                time.sleep(1)
            except Exception as e:
                print(e)
                testStatus = False
                return

            selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
            if selectedEntriesNum == 3:
                self.logi.appendMsg(
                    'PASS - the number of selected entries is: ' + str(selectedEntriesNum) + ' as expected')
            else:
                self.logi.appendMsg('FAIL - step 6: the number of selected entries is: ' + str(
                    selectedEntriesNum) + ' and should have been 1')
                testStatus = False


            self.logi.appendMsg("INFO - step 7: Going to delete access profiles")
            if self.entrypagefuncs.bulk_delete_selected(confirm_delete=False) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to delete access profiles")
                return
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(3)

            self.entrypagefuncs.cancel_selected()

            try:
                self.entrypagefuncs.selectEntries("2,8")
                time.sleep(1)
            except Exception as e:
                print(e)
                testStatus = False
                return

            selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
            if selectedEntriesNum == 6:
                self.logi.appendMsg('PASS -  step 8: the number of selected entries is 6 as expected')
            else:
                self.logi.appendMsg(
                    'FAIL - step 8: the number of selected entries should have been 6 and actually it is: ' + str(
                        selectedEntriesNum))
                testStatus = False

            self.logi.appendMsg("INFO - step 9: Going to delete access profiles")
            if self.entrypagefuncs.bulk_delete_selected() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 9: FAILED to delete access profiles")
                return
            else:
                self.logi.appendMsg("Pass - step 9")


        except Exception as e:
            print(e)
            testStatus = False
            pass

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1174', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1174', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True
    #===============================================================================
    pytest.main(args=['test_1174_access_control_bulk_action.py','-s'])
    #===============================================================================

