# ===============================================================================================================
#  @Author: Zeev Shulman 24/11/2022
#
#  @description:
#       - open a leaderboard with users that have country and title data
#       - get userScore/report for 'opt-in' users with additional headers for country and title
#       - validate result has the new headers, all known titles and countries
#       - get userScore/report for 'opt-out' users with additional headers for country and title
#       - validate known users have the expected title and country
#
#
# ===============================================================================================================

import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)
# ========================================================================
import LeaderBoardService
import Config
import Practitest
import reporter2

#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
    Practi_TestSet_ID = '17888'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()
    pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'ini'))
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
            self.practitest = Practitest.practitest('4586', 'APITests')
            if isProd:
                print('===== PRODUCTION ENVIRONMENT =====')
                self.lbId = "63df9747e8833763260cfa16"#"63dba4bf80f5e5a3e2366541"#"6370e5c914ef1fc7f7395818"
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
                self.lbId = '638621c7b4e8dc7d9c2aa6e0' #"6385d742b4e8dc7d9c2a96a3"  # prod '6370e5c914ef1fc7f7395818'
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
            self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
            self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
            self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
            self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
            self.url = inifile.RetIniVal('Environment', 'KMC_URL')
            self.logi = reporter2.Reporter2('test_1001_score_actions')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)

            # self.practitest = Practitest.practitest('17888')
        except Exception as Exp:
            print(Exp)

    def test_4522_LB_Configurable_report(self):
        global testStatus
        try:
            print("-- test_4522_LB_Configurable_report --")
            # Partner_ID = '4800142'
            postfix = "b"
            validate_list = ["COUNTRY,TITLE","DOORMAN","HR","DEV","CEO","QA","UK","USA","SPAIN","UAE"]
            additional_headers =[{"name": "country", "path": "country"},{"name": "title", "path": "title"}]
            # -----------------------------
            r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
            print("Info - validate 'opt-in' report with additional Headers")
            r_in = self.game_service.userScoreReport(self.lbId, usersOpting="in",additionalHeaders=additional_headers)
            report_in = getEmailReport(self, self.lbId)
            report_in = report_in.upper()
            for need_to_find in validate_list:
                if need_to_find not in report_in:
                    print("Fail - could not find: "+need_to_find)
                    testStatus = False
            if testStatus:
                print("Pass - found expected headers and options in the 'opt-in' report")

            print("Info - validate 'out' report with additional Headers")
            email = self.lbId+postfix+"@mailinator.com"
            r_out = self.game_service.userScoreReport(self.lbId, email=email, usersOpting="out",additionalHeaders=additional_headers)
            report_out = getEmailReport(self, self.lbId,postfix)
            if "Barbara John,UK,DOORMAN" in report_out and "Roger Zelazny,USA,Doorman" in report_out:
                print("Pass - found expected users with title and country in 'opt-out' report")
            else:
                print("Fail -")
                testStatus = False

        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus
        print("")
        print("---------- Teardown ---------")
        r = self.game_service.LBUpdate(self.lbId, "", "", "disabled")
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '356', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '356', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_4522_LB_Configurable_report.py', '-s'])
    # ===========================================================================

def getEmailReport(self,lbid,postfix=""):
    import RDOM
    import MySelenium

    Wdobj = MySelenium.seleniumWebDrive()
    Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")
    Wd.maximize_window()
    try:
        print("INFO - opening email Inbox")
        Wd.get("https://www.mailinator.com/v4/public/inboxes.jsp?to=" + lbid+postfix)
        # Report for leaderboard ID 635552dbe74ddf4af65d8930
        time.sleep(1)
        Report = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", "Report for leaderboard")
        # Try every 5 sec's - 4 minutes sleeps + 48 find_elements will take up to 10 minutes
        for t in range(0, 48):
            r = Wd.find_elements_by_xpath(Report)
            if len(r) > 0:
                break
            time.sleep(5)

        r[0].click()
        print("PASS - opening email massage")
        time.sleep(5)
        Wd.find_element_by_xpath(RDOM.JASON_TAB).click()
        time.sleep(3)
        txt = str(Wd.find_element_by_xpath(RDOM.EMAIL_MSG_JSON).text)
        # Extracting the report
        txt_chunks = txt.split('"body": "')
        txt_chunks_chunks = txt_chunks[1].split('"')
        to_return = txt_chunks_chunks[0]
        Wd.quit()
        return to_return
    except Exception as Exp:
        print(Exp)
        print("FAIL -  FAILED to find the email report")
        return False