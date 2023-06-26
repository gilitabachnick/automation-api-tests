# ===============================================================================================================
#  @Author: Zeev Shulman 14/12/21
#
#  @description: Upload an entry
#                KMC>ENTRY>CAPTION upload caption
#                Captions & Enrich > submit machine translation (English to French)
#                                  > submit machine translation (Spanish to English - with caption upload in iframe)
#                verify assets created in BE
#                   1. in API 3 items created for the entry (1 automated 2 created in Captions & Enrich)
#                   2. in Entry investigation>"entry-investigate caption asset id th" == API>captionAssetId (*2)
#
#  Replaces the following tests in Reach manual regression/post production:
#      6690 - send machine translation with / without caption
#
# ===============================================================================================================

import os
import sys
import time
import subprocess

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

# ========================================================================
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from KalturaClient import *
from KalturaClient.Plugins.Reach import *
import ClienSession
# ========================================================================

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

if isProd:
    isProd = False
    print("FAIL - This is a QA only test, DOESN'T RUN ON PROD")
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
                self.Partner_ID = "1788671"
                self.Initials = "CR" #"Kaltura internal - Ella Lidich"
                self.AdminSecret     = inifile.RetIniVal(section, 'AdminSecretMR')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')
                self.Partner_ID = "6265"
                self.KMCAccountName = "CLONE REACH Template"
                self.Initials = "CR"
                self.AdminSecret     = inifile.RetIniVal(section, 'AdminSecretReach')

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('1328')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome", SaveToC=True)

            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_6690_Reach_machine_translation')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            # ==================================================================
            # generate KS for Partner_ID
            # ==================================================================
            self.ServerURL = inifile.RetIniVal(section, "ServerURL")
            mySess = ClienSession.clientSession(self.Partner_ID, self.ServerURL, self.AdminSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
            myKS = mySess.GetKs()
            self.KS = str(myKS[2])

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)

    def test_6690_Reach_machine_translation(self):
        global testStatus
        self.logi.initMsg('test_6690_Reach_machine_translation')

        # ===========================================================================
        # Login to KMC, upload Entry and captions
        # ===========================================================================
        try:
            self.logi.appendMsg("INFO - login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL -  FAILED to login to KMC")
                return
            time.sleep(1)

            # check if correct account   kUserInitials "//*[contains(@class,'kUserInitials')]"
            if self.Wd.find_element_by_xpath("//*[contains(@class,'kUserInitials')]").text not in self.Initials:
                self.BasicFuncs.ChangeKMCAccount(self.Wd, self.Wdobj, self.logi, str(self.Partner_ID))

            self.logi.appendMsg("INFO - upload Entry")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
            try:
                uploadFromDesktop = self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            except Exception as Exp:
                print(Exp)
                self.logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
                self.logi.reportTest('fail', self.sendto)
                testStatus = False
                return
            uploadFromDesktop.click()
            time.sleep(5)

            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe',
                                        pth + r'\ReachCaption.mp4')
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                subprocess.call([pth2 + "\\openFile.exe", pth + "\\ReachCaption.mp4"])

            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()

            try:
                entry_id = self.BasicFuncs.get_entry_id(self.Wd, row_num=0)
            except Exception as Exp:
                print(Exp)
                self.logi.appendMsg("FAIL - Could not get entry by id")
                testStatus = False
                return

            self.logi.appendMsg("INFO- going to wait until the entry will be in status Ready")
            entryStatus, lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd, entry_id)
            if not entryStatus:
                self.logi.appendMsg(
                    "FAIL - the entry \"ReachCaption.mp4\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS - the entry \"ReachCaption.mp4\" uploaded successfully")
            time.sleep(1)
            self.logi.appendMsg("INFO - going to uploaded srt")
            self.BasicFuncs.selectEntryfromtbl(self.Wd, entry_id)
            self.Wd.find_element_by_xpath(RDOM.ENTRY_CAPTION).click()
            self.Wd.find_element_by_xpath(RDOM.ADD_CAPTION).click()

            self.Wd.find_element_by_xpath(RDOM.UPLOAD_SRT).click()
            time.sleep(1)

            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe',
                                        pth + r'\ReachCaption.srt')
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                subprocess.call([pth2 + "\\openFile.exe", pth + "\\ReachCaption.srt"])
            time.sleep(3)

            btns = self.Wd.find_elements_by_xpath(RDOM.ADD_CAPTION)
            btns[1].click()

            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()

            self.logi.appendMsg("PASS - srt uploaded successfully")
            time.sleep(3)

        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - Failed to Login to KMC, upload Entry")
            return

        # ===========================================================================
        #               Captions & Enrich in iframe (from KMS)
        # ===========================================================================
        try:
            self.logi.appendMsg("INFO - going to open Captions & Enrich")
            self.Wd.find_element_by_xpath(RDOM.CAPTIONS_N_ENRICH).click()
            time.sleep(3)
            rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)
            # iframes before 6/2022
            self.Wd.switch_to.frame(1)
            time.sleep(1)
            # frames = self.Wd.find_elements_by_xpath("//iframe")
            # time.sleep(1)
            # self.Wd.switch_to.frame(frames[0])
            # time.sleep(1)

        except Exception as Exp:
            self.logi.appendMsg("FAIL - FAILED to load Captions & Enrich")
            testStatus = False
            print(Exp)
            return

        try:
            self.logi.appendMsg("INFO - Submit: Machine, Translation, English, French")
            element = self.Wd.find_element_by_xpath(RDOM.FEATURE_SERVICE)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("machine")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(1)
            element = self.Wd.find_element_by_xpath(RDOM.FEATURE_LANGUAGE)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("English")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(1)
            element = self.Wd.find_element_by_xpath(RDOM.FEATURE_ALIGNMENT)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("Translation")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(1)
            element = self.Wd.find_element_by_xpath(RDOM.TARGET_TRANSLATION)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("French")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.SUBMIT_BTN).click()
            self.logi.appendMsg("PASS - Translation 1 with caption submitted")
            time.sleep(3)
        except Exception as Exp:
            self.logi.appendMsg("FAIL - FAILED to send translation")
            testStatus = False
            print(Exp)
            return

        try:
            self.Wd.back()
            self.Wd.refresh()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.ENTRY_CAPTION).click()
            time.sleep(1)
            try:
                self.logi.appendMsg("INFO - going to open Captions & Enrich")
                self.Wd.find_element_by_xpath(RDOM.CAPTIONS_N_ENRICH).click()
                time.sleep(3)
                rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)
                # iframes before 6/2022
                self.Wd.switch_to.frame(1)
                time.sleep(1)
                # frames = self.Wd.find_elements_by_xpath("//iframe")
                # time.sleep(1)
                # self.Wd.switch_to.frame(frames[0])
                # time.sleep(1)
            except Exception as Exp:
                self.logi.appendMsg("FAIL - FAILED to load Captions & Enrich")
                testStatus = False
                print(Exp)
                return

            self.logi.appendMsg("INFO - Submit: Machine, Translation, Spanish ,English")
            element = self.Wd.find_element_by_xpath(RDOM.FEATURE_SERVICE)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("Machine")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(1)
            element = self.Wd.find_element_by_xpath(RDOM.FEATURE_LANGUAGE)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("Spanish")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(1)
            element = self.Wd.find_element_by_xpath(RDOM.FEATURE_ALIGNMENT)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("Translation")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(1)
            element = self.Wd.find_element_by_xpath(RDOM.TARGET_TRANSLATION)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys("English")
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.UPLOAD_CAPTIONS_BTN).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.UPLOAD_BROWSE_BTN).click()
            time.sleep(3)
            if self.Wdobj.RUN_REMOTE:
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe',
                                        pth + r'\ReachCaption.srt')
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                subprocess.call([pth2 + "\\openFile.exe", pth + "\\ReachCaption.srt"])
            time.sleep(5)
            self.Wd.find_element_by_xpath(RDOM.CAPTIONS_SAVE).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.SUBMIT_BTN).click()
            time.sleep(3)
            self.logi.appendMsg("PASS - Translation 2 without caption submitted")
        except Exception as Exp:
            self.logi.appendMsg("FAIL - FAILED to send translation")
            testStatus = False
            print(Exp)
            return

        # ===========================================================================
        # KalturaEntryVendorTask().add() - 2 REACH requests
        # Using API
        # ===========================================================================
        try:
            self.logi.appendMsg("INFO - creating entryvendortask list using API")
            config = KalturaConfiguration(self.Partner_ID)
            config.serviceUrl = "https://qa-apache-php7.dev.kaltura.com/"
            client = KalturaClient(config)
            client.setKs(self.KS)
            entry_vendor_task = KalturaEntryVendorTask()
            entry_vendor_task.entryId = entry_id
            filter = KalturaEntryVendorTaskFilter()
            filter.entryIdEqual = entry_id
            pager = None
            result = client.reach.entryVendorTask.list(filter, pager)
            print(result)

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL -  FAILED to create reach requests via API")
            testStatus = False
            return

        # ==============================================================================================
        # Verify - 3 objects created & the 2 translation captionAssetId's exists in Entry Investigation
        # ==============================================================================================
        try:
            self.logi.appendMsg("INFO - find task objects and captionAssetIds")
            if len(result.objects) == 3:
                AssetId_1 = result.objects[1].taskJobData.captionAssetId
                AssetId_2 = result.objects[2].taskJobData.captionAssetId
                self.logi.appendMsg("PASS - for:" + entry_id + " 3 tasks, AssetIds " + AssetId_1 + " ," + AssetId_2)
            else:
                testStatus = False
                self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED find 3 task objects"))
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED find task objects and captionAssetIds"))
            return

        try:
            self.logi.appendMsg(
                "INFO - going to login to Admin Console: userName - " + self.user + " , PWD - " + self.pwd)
            ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                        self.user, self.env)
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd, self.Wdobj, self.logi, self.admin_url, self.user,
                                                    self.pwd, ks)
            if (rc):
                self.logi.appendMsg("PASS - Admin Console login")
            else:
                self.logi.appendMsg(
                    "FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                testStatus = False
                return
            self.Wd.maximize_window()

        except Exception as Exp:
            self.logi.appendMsg(
                "FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            print(Exp)
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - going to Investigate Entry")
            self.Wd.find_element_by_xpath(RDOM.BATCH_PROCESS_CONTROL_TAB).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.ENTRY_ID_INPUT).send_keys(entry_id)
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.ENTRY_ID_SEARCH).click()
            time.sleep(3)
            asset_id1_xpath = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", str(AssetId_1))
            asset_id2_xpath = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", str(AssetId_2))

            if self.Wd.find_element_by_xpath(asset_id1_xpath).text == AssetId_1:
                if self.Wd.find_element_by_xpath(asset_id2_xpath).text == AssetId_2:
                    self.logi.appendMsg("PASS - translation assets verified in Entry Investigation")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to verify translation assets in Entry Investigation")
            testStatus = False
            return


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
                self.practitest.post(Practi_TestSet_ID, '6690', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '6690', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_6690_Reach_machine_translation.py', '-s'])
    # ===========================================================================
