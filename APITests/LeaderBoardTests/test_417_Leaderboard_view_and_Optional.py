# ===============================================================================================================
#  @Author: Zeev Shulman 16/05/2022
#
#  ****************** Test will need adjustment if rules change ******************
#
#  @description:
#       Validate view rule - '5 points per minute'
#       Validate Exhaust limitation - 'max points = 5*[(entry duration)/60]'
#       Validate Excluded users get no points
#
#  The test takes ~ 5 min
#
# ===============================================================================================================

import os
import sys
import random

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
                self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')

            else:
                section = "Testing"
                self.env = 'testing'
                print('===== TESTING ENVIRONMENT =====')

            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.practitest = Practitest.practitest('17888')
            self.logi = reporter2.Reporter2('test_417_Leaderboard_view_and_Optional')
            self.Leader_board = LeaderBoard.LeaderBoard(self.env, "LB_usr1")

            self.excluded_users = []
            exc_user_list = self.Leader_board.retGroupUserList("LBexclude")
            for i in range(0, len(exc_user_list.objects)):
                self.excluded_users.append(exc_user_list.objects[i].userId)

        except Exception as Exp:
            print(Exp)

    def test_417_Leaderboard_view_and_Optional(self):
        global testStatus
        self.logi.initMsg('test_417_Leaderboard_view_and_Optional')
        try:
            print("-------------- View Normal --------------")
            print("Info - select random user, view 1 min of a very long entry, get 5 points")
            lbId = 5
            list_before = self.Leader_board.getLeaderBoardList(lbId, None, 1000)
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects)
            userID_str = list_before.objects[n].userId #"LB_usr89"

            print("Before - " + userID_str + " rank:" + str(list_before.objects[n].rank) + ", score:" + str(
                list_before.objects[n].score))
            r = LeaderBoardFuncs.playEntry(self, userID_str, "1_av8kzatt", 60)
            # fake entry test = Leader --------- BoardFuncs.playEntry(self, userID_str, "1_a123z4tt", 60)
            if r == False:
                print("FAIL - playEntry")
                testStatus = False
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            print("After  - " + list_after.objects[0].userId + " rank:" + str(
                list_after.objects[0].rank) + ", score:" + str(list_after.objects[0].score))
            if list_after.objects[0].score == list_before.objects[n].score+5:
                print("PASS")
            else:
                print("FAIL")
                testStatus = False


            print("-------------- __optional category entry --------------")
            print("Info - view 1 min of __optional, get NO points")
            optional_before = list_after
            # 1_0329m2kp is long un exhausted Entry that would give points if not __optional category rule
            r = LeaderBoardFuncs.playEntry(self, userID_str, "1_0329m2kp", 60)
            if r == False:
                print("FAIL - playEntry")
                testStatus = False
            optional_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            if len(optional_after.objects) != 0:
                print("After  - " + userID_str + " rank:" + str(optional_after.objects[0].rank) + ", score:" + str(
                    optional_after.objects[0].score))
                if optional_after.objects[0].score == optional_before.objects[0].score:
                    print("PASS")
                else:
                    print("FAIL")
                    testStatus = False

            print("-------------- EXHAUSTED entry --------------")
            exhausted_usr = "LB_usr40"
            exhausted_entry = "1_gef3vzso"
            print("Info -  user " + exhausted_usr+", view 1 min of previewed EXHAUSTED entry " + exhausted_entry + ", get NO points")

            exhausted_usr_before = self.Leader_board.getLeaderBoardList(lbId, exhausted_usr)
            print("Before - " + exhausted_usr + " rank:" + str(exhausted_usr_before.objects[0].rank) + ", score:" + str(
                exhausted_usr_before.objects[0].score))
            r = LeaderBoardFuncs.playEntry(self, exhausted_usr, exhausted_entry, 60)
            if r == False:
                print("FAIL - playEntry")
                testStatus = False
            exhausted_usr_after = self.Leader_board.getLeaderBoardList(lbId, exhausted_usr)
            print("After  - " + exhausted_usr_after.objects[0].userId + " rank:" + str(
                exhausted_usr_after.objects[0].rank) + ", score:" + str(exhausted_usr_after.objects[0].score))
            if exhausted_usr_after.objects[0].score == exhausted_usr_before.objects[0].score:
                print("PASS")
            else:
                print("FAIL")
                testStatus = False

            print("-------------- EXCLUDED user --------------")
            print("Info - select random EXCLUDED user, view 1 min of a very long entry, get NO points")
            m = random.randint(0, len(self.excluded_users) - 1)
            userID_str = self.excluded_users[m]
            excluded_before = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            # if userID_str is excluded and DELETED excluded_before will be empty: i.e. [0] is 'list out of range'
            if len(excluded_before.objects) != 0:
                print("Before - " + userID_str + " rank:" + str(excluded_before.objects[0].rank) + ", score:" + str(excluded_before.objects[0].score))
            r = LeaderBoardFuncs.playEntry(self, userID_str, "1_av8kzatt", 60)
            if r == False:
                print("FAIL - playEntry")
                testStatus = False
            excluded_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            if len(excluded_after.objects) != 0:
                print("After  - " + userID_str + " rank:" + str(excluded_after.objects[0].rank) + ", score:" + str(excluded_after.objects[0].score))
                if excluded_after.objects[0].score == excluded_before.objects[0].score:
                    print("PASS")
                else:
                    print("FAIL")
                    testStatus = False
            else:
                print("PASS")

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
        # action:delete excluded users or adjust the test to prevent false FAILs when excluded users rand selected
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '417', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '417', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_417_Leaderboard_view_and_Optional.py', '-s'])
    # ===========================================================================