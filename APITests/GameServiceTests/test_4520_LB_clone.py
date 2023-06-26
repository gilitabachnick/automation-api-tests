# ===============================================================================================================
#  @Author: Zeev Shulman 23/11/2022
#
#  @description:
#       - clone Leaderboard and compare response to old and new Leaderboards
#           leaderboard/get: display policies, sub leaderboards, description etc.
#       - get old and new rules/list and compare the rules
#       - send score events (quiz)
#       - Validate score change and display policies preformed as expected
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
                self.old_lbId = "63dba4bf80f5e5a3e2366541"
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
                self.old_lbId = '63db9ffa9601cca51662846e'
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

    def test_4520_LB_clone(self):
        global testStatus
        try:
            print("-- test_4520_LB_clone --")
            userID_list = ["usr0", "opt1", "opt2", "opt3", "opt4", "opt5", "opt6"]
            points_add = 30
            entry = LeaderBoardFuncs.generate_rnd_entry() #'1_s4acvgzg'

            print("Info - get LB, clone LB, get new LB")
            # compare all LB fields in: [0] original_lb/get, [1] cloned response, [2] cloned.get
            response_list = []
            response_list.append(self.game_service.LBGet(self.old_lbId))
            response_list.append(self.game_service.leaderboardClone(self.old_lbId))
            time.sleep(2)
            response_Jsons = []
            for j in response_list:
                response_Jsons.append(json.loads(str(j.text)))
            new_lbid = response_Jsons[1]["id"]
            response_list.append(self.game_service.LBGet(new_lbid))
            response_Jsons.append(json.loads(str(response_list[2].text)))
            print("Pass - get LB, clone LB, get new LB")
            print("Info - compare old and new leaderboard:")
            print(new_lbid)
            compare_7 = 0
            if response_Jsons[0]["objectType"] == response_Jsons[1]["objectType"] == response_Jsons[2]["objectType"]:
                compare_7 += 1
            else:
                print("Fail - compare compare objectType")
                testStatus = False
            if response_Jsons[0]["partnerId"] == response_Jsons[1]["partnerId"] == response_Jsons[2]["partnerId"]:
                compare_7 += 1
            else:
                print("Fail - compare partnerId")
                testStatus = False
            if response_Jsons[0]["name"] == response_Jsons[1]["name"] == response_Jsons[2]["name"]:
                compare_7 += 1
            else:
                print("Fail - compare name")
                testStatus = False
            if response_Jsons[0]["description"] == response_Jsons[1]["description"] == response_Jsons[2]["description"]:
                compare_7 += 1
            else:
                print("Fail - compare description")
                testStatus = False
            # regardless off the original response_Jsons[0]["status"], cloned status is "disabled"
            if response_Jsons[1]["status"] == response_Jsons[2]["status"] == 'disabled':
                compare_7 += 1
            else:
                print("Fail - compare status")
                testStatus = False
            if response_Jsons[0]["participationPolicy"] == response_Jsons[1]["participationPolicy"] == response_Jsons[2]["participationPolicy"]:
                compare_7 += 1
            else:
                print("Fail - compare description")
                testStatus = False
            if response_Jsons[0]["subLeaderboards"] == response_Jsons[1]["subLeaderboards"] == response_Jsons[2]["subLeaderboards"]:
                compare_7 += 1
            else:
                print("Fail - compare subLeaderboards")
                testStatus = False
            if compare_7 == 7:
                print("Pass - compare")
            else:
                print("Fail - compare")
                testStatus = False
                print(response_Jsons[0])
                print(response_Jsons[1])
                print(response_Jsons[2])
            print("--------------")
        except Exception as Exp:
            print(Exp)
            testStatus = False

        try:
            print("Info - compare rules")
            r_old_rules = self.game_service.ruleList(self.old_lbId)
            r_new_rules = self.game_service.ruleList(self.old_lbId)
            old_rules = (str(r_old_rules.text).rsplit("createdAt"))
            new_rules = (str(r_new_rules.text).rsplit("createdAt"))
            if old_rules[0] == new_rules[0]:
                print("Pass - rule/list compare")
            else:
                print("Fail - rule/list compare")
                testStatus = False

            print("------------------")
            r = self.game_service.LBUpdate(new_lbid, "", "", "enabled")
        except Exception as Exp:
            print(Exp)
            testStatus = False

        try:
            time.sleep(2)
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
        time.sleep(2)

        try:
            print("Info - validate scores")
            list_after = self.game_service.userScoreList(new_lbid)
            list_dict = json.loads(str(list_after.text))
            objects = list_dict["objects"]
            compare_3 = 0
            for obj in objects:
                if obj["id"] == "usr0":
                    if obj["score"] == points_add:
                        compare_3 += 1
                if obj["id"] == "opt3":
                    if obj["score"] == points_add:
                        compare_3 += 1
                if obj["id"] == "opt4":
                    if obj["score"] == points_add:
                        compare_3 += 1
            if compare_3 == 3:
                print("Pass -  validate scores")
            else:
                print("Fail -  validate scores")
                testStatus = False

            print("Info - leaderboard/delete")
            r = self.game_service.LBDelete(new_lbid)
            del_dict = json.loads(str(r.text))
            if r == False or del_dict["status"] == "enabled":
                print("Fail - leaderboard/delete")
                testStatus = False
            else:
                print("Pass - leaderboard/delete")
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
        pytest.main(args=['test_4520_LB_clone.py', '-s'])
    # ===========================================================================