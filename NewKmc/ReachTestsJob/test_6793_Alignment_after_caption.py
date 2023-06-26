#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# @author: Zeev Shulman
# @date: 06/10/2021
#
# @description :
# 1) KMC: upload entry, add caption (.srt), goto Caption&Enrich, set: service-Machine English Feature-Alignment,
#       Upload .txt, remember entryID + in Related Files AssetID.
# 2) testMe: KS + entryVendorTask>list>Edit (filter), filter:EntryIdEqual (entryID) Send,
#       Validation: in XML find AssetID inside <textTranscriptID> </...>
#
# Replaces the following tests in Reach manual regression/post production:
#   6793 - E2E send alignment request when caption with same language and accuracy 99% already exists
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#

import os
import subprocess
import sys
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import DOM
import MySelenium
import KmcBasicFuncs
import reporter2
import Config
import Practitest
import RDOM

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '14657'
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
        global testStatus

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
                self.user = "power.any.video@mailinator.com"
                self.pwd = "Jrt)1939"
                self.Partner_ID = 6265
                self.KMCAccountName = "MAIN Template"

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('1328')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_6793_Alignment_after_caption')

        except Exception as Exp:
            print(Exp)

    def test_6793_Alignment_after_caption(self):

        global testStatus
        try:
            # Login KMC
            self.logi.initMsg('test_6793_Alignment_after_caption')
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            self.logi.appendMsg("INFO - going to upload MP4 file")
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

            self.logi.appendMsg("INFO - going to wait until the entry will be in status Ready")
            entryStatus, lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd, entry_id)
            if not entryStatus:
                self.logi.appendMsg(
                    "FAIL - the entry \"ReachCaption.mp4\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False

            else:
                self.logi.appendMsg("PASS - the entry \"ReachCaption.mp4\" uploaded successfully")

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

            # =====================================================================================
            # Need an ADD_CAPTION list to find the Add Caption element
            # when the load window is open there are two buttons with the same name, class etc
            # =====================================================================================
            btns = self.Wd.find_elements_by_xpath(RDOM.ADD_CAPTION)
            btns[1].click()

            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.MR_SAVE_BTN).click()

            self.logi.appendMsg("PASS - srt uploaded successfully")
            time.sleep(3)

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
                self.logi.appendMsg("INFO - going to set request params to: Machine, English, Alignment")
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
                actions.send_keys("Alignment")
                actions.send_keys(Keys.ENTER)
                actions.perform()
                time.sleep(3)
            except Exception as Exp:
                self.logi.appendMsg("FAIL - FAILED to set params")
                testStatus = False
                print(Exp)
                return

            try:
                self.logi.appendMsg("INFO - going to upload txt")
                self.Wd.find_element_by_xpath(RDOM.UPLOAD_TXT).click()
                time.sleep(3)
                self.Wd.find_element_by_xpath(RDOM.SELECT_FILE_BTN).click()
                time.sleep(3)
                # ========== remove after uncomment caption upload
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                # ==========
                subprocess.call([pth2 + "\\openFile.exe", pth + "\\ReachCaption.txt"])
                rc = self.BasicFuncs.wait_element(self.Wd, RDOM.CAPTIONS_SAVE, 60)
                time.sleep(3)
                self.Wd.find_element_by_xpath(RDOM.CAPTIONS_SAVE).click()
                time.sleep(10)
                self.Wd.find_element_by_xpath(RDOM.SUBMIT_BTN).click()
                time.sleep(3)
            except Exception as Exp:
                if isProd:
                    self.logi.appendMsg("SUBMIT_BTN not working in prod")
                else:
                    self.logi.appendMsg("FAIL - FAILED to upload txt")
                    testStatus = False
                    print(Exp)
                    return

            try:
                self.logi.appendMsg("INFO - ENTRY>RELATED FILES for validation data")
                time.sleep(1)
                self.Wd.back()
                self.Wd.refresh()
                time.sleep(1)
                rc = self.BasicFuncs.wait_element(self.Wd, DOM.RELATED_FILES, 10)
                time.sleep(3)
                self.Wd.find_element_by_xpath(DOM.RELATED_FILES).click()

                asset_id = self.Wd.find_element_by_xpath(RDOM.RELATED_ASSET_ID).text
                if len(asset_id) > 5:
                    self.logi.appendMsg("PASS- Alignment: EntryID: " + entry_id + " AssetID: "+asset_id)
                else:
                    self.logi.appendMsg("FAIL - FAILED to find Alignment data for validation")
                    testStatus = False
                    return
            except Exception as Exp:
                self.logi.appendMsg("FAIL - FAILED to find Alignment data for validation")
                testStatus = False
                print(Exp)
                return

            try:
                self.logi.appendMsg(
                    "INFO - going to login to Admin Console: userName - " + self.user + " , PWD - " + self.pwd)
                ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                            'zeev.shulman@kaltura.com', self.env)
                rc = self.BasicFuncs.invokeConsoleLogin(self.Wd, self.Wdobj, self.logi, self.admin_url, 'zeev.shulman@kaltura.com',
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
                self.logi.appendMsg("INFO - going to look for alignment asset in Entry Investigation")
                self.Wd.find_element_by_xpath(RDOM.BATCH_PROCESS_CONTROL_TAB).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.ENTRY_ID_INPUT).send_keys(entry_id)
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.ENTRY_ID_SEARCH).click()
                time.sleep(3)
                self.logi.appendMsg("INFO - going to Investigate Entry")
                asset_id_xpath  = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", str(asset_id))
                file_name_xpath = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", "ReachCaption.txt")

                if self.Wd.find_element_by_xpath(asset_id_xpath).text == asset_id:
                    if self.Wd.find_element_by_xpath(file_name_xpath):
                        self.logi.appendMsg("PASS - alignment txt was found")
            except Exception as Exp:
                print(Exp)
                self.logi.appendMsg("FAIL - FAILED to find alignment asset")
                testStatus = False
                return

        except Exception as Exp:
            print(Exp)
            testStatus = False

    def teardown_class(self):
        global testStatus

        try:
            # Invoke and login
            self.logi.appendMsg("INFO - TEARDOWN going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - TEARDOWN FAILED to login to KMC")
            else:
                time.sleep(1)
                self.logi.appendMsg("INFO - TEARDOWN: going to delete ReachCaption")
                self.BasicFuncs.deleteEntries(self.Wd, "ReachCaption")

        except Exception as Exp:
            testStatus = False
            self.logi.appendMsg("FAIL - TEARDOWN FAILED to login to KMC to delete ReachCaption")
            print(Exp)

        try:
            self.Wd.quit()
        except Exception as Exp:
            self.logi.appendMsg("FAIL - TEARDOWN: FAILED to Quit")
            print(Exp)
        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '6793', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '6793', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_6793_Alignment_after_caption'])
    # ===========================================================================
