# ===============================================================================================================
#  @Author: Zeev Shulman 08/11/2022
#
#  ****************** 100 users watch VOD ******************
#
#  @description:
#       - send X [100] concurrent view events to analytics
#       - Validate score,rank change appropriately
#       - use userScore/get userScore/list
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
            #self.logi = reporter2.Reporter2('test_1001_score_actions')
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.game_service = LeaderBoardService.GameService(isProd)

        except Exception as Exp:
            print(Exp)

    def test_4514_VL_rule2_vod(self):
        global testStatus
        try:

            print("**** test_4514_VL_rule2_vod ****")
            sessionId = "itsfake1-7c64-4ad5-015c-3727ca5ae7cf"
            entry = "1_n9sto0oe"
            view_seconds = 120
            delta_score = 20 # (view_seconds / 60) * 10 = 50, but vod duration is 4 mins so 40 is the cap
            KMS_KS_list = []
            n_range = [0, 100]
            first = "usr0"
            last = "usr99"

            r = self.game_service.LBUpdate(self.lbId, "", "", "enabled")
# ===== create list of KS
            for n in range(n_range[0], n_range[1]):
                userID_str = "usr" + str(n)
                KMS_KS_list.append(LeaderBoardFuncs.genKMS_KS(self, userID_str))

# ===== create list of unique sessionId
            sessionIds = ["%05d" % idx for idx in range(n_range[1])]
            for n in range(n_range[0], n_range[1]):
                sessionIds[n] = sessionIds[n] + sessionId[5:]

            # get first & last baseline score - response is list of 2 ints
            first_last_before = getFirstandLast(self, first, last, self.lbId)
            # userscore/list for validation after changes
            list_before = self.game_service.userScoreList(self.lbId,pageSize="100")

            # creates A requests list
            will_be_request = []
            PLAY_EVENT_TYPE = "99"  # "3"
            counter = 0
            for iKMS_KS in KMS_KS_list:
                play_url = self.analyticsUrl + "&eventType=" + PLAY_EVENT_TYPE + "&partnerId=" + str(
                    self.Partner_ID) + "&ks=" + iKMS_KS + "&sessionId=" + sessionIds[counter] + "&entryId=" + entry + "&reactionType=7"
                counter += 1
                will_be_request.append(play_url)

        except Exception as Exp:
            print(Exp)
            testStatus = False

        try:
            pool = Pool(100)
            # Creates a pool of threads; more threads = more concurrency.
            # "pool" is a module attribute; you can be sure there will only
            # be one of them in your application
            # as modules are cached after initialization.
            print("start sending events: " + str(datetime.datetime.now()))
            futures = []
            times = int(view_seconds / 10)
            for it in range(times):
                for request in will_be_request:
                    futures.append(pool.apply_async(requests.get, [request]))
                    # futures is now a list of responses.
                if it == times:
                    break # don't wait after last set of requests
                print("-----wait 10 sec-------")
                time.sleep(10)
            print("end sending events: " + str(datetime.datetime.now()))

        except Exception as Exp:
            print(Exp)
            testStatus = False

        try:
            print("Info - check for not [200] responses from analytics")
            output = [p.get() for p in futures]
            output2 = [p.get().text for p in futures]
            not_200_response = False
            for count, value in enumerate(output):
                if str(value).find("200") == -1:
                    not_200_response = True
                    print("Fail - err from analytics:")
                    print(count, value, output2[count])
            print("Pass - no err responses from analytics")

            first_last_after = getFirstandLast(self, first, last, self.lbId)
            counter = 0
            while first_last_after[0]<first_last_before[0]+delta_score:
                # increase counter limit or add time.sleep if needed with x*10,000 users testing
                first_last_after = getFirstandLast(self, first, last, self.lbId)
                counter += 1
                time.sleep(10)
                if counter > 30: # 5 min
                    break
            print("----------------")
            print("Info - validate score using userscore/get and userscore/list")
            i_dict_before = json.loads(str(list_before.text))
            list_after = self.game_service.userScoreList(self.lbId,pageSize="500")
            i_dict = json.loads(str(list_after.text))
            total_count = i_dict["totalCount"]
            print("totalCount=" + str(total_count))
            print("Info - first & last before: " + str(first_last_before) + " add points: " + str(delta_score))
            print("Info - first & last after: " + str(first_last_after))
            if counter < 30 and total_count >= n_range[1]-n_range[0]:
                time.sleep(5)
                print("Pass - last score was updated by: " + str(datetime.datetime.now()))
            else:
                print("Fail - last score was not updated by: " + str(datetime.datetime.now()))
                testStatus = False

            print("----------------")
            print("Info - userscore/list validate")
            #time.sleep(3)
            objects = i_dict["objects"]
            objects_before = i_dict_before["objects"]
            if i_dict["totalCount"] == i_dict_before["totalCount"] >= 100:
                print("Pass - totalCount is as expected")
            else:
                print("fail - totalCount")
                testStatus = False

            sigma_before = 0
            sigma_after = 0
            counter=0
            for obj in objects:
                sigma_after += obj["score"]
                counter += 1
                if counter == 100:
                    break
            counter = 0
            for obj2 in objects_before:
                sigma_before += obj2["score"]
                counter += 1
                if counter == 100:
                    break
            if sigma_after == sigma_before +delta_score*100:
                print("Pass - userscore/list, aggregate scores are as expected")
            else:
                print("Fail E2E userscore/list validate")
                testStatus = False

            print("----------------")
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
        pytest.main(args=['test_4514_VL_rule2_vod.py', '-s'])
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

