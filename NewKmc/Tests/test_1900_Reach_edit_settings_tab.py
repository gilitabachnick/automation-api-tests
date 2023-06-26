#================================================================================================================================
#  @Author: Erez Bouskila
#  updated: Zeev Shulman 24/6/21
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

#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '2087'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
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
                self.Partner_ID = inifile.RetIniVal(section, 'partnerElla')
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
            self.practitest = Practitest.practitest('4586')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            # test-boolean23 must exist in KMC at runtime or fail step3
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


    def test_1900_Reach_edit_settings_tab(self):

        global testStatus
        self.logi.initMsg('test_1900_Reach_edit_settings_tab')

        try:
            # Invoke and login
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 2: Going to navigate to reach settings tab")
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
            time.sleep(1)
            #================================================================
            # Check is this the expected Partner ID - Than goto REACH TAB
            #================================================================
            try:
                self.Wd.find_element_by_xpath(DOM.PARTNER_ID.replace('PID', str(self.Partner_ID)))
                time.sleep(3)
            except Exception as e:
                # Wrong account, change PID
                print(e)
                self.logi.appendMsg("INFO - Wrong account, changing to: " + self.KMCAccountName + " " + str(self.Partner_ID))
                self.BasicFuncs.ChangeKMCAccount(self.Wd, self.Wdobj, self.logi, self.KMCAccountName)
                self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
                time.sleep(2)
            self.Wd.find_element_by_xpath(DOM.REACH_TAB).click()
            time.sleep(3)

            self.logi.appendMsg("INFO - step 3: Going to open reach profile")
            if self.settingsfuncs.select_reach_profile(self.reach_profile_name_old) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to open reach profile")
                return
            else:
                self.logi.appendMsg("Pass - step 3")
            
            time.sleep(5)
            self.logi.appendMsg("INFO - step 4: Going to change reach profile name")
            if self.settingsfuncs.edit_reach_profile_name(self.reach_profile_name_new) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to going to change reach profile name")
            else:
                self.logi.appendMsg("Pass - step 4")


            self.logi.appendMsg("INFO - step 5: Going to change slider option")
            if self.settingsfuncs.edit_slide_value() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to change slider option")
            else:
                self.logi.appendMsg("Pass - step 5")


            self.logi.appendMsg("INFO - step 6: Going to change Content Deletion Policy value")
            if self.settingsfuncs.edit_drop_down_metadata_item(drop_down_item=0, select_field_item=1) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to change Content Deletion Policy value")
            else:
                self.logi.appendMsg("Pass - step 6")

            self.logi.appendMsg("INFO - step 7: Going to change Task Processing Region value")
            if self.settingsfuncs.edit_drop_down_metadata_item(drop_down_item=1, select_field_item=1) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to change Task Processing Region value")
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(1)

            self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()
            time.sleep(1)
            try:
                self.logi.appendMsg("INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
               
                if "nv" not in self.url:  # Bypass NVD console user/pass login
                    ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,  'zeev.shulman@kaltura.com', self.env)
                else:
                    ks = False
                print(ks)
                print(self.admin_url)
                rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.admin_url,self.user,self.pwd,ks)
                if(rc):
                    self.logi.appendMsg("PASS - Admin Console login.")
                else:
                    self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                    testStatus = False
                    return
            except Exception as Exp:
                print(Exp)

            self.Wd.maximize_window()

            self.logi.appendMsg("INFO - step 8: Going to navigate to reach profiles and verify changes")
            try:
                self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_TAB).click()
                self.Wd.find_element_by_xpath(DOM.MACONSOLE_REACH_PROFILES).click()
                self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_FILTER_TEXT).send_keys(self.Partner_ID)
                self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
                self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
                # Expand items list from 10 to 100
                self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_PAGE_SIZE).click()
                self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_PAGE_100).click()
                # find the row in reach profiles table - old version was going for specific row [4],[10]
                try:
                    rows = self.Wd.find_elements_by_xpath(DOM.ADMINCONSOLE_REACH_PROFILES_TABLE)
                    i = -1
                    profile_name = self.reach_profile_name_new[1:-1]
                    for e in rows:
                        i = i + 1
                        if e.text == profile_name:
                            break
                    time.sleep(1)
                    configurate = DOM.ADMINCONSOLE_REACH_PROFILE_CONFIG.replace('tr[*]', 'tr[' + str(i + 1) + ']')
                except Exception as Exp:
                    print(Exp)

                self.Wd.find_element_by_xpath(configurate).click()

                name_textfield = self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_REACH_PROFILE_NEW)
                content_deletion_policy = self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_REACH_PROFILE_DELITION)
                enable_machine_moderation = self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_REACH_PROFILE_MODERATION)
                vendor_task_processing_region = self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_REACH_PROFILE_REGION)
                time.sleep(1)

                if name_textfield.get_attribute("value") == 'test-boolean new':
                    self.logi.appendMsg('Pass - Name changed')

                if content_deletion_policy.get_attribute("selected"):
                    self.logi.appendMsg('Pass - contentDeletionPolicy changed')

                if enable_machine_moderation.get_attribute("selected"):
                    self.logi.appendMsg('Pass - Moderation on Machine Requests changed')

                if vendor_task_processing_region.get_attribute("selected"):
                    self.logi.appendMsg('Pass - Task Processing Region changed')

                self.logi.appendMsg("Pass - step 8")
            except Exception as e:
                print(e)
                testStatus = False
                self.logi.appendMsg("FAIL - step 8: FAILED to navigate to reach profiles")

        except Exception as e:
            print(e)
            testStatus = False

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):

        global testStatus
        try:
            # Invoke and login
            self.logi.appendMsg("INFO - TEARDOWN 1: Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - TEARDOWN 1: FAILED to login to KMC")
            else:
                time.sleep(1)

                self.logi.appendMsg("INFO - TEARDOWN 2: Going to navigate to reach settings tab")
                if self.settingsfuncs.open_reach_menu() == False:
                    testStatus = False
                    self.logi.appendMsg("FAIL - TEARDOWN 2: FAILED to navigate to reach settings tab")
                else:
                    self.logi.appendMsg("Pass - TEARDOWN 2")

                    time.sleep(5)

                    self.logi.appendMsg("INFO - TEARDOWN 3: Going to open reach profile")
                    if self.settingsfuncs.select_reach_profile(self.reach_profile_name_new) == False:
                        testStatus = False
                        self.logi.appendMsg("FAIL - TEARDOWN 3: FAILED to open reach profile")

                    else:
                        self.logi.appendMsg("Pass - TEARDOWN 3")

                        self.logi.appendMsg("INFO - TEARDOWN 4: Going to going to change reach profile name")
                        if self.settingsfuncs.edit_reach_profile_name(self.reach_profile_name_old) == False:
                            testStatus = False
                            self.logi.appendMsg("FAIL - TEARDOWN 4: FAILED to going to change reach profile name")
                        else:
                            self.logi.appendMsg("Pass - TEARDOWN 4")

                        self.logi.appendMsg("INFO - TEARDOWN 5: Going to going to change slider option")
                        if self.settingsfuncs.edit_slide_value() == False:
                            testStatus = False
                            self.logi.appendMsg("FAIL - TEARDOWN 5: FAILED to going to change slider option")
                        else:
                            self.logi.appendMsg("Pass - TEARDOWN 5")

                        self.logi.appendMsg("INFO - TEARDOWN 6: Going to change Content Deletion Policy value")
                        if self.settingsfuncs.edit_drop_down_metadata_item(drop_down_item=0, select_field_item=3) == False:
                            testStatus = False
                            self.logi.appendMsg("FAIL - TEARDOWN 6: FAILED to change Content Deletion Policy value")
                        else:
                            self.logi.appendMsg("Pass - TEARDOWN 6")

                        self.logi.appendMsg("INFO - TEARDOWN 7: Going to change Task Processing Region value")
                        if self.settingsfuncs.edit_drop_down_metadata_item(drop_down_item=1, select_field_item=0) == False:
                            testStatus = False
                            self.logi.appendMsg("FAIL - TEARDOWN 7: FAILED to change Task Processing Region value")
                        else:
                            self.logi.appendMsg("Pass - TEARDOWN 7")

                        time.sleep(1)
                        self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()

        except Exception as Exp:
            print(Exp)

        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '1900', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '1900', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_1900_Reach_edit_settings_tab.py', '-s'])
    # ===========================================================================
