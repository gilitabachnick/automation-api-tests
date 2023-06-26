# ===============================================================================================================
#  @Author: Zeev Shulman 20/9/21
#
#  @description: Send email with link to CSV containing KMC>SERVICES DASHBOARD>Service Requests table
#  and verify data
#
#  Replaces the following tests in Reach manual regression/post production:
#  5333 Export to CSV caption requests list
#
# ===============================================================================================================

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
                self.Export_File_PID = 'export_1788671'

                # self.user = inifile.RetIniVal(section, 'userElla')
                # self.pwd = inifile.RetIniVal(section, 'passElla')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.Export_File_PID = 'export_6265'

                # self.user = inifile.RetIniVal(section, 'reachUserName')
                # self.pwd = inifile.RetIniVal(section, 'partnerId4770_PWD')

            self.user = "power.any.video@mailinator.com"
            self.pwd = "Jrt)1939"
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

            self.logi = reporter2.Reporter2('test_5333_Email_Service_Requests')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    # Every try except block in the text does what the appendMsg() "INFO" says
    #   Unlike test_1921, 1922, CSV gets a unique name created when exported.
    #   CSV_file_path will be filled after download
    # ===========================================================================
    def test_5333_Email_Service_Requests(self):
        global testStatus
        global CSV_file_path
        try:
            self.logi.initMsg('test_5333_Email_Service_Requests')
            self.logi.appendMsg("INFO - going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL -  FAILED to login to KMC")
                return
            time.sleep(1)
            self.logi.appendMsg("PASS - login to KMC")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL -  FAILED to login to KMC")
            return

        try:
            self.logi.appendMsg("INFO - going to navigate to SERVICES DASHBOARD")
            self.Wd.find_element_by_xpath(RDOM.SERVICES_DASHBOARD).click()
            time.sleep(1)
            self.logi.appendMsg("PASS - navigate to SERVICES DASHBOARD")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL -  FAILED to navigate to SERVICES DASHBOARD")
            return

        try:
            self.logi.appendMsg("INFO - Going to check for requests")
            # "//iframe" is generic waiting for any iframe
            rc = self.BasicFuncs.wait_element(self.Wd, "//iframe", 60)
            self.Wd.switch_to.frame(0)
            time.sleep(10)

            # requests_number and cost of the first will be used for validation
            requests_string = self.Wd.find_element_by_xpath(RDOM.SERVICES_REQUEST_NUM).text
            for word in requests_string.split():
                if word.isdigit():
                    requests_number = (int(word))
                    break

            if requests_number > 0:
                self.logi.appendMsg("PASS - requests found")
                try:
                    cost = self.Wd.find_element_by_xpath(RDOM.SERVICES_FIRST_COST).text
                except:
                    # prod and testing create different xPaths
                    cost = self.Wd.find_element_by_xpath(RDOM.SERVICES_FIRST_COST_OLD).text
            else:
                self.logi.appendMsg("FAIL -  FAILED to find requests")
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find requests"))
            return

        try:
            self.logi.appendMsg("INFO - Going to export CSV")
            self.Wd.find_element_by_xpath(RDOM.SERVICES_EMAIL_CSV).click()
            self.logi.appendMsg("PASS - export CSV")
            time.sleep(5)

        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to export CSV"))
            return

        try:
            self.logi.appendMsg("INFO - opening email massage")
            usr = "power.any.video" #self.user.replace("@mailinator.com", "") + "\n"
            self.Wd.get("https://www.mailinator.com/v4/public/inboxes.jsp?to=" + usr)
            rc = self.BasicFuncs.wait_element(self.Wd, RDOM.SERVICES_EMAIL_CAPTION, 180)
            if rc:
                self.Wd.find_element_by_xpath(RDOM.SERVICES_EMAIL_CAPTION).click()
                self.logi.appendMsg("PASS - opening email massage")
                time.sleep(5)
            else:
                testStatus = False
                self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find the email massage"))
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find the email massage"))
            return

        try:
            self.logi.appendMsg("INFO - extracting CSV link and downloading")
            self.Wd.find_element_by_xpath(RDOM.JASON_TAB).click()
            time.sleep(3)
            txt = str(self.Wd.find_element_by_xpath(RDOM.EMAIL_MSG_JSON).text)
            # Extracting the link from Kaltura's automated response
            txt_chunks = txt.split("csv: ")
            txt_chunks_chunks = txt_chunks[1].split("<br")
            link = txt_chunks_chunks[0]
            print(link)
            self.Wd.get(link)
            time.sleep(3)
            self.logi.appendMsg("PASS - extracted CSV link")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to extract and download the CSV link "))
            return

        try:
            self.logi.appendMsg("INFO - Going open downloaded CSV")
            CSVpth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
            folder_content = os.listdir(CSVpth)
            export_file_name = ""
            for f in folder_content:
                if self.Export_File_PID in str(f):
                    export_file_name = str(f)
                    break
            if export_file_name != "":
                CSV_file_path = os.path.join(CSVpth, export_file_name)
                CSVfile = open(CSV_file_path, mode='r')
                CSVdata = CSVfile.read()
                rows = str(CSVdata).split("\n")
                time.sleep(1)
                CSVfile.close()
                self.logi.appendMsg("PASS - CSV Opened")

            self.logi.appendMsg("INFO - Going to Validate Exported data")
            # validating by comparing num of Requests and the cost of the top request
            # the (or == -1) is in case KALTURA stops sending CSV with an empty line
            if (requests_number == (len(rows)-2) or requests_number == (len(rows)-1)) and cost in CSVdata:
                self.logi.appendMsg("PASS - Exported data Validated")
            else:
                self.logi.appendMsg("FAIL - FAILED to Validate Exported data")
                testStatus = False
        except Exception as Exp:
            testStatus = False
            self.logi.appendMsg("FAIL - FAILED to Validate Exported data")
            print(Exp)

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):
        global testStatus
        global CSV_file_path
        try:
            self.Wd.quit()
        except Exception as Exp:
            print("Teardown quit() Exception")
            print(Exp)

        try:
            self.logi.appendMsg("TEARDOWN - Going to Delete 'export.csv'")
            os.remove(CSV_file_path)
            time.sleep(1)
            if os.path.exists(CSV_file_path):
                testStatus = False
                self.logi.appendMsg("TEARDOWN - FAILED to to Delete 'export.csv'")
            else:
                self.logi.appendMsg("TEARDOWN - PASS, 'export.csv' Deleted")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("TEARDOWN - FAILED to to Delete 'export.csv'")

        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '5333', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '5333', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_5333_Email_Service_Requests.py', '-s'])
    # ===========================================================================
