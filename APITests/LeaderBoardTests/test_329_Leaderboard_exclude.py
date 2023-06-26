# ===============================================================================================================
#  @Author: Zeev Shulman 17/05/2022
#
#
#  @description: Dynamic group exclude
#       1) random user gets added to excluded list
#       2) user gets C&C upvote - gets NO points
#       3) user gets removed from excluded group
#       4) user gets C&C upvote - DOES get points
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
            #pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('===== PRODUCTION ENVIRONMENT =====')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
                self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
                self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
                self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
                self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')

            else:
                section = "Testing"
                self.env = 'testing'
                print('===== TESTING ENVIRONMENT =====')

            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.practitest = Practitest.practitest('17888')
            self.logi = reporter2.Reporter2('test_329_Leaderboard_exclude')
            self.Leader_board = LeaderBoard.LeaderBoard(self.env, "LB_usr1")

        except Exception as Exp:
            print(Exp)

    def test_329_Leaderboard_exclude(self):
        global testStatus
        self.logi.initMsg('test_329_Leaderboard_exclude')
        try:
            print("-------------- exclude and upvote NO points --------------")
            lbId = 5
            excluded_group = "LBexclude"
            list_before = self.Leader_board.getLeaderBoardList(lbId, None, 1000)
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects, 6)
            userID_str = list_before.objects[n].userId
            entryID = LeaderBoardFuncs.generate_rnd_entry()

            print("Before - " + userID_str + " rank:" + str(list_before.objects[n].rank) + ", score:" + str(
                list_before.objects[n].score))

            score_before = list_before.objects[n].score
            list_of_voters = [list_before.objects[5].userId, list_before.objects[1].userId, list_before.objects[2].userId,
                              list_before.objects[3].userId, list_before.objects[4].userId]

            print("Info - add user " + userID_str + " to excluded group: " + excluded_group)
            self.Leader_board.addUserToGroup(userID_str, excluded_group)  # addUserToGroup(self,userId, groupId):
            time.sleep(15)
            r = LeaderBoardFuncs.upvoteComment(self, userID_str, entryID, list_of_voters, True)
            excluded_users = []
            exc_user_list = self.Leader_board.retGroupUserList(excluded_group)
            for i in range(0, len(exc_user_list.objects)):
                excluded_users.append(exc_user_list.objects[i].userId)
            print(exc_user_list)
            if userID_str in excluded_users:
                print("PASS - user was excluded")
            else:
                print("FAIL - to exclude user")
                testStatus = False
                return

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

            print("-------------- remove exclude and upvote GET points --------------")
            self.Leader_board.removeUserFromeGroup(userID_str, excluded_group)
            time.sleep(30)
            r = LeaderBoardFuncs.upvoteComment(self, userID_str, entryID, list_of_voters, False)
            time.sleep(5)
            if r == False:
                print("FAIL - upvoteComment()")
                testStatus = False
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            print("    score:" + str(list_after.objects[0].score))
            if score_before != list_after.objects[0].score:
                print("PASS")
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
                self.practitest.post(Practi_TestSet_ID, '329', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '329', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_329_Leaderboard_exclude.py', '-s'])
    # ===========================================================================