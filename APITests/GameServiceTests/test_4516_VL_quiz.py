# ===============================================================================================================
#  @Author: Zeev Shulman 08/11/2022
#
#  ****************** quiz VL rules ******************
#
#  @description:
#       - upload entry with category:'quiz'
#       - send X*K events/second to analytics (1,000 a second and higher)
#       - record the time it took to send the events
#       - Validate score/rank change appropriately
#       - record the time it took to get an accurate report
#
#
# ===============================================================================================================

import os
import sys
import datetime
import requests
import json
from multiprocessing.dummy import Pool
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
            #self.url = inifile.RetIniVal('Environment', 'KMC_URL')
            #self.logi = reporter2.Reporter2('test_1001_score_actions')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)
            self.FileName = 'Yellow-Blue-Gree-Red.mp4'  # inifile.RetIniVal('Entry', 'File'
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
            self.FileName = os.path.join(path, self.FileName)

        except Exception as Exp:
            print(Exp)

    def test_4516_VL_quiz(self):
        global testStatus
        try:
            points_add = 50
            QUIZ_EVENT_TYPE = "30001"
            entry = '1_81nmfjyt'
            bonus = 20

            r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
            print("Info - Upload new Entry with category 'quiz' file: " + str(self.FileName))
            entry = LeaderBoardFuncs.create_new_entry(self, self.FileName, "quiz")
            if entry == False:
                print("Fail - failed Upload new Entry")
                testStatus = False
                return

            list_before = self.game_service.userScoreList(self.lbId,pageSize="101")
            n_range = [0, 101]
            will_be_request = [] # creates 1000 requests list
            for n in range(n_range[0], n_range[1]):
                userID_str = "usr" + str(n)
                quiz_url = self.analyticsUrl + "&eventType=" + QUIZ_EVENT_TYPE + "&partnerId=" + str(self.Partner_ID) + \
                           "&userId=" + userID_str + "&entryId=" + entry + "&version=0" + "&score=" + \
                           str(points_add) + "&calculatedScore=" + "77" + "&reactionType=7"
                will_be_request.append(quiz_url)

        except Exception as Exp:
            print(Exp)
            testStatus = False

        try:
            pool = Pool(101)
            print("Info - start sending events: " + str(datetime.datetime.now()))
            futures = []
            counter = 0
            for request in will_be_request:
                futures.append(pool.apply_async(requests.get, [request]))
                counter += 1
                if counter == 100:
                    # making sure usr100 does NOT get the bonus
                    time.sleep(10)

            print("Pass - end sending events: " + str(datetime.datetime.now()))
        except Exception as Exp:
                print(Exp)
                print("Fail - Quiz sending events")
                testStatus = False

        try:
            time.sleep(10)
            i_dict_before = json.loads(str(list_before.text))
            list_after = self.game_service.userScoreList(self.lbId, pageSize="101")
            i_dict = json.loads(str(list_after.text))
            objects = i_dict["objects"]
            objects_before = i_dict_before["objects"]
            print("Info - validate all 101 users scores before vs after")
            for obj in objects:
                for obj2 in objects_before:
                    if obj["id"] == obj2["id"]:
                        # before and after - same user
                        if obj["score"] == obj2["score"]+points_add+bonus:
                            # first 100 users quiz and bonus scores as expected
                            break
                        else:
                            if obj["id"] == "usr100" and obj["score"] == obj2["score"]+points_add:
                                # making sure usr100 DID NOT get the bonus
                                print("----------")
                                print(objects_before[len(objects_before) - 2])
                                print(objects[len(objects)-2])
                                print(obj2)
                                print(obj)
                                print("Pass - Quiz 50 points and bonus stops at 100")
                                print("----------")
                            else:
                                print("----------")
                                # missing points!
                                testStatus = False
                                print("Fail - Quiz scoring")
                                print(obj2)
                                print(obj)
                                print("----------")
                            break

        except Exception as Exp:
                print(Exp)
                testStatus = False
        try:
            r_usr0 = self.game_service.userScoreGet(self.lbId, "usr0")
            usr0_dict = json.loads(str(r_usr0.text))
            usr0_score = usr0_dict["score"]
            print("Info - send exhausted Quiz entry get no points")
            r = requests.get(will_be_request[0])
            time.sleep(2)
            r_exh = self.game_service.userScoreGet(self.lbId, "usr0")
            exh_dict = json.loads(str(r_exh.text))
            if exh_dict["score"] == usr0_score:
                print("Pass - exhausted entry get no points")
            print("Info - send wrong category Quiz entry get no points")
            wrong_cat_request = will_be_request[0].replace(entry,"1_hurznwpf")
            r = requests.get(will_be_request[0])
            time.sleep(2)
            r_cat = self.game_service.userScoreGet(self.lbId, "usr0")
            exh_dict = json.loads(str(r_exh.text))
            if exh_dict["score"] == usr0_score:
                print("Pass - wrong category entry get no points")
            else:
                print("Fail - points given when they shouldn't")
                testStatus = False
            try:
                r = LeaderBoardFuncs.delete_entry(self, entry)
            except Exception as Exp:
                print(Exp)

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
        pytest.main(args=['test_4516_VL_quiz.py', '-s'])
    # ===========================================================================
