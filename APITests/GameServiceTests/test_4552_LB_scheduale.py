# ===============================================================================================================
#  @Author: Zeev Shulman 06/12/2022
#
#  @description:
#       - schedule past, current and future leaderboards
#       - send analytics score events (quiz)
#       - validate only current leaderboard users got points
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
                self.lbId = '6396e824f9b2d0da5d8be9e5' ### need to create LB with status: schedualed
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
                self.lbId = '638da849b4e8dc7d9c2b6a7f' # status: schedualed
                #self.lbId_id_list = ['63888910b4e8dc7d9c2af3b8', '6388aa9ab4e8dc7d9c2af724', '6388ab58b4e8dc7d9c2af744']

            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
            self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
            self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
            self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
            self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
            self.url = inifile.RetIniVal('Environment', 'KMC_URL')
            self.logi = reporter2.Reporter2('test_4552_LB_scheduale')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)
        except Exception as Exp:
            print(Exp)

    def test_4552_LB_scheduale(self):
        global testStatus

        points_add = 25
        list_scores_response = []
        past_dates = ["2021-12-05T10:42:00.000Z","2022-12-05T10:50:00.000Z"]
        current_dates = ["2022-12-05T00:50:00.000Z","2030-12-05T10:50:00.000Z"]
        future_dates = ["2030-12-06T00:50:00.000Z","2031-12-05T10:50:00.000Z"]
        userID_list = ["usr10", "usr11", "usr12", "usr13", "usr14"]  # ['update1','update2','update3','usr3_was','usr0']
        leaderboard_dates = [past_dates,current_dates,future_dates]

        try:
            list_scores_response.append(self.game_service.userScoreList(self.lbId))
        except Exception as Exp:
            print(Exp)
            print("Fail - userScore/List")
            testStatus = False
            return
        try:
            for start_end in leaderboard_dates:
                print("Info - update leaderboard schedule")
                r = self.game_service.LBUpdate(self.lbId, status="scheduled", startDate=start_end[0], endDate=start_end[1])
                time.sleep(1)
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
                    print("FAIL - quizPoints")
                    testStatus = False
                    return
                time.sleep(1)
                list_scores_response.append(self.game_service.userScoreList(self.lbId))
            print("Info - validate scores")

            # for i in range(len(list_scores_response)):
            #     print(str(list_scores_response[i].text))
            if list_scores_response[0].text == list_scores_response[1].text and \
                    list_scores_response[1].text != list_scores_response[2].text and\
                        list_scores_response[2].text == list_scores_response[3].text:
                print("Pass - validate scores")
                print(str(list_scores_response[0].text))
                print(str(list_scores_response[2].text))
            else:
                print("FAIL - validate scores")
                testStatus = False
                print(list_scores_response)
                print(str(list_scores_response[0].text))
                print(str(list_scores_response[1].text))
                print(str(list_scores_response[2].text))
                print(str(list_scores_response[3].text))
            print("-------------")

        except Exception as Exp:
            print(Exp)
            print("FAIL - update/compare")
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
        pytest.main(args=['test_4552_LB_scheduale.py', '-s'])
    # ===========================================================================
