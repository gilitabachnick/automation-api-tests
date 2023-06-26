# ===============================================================================================================
#  @Author: Zeev Shulman 07/11/2022
#
#  ****************** load *k events ******************
#
#  @description:
#       - send X*K events to analytics (1,000 a second and higher)
#       - record the time it took to send the events
#       - Validate score/rank change appropriately, the time it took to get an accurate report
#
#
# ===============================================================================================================

import os
import datetime
import requests
from multiprocessing.dummy import Pool
import time
import Config


#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = True
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
        print("***  Leaderboard load quiz test  ***")

    def test_LB_Load_quiz(self):
        global testStatus
        try:
            entryID = ["1_30k8qovj", "1_8uh3h36j", "1_knlfczev", "1_saaxxbfe", "1_knmlpgoq", "1_097juzgl"]
            QUIZ_EVENT_TYPE = "30001"
            analyticsUrl = 'https://analytics.kaltura.com/api_v3/index.php?service=analytics&action=trackEvent'
            Partner_ID = '4800142'
            number_events_total = 2000 #50000
            pool_size = 1000

            will_be_request = [] # creates 50000 requests list
            for j in range(1, 2001):
                userID_str = "usr"+str(j)
                # &score is used &calculatedScore is ignored by LB/Analytics
                quiz_url = analyticsUrl + "&eventType=" + QUIZ_EVENT_TYPE + "&partnerId=" + str(Partner_ID) + \
                           "&userId=" + userID_str + "&entryId=" + entryID[2] + "&version=0" + "&score=" + \
                           str(j) + "&calculatedScore=" + "77" + "&reactionType=7"
                will_be_request.append(quiz_url)

        except Exception as Exp:
            print(Exp)
            testStatus = False

        try:
            print("Info - LB load: Quiz")
            # Creates a pool with 1000 threads; more threads = more concurrency.
            pool = Pool(pool_size)
            print("start sending events: " + str(datetime.datetime.now()))
            # futures = []
            actual_concurrent_events = 1000 #pool_size
            for ik in range(0,number_events_total,pool_size):
                futures = []
                for i in range(actual_concurrent_events):
                    futures.append(pool.apply_async(requests.get, [will_be_request[ik+i]]))
                    # futures is list of futures responses.
                time.sleep(0.1)
                try:
                    print("Info - sent " + str(ik+1000) + " events. All errors - and every [m] response in each pool:")
                    m = 100
                    output = [p.get() for p in futures]
                    output2 = [p.get().text for p in futures]
                    for count, value in enumerate(output):
                        if (count % m) == 0:
                            print(ik+count, value, output2[count])
                        if str(value).find("200") == -1:
                            print("********* Fail - err from analytics: *********")
                            print(count, value, output2[count])

                except Exception as Exp:
                    print(Exp)
                    testStatus = False
                print("-------------")
            print("end sending events: " + str(datetime.datetime.now()))
            # check results in userScore/list
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
            else:
                print("  *** FAIL ***")
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_LB_Load_quiz.py', '-s'])
    # ===========================================================================

