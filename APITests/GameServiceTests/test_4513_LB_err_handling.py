# ===============================================================================================================
#  @Author: Zeev Shulman 06/12/2022
#
#  @description:
#       - schedule past, current and future leaderboards.
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
                self.lbId = '' ### need to create LB with status: schedualed
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
            self.logi = reporter2.Reporter2('test_4513_LB_err_handling')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)
        except Exception as Exp:
            print(Exp)

    def test_4513_LB_err_handling(self):
        #add wrong ks test?
        global testStatus

        data_LBcreate = [
             {'name': 'err handling', 'description': '', 'status': 'disabled', 'participationPolicy': {'userDefaultPolicy': 'display', 'policies': [{'policy': 'do_not_display', 'matchCriteria': 'byGroup','values': ['bla']}]}},
             {'name': '', 'description': '', 'status': 'disabled', 'participationPolicy': {'userDefaultPolicy': 'display', 'policies': []}},
             {'name': 'B', 'description': '', 'status': None,
              'participationPolicy': {'userDefaultPolicy': 'display', 'policies': []}},
             {'name': 'C', 'description': '', 'status': 'scheduled',
              'participationPolicy': {'userDefaultPolicy': '', 'policies': []}},
             {"name": "string", "description": "string", "status": "disabled", "participationPolicy": {
                "userDefaultPolicy": "display",
                "policies": [{"policy": "do_not_display", "matchCriteria": "byGod", "values": ["blag"]}]}}
            ]

        expected_LBcreate = [
            #'{"statusCode":400,"message":["participationPolicy.policies.0.groupsIds must be an array","participationPolicy.policies.0.groupsIds should not be empty","participationPolicy.policies.0.each value in groupsIds must be a string","participationPolicy.policies.0.each value in groupsIds should not be empty"],"error":"Bad Request"}',
            '{"statusCode":404,"message":"Failed to find the Groups of Participation Policy with the policy',
            '{"statusCode":400,"message":["name should not be empty"],"error":"Bad Request"}',
            '{"statusCode":400,"message":["status must be a valid enum value"],"error":"Bad Request"}',
            '{"statusCode":400,"message":["status scheduled should have startDate and endDate","participationPolicy.userDefaultPolicy must be a valid enum value"],"error":"Bad Request"}',
            #'{"statusCode":400,"message":["participationPolicy.policies.0.groupsIds must be an array","participationPolicy.policies.0.groupsIds should not be empty","participationPolicy.policies.0.each value in groupsIds must be a string","participationPolicy.policies.0.each value in groupsIds should not be empty"],"error":"Bad Request"}'
            '{"statusCode":400,"message":["participationPolicy.policies.0.matchCriteria must be a valid enum value"]'
        ]
        data_LBget = {"id": "wrongid"}
        expected_LBget = '{"statusCode":400,"message":["id must be a valid id"],"error":"Bad Request"}'

        try:
            #r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
            print("Info - leaderboard/create errs")
            counter = 0
            for j in data_LBcreate:
                r = self.game_service.errHandler(j,"leaderboard/create")
                if expected_LBcreate[counter] in r:
                    print("pass: " + r)
                else:
                    print(r)
                    print(expected_LBcreate[counter])
                    print("Fail - leaderboard/create errs")
                    testStatus = False
                    #return
                counter += 1
            print("Info - leaderboard/get errs")
            r = self.game_service.errHandler(data_LBget,"leaderboard/get")
            if expected_LBget in r:
                print("pass: " + r)
            else:
                print(r)
                print("Fail - leaderboard/get errs")
                testStatus = False
                # return

        except Exception as Exp:
            print(Exp)
            print(r)
            print("Fail - leaderboard/create errs")
            testStatus = False
            return


        data_LBupdate = [{"id": "wrongid","status": "disabled"},
                         {"id": "63637fcd873c130bdb607cdc",'participationPolicy': {'userDefaultPolicy': 'display', 'policies': [{'policy': 'do_not_display', 'matchCriteria': 'byGroup','values': ['bla']}]}}
                         ]
        expected_LBupdate = ['{"statusCode":400,"message":["id must be a valid id"],"error":"Bad Request"}',
                             #'{"statusCode":400,"message":["participationPolicy.policies.0.groupsIds must be an array","participationPolicy.policies.0.groupsIds should not be empty","participationPolicy.policies.0.each value in groupsIds must be a string","participationPolicy.policies.0.each value in groupsIds should not be empty"],"error":"Bad Request"}'
                             '{"statusCode":404,"message":"Failed to find the Groups of Participation Policy with the policy'
                            ]
        try:
            print("Info - leaderboard/update errs")
            counter = 0
            for j in data_LBupdate:
                r = self.game_service.errHandler(j,"leaderboard/update")
                if expected_LBupdate[counter] in r:
                    print("pass: " + r)
                else:
                    print(r)
                    print("Fail - leaderboard/update errs")
                    testStatus = False
                    #return
                counter += 1


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
        #r = self.game_service.LBUpdate(self.lbId, "", "", "disabled")
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
        pytest.main(args=['test_4513_LB_err_handling.py', '-s'])
    # ===========================================================================
