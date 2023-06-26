# ===============================================================================================================
#  @Author: Zeev Shulman 21/11/21
#
#  @description: Upload an entry
#                Create Reach requests via API using KMS session (KS)
#                approve/reject in KMC>SERVICES DASHBOARD
#                verify 4 appropriate eMail notification arrived
#
#  Replaces the following tests in Reach manual regression/post production:
#  5390 - Notifications to an group of moderators once a request is waiting for approval
#  5391 - Notification for a requester once a request approved
#  5392 - Notification for a requester once a request rejected
# ===============================================================================================================

import os
import sys
import time
import subprocess

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from KalturaClient import *
from KalturaClient.Plugins.Reach import *
# ========================================================================

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
                print('===== PRODUCTION ENVIRONMENT =====')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.Partner_ID = 1788671
                self.user_secret = inifile.RetIniVal(section, 'UserSecretReach')
                self.user = inifile.RetIniVal(section, 'userElla')
                self.pwd = inifile.RetIniVal(section, 'passElla')

                self.serviceUrl = "https://www.kaltura.com/"
                self.reachProfile_name = "yearly test"
                self.reachProfileId = 129573
                self.catalogItemId_list = [9983, 6733]
            else:
                section = "Testing"
                self.env = 'testing'
                print('===== TESTING ENVIRONMENT =====')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.Partner_ID = 6265
                self.user_secret = inifile.RetIniVal(section, 'UserSecretReach')
                self.user = inifile.RetIniVal(section, 'reachUserName')
                self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')

                self.serviceUrl = "https://qa-apache-php7.dev.kaltura.com/"
                self.reachProfile_name = "Do NOT Delete"
                self.reachProfileId = 225
                self.catalogItemId_list = [176, 227]

            # mail_to_notify, as defined in PID's event notifications templates
            self.mail_to_notify = "kalturaQArules"
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"

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

            self.logi = reporter2.Reporter2('test_5390_Reach_notifications')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)

    def test_5390_Reach_notifications(self):
        global testStatus
        self.logi.initMsg('test_5390_Reach_notifications')

        # ===============================================================================
        # Create Session (KS) emulating KMS user requiring approval for REACH requests
        # Using API
        # ===============================================================================
        try:
            config = KalturaConfiguration()
            config.serviceUrl = self.serviceUrl
            client = KalturaClient(config)
            secret = self.user_secret
            userId = self.user
            partnerId = self.Partner_ID
            expiry = None
            privileges = self.privileges
            KMS_KS = client.session.start(secret, userId, type, partnerId, expiry, privileges)
            print(KMS_KS)

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to create KMS KS")
            testStatus = False
            return

        # ===========================================================================
        # Login to KMC, upload Entry, navigate to SERVICES DASHBOARD
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
            self.Wd.find_element_by_xpath(RDOM.SERVICES_DASHBOARD).click()
            time.sleep(1)
            self.logi.appendMsg("PASS - navigate to SERVICES DASHBOARD")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - Failed to Login to KMC, upload Entry, navigate to SERVICES DASHBOARD")
            return

        # ===========================================================================
        # KalturaEntryVendorTask().add() - 2 REACH requests
        # Using API
        # ===========================================================================
        try:
            self.logi.appendMsg("INFO - creating reach 2 requests via API")
            config = KalturaConfiguration()
            config.serviceUrl = self.serviceUrl
            client = KalturaClient(config)
            client.setKs(KMS_KS)

            entry_vendor_task = KalturaEntryVendorTask()
            entry_vendor_task.entryId = entry_id
            entry_vendor_task.reachProfileId =   self.reachProfileId
            entry_vendor_task.catalogItemId = self.catalogItemId_list[0]
            result = client.reach.entryVendorTask.add(entry_vendor_task)
            print(result)
            entry_vendor_task = KalturaEntryVendorTask()
            entry_vendor_task.entryId = entry_id
            entry_vendor_task.reachProfileId = self.reachProfileId
            entry_vendor_task.catalogItemId = self.catalogItemId_list[1]
            result = client.reach.entryVendorTask.add(entry_vendor_task)
            print(result)
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL -  FAILED to create reach requests via API")
            testStatus = False
            return

        # ===========================================================================
        # KMC>SERVICES DASHBOARD, approved & rejected requests
        # ===========================================================================
        try:
            # "//iframe" is generic waiting for any iframe
            rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)
            self.Wd.switch_to.frame(0)
            time.sleep(10)
            self.logi.appendMsg("INFO- going to set Unit to REACH Profile Name")
            element = self.Wd.find_element_by_xpath(RDOM.SERVICES_UNIT)
            actions = ActionChains(self.Wd)
            actions.move_to_element(element).click_and_hold()
            actions.send_keys(self.reachProfile_name)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(3)
            self.logi.appendMsg("PASS - Unit: REACH Profile Name selected")
            self.logi.appendMsg("INFO - going to reject top request")
            entry_1_box = RDOM.SERVICES_ENTRY_BOX.replace("TEXTTOREPLACE", "1")
            entry_2_box = RDOM.SERVICES_ENTRY_BOX.replace("TEXTTOREPLACE", "2")
            self.Wd.find_element_by_xpath(entry_1_box).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.SERVICES_REJECT).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.YES_TEXT).click()
            time.sleep(3)
            self.logi.appendMsg("INFO - going to approve second row request")
            self.Wd.find_element_by_xpath(entry_1_box).click()
            time.sleep(1)
            try:
                self.Wd.find_element_by_xpath(entry_2_box).click()
            except:
                print("iframe changed behavior - test might need revision")
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.SERVICES_APPROVE).click()
            time.sleep(3)
            self.Wd.find_element_by_xpath(RDOM.YES_TEXT).click()
            time.sleep(1)
            self.logi.appendMsg("PASS - requests approved & rejected in KMC>SERVICES DASHBOARD")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL -  FAILED to approve/reject requests in KMC>SERVICES DASHBOARD")
            return

        # =====================================================================================
        # To save extra login after email check - Delete Entry is not in teardown
        # =====================================================================================
        try:
            time.sleep(1)
            self.Wd.back()
            self.Wd.refresh()
            time.sleep(3)
            self.BasicFuncs.deleteEntries(self.Wd, "ReachCaption")
        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to delete entry")

        # ===========================================================================
        # Verify eMail notifications
        # ===========================================================================
        try:
            self.logi.appendMsg("INFO - opening email Inbox")
            self.Wd.get("https://www.mailinator.com/v4/public/inboxes.jsp?to=" + self.mail_to_notify)
            if rc:
                time.sleep(1)
                how_many_correct_emails = 0
                awaiting_approval = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", "awaiting approval")
                approved = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", "request is approved")
                rejected = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", "request was rejected")
                # Try every 5 sec's - 4 minutes sleeps + 48 find_elements will take up to 10 minutes
                for t in range(0, 48):
                    self.Wd.find_elements_by_xpath(approved)
                    if len(self.Wd.find_elements_by_xpath(awaiting_approval)) > 0:
                        how_many_correct_emails += 1
                        break
                    time.sleep(5)
                if len(self.Wd.find_elements_by_xpath(rejected)) > 0:
                    how_many_correct_emails += 1
                if len(self.Wd.find_elements_by_xpath(awaiting_approval)) > 1:
                    how_many_correct_emails += 2
                if how_many_correct_emails == 4:
                    self.logi.appendMsg("PASS - 4 correct email notifications found")
                else:
                    self.logi.appendMsg("FAIL - found " + str(how_many_correct_emails) + " correct email notifications out off 4")
                time.sleep(1)
            if not rc:
                testStatus = False
                self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find the email notifications"))

        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find the email notifications"))


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
                self.practitest.post(Practi_TestSet_ID, '5390', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '5390', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_5390_Reach_notifications', '-s'])
    # ===========================================================================