# ===============================================================================================================
# @Author: Zeev Shulman 15/12/21
#
#       Free trial flow: 3 packages/subscriptions/plans one after the other
#
#
#
# ===============================================================================================================


import os
import sys
import time
import json

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1,pth)

import reporter2
import Practitest
import Config
import SelfServeClient

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '20271'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()
    if str(isProd) == 'true':
        isProd = True
    else:
        isProd = False

testStatus = True

class TestClass:
    # ===========================================================================
    # SETUP
    # ===========================================================================
    def setup_class(self):
        global testStatus
        try:
            if isProd:
                self.env = 'prod'
            else:
                self.env = 'testing'
            print("")
            print("----- Setup - " + self.env + " -------")
            self.sendto = "zeev.shulman@Kaltura.com"
            self.PurcheseManager = SelfServeClient.purchasManager(isProd)
            self.PackageManager = SelfServeClient.packageManager(isProd)
            self.pwd = SelfServeClient.PASSWORD
            self.practitest = Practitest.practitest('20271')
            self.logi = reporter2.Reporter2('test_240_API_free_trail_varius_plans')
        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

    def test_240_API_free_trail_varius_plans(self):
        global testStatus
        self.logi.initMsg('test_240_API_free_trail_varius_plans')
        # ======================================================================================
        # will test for all plans in plans_list
        # ======================================================================================
        try:
            if isProd:
                plans_list = [SelfServeClient.dict_plan["classroom-free"],
                              SelfServeClient.dict_plan["webinars-free-isProd"],
                              SelfServeClient.dict_plan["vpass-free"]]
            else:
                plans_list = [SelfServeClient.dict_plan["classroom-free"],
                              SelfServeClient.dict_plan["webinars-free"],
                              SelfServeClient.dict_plan["vpass-free"]]

            for plan in plans_list:
                print("")
                print("++++++++ Testing subscription: " + plan + " ++++++++")
                self.eMail = str(int(time.time())) + "@mailinator.com" # unique email based on time
                # ===========================================================================
                # The test starts here
                # ===========================================================================
                iteration_status = True
                try:
                    print("Info - postEmailValidation: valid email format and existing package")
                    rc = SelfServeClient.email_validation_form1(self, self.eMail, plan) #email_validation_form1(self, self.eMail, plan)
                    if rc:
                        print("Pass - postEmailValidation")
                    else:
                        print("Fail - postEmailValidation")
                except Exception as Exp:
                    print(Exp)
                    iteration_status = False
                    print("Fail - postEmailValidation")

                try:
                    print("Info - putPartnerRegister")
                    ui_hash = SelfServeClient.get_ui_hash(self, self.eMail)
                    rc2 = self.PurcheseManager.putPartnerRegister_UIhash("Finn", "Underwood", self.eMail, "API Testing KPF", "CFO", self.pwd, ui_hash)
                    if rc2:
                        is_dict = json.loads(rc2.text)
                        # print(is_dict)
                        subscriptionType = is_dict["subscriptionType"]
                        subscriptionId = is_dict["subscriptionId"]
                        if subscriptionType == "FREE":
                            print("Subscription Type: " + subscriptionType + ", subscription Id: " + subscriptionId)
                            print("Pass - putPartnerRegister and Free Subscription created")
                        else:
                            print("Fail - No FREE subscription")
                            iteration_status = False
                    else:
                        print("Fail - putPartnerRegister")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    iteration_status = False
                    print("Fail - putPartnerRegister")

                try:
                    print("Info - postPartnerLogin")
                    rc3 = self.PurcheseManager.postPartnerLogin(self.eMail, self.pwd)
                    if rc3:
                        will_be_token = rc3.json()
                        is_token = will_be_token["access_token"]
                        # path = rc3.url
                        print("Pass - postPartnerLogin")
                    else:
                        print("Fail - postPartnerLogin")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    iteration_status = False
                    print("Fail - postPartnerLogin")

                if iteration_status == False: testStatus = False
                str_status = "PASS" if iteration_status else "FAIL"
                print("========= " + str_status + " subscription: " + plan + " =========")

        except Exception as Exp:
            print(Exp)
            print("Fail - failed to initiate testing")
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
                self.practitest.post(Practi_TestSet_ID, '240', '0')
                # self.logi.reportTest('pass', self.sendto)
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '240', '1')
                # self.logi.reportTest('fail', self.sendto)
                assert False
        except Exception as Exp:
            print(Exp)


    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_240_API_free_trail_varius_plans.py', '-s'])
    # ===========================================================================
