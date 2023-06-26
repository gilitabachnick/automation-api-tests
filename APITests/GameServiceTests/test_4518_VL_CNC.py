# ===============================================================================================================
#  @Author: Zeev Shulman 29/08/2022
#
#  ****************** load *k events ******************
#
#  @description:
#       - send X*K events/second to analytics (1,000 a second and higher)
#       - record the time it took to send the events
#       - Validate score/rank change appropriately
#       - record the time it took to get an accurate report
#
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
import LeaderBoardFuncs
import LeaderBoardService
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
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            self.practitest = Practitest.practitest('4586', 'APITests')
            if isProd:
                print('===== PRODUCTION ENVIRONMENT =====')
                self.lbId = '636cc237befd23a4a151970d'
            else:
                print("Info - this test doesnt run on QA, only STG with prod params")
                print('===== STG ENVIRONMENT =====')
                self.lbId = '6388bc18b4e8dc7d9c2af8cb'
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
            self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
            self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
            self.admin_secret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
            self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
            self.url = inifile.RetIniVal('Environment', 'KMC_URL')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)
        except Exception as Exp:
            print(Exp)

    def test_4518_VL_CNC(self):
        global testStatus
        try:
            r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
            print("Pass - CNC events sent")
            points_add = 30
            entry = LeaderBoardFuncs.generate_rnd_entry()#'1_s4acvgzg'
            # get userScoreList baseline score for validation
            list_before = self.game_service.userScoreList(self.lbId, pageSize="20")
            i_dict_before = json.loads(str(list_before.text))
            objects_before = i_dict_before["objects"]
            n_range = [0, 20]
            print("Info - sending CNC events")
            for n in range(n_range[0], n_range[1]):
                userID_str = "usr" + str(n)
                list_of_voters = [userID_str,"usr" + str(n+1),"usr" + str(n+2),"usr" + str(n+3)]
                r = LeaderBoardFuncs.upvoteComment(self, userID_str, entry, list_of_voters, False)

            print("Pass - CNC events sent")

        except Exception as Exp:
            print(Exp)
            print("Fail - sending CNC events")
            testStatus = False
            return

        try:
            time.sleep(10)
            list_after = self.game_service.userScoreList(self.lbId, pageSize="15")
            i_dict = json.loads(str(list_after.text))
            objects = i_dict["objects"]

            print("Info - validate all 15 users scores before vs after")
            for obj in objects:
                for obj2 in objects_before:
                    if obj["id"] == obj2["id"]:
                        # before and after - same user
                        if obj["score"] == obj2["score"]+points_add:
                            # score added as expected:1 self vote no points + 4 other users = 10*4
                            # validate 15, print 1 ["usr10"]
                            if obj["id"]=="usr10":
                                print("score before, after 4 CNC: " +str(obj2["score"]) + ", "+str(obj2["score"]))
                            break
                        else:
                            print("----------")
                            # missing points!
                            testStatus = False
                            print("Fail - C&C scoring")
                            print(obj2)
                            print(obj)
                            print("----------")
            if testStatus:
                print("Pass - validate all 15 users scores before vs after")


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
            r = self.game_service.LBUpdate(self.lbId, "", "", "disabled")
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
        pytest.main(args=['test_4518_VL_CNC.py', '-s'])
    # ===========================================================================