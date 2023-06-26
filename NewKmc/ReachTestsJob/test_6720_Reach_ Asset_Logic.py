# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# @author: Zeev Shulman
# @date: 08/11/2021
#
# @description :
# 1) KMC: upload entry, add caption (.srt) add another caption of the same language and accuracy, after save
#       only 1 is on
# 2) add another caption of the same language lower accuracy, after save
#       first entry is on
#
# Replaces the following tests in Reach manual regression/post production:
#   	6720 - Caption assets logic
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
                # self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("firefox")
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user = "power.any.video@mailinator.com"  # inifile.RetIniVal(section, 'reachUserName')
                self.pwd = "Jrt)1939"  # inifile.RetIniVal(section, 'partnerId4770_PWD')
                self.Partner_ID = 6265
                self.KMCAccountName = "MAIN Template"
                # self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

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
            self.logi = reporter2.Reporter2('test_6720_Reach_Asset_Logic')

        except Exception as Exp:
            print(Exp)

    def test_6720_Reach_Asset_Logic(self):
        global testStatus

        try:
            # Login KMC
            self.logi.initMsg('test_6720_Reach_Asset_Logic')
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - Failed to login to KMC")
            self.logi.reportTest('fail', self.sendto)
            testStatus = False
            return

        try:
            self.logi.appendMsg("INFO - going to upload MP4 file")
            uploadFromDesktop = self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
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
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - Failed to upload MP4 file")
            self.logi.reportTest('fail', self.sendto)
            testStatus = False
            return

        try:
            entry_id = self.BasicFuncs.get_entry_id(self.Wd, row_num=0)
            self.logi.appendMsg("INFO - going to wait until the entry will be in status Ready")
            entryStatus, lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd, entry_id)
            if not entryStatus:
                self.logi.appendMsg(
                    "FAIL - the entry \"ReachCaption.mp4\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                self.logi.appendMsg("PASS - the entry \"ReachCaption.mp4\" uploaded successfully")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - MP4 not in: status Ready")
            testStatus = False
            return

        # ===========================================================================
        # Upload 3 Caption srt sets
        #  - First do nothing
        #  - Second see only 1 is selected
        #  - Third verify a caption with 100% accuracy was selected
        # ===========================================================================
        try:
            self.logi.appendMsg("INFO - going to uploaded 3 Caption srt sets")
            self.BasicFuncs.selectEntryfromtbl(self.Wd, entry_id)
            self.Wd.find_element_by_xpath(RDOM.ENTRY_CAPTION).click()
            for i in range(1, 4):
                self.Wd.find_element_by_xpath(RDOM.ADD_CAPTION).click()
                if i == 3:
                    element = self.Wd.find_element_by_xpath(RDOM.CAPTION_QUALITY_SLIDER)
                    actions = ActionChains(self.Wd)
                    actions.move_to_element(element).click_and_hold()
                    actions.send_keys(Keys.ARROW_LEFT)
                    actions.send_keys(Keys.ARROW_LEFT)
                    actions.send_keys(Keys.ARROW_LEFT)
                    actions.send_keys(Keys.ARROW_LEFT)
                    actions.send_keys(Keys.ARROW_LEFT)
                    actions.release()
                    actions.perform()
                    time.sleep(1)

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

                self.logi.appendMsg("PASS - srt num " + str(i) + " uploaded successfully")
                time.sleep(3)
                if i == 2:
                    yes_list = self.Wd.find_elements_by_xpath(RDOM.YES_TEXT)
                    if len(yes_list)==1:
                        self.logi.appendMsg("PASS - 1 srt selected")
                    else:
                        self.logi.appendMsg("FAIL - failed to select 1 srt")
                        testStatus = False
                        return

                # =====================================================================================
                # Cycle through lines of captions SRTs
                # Verify selected caption is 100% accuracy
                # =====================================================================================
                elif i == 3:
                    srt_list = self.Wd.find_elements_by_xpath(RDOM.CAPTION_LINES)
                    index = 0
                    max_accuracy_selected = False
                    for el in srt_list:
                        index = index + 1
                        display_xp = RDOM.CAPTION_SELECTED.replace("TEXTTOREPLACE", str(index))
                        display = self.Wd.find_element_by_xpath(display_xp).text
                        accuracy_xp = RDOM.CAPTION_ACCURACY.replace("TEXTTOREPLACE", str(index))
                        accuracy = self.Wd.find_element_by_xpath(accuracy_xp).text
                        if accuracy == "100%" and display == "Yes":
                            max_accuracy_selected = True
                            break
                    if max_accuracy_selected:
                        self.logi.appendMsg("PASS - Max accuracy selected")
                    else:
                        self.logi.appendMsg("FAIL - Max accuracy NOT selected")
                        testStatus = False

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - caption asset logic failed")
            testStatus = False
            return

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):
        global testStatus

        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(1)
            self.BasicFuncs.deleteEntries(self.Wd, "ReachCaption")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - TEARDOWN: FAILED to delete entry")
            testStatus = False

        try:
            self.Wd.quit()
        except Exception as Exp:
            print("Teardown quit() Exception")
            print(Exp)

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '6720', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '6720', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_6720_Reach_Asset_Logic.py', '-s'])
    # ===========================================================================
