# ===============================================================================================================
#  @Author: Zeev Shulman 04/04/2022
#
#  @description:
#       Validate tie breaker rule - first user to get same score gets higher rank:
#       - choose a random user (not ranked 1)
#       - if distance from higher rank < 30 score make it 30 (up to 10 quiz point + 20 bonus)
#       - add qiz points to chosen user so that [n].score = [n-1].score
#       - verify the chosen user, that got the score latter, has a lower rank
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

            self.practitest = Practitest.practitest('17888')
            self.logi = reporter2.Reporter2('test_349_Leaderboard_tiebreak')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.Leader_board = LeaderBoard.LeaderBoard("prod", "LB_usr1")

        except Exception as Exp:
            print(Exp)

    def test_349_Leaderboard_tiebreak(self):
        global testStatus
        self.logi.initMsg('test_349_Leaderboard_tiebreak')
        # tie break for lbId 5 will be complex, will require new entry for quiz
        lbId = 4
        try:
            print("\nInfo - choose random user[n] where users[n, n-1] are not in the excluded group")
            list_before = self.Leader_board.getLeaderBoardList(lbId, None, 1000)
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects, 2)
            while LeaderBoardFuncs.is_excluded(self, list_before.objects[n-1].userId):
            #while LeaderBoardFuncs.is_excluded(self, "LB_usr15"):
                print("Info - user[n-1] " + list_before.objects[n-1].userId + " is excluded, choose another")
                n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects, 2)
            userID_str = list_before.objects[n].userId  # "oded.berihon+zeev@kaltura.com"
            hi_userID_str = list_before.objects[n-1].userId


            entryID = LeaderBoardFuncs.generate_rnd_entry()
            points_add = list_before.objects[n - 1].score - list_before.objects[n].score - 20

            print("Info - Tie break: add points to user[n] to equal user[n-1], a higher ranked user")
            print("Before - " + hi_userID_str + " rank:" + str(
                list_before.objects[n - 1].rank) + ", score:" + str(list_before.objects[n - 1].score))
            print("Before - " + userID_str + " rank:" + str(list_before.objects[n].rank) + ", score:" + str(
                list_before.objects[n].score))
            print("--------------------------------------")
            if list_before.objects[n - 1].score < list_before.objects[n].score + 30:
                print("not enough delta to add quiz result to equalize n, n-1 score: add 30 to user[n-1] first")
                r = LeaderBoardFuncs.quizPoints(self, hi_userID_str, entryID, 10)
                if r == False:
                    print("FAIL - quizPoints() ")
                    testStatus = False
                points_add += 30
                time.sleep(10)

            r = LeaderBoardFuncs.quizPoints(self, userID_str, entryID, points_add)
            if r == False:
                print("FAIL - quizPoints() ")
                testStatus = False
            time.sleep(10)
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            hi_after = self.Leader_board.getLeaderBoardList(lbId, hi_userID_str)
            print("After - " + hi_after.objects[0].userId + " rank:" + str(hi_after.objects[0].rank) + ", score:" + str(
                hi_after.objects[0].score))
            print("After - " + list_after.objects[0].userId + " rank:" + str(
                list_after.objects[0].rank) + ", score:" + str(list_after.objects[0].score))
            print("--------------------------------------")
            tie_break = False
            if (list_before.objects[n].score < list_after.objects[0].score):
                print("Pass - score was changed")
                if (hi_after.objects[0].score == list_after.objects[0].score):
                    print("Pass - score was made equal, time to check tie breaker")
                    if (hi_after.objects[0].rank < list_after.objects[0].rank):
                        print("Pass - First user of the 2 to get the score kept the higher rank")
                        tie_break = True

            if tie_break == False:
                print("FAIL -  failed to validate tie break")
                testStatus = False

        except Exception as Exp:
            print(Exp)
            print("FAIL -  failed to validate tie break")
            testStatus = False

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
                self.practitest.post(Practi_TestSet_ID, '349', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '349', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_349_Leaderboard_tiebreak.py', '-s'])
    # ===========================================================================
