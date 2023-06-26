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
            self.entryName = "15SecAdErez"

            self.logi = reporter2.Reporter2('test_75_localization_of_entry_details')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

            self.entriesName = "AudioAdmin_12"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except:
            pass

    def test_75_localization_of_entry_details(self):

        global testStatus
        self.logi.initMsg('test_75_localization_of_entry_details')

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

            self.logi.appendMsg("INFO - step 1.1: Going to upload vod entry and verify upload")
            try:
                entryStatus = self.basicFuncs.upload_entry_and_wait_for_status_ready(self.Wd, '15SecAdErez.mp4',
                                                                       self.sendto, self.basicFuncs, self.logi, self.Wdobj)
                if not entryStatus:
                    self.logi.appendMsg("FAIL - the entry \"15SecAdErez.mp4\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS step 1.1 - the entry \"15SecAdErez.mp4\" uploaded successfully")

            except Exception as e:
                self.logi.appendMsg(e)
                testStatus = False
                pass

            time.sleep(1)

            self.logi.appendMsg("INFO - step 2: Going to open upload entry")
            rc = self.basicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                self.logi.appendMsg("FAIL - step 2 - could not find the entry- " + self.entryName + " in entries table")
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to open account menu")
            user_menu = self.Wd.find_element_by_xpath(DOM.ACCOUNT_USERNAME)
            if user_menu == None:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to open account menu")
                return
            else:
                user_menu.click()
                self.logi.appendMsg("PASS - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to open language menu")
            account_lang = self.Wd.find_element_by_xpath(DOM.CHANGE_ACCOUNT_LANGUAGE)
            if account_lang == None:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to language menu")
                return
            else:
                account_lang.click()
                self.logi.appendMsg("PASS - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to Going to change account language to Deutsch")
            lang_list = self.Wd.find_elements_by_xpath(DOM.LANGUAGE_MENU_LIST)
            if lang_list == None:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to change account language to Deutsch")
                return
            else:
                lang_list[0].click()
                self.logi.appendMsg("PASS - step 5")

            time.sleep(5)

            self.logi.appendMsg("INFO - step 6: Going to verify Deutsch save button")
            deutsch_save_button = self.Wd.find_element_by_xpath(DOM.DEUTSCH_SAVE_BUTTON)
            if deutsch_save_button.text == 'Speichern':
                self.logi.appendMsg("PASS step 6 - Deutsch save button found")
            else:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED Deutsch save button NOT found")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to open account menu")
            user_menu = self.Wd.find_element_by_xpath(DOM.ACCOUNT_USERNAME)
            if user_menu == None:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to open account menu")
                return
            else:
                user_menu.click()
                self.logi.appendMsg("PASS - step 7")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 8: Going to open language menu")
            account_lang = self.Wd.find_element_by_xpath(DOM.CHANGE_ACCOUNT_LANGUAGE)
            if account_lang == None:
                testStatus = False
                self.logi.appendMsg("FAIL - step 8: FAILED to language menu")
                return
            else:
                account_lang.click()
                self.logi.appendMsg("PASS - step 8")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 9: Going to Going to change account language to English")
            lang_list = self.Wd.find_elements_by_xpath(DOM.LANGUAGE_MENU_LIST)
            if lang_list == None:
                testStatus = False
                self.logi.appendMsg("FAIL - step 9: FAILED to Going to change account language to English")
                return
            else:
                lang_list[0].click()
                self.logi.appendMsg("PASS - step 9")

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

        try:
            # Delete the Uploaded entry
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            self.basicFuncs.deleteEntries(self.Wd, self.entryName)
        except Exception as Exp:
            print(Exp)
            pass

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '75', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '75', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_75_localization_of_entry_details.py -s')
    #===========================================================================
 
        