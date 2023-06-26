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

            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)
            self.FileName = 'Yellow-Blue-Gree-Red.mp4'  # inifile.RetIniVal('Entry', 'File'
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
            self.FileName = os.path.join(path, self.FileName)
        except Exception as Exp:
            print(Exp)

    def test_4517_VL_Live(self):
        global testStatus
        try:
            n_range = [17, 19]
            first = "usr" + str(n_range[0])  # usr17
            last = "usr" + str(n_range[0]+1)  # usr18
            entry= "1_hz8as9f7"#"1_zf76c29r"
            entry_no_cat = "1_y186zjns"
            delta_score = 10

            r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
            # get first & last baseline score - response is list of 2 ints
            print("Info - scores before Live events sent")
            first_last_1 = getFirstandLast(self, first, last, self.lbId)
            print(first_last_1)
            for n in range(n_range[0], n_range[1]):
                userID_str = "usr" + str(n)
                r = LeaderBoardFuncs.playEntry(self, userID_str, entry, 30)

            print("Info - scores after 30 sec Live events sent")
            time.sleep(3)
            first_last_2 = getFirstandLast(self, first, last, self.lbId)
            print(first_last_2)
            if first_last_1[0] == first_last_2[0] and first_last_1[1] == first_last_2[1]:
                print("Pass - score did not change after less than 60 sec")
            else:
                print("Fail - score changed after less than 60 sec")
                testStatus = False
            print("-------------")

            for n in range(n_range[0], n_range[1]):
                userID_str = "usr" + str(n)
                r = LeaderBoardFuncs.playEntry(self, userID_str, entry, 30)
            time.sleep(10)
            first_last_3 = getFirstandLast(self, first, last, self.lbId)
            print("Info - scores after 60 sec Live events sent")
            print(first_last_3)
            if first_last_1[0]+delta_score == first_last_3[0] and first_last_1[1]+delta_score == first_last_3[1]:
                print("Pass - score updated after 60 sec as expected")
            else:
                print("Fail - score did NOT update after 60 sec as expected")
                testStatus = False
            print("-------------")

            for n in range(n_range[0], n_range[1]):
                userID_str = "usr" + str(n)
                r = LeaderBoardFuncs.playEntry(self, userID_str, entry_no_cat, 60)
            time.sleep(3)
            first_last_4 = getFirstandLast(self, first, last, self.lbId)
            print("Info - scores after 60 sec NO category events sent")
            print(first_last_4)
            if first_last_3[0] == first_last_3[0] and first_last_3[1] == first_last_4[1]:
                print("Pass - No category score did not change")
            else:
                print("Fail - score changed after No category")
                testStatus = False
            print("-------------")

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
        pytest.main(args=['test_4517_VL_Live.py', '-s'])
    # ===========================================================================


def getFirstandLast(self,first,last,lbId):
    try:
        r_first = self.game_service.userScoreGet(lbId, first)
        r_last = self.game_service.userScoreGet(lbId, last)
        if r_first:
            first_dict = json.loads(str(r_first.text))
            first_score = first_dict["score"]
        else:
            first_score = 0
        if r_last:
            last_dict = json.loads(str(r_last.text))
            last_score = last_dict["score"]
        else:
            last_score = 0
        return [first_score, last_score]
    except Exception as Exp:
        print(Exp)
        print("Fail - to get first and last score")
        return [0, 0]