# ===============================================================================================================
#  @Author: Zeev Shulman 08/12/2022
#
# @description:
#       - enable a leaderboard with userDefaultPolicy "do_not_display",
#         and emails filters  ["display", "do_not_display", "do_not_save"]
#       - send analytics score events (quiz)
#
#       - validate only "display" domains are shown in userscore/list
#       - validate only "do_not_display" domains are shown in the "out" report
#       - validate only "do_not_save" domains are not shown anywhere
#
# ===============================================================================================================

import os
import sys
import json
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)
# ========================================================================
import LeaderBoardFuncs
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
                self.lbId_id_list = ['63e0d8f524ec6aa69281411d']
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
                ### self.lbId_id_list = ['638da849b4e8dc7d9c2b6a7f'] # status: schedualed
                self.lbId_id_list = ['639f27c72cc4d62d2fa2bf72']

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
        except Exception as Exp:
            print(Exp)

    def test_4561_LB_display_by_domain(self):
        global testStatus
        try:
            points_add = 30
            userDefaultPolicy = ["do_not_display","display", "do_not_save"]
            userID_list = ["usr0", "email1", "email2", "email3", "email4", "usr1", "usr2"]  # ['update1','update2','update3','usr3_was','usr0']
            displyed = ["email1", "email2"]
            not_displyed = ["email3", "email4","usr0"]
            not_saved = ["usr1","usr2"]
            list_response_before = []
            list_response_after = []

            # userDefaultPolicy = ["display", "do_not_display", "do_not_save"]
            # userID_list = ["usr0", "opt1", "opt2", "opt3", "opt4", "opt5",
            #                "opt6"]  # ['update1','update2','update3','usr3_was','usr0']
            # should_not_bedisplyed = ["opt1", "opt2", "opt5", "opt6"]
            try:

                print("Info - get userScore/List, on 3 display policy leaderboards to use in validation")
                for lbid in self.lbId_id_list:
                    list_response_before.append(self.game_service.userScoreList(lbid))
                    r = self.game_service.LBUpdate(lbid, "", "", "enabled")
                print("Pass - userScore/List obtained & LB enabled")
            except Exception as Exp:
                print(Exp)
                print("Fail - userScore/List")
                testStatus = False
                return

            try:
                print("Info - send quiz scores to all users in userID_list")
                entryID = LeaderBoardFuncs.generate_rnd_entry()
                for userID_str in userID_list:
                    r = LeaderBoardFuncs.quizPoints(self, userID_str, entryID, points_add)
                    if r == False:
                        print("FAIL - quizPoints")
                        testStatus = False
                        return
                print("Pass - quiz scores sent to analytics")
            except Exception as Exp:
                print(Exp)
                testStatus = False
                return

            try:
                time.sleep(10)
                print("Info - validate, compare before and after userScore/List ")
                for i in range(1):
                    print("Info - userDefaultPolicy = " + str(userDefaultPolicy[i]))
                    list_response_after.append(self.game_service.userScoreList(self.lbId_id_list[i]))
                    list_dict_before = json.loads(str(list_response_before[i].text))
                    list_dict = json.loads(str(list_response_after[i].text))
                    if list_dict["totalCount"] != list_dict_before["totalCount"]:
                        print("Fail - totalCount")
                    else:
                        print("Pass - totalCount, no new users added")

                    objects_before = list_dict_before["objects"]
                    objects = list_dict["objects"]
                    for obj_b in objects_before:
                        #displyed = ["email1", "email2"]
                        if obj_b["id"] == "email1":
                            expected_score1 = obj_b["score"] + points_add
                            print("Info - user email1 score before = " + str(obj_b["score"]))
                        if obj_b["id"] == "email2":
                            expected_score2 = obj_b["score"] + points_add
                            print("Info - user email2 score before = "+str(obj_b["score"]))

                    for obj in objects:
                        if obj["id"] == "usr0":
                            print("FAIL -  usr0 should not appear")
                            testStatus = False
                            return
                        if obj["id"] == "email1":
                            print("Info - user email1 score after = " + str(obj["score"]))
                            if obj["score"] != expected_score1:
                                print("FAIL -  display policy score")
                                testStatus = False
                                return
                        if obj["id"] == "email2":
                            print("Info - user email2 score after = " + str(obj["score"]))
                            if obj["score"] != expected_score2:
                                print("FAIL -  display policy score")
                                testStatus = False
                                return
                        if obj["id"] in not_displyed:
                            print("FAIL -  display policy violation")
                            testStatus = False
                            return
                    print("Pass - scores changed as expected, and 'do no display' and 'do not save' users are out")
                    print('----------------------------')
            except Exception as Exp:
                print(Exp)
                testStatus = False
                return
            for lbid in self.lbId_id_list:
                r = self.game_service.LBUpdate(lbid, "", "", "disabled")

            try:
                list_response_reports = []
                for i in range(1):
                    print("Info - Report userDefaultPolicy = " + str(userDefaultPolicy[i]))
                    r = self.game_service.userScoreReport(self.lbId_id_list[i])
                    list_response_reports.append(getEmailReport(self, self.lbId_id_list[i]))
                    if "usr0" in list_response_reports[i] and "email3" in list_response_reports[i] and "email4" in list_response_reports[i]:
                        print("Pass - users in no-display group are in the 'out' report")
                    else:
                        print("Fail - users in no-display group are NOT in the 'out' report")
                        testStatus = False
                    if "usr1" in list_response_reports[i] or "usr2" in list_response_reports[i]: #"usr1","usr2"
                        print("Fail - do_not_save email mailinator.com users are in the 'out' report")
                        testStatus = False
                    else:
                        print("Pass - NO do_not_save email, mailinator.com, users are in the 'out' report")

                    print('----------------------------')
            except Exception as Exp:
                print(Exp)
                testStatus = False
        except Exception as Exp:
                print(Exp)
                testStatus = False

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus
        print("")
        print("---------- Teardown ---------")
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
        pytest.main(args=['test_4561_LB_display_by_domain.py', '-s'])
    # ===========================================================================

def getEmailReport(self,lbid):
    import RDOM
    import MySelenium
    Wdobj = MySelenium.seleniumWebDrive()
    Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")
    Wd.maximize_window()
    try:
        print("INFO - opening email Inbox")
        Wd.get("https://www.mailinator.com/v4/public/inboxes.jsp?to=" + lbid)
        # Report for leaderboard ID 635552dbe74ddf4af65d8930
        time.sleep(1)
        Report = RDOM.FIND_STRING_ANYWHERE.replace("TEXTTOREPLACE", "Report for leaderboard")
        # Try every 5 sec's - 4 minutes sleeps + 48 find_elements will take up to 10 minutes
        for t in range(0, 48):
            r = Wd.find_elements_by_xpath(Report)
            if len(r) > 0:
                break
            time.sleep(5)

        r[-1].click()
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