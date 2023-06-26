# ===============================================================================================================
#  @Author: Zeev Shulman 15/05/2022
#
#  ****************** Test will need adjustment if rules change ******************
#
#  @description:
#       Validate Quiz rule - 'Points based on first quiz scoring (per quiz); Entry in category __optional/254757933'
#       Validate Quiz Bonus - '20 points for first 50 users to complete a quiz (per quiz); Entry in category __optional'
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
#import reporter2
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
        global testStatus
        try:

            if isProd:
                section = "Production"
                self.env = 'prod'
                print('===== PRODUCTION ENVIRONMENT =====')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))

                self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
                self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
                self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
                self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
                self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')

            else:
                section = "Testing"
                self.env = 'testing'
                print('===== TESTING ENVIRONMENT =====')

            if Run_locally:
                self.FileName = inifile.RetIniVal('Entry', 'File')
            else:
                #fix Jenkins/Adi using KMC vs API path
                self.FileName = 'red-green-blue.mp4'

            path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
            self.FileName = os.path.join(path, self.FileName)
            print("SETUP - Upload new Entry with category '__lbQuiz' file: " + str(self.FileName))
            self.entryID = LeaderBoardFuncs.create_new_entry(self, self.FileName, "__optional,__lbQuiz")
            if self.entryID == False:
                print("Fail - failed Upload new Entry")
                testStatus = False

            self.practitest = Practitest.practitest('17888')
            #self.logi = reporter2.Reporter2('test_418_Leaderboard_Quiz_only_category')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.Leader_board = LeaderBoard.LeaderBoard("prod", "LB_usr1")

        except Exception as Exp:
            print(Exp)

    def test_418_Leaderboard_Quiz_only_category(self):
        global testStatus
        #self.logi.initMsg('test_418_Leaderboard_Quiz_only_category')
        try:
            # used for validation, change if rule changes
            lbId = 5
            quiz_bonus = 20
            points_add = 31

            print("-------------- Quiz Not '__lbQuiz' = No points--------------")
            print("Info - select random user, rnd Entry, submit Quiz")
            lbId = 5
            list_before = self.Leader_board.getLeaderBoardList(lbId, None, 1000)
            n = LeaderBoardFuncs.rnd_unexluded_user(self, list_before.objects)
            userID_str = list_before.objects[n].userId
            print("Before - " + userID_str + " rank:" + str(list_before.objects[n].rank) + ", score:" + str(
                list_before.objects[n].score))
            entryID = LeaderBoardFuncs.generate_rnd_entry()
            r = LeaderBoardFuncs.quizPoints(self, userID_str, entryID, points_add)
            if r == False:
                print("FAIL - quizPoints")
                testStatus = False
            list_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            print("After  - " + list_after.objects[0].userId + " rank:" + str(
                list_after.objects[0].rank) + ", score:" + str(list_after.objects[0].score))
            if list_after.objects[0].score == list_before.objects[n].score:
                print("PASS - Quiz not in '__lbQuiz' gets no points")
            else:
                print("FAIL - Quiz not in '__lbQuiz' Got points")
                testStatus = False

            print("-------------- Quiz in '__lbQuiz' --------------")
            # Assuming 60 users already exist, and less then 10 of the top 60 are excluded
            for i in range(0, 60):
                userID_str = list_before.objects[i].userId
                r = LeaderBoardFuncs.quizPoints(self, userID_str, self.entryID, points_add)
                if r == False:
                    print("FAIL - quizPoints() "+userID_str)
                    testStatus = False

            bonus_counter = 0
            excluded_counter = 0
            no_bonus_counter = 0
            #list_after = self.Leader_board.getLeaderBoardList(4, None, 1000)
            time.sleep(10)
            for j in range(0, 60):
                list_after = self.Leader_board.getLeaderBoardList(lbId, list_before.objects[j].userId)
                if list_before.objects[j].score + points_add + quiz_bonus == list_after.objects[0].score:
                    # quiz and bonus added
                    bonus_counter += 1
                elif list_before.objects[j].score + points_add == list_after.objects[0].score:
                    # quiz added NO bonus
                    if bonus_counter != 50:
                        print("Hmmm, bonus_counter should be 50 before users get no bonus. This time: " + str(bonus_counter))
                    no_bonus_counter += 1
                elif list_before.objects[j].score == list_after.objects[0].score:
                    excluded_counter += 1
                    ########## was for lbId = 4 ##########
                    print(list_before.objects[j].userId+ "----------")
                    if LeaderBoardFuncs.is_excluded(self, list_before.objects[j].userId):
                        print("Excluded: " + list_before.objects[j].userId )
                    else:
                        print("suspected excluded not in 'LBexclude': " + list_before.objects[j].userId)
                else:
                    print("Fail - whoa what happened to the points ?")
                    print("Before - " + str(list_before.objects[j].userId) + " rank:" + str(list_before.objects[j].rank) + ", score:" + str(
                                    list_before.objects[j].score))
                    print("after - " + str(list_after.objects[0].userId) + " rank:" + str(list_after.objects[0].rank) + ", score:" + str(list_after.objects[0].score))
                    print("======================")

            print("Num of users that got bonus: " + str(bonus_counter))
            print("Num of NO bonus users: " + str(no_bonus_counter))
            print("Num of excluded: " + str(excluded_counter))

            if (bonus_counter+no_bonus_counter+excluded_counter) == 60 and bonus_counter == 50:
                print("Out of 60 users: 'first 50' got bonus, rest got quiz score, excluded got nothing")
                print("PASS")
            else:
                print("FAIL")
                testStatus = False

            # try:
            #     r = LeaderBoardFuncs.delete_entry(self, self.entryID)
            # except Exception as Exp:
            #     print(Exp)

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
            r = LeaderBoardFuncs.delete_entry(self, self.entryID)
        except Exception as Exp:
            print(Exp)
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '418', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '418', '1')
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_418_Leaderboard_Quiz_only_category.py', '-s'])
    # ===========================================================================
