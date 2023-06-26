#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# @author: Zeev Shulman
#
# @date: 20/9/21
#
# @description : tests captions editor in kmc - replaces test "4142 edit captions" in the manual Reach test set
#
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#

import os
import subprocess
import sys
import time

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

            self.admin_url = inifile.RetIniVal(section, 'admin_url')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')

            self.logi = reporter2.Reporter2('test_4142_Edit_Captions')

        except Exception as Exp:
            print(Exp)

    def test_4142_Edit_Captions(self):

        global testStatus
        try:
            # Login KMC
            self.logi.initMsg('test_4142_Edit_Captions')
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
                return

            else:
                self.logi.appendMsg("PASS - the entry \"ReachCaption.mp4\" uploaded successfully")

            self.logi.appendMsg("INFO - going to uploaded srt")
            # entry_id = '0_dwt9whpf' - for skipping upload
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

            self.logi.appendMsg("INFO - going to open Closed Captions Editor")
            time.sleep(3)
            dots = self.Wd.find_elements_by_xpath(RDOM.MORE_OPTIONS_DOTS)
            dots[1].click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.CC_EDITOR).click()

            time.sleep(3)
            # ===========================================================================
            #               Editing the Caption in iframe (from KMS)
            # ===========================================================================
            try:
                # "//iframe" is generic waiting for any iframe & its nested, hence 2 times switch_to
                rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)
                time.sleep(10)
                # iframes before 6/2022
                self.Wd.switch_to.frame(1)
                time.sleep(10)
                self.Wd.switch_to.frame(0)
                time.sleep(1)

                # frames = self.Wd.find_elements_by_xpath("//iframe")
                # time.sleep(1)
                # self.Wd.switch_to.frame(frames[0])
                # frames2 = self.Wd.find_elements_by_xpath("//iframe")
                # time.sleep(10)
                # self.Wd.switch_to.frame(frames2[0])
                # time.sleep(1)
            except Exception as Exp:
                self.logi.appendMsg("FAIL - FAILED to load caption editor")
                testStatus = False
                print(Exp)
                return
            try:
                self.logi.appendMsg("INFO - change a time and revert")
                time_caption = self.Wd.find_element_by_xpath(RDOM.CAPTION_TIME)
                # //*[@id="root"]/div/div[3]/div[2]/div[1]/div[1]/div/div/div/div[2]/div[2]/div/div[1]/input[2]
                #time_caption = self.Wd.find_element_by_xpath('//*[@id="root"]/div/div[3]/div[2]/div[1]/div[1]/div/div/div/div[2]/div[2]/div/div[1]/input[2]')
                time_caption.send_keys(Keys.CONTROL, 'a')
                time.sleep(1)

                time_caption.send_keys("00:00:06,333")
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.CAPTIONS_REVERT).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.CAPTION_TIME)
                # completion of sequence without exception means pass
                self.logi.appendMsg("PASS - change and reverted time stamp")
                time.sleep(1)
            except Exception as Exp:
                #//iframe[contains(@src,'https://qa-apache-php7.dev.kaltura.com/apps/captionstudio/latest/index.html?entryid=0_728vs1zf&amp;assetid=0_i37avev5&amp;pid=6265&amp;serviceurl=https://qa-apache-php7.dev.kaltura.com&amp;cdnurl=https://qa-apache-php7.dev.kaltura.com&amp;ks=ZjA2YTZlODIyMmNmMTA5MDcyOTM1MTc5MTg2YjQ2ZGI5YjU4ZDVhOHw2MjY1OzYyNjU7MTY1NTgyMTE5NTsyOzE2NTU3MzQ3OTUuNDQwMjtlbGxhbGlkaWNoQGdtYWlsLmNvbTtkaXNhYmxlZW50aXRsZW1lbnQsYXBwaWQ6a21jOzs=')]
                #//iframe[@class='ng-star-inserted']
                #//iframe[@class='kccs-frame']

                print(Exp)
                self.logi.appendMsg("FAIL - FAILED to change and revert time stamp")
                testStatus = False
                return
            try:
                self.logi.appendMsg("INFO - change a caption")
                # find caption texts, caption_rows[5] picked randomly to be changed
                caption_rows = self.Wd.find_elements_by_xpath(RDOM.CAPTIONS_ROWS)
                caption = caption_rows[5].text
                caption_rows[5].send_keys(Keys.CONTROL, 'a')
                time.sleep(1)
                caption_rows[5].send_keys("Testing captions edit")
                time.sleep(1)
                if caption_rows[5].text == "Testing captions edit":
                    self.logi.appendMsg("PASS - caption changed")
                else:
                    self.logi.appendMsg("FAIL - FAILED to change the caption")
                    testStatus = False
                    return

                self.logi.appendMsg("INFO - search and change")
                self.Wd.find_element_by_xpath(RDOM.CAPTION_SEARCH).send_keys("Testing captions edit")
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.CAPTION_TO_REPLACE).send_keys(caption)
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.CAPTIONS_REPLACE).click()
                time.sleep(1)
                if caption_rows[5].text == caption:
                    self.logi.appendMsg("PASS - caption searched and changed")
                else:
                    self.logi.appendMsg("FAIL - FAILED to search and change the caption")
                    testStatus = False
                    return

                self.logi.appendMsg("INFO - Add speaker")
                self.Wd.find_element_by_xpath(RDOM.SPEAKER_BOXES).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.NEW_SPEAKER).send_keys("CEO")
                time.sleep(1)
                checkboxes = self.Wd.find_elements_by_xpath(RDOM.SPEAKER_BOXES)
                checkboxes[5].click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.ADD_SPEAKER).click()
                time.sleep(1)
                self.logi.appendMsg("INFO - Save changes")
                self.Wd.find_element_by_xpath(RDOM.CAPTIONS_SAVE).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(RDOM.CAPTIONS_YES).click()
                time.sleep(3)

                if "CEO" in caption_rows[5].text:
                    self.logi.appendMsg("PASS - Added speaker & changes saved")
                else:
                    self.logi.appendMsg("FAIL - FAILED to add speaker and save")
                    testStatus = False
                    return

            except Exception as Exp:
                print(Exp)
                testStatus = False

            try:
                self.logi.appendMsg("INFO - out of the editor, verify txt file exists")
                time.sleep(1)
                self.Wd.back()
                self.Wd.refresh()
                time.sleep(1)
                rc = self.BasicFuncs.wait_element(self.Wd, DOM.RELATED_FILES, 10)
                time.sleep(3)
                self.Wd.find_element_by_xpath(DOM.RELATED_FILES).click()
                time.sleep(1)

                if self.Wd.find_element_by_xpath(RDOM.TRANSCRIPT_TXT).is_displayed():
                    self.logi.appendMsg("PASS - txt file exists")
                else:
                    self.logi.appendMsg("FAIL - FAILED to verify txt file exists")
                    testStatus = False
            except Exception as Exp:
                self.logi.appendMsg("FAIL - FAILED to verify .txt exists")
                print(Exp)
                testStatus = False

        except Exception as Exp:
            print(Exp)
            testStatus = False

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
            self.logi.appendMsg("FAIL - TEARDOWN: FAILED to Quit")
            print(Exp)
        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '4142', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '4142', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_4142_Edit_Captions', '-s'])
    # ===========================================================================
