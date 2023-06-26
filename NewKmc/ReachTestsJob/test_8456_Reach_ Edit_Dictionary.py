#================================================================================================================================
#  @Author: Zeev Shulman 20/9/21
#  @description : Reach - profiles tab - edit dictionary tab
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
                self.Partner_ID = 6265
                self.KMCAccountName = "MAIN Template"

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('1328')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            # test-boolean23 must exist in KMC at runtime or fail
            self.reach_profile_name_old = ' test-boolean23 '
            self.reach_profile_name_new = ' test-boolean new '
            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_1900_Reach_edit_settings_tab')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)


    def test_8456_Reach_Edit_Dictionary(self):
        global testStatus
        try:
            # Invoke and login
            self.logi.initMsg('test_8456_Reach_Edit_Dictionary')
            self.logi.appendMsg("INFO - Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - FAILED to login to KMC")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - going to navigate to reach settings tab")
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
            time.sleep(1)
            # ================================================================
            # Check is this the expected Partner ID - Than goto REACH TAB
            # ================================================================
            try:
                self.Wd.find_element_by_xpath(DOM.PARTNER_ID.replace('PID', str(self.Partner_ID)))
                time.sleep(3)
            except Exception as e:
                # Wrong account, change PID
                print(e)
                self.logi.appendMsg(
                    "INFO - wrong account, changing to: " + self.KMCAccountName + " " + str(self.Partner_ID))
                self.BasicFuncs.ChangeKMCAccount(self.Wd, self.Wdobj, self.logi, self.KMCAccountName)
                time.sleep(2)
                self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
                time.sleep(2)
            self.Wd.find_element_by_xpath(DOM.REACH_TAB).click()
            time.sleep(3)

            self.logi.appendMsg("INFO - Going to open reach profile")
            if self.settingsfuncs.select_reach_profile(self.reach_profile_name_old) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Failed to open reach profile")
                return
            else:
                self.logi.appendMsg("PASS - Opened reach profile")
            time.sleep(1)

            self.logi.appendMsg("INFO - Going to add English Dictionary and write words into it")
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_DICTIONARY).click()
            try:
                # If english dictionary exists move on
                self.Wd.find_element_by_xpath(RDOM.ENGLISH_LANGUAGE)
            except:
                # If english dictionary not found create one
                self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_ADD_DICTIONARY).click()
            time.sleep(1)
            # new_dictionary_counter will be used to verify new words were saved to the dictionary
            word_counters = self.Wd.find_elements_by_xpath(RDOM.DICTIONARY_WORD_COUNTER)
            new_dictionary_counter = word_counters[0].text

            # in input_fields:  0,2,4  etc. are Language fields - 1,3,5 are are Words fields
            input_fields = self.Wd.find_elements_by_xpath(RDOM.REACH_PROFILE_DICTIONARY_FIELDS)
            input_fields[1].send_keys("electroencephalogram\n")
            input_fields[1].send_keys("CHIPOTLE\n")
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()
            time.sleep(1)

            # Moving to another tab and back resets unsaved dictionaries for verification
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CREDIT).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_DICTIONARY).click()
            time.sleep(1)

            # word_counters[0] should be different after Save
            word_counters = self.Wd.find_elements_by_xpath(RDOM.DICTIONARY_WORD_COUNTER)
            if word_counters[0].text == new_dictionary_counter:
                testStatus = False
                self.logi.appendMsg("FAIL -  Failed to save new words to the Dictionary")
                return
            else:
                self.logi.appendMsg("PASS - New words added and Saved to the Dictionary")

            self.logi.appendMsg("INFO - Going to add Chinese dictionary")
            try:
                # If Chinese dictionary exists move on
                self.Wd.find_element_by_xpath(RDOM.CHINESE_LANGUAGE)
            except:
                # If Chinese dictionary not found add dictionary and change English to Chinese
                self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_ADD_DICTIONARY).click()
                self.Wd.find_element_by_xpath(RDOM.ENGLISH_LANGUAGE).click()
                self.Wd.find_element_by_xpath(RDOM.CHINESE_LANGUAGE).click()

            time.sleep(1)
            input_fields = self.Wd.find_elements_by_xpath(RDOM.REACH_PROFILE_DICTIONARY_FIELDS)
            input_fields[1].send_keys("歡迎來到 Kaltura\n")
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()
            time.sleep(1)
            # Moving to another tab and back resets unsaved dictionaries for verification
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CREDIT).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_DICTIONARY).click()
            time.sleep(1)
            self.logi.appendMsg("PASS - Added Chinese dictionary")

            self.logi.appendMsg("INFO - Going to Delete Dictionaries")
            # Delete dictionaries - bug: can't delete all - when fixed change to: len(delete_icons) > 0
            delete_icons = self.Wd.find_elements_by_xpath(RDOM.REACH_PROFILE_DELETE_DICTIONARY)
            while len(delete_icons) > 1:
                delete_icons[len(delete_icons)-1].click()
                time.sleep(1)
                # clicking() on the icon deletes the element hence find_elements in the loop
                delete_icons = self.Wd.find_elements_by_xpath(RDOM.REACH_PROFILE_DELETE_DICTIONARY)

            # ========================================================================
            # Can delete below section if/when delete dictionary is fixed
            # changing to spanish so as not to add the same words again and again
            # ========================================================================
            time.sleep(1)
            if len(self.Wd.find_elements_by_xpath(RDOM.CHINESE_LANGUAGE)) > 0:
                self.Wd.find_element_by_xpath(RDOM.CHINESE_LANGUAGE).click()
            elif len(self.Wd.find_elements_by_xpath(RDOM.ENGLISH_LANGUAGE)) > 0:
                self.Wd.find_element_by_xpath(RDOM.ENGLISH_LANGUAGE).click()
            try:
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.SPANISH_LANGUAGE).click()
                time.sleep(1)
            except Exception as Exp:
                # This is not a fail just a precaution
                print(Exp)

            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()
            time.sleep(1)
            # Moving to another tab and back resets unsaved dictionaries for verification
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_CREDIT).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.REACH_PROFILE_DICTIONARY).click()
            time.sleep(1)
            # Verify deletion
            delete_icons = self.Wd.find_elements_by_xpath(RDOM.REACH_PROFILE_DELETE_DICTIONARY)
            if len(delete_icons) == 1:
                self.logi.appendMsg("PASS - Dictionaries deleted ")
            time.sleep(1)

        except Exception as Exp:
            testStatus = False
            print(Exp)

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus
        try:
            self.Wd.quit()
        except Exception as Exp:
            print("Teardown quit() Exception")
            print(Exp)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '8456', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '8456', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_8456_Reach_Edit_Dictionary.py', '-s'])
    # ===========================================================================
