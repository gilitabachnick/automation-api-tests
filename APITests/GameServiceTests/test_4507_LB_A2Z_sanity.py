# ===============================================================================================================
#  @Author: Zeev Shulman 12/10/2022
#
#  @description:
#      Game service API, AKA leaderboard, sanity:
#      1) most '/leaderboard/' actions done once -
#      2) most '/Rule/' actions done once
#      3) send confirmation events to analytics
#      4) '/userscore/get' and '/userscore/list' results validated -
#           including score, rank, BE kuser data and tiebreaker
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
import LeaderBoardService
import Practitest
import reporter2
import Config

#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    Practi_TestSet_ID = '17888'
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
            self.practitest = Practitest.practitest('4586', 'APITests')
            if isProd:
                print('===== PRODUCTION ENVIRONMENT =====')
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
            self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
            self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
            self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
            self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
            self.url = inifile.RetIniVal('Environment', 'KMC_URL')
            self.logi = reporter2.Reporter2('test_4507_LB_A2Z_sanity')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)
            # self.practitest = Practitest.practitest('17888')
        except Exception as Exp:
            testStatus = False
            print(Exp)
            testStatus = False

    def test_4507_LB_A2Z_sanity(self):
        global testStatus
        self.logi.initMsg('test_4507_LB_A2Z_sanity')
        # responses_list[] will be used for validation throughout the test
        responses_list = []
        try:
            print("=== all '/leaderboard/' actions done once ===")
            print("Info - create new Leaderboard")
            step = 0
            r = self.game_service.LBCreate("E2E LbTesting", "E2E created", "disabled")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            lbId = responses_list[0]["id"]
            print("Pass - New Leaderboard created step: " + str(step))
            print("Info - update Leaderboard")
            step += 1
            r = self.game_service.LBUpdate(lbId,"","E2E updated", "enabled")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            invalid_LbResponse = True
            if responses_list[0]["status"] == "disabled":
                if responses_list[1]["status"] == "enabled":
                    print("Pass - update Leaderboard step: " + str(step))
                    invalid_LbResponse = False
            if invalid_LbResponse:
                print("Fail E2E step: " + str(step) + " invalid update Leaderboard")
                testStatus = False
                return

            print("Info - list Leaderboard")
            step += 1
            time.sleep(3)
            r = self.game_service.LBList("enabled")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            if lbId in r.text:
                print("Pass - list, new id validated, enabled")
            else:
                print("Fail E2E step: " + str(step) + "  leaderboard/list validation")
                testStatus = False
                #return

            print("Info - get Leaderboard")
            step += 1
            r = self.game_service.LBGet(lbId)
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            if responses_list[3]["description"] == "E2E updated" and responses_list[3]["status"] == "enabled":
                print("Pass - get, description validated & status enabled")
            else:
                print("Fail E2E step: " + str(step) + " invalid get Leaderboard")
                testStatus = False
                return
            print("*** Pass all Leaderboard Actions ***")

        except Exception as Exp:
            print("Fail E2E step: "+str(step))
            print(Exp)
            testStatus = False
            return

        try:
            print("=== all '/Rule/' actions done once ===")
            print("Info - rule/create: Confirmation 50")
            step += 1
            #ruleCreate(self, ruleType, gameObjectId, name, description="", status="disabled", points="", maxPoints="")
            r = self.game_service.ruleCreate("confirmation", lbId, "Confirmation 50",
                                         "33 confirmation", "enabled", "33", "33")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - Confirmation 50, created")
            ruleId = responses_list[-1]["id"]
            print("Info - rule/delete")
            step += 1
            r = self.game_service.ruleDelete(ruleId)
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - rule/delete")
            print("Info - rule/update")
            step += 1
            #ruleUpdate(self, id, name="", description="", status="", points="", maxPoints="exclude")
            r = self.game_service.ruleUpdate(ruleId,"","50 confirmation","enabled","50","50")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            invalid_ruleUpdate = True
            if responses_list[-1]["status"] == "enabled":
                if responses_list[-2]["status"] == "disabled":
                    if responses_list[-3]["status"] == "enabled":
                        print("Pass - verification of status changes: create[enabled]>delete[disabled]>update[enabled]")
                        invalid_ruleUpdate = False
            if invalid_ruleUpdate:
                print("Fail E2E step: " + str(step) + " invalid rule/Update")
                testStatus = False
                return

            print("Info - rule/get")
            step += 1
            r = self.game_service.ruleGet(ruleId)
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - rule/get")
            invalid_ruleUpdate = True
            if responses_list[-1]["points"] == "50" and responses_list[-1]["maxPoints"] == "50":
                if responses_list[-3]["points"] == "33" and responses_list[-3]["maxPoints"] == "33":
                    print("Pass - verification, points and maxPoints updated to 50")
                    invalid_ruleUpdate = False
            if invalid_ruleUpdate:
                print("Fail E2E step: " + str(step) + " invalid rule/get")
                testStatus = False
                return

            print("Info - rule/create: Confirmation 20")
            step += 1
            # ruleCreate(self, ruleType, gameObjectId, name, description="", status="disabled", points="", maxPoints="")
            r = self.game_service.ruleCreate("confirmation", lbId, "Confirmation 20",
                                             "20 confirmation All in 1 test", "enabled", "20", "20")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - Confirmation 20, created")
            #ruleId2 = responses_list[-1]["id"]

            print("Info - rule/create: confirmBonus 5 points, first 2 users")
            step += 1
            # ruleCreate(self, ruleType, gameObjectId, name, description="", status="disabled", points="", maxPoints="")
            r = self.game_service.ruleCreate("confirmBonus", lbId, "confirmBonus 5 to 2",
                "5 points confirmation Bonus to 2 users", "enabled", "5", "10")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - confirmBonus 5 points, first 2 users created")

            print("Info - rule/create: external")
            step += 1
            # ruleCreate(self, ruleType, gameObjectId, name, description="", status="disabled", points="", maxPoints="")
            r = self.game_service.ruleCreate("external", lbId, "first_external_rule",
                                             "External rule - first_external_rule", "enabled", "", "")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - external rule created")

            print("Info - rule/create: vod")
            step += 1
            # ruleCreate(self, ruleType, gameObjectId, name, description="", status="disabled", points="", maxPoints="")
            r = self.game_service.ruleCreate("vod", lbId, "Watch VOD entry",
                                             "5 points for each minute viewed on VOD entries, Max points is according to each entry's duration by minutes", "enabled", "5", "")
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - external rule created")

            #ruleId3 = responses_list[-1]["id"]
            print("------------------")
            print("Info - rule/list")
            step += 1

            r = self.game_service.ruleList(lbId)
            print(str(r.text))
            responses_list.insert(step, json.loads(str(r.text)))
            print("Pass - rule/list retrieved")
            print("Info - rule/list validate")
            step += 1
            if responses_list[-1]["totalCount"] == 5 and "Confirmation 50" in r.text and "Confirmation 20" in r.text and "confirmBonus 5" in r.text and "first_external_rule" in r.text and "Watch VOD entry" in r.text:
                print("Pass - rule/list all 5 rules validated")
            else:
                print("Fail E2E step: " + str(step) + " rule/list 5 rules NOT validated")
                testStatus = False
                return
            print("*** Pass all Rule Actions ***")
            print("------------------")

        except Exception as Exp:
                print("Fail E2E step: "+str(step))
                print(Exp)
                testStatus = False
                return

        try:
            print("Info - send confirmation events")
            import LeaderBoardFuncs
            step += 1
            userID_list = ["usr0", "usr1", "usr2", "usr3"] # "block1"
            for userID_str in userID_list:
                r = LeaderBoardFuncs.register_to_LB(self, userID_str, False)
                if r == False:
                    print("FAIL - confirmation " + userID_str)
                    testStatus = False
            print("Pass - confirmations sent to analytics")
            print("=== '/userScore/' actions ===")
            print("Info - userscore/get validate")
            step += 1
            time.sleep(3)
            r_first = self.game_service.userScoreGet(lbId, "usr0")
            first_dict = json.loads(str(r_first.text))
            if str(first_dict["score"]) == "75" and first_dict["id"]=="usr0" and str(first_dict["rank"])=="1":
                    print("Pass - confirmation and bonus rules score, id and rank validated")
            else:
                print("Fail E2E step: " + str(step) + " userscore/get validate")
                testStatus = False
            print("Info - userscore/list validate")
            step += 1
            validate_5of5 = 0

            r_list = self.game_service.userScoreList(lbId)
            list_dict = json.loads(str(r_list.text))
            if list_dict["totalCount"] == 4:
                print("Pass - totalCount = 4 as expected")
                validate_5of5 += 1
            else:
                # second chance if analytics is slow (happens)
                time.sleep(15)
                r_list = self.game_service.userScoreList(lbId)
                list_dict = json.loads(str(r_list.text))
                if list_dict["totalCount"] == 4:
                    print("Pass - totalCount = 4 as expected")
                    validate_5of5 += 1

            objects = list_dict["objects"]
            for obj in objects:
                if obj["id"] == "usr0":
                    if obj["score"] == 75 and obj["rank"] == 1:
                        validate_5of5 += 1
                if obj["id"] == "usr1":
                    if obj["score"] == 75 and obj["rank"] == 2:
                        validate_5of5 += 1
                if obj["id"] == "usr2":
                    if obj["score"] == 70 and obj["rank"] == 3:
                        validate_5of5 += 1
                if obj["id"] == "usr3" or obj["id"] == "usr3_was":
                    if obj["score"] == 70 and obj["rank"] == 4:
                        validate_5of5 += 1

            if validate_5of5 == 5:
                print("Pass - userscore/list: scores, ranks, puser ids, tie breakers are validated")
                print("*** Pass userScore Actions ***")
            else:
                print("Fail E2E step: " + str(step) + " userscore/list validate")
                print(str(r_list.text))
                testStatus = False

        except Exception as Exp:
            print("Fail E2E step: " + str(step))
            print(Exp)
            testStatus = False

        try:
            print("Info - leaderboard/delete")
            r = self.game_service.LBDelete(lbId)
            del_dict = json.loads(str(r.text))
            if r == False or del_dict["status"] == "enabled":
                print("Fail - leaderboard/delete")
                testStatus = False
            else:
                print("Pass - leaderboard/delete")
        except Exception as Exp:
            print("Fail - leaderboard/delete")
            print(Exp)
            testStatus = False

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):
        global testStatus
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '416', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '416', '1')
                assert False
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_4507_LB_A2Z_sanity.py', '-s'])
    # ===========================================================================




