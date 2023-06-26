# ===============================================================================================================
#  @Author: Zeev Shulman 04/04/2022
#
#  ****************** Test will need adjustment if rules change ******************
#
#  @description:
#       Validate  C&C upvote rule - '20 points to a comment with 5 upvotes by unique users.'
#       Validate limitations - '2 per user per entry. no self-upvote. unique users'
#
#       - C&C upvote a 'random' existing user using analytics API
#       - verify score and rank change following the upvote
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
            self.logi = reporter2.Reporter2('test_359_Leaderboard_Upvote')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.Leader_board = LeaderBoard.LeaderBoard("prod", "LB_usr1")

        except Exception as Exp:
            print(Exp)

    def test_359_Leaderboard_Upvote(self):
        global testStatus
        self.logi.initMsg('test_359_Leaderboard_Upvote')
        lbId = 5
        try:
            list_before = self.Leader_board.getLeaderBoardList(lbId, None, 1000)
            # rnd_unexluded_user(... 6) because the first 5 will do the up-voting
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects, 6)
            userID_str = list_before.objects[n].userId #"oded.berihon+zeev@kaltura.com"

            print("\nInfo - upvote self, should not add points")
            print("Before - " + userID_str + " rank:" +str(list_before.objects[n].rank) +", score:"+ str(list_before.objects[n].score))
            entryID = LeaderBoardFuncs.generate_rnd_entry()
            #entryID = "1_av6tf5f1"
            score_before = list_before.objects[n].score
            list_of_voters = [userID_str, list_before.objects[1].userId, list_before.objects[2].userId,
                              list_before.objects[3].userId, list_before.objects[4].userId]
            r = LeaderBoardFuncs.upvoteComment(self, userID_str, entryID, list_of_voters, False)
            if r == False:
                print("FAIL - upvoteComment()")
                testStatus = False
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            print("    score:" + str(list_after.objects[0].score))
            if score_before == list_after.objects[0].score:
                print("PASS")
            else:
                print("FAIL")
                testStatus = False

            print("Info - upvote same users, should not add points")
            list_of_voters[0] = list_before.objects[1].userId
            r = LeaderBoardFuncs.upvoteComment(self, userID_str, entryID, list_of_voters, False)
            if r == False:
                print("FAIL - upvoteComment()")
                testStatus = False
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            print("    score:" + str(list_after.objects[0].score))
            if score_before == list_after.objects[0].score:
                print("PASS")
            else:
                print("FAIL")
                testStatus = False

            print("Info - upvote 5 unique users should add 20*points, *3 comments with max 2 limitation = +40 score")
            list_of_voters[0] = list_before.objects[5].userId
            r = LeaderBoardFuncs.upvoteComment(self, userID_str, entryID, list_of_voters, True)
            if r == False:
                print("FAIL - upvoteComment()")
                testStatus = False
            time.sleep(10)
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            print("After  - " + list_after.objects[0].userId + " rank:" + str(list_after.objects[0].rank) + ", score:" + str(list_after.objects[0].score))
            if score_before+40 == list_after.objects[0].score:
                print("PASS - 40 added to user's score")
            else:
                print("FAIL")
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
                self.practitest.post(Practi_TestSet_ID, '359', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '359', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_359_Leaderboard_Upvote.py', '-s'])
    # ===========================================================================