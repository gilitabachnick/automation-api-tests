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
import uploadFuncs
import Config
import Practitest
import Entrypage
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
            self.user = inifile.RetIniVal(section, 'userName6')
            self.pwd = inifile.RetIniVal(section, 'pass6')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.logi = reporter2.Reporter2('test_76_navigation_between_entries')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.entrypagefuncs = Entrypage.entrypagefuncs(self.Wd)
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.practitest = Practitest.practitest('4586')
            self.entryName = 'Draft Entry'
            self.entryName2 = 'Draft Entry 2'



            self.entriesName = "AudioAdmin_12"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print (Exp)
            pass

    def test_76_navigation_between_entries(self):

        global testStatus
        self.logi.initMsg('test_76_navigation_between_entries')

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

            self.logi.appendMsg("INFO - step 2: Going to prepare an empty video entry")
            if self.uploadFuncs.prepare_entry(entry_type='video', entry_name=self.entryName2) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to prepare an empty video entry")
                return
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to prepare a 2nd empty video entry")
            if self.uploadFuncs.prepare_entry(entry_type='video', entry_name=self.entryName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to prepare a 2nd empty video entry")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(5)

            self.logi.appendMsg("INFO - step 4: Going to open first entry")
            rc = self.basicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL step 4 - could not find the entry- " + self.entryName + " in entries table")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(2)

            self.logi.appendMsg("INFO - step 5: Going to navigate to next entry")
            if self.entrypagefuncs.navigate_entries('next') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to navigate to next entry")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to verify next entry name")
            try:
                time.sleep(1)
                current_entry_name_title = self.Wd.find_element_by_xpath(DOM.ENTRY_NAME)
                if current_entry_name_title.is_displayed():
                    current_entry_name = current_entry_name_title.get_attribute("value")
                    time.sleep(1)

                    if current_entry_name != self.entryName2:
                        testStatus = False
                        self.logi.appendMsg("FAIL - step 6: FAILED to verify next entry name")
                        return False
                    else:
                        self.logi.appendMsg("Pass - step 6")
            except:
                self.logi.appendMsg("FAIL - step 6: FAILED to verify next entry name")
                return False

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to navigate to previous entry")
            if self.entrypagefuncs.navigate_entries('previous') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to navigate to next entry")
                return
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 8: Going to verify previous entry name")
            try:
                time.sleep(1)
                current_entry_name_title = self.Wd.find_element_by_xpath(DOM.ENTRY_NAME)
                if current_entry_name_title.is_displayed():
                    current_entry_name = current_entry_name_title.get_attribute("value")

                    if current_entry_name != self.entryName:
                        testStatus = False
                        self.logi.appendMsg("FAIL - step 8: FAILED to verify next entry name")
                        return False
                    else:
                        self.logi.appendMsg("Pass - step 8")
            except:
                self.logi.appendMsg("FAIL - step 8: FAILED to verify next entry name")
                return False

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
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            self.basicFuncs.deleteEntries(self.Wd, 'Draft Entry')
        except:
            pass

        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '76', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '76', '0')
            assert True

    #===========================================================================
    # pytest.main('test_76_navigation_between_entries.py -s')
    #===========================================================================
 
        
