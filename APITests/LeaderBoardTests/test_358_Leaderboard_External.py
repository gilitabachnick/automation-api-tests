# ===============================================================================================================
#  @Author: Zeev Shulman 11/04/2022
#
#  ****************** Test will need adjustment if rules change ******************
#
#  @description:
#       Validate external rules -
#
#
#
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

import LeaderBoard
import LeaderBoardFuncs
import reporter2
import Config
import Practitest

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

            if isProd:
                section = "Production"
                self.env = 'prod'
                print('===== PRODUCTION ENVIRONMENT =====')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))

                self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
                self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
                self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
                self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
            else:
                section = "Testing"
                self.env = 'testing'
                print('===== TESTING ENVIRONMENT =====')

            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.practitest = Practitest.practitest('17888')
            self.logi = reporter2.Reporter2('test_358_Leaderboard_External')
            self.Leader_board = LeaderBoard.LeaderBoard("prod", "LB_usr1")

            self.excluded_users = []
            exc_user_list = self.Leader_board.retGroupUserList("LBexclude")
            for i in range(0, len(exc_user_list.objects)):
                self.excluded_users.append(exc_user_list.objects[i].userId)

        except Exception as Exp:
            print(Exp)

    def test_358_Leaderboard_External(self):
        global testStatus
        self.logi.initMsg('test_358_Leaderboard_External')
        external_rules = ["Bonus_Quiz_Score", "Schedule_training", "Bonus_Schedule_Training_Score",
                          "Conduct_Training_Score",
                          "Bonus_Conduct_Training_Score", "Additional_Score"]

        try:
            print("----------------------------------------")
            print("INFO - Random un-excluded user external rules Schedule_training, 'delta' then 'upsert'")
            list_before = self.Leader_board.getLeaderBoardList(4, None, 1000)
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects)
            userID_str = list_before.objects[n].userId
            points_add = 100
            points_add2 = 10

            print("Before - " + userID_str + " rank:" + str(list_before.objects[n].rank) + ", score:" + str(
                list_before.objects[n].score))
            r = LeaderBoardFuncs.externalRule(self, userID_str, str(points_add), external_rules[1])
            if r == False:
                print("FAIL - externalRule()")
                testStatus = False
            time.sleep(10)
            delta_after = self.Leader_board.getLeaderBoardList(4, userID_str)
            print("After delta - " + delta_after.objects[0].userId + " rank:" + str(
                delta_after.objects[0].rank) + ", score:" + str(delta_after.objects[0].score))
            if delta_after.objects[0].score == list_before.objects[n].score+points_add:
                print("PASS - delta\n")
            else:
                print("FAIL\n")
                testStatus = False

            r = LeaderBoardFuncs.externalRule(self, userID_str, str(points_add2), external_rules[1], "upsert")
            if r == False:
                print("FAIL - externalRule()")
                testStatus = False
            time.sleep(10)
            upsert_after = self.Leader_board.getLeaderBoardList(4, userID_str)
            print("After upsert - " + upsert_after.objects[0].userId + " rank:" + str(
                upsert_after.objects[0].rank) + ", score:" + str(upsert_after.objects[0].score))
            if upsert_after.objects[0].score <= delta_after.objects[0].score-(points_add - points_add2):
                print("PASS - upsert\n")
            else:
                print("FAIL\n")
                testStatus = False

            # if list of external rule names changes, external_rules[] need to be updated & expected score as well
            print("INFO - Random un-excluded user multi external rules 'delta'. Currently 2 rules in the list are defined ")
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects)
            userID_str = list_before.objects[n].userId
            action_type = "delta"  # "upsert"
            points_add3 = 20
            multi_before = self.Leader_board.getLeaderBoardList(4, userID_str)
            print("Before - " + userID_str + " rank:" + str(multi_before.objects[0].rank) + ", score:" + str(
                multi_before.objects[0].score))
            for rul in external_rules:
                r = LeaderBoardFuncs.externalRule(self, userID_str, str(points_add3), rul, action_type)
                if r == False:
                    print("FAIL - externalRule()")
                    testStatus = False
            time.sleep(10)
            multi_after = self.Leader_board.getLeaderBoardList(4, userID_str)
            print("After upsert - " + multi_after.objects[0].userId + " rank:" + str(
                multi_after.objects[0].rank) + ", score:" + str(multi_after.objects[0].score))
            if multi_after.objects[0].score == multi_before.objects[0].score+2*points_add3:
                print("PASS -  multi external rules\n")
            else:
                print("FAIL\n")
                testStatus = False

        except Exception as Exp:
            print(Exp)
            print("FAIL - external rules delta_upsert")
            testStatus = False
            return

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus
        print("")
        print("---------- Teardown ---------")
        # action:delete excluded users or adjust the test to prevent false FAILs when excluded users rand selected
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '358', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '358', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_358_Leaderboard_External.py', '-s'])
    # ===========================================================================
