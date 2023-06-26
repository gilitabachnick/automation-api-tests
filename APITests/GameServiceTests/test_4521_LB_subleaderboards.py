# ===============================================================================================================
#  @Author: Zeev Shulman 24/11/2022
#
#  @description:
#       - open a leaderboard with sub-leaderboards
#       - use userScore/getSubGameOptions to get the options
#       - use userScore/list with subGameProperties
#       - validate the results
#           example:  "subGameProperties": { "id": 2, "option": "SPAIN_HR"}
#           returns users with user.country: spain, user.title: HR and no-one else
#
#
# ===============================================================================================================

import os
import sys
import json

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)
# ========================================================================
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
                self.lbId = "6370e5c914ef1fc7f7395818"
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
                self.lbId = '638621c7b4e8dc7d9c2aa6e0' #"6385d742b4e8dc7d9c2a96a3"  # prod '6370e5c914ef1fc7f7395818'
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

            # self.practitest = Practitest.practitest('17888')
        except Exception as Exp:
            print(Exp)

    def test_4521_LB_subleaderboards(self):
        global testStatus
        try:
            print("-- test_4521_LB_subleaderboards --")
            # Partner_ID = '4800142'
            #lbId = "6370e5c914ef1fc7f7395818" #"636cc237befd23a4a151970d"
            expected_spain_users = "usr19,usr28,usr21,usr24,usr26,usr29,usr22,usr25,usr27,usr23,usr30,usr20"
            expected_HR_users = "usr28,usr29,usr26,usr27,usr30"
            expected_spain_HR_users = "usr28,usr29,usr26,usr27,usr30"
            expected_options_sets = ['"UK","USA","SPAIN","UNKNOWN","UAE"]',
                '["DOORMAN","HR","UNKNOWN","DEV","CEO","QA"]',
                '["UAE_QA","UNKNOWN_UNKNOWN","SPAIN_DOORMAN","UK_QA","UAE_DEV","USA_DOORMAN","SPAIN_HR","SPAIN_DEV","USA_CEO","UK_DOORMAN","UAE_DOORMAN"]']
            # -----------------------------
            r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
            print("Info - get SubGameOptions")
            verify3 = 0
            for i in range(0, 3):
                r = self.game_service.userScoregetSubGameOptions(self.lbId, subGameId=i)
                if r.status_code == 200:
                    if expected_options_sets[i] in str(r.text):
                        print("sub leaderboard " + str(i) + " options found: " + expected_options_sets[i])
                        verify3 += 1
            if verify3 == 3: print("Pass - get SubGameOptions")
            print("Info - compare sub filters - spain, HR & spain_HR - to expected users lists")
            sub_list0 = self.game_service.userScoreList(self.lbId,subGameid=0, option="SPAIN")
            spain_objects = json.loads(str(sub_list0.text))["objects"]
            sub_list1 = self.game_service.userScoreList(self.lbId, subGameid=1, option="HR")
            HR_objects = json.loads(str(sub_list1.text))["objects"]
            sub_list2 = self.game_service.userScoreList(self.lbId, subGameid=2, option="SPAIN_HR")
            spain_HR_objects = json.loads(str(sub_list2.text))["objects"]
            if len(spain_objects)==0 or len(HR_objects)==0 or len(spain_HR_objects)==0:
                print("Fail - empty subleaderboard")
                print(str(spain_objects))
                print(str(HR_objects))
                print(str(spain_HR_objects))
                testStatus = False
                return

            for obj in spain_objects:
                if obj["id"] in expected_spain_users:
                    pass
                else:
                    testStatus = False
                    print("Fail - expected_spain_users validation")
                    print(str(spain_objects))
            for obj in HR_objects:
                if obj["id"] in expected_HR_users:
                    pass
                else:
                    testStatus = False
                    print("Fail - expected_HR_users validation")
                    print(str(HR_objects))
            for obj in spain_HR_objects:
                if obj["id"] in expected_spain_HR_users:
                    pass
                else:
                    testStatus = False
                    print("Fail - expected_spain_HR_users validation")
                    print(str(spain_HR_objects))

            if testStatus:
                print(str(spain_objects))
                print(str(HR_objects))
                print(str(spain_HR_objects))
                print("Pass - users in the 3 sub filters are identical to the expected users lists")

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
        r = self.game_service.LBUpdate(self.lbId, "", "", "disabled")
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
        pytest.main(args=['test_4521_LB_subleaderboards.py', '-s'])
    # ===========================================================================