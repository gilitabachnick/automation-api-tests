# ===============================================================================================================
# @Author: Zeev Shulman 29/12/21
#
#
#       Paid flow
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
    isProd = True
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

# This should be removed if/when credit card tests can be run on production
if isProd:
    isProd = False
    print("Warning - This is a QA only test, DOESN'T RUN ON PROD")
    print("----- The test will continue on QA/dev env ------")

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
            self.logi = reporter2.Reporter2('test_241_API_purchase_various_plans')
        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

    def test_241_API_purchase_various_plans(self):
        global testStatus
        self.logi.initMsg('test_241_API_purchase_various_plans')
        # ======================================================================================
        # will test for all subscriptions in subscriptions_list
        #     will use plans in plans_list with the same index
        # ======================================================================================
        try:

            plans_list = [SelfServeClient.dict_plan["classroom-standard-monthly"],
                          SelfServeClient.dict_plan["classroom-pro-monthly"],
                          SelfServeClient.dict_plan["classroom-pro-addon"],
                          SelfServeClient.dict_plan["vpass-6000"],
                          SelfServeClient.dict_plan["vpass-pay"]]
            subscriptions_list = [SelfServeClient.dict_subscription_json["classroom-standard-monthly"],
                                  SelfServeClient.dict_subscription_json["classroom-pro-monthly"],
                                  SelfServeClient.dict_subscription_json["classroom-pro-addon"],
                                  SelfServeClient.dict_subscription_json["vpass-6000"],
                                  SelfServeClient.dict_subscription_json["vpass-pay"]]
            card_json = SelfServeClient.dict_card_json["card_ok"]
            index = 0
            for subscription in subscriptions_list:
                print("")
                print("++++++++ Testing subscription: " + subscription + " ++++++++")
                # unique email based on time
                self.eMail = str(int(time.time())) + "@mailinator.com"
                plan = plans_list[index]
                index += 1
                # ===========================================================================
                # The test starts here
                # ===========================================================================
                iteration_status = True
                try:
                    print("Info - postEmailValidation: valid email format and existing package")
                    rc = SelfServeClient.email_validation_form1(self, self.eMail, plan)
                    if rc:
                        print("Pass - postEmailValidation")
                    else:
                        print("Fail - postEmailValidation")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    print("Fail - postEmailValidation")
                    iteration_status = False

                try:
                    print("Info - putPartnerRegister")
                    ui_hash = SelfServeClient.get_ui_hash(self, self.eMail)
                    rc2 = self.PurcheseManager.putPartnerRegister_UIhash("Finn", "Underwood", self.eMail, "API Testing KPF",
                                                                         "CFO", self.pwd, ui_hash)
                    if rc2:
                        print("Pass - putPartnerRegister")
                    else:
                        print("Fail - putPartnerRegister")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    print("Fail - putPartnerRegister")
                    iteration_status = False

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
                    print("Fail - postPartnerLogin")
                    iteration_status = False

                try:
                    print("Info - post Subscription")
                    # rc4 = SelfServeClient.chargeBe_CC_UI(self, ui_hash, card_json)  ###### UI #########
                    rc4 = self.PackageManager.postSubscription_UIhash(ui_hash, subscription, is_token)
                    if rc4:
                        print("Pass - Subscription created")
                        is_dict = json.loads(rc4.text)
                        pid = str(is_dict["partner_id"])
                        product = is_dict["product"]
                        product_type = is_dict["type"]
                        status = is_dict["status"]
                        print("PID: " + pid + ", Subscription: " + product + " " + product_type + ", Status: " + status)
                    else:
                        print("Fail - Failed to create Subscription")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    print("Fail - Failed to create Subscription")
                    iteration_status = False

                try:
                    print("Info - PUT credit card data")
                    rc5 = self.PurcheseManager.putPartnerCard_UIhash(card_json, is_token)
                    # rc5 = SelfServeClient.chargeBe_CC_UI(self, card_json) ###### UI #########
                    if rc5:
                        is_dict2 = json.loads(rc5.text)
                        status_card = is_dict2["payment_source"]["status"]
                        l4 = is_dict2["payment_source"]["card"]["last4"]
                        print("Pass - The card ending with the digits: " + l4 + " status is: " + status_card)
                    else:
                        print("Fail - credit card validation")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    print("Fail - credit card validation")
                    iteration_status = False

                try:
                    # wait 5 sec increments for status to update
                    for num in range(8):
                        time.sleep(5)
                        print("Info - get subscription status")
                        rc6 = self.PackageManager.getSubscriptionPartner(pid, is_token)
                        status_changed = False
                        if rc6:
                            is_dict3 = json.loads(rc6.text)[0]
                            status_final = is_dict3["status"]
                            if status_final != status:
                                status_changed = True
                                break
                    if status_changed:
                        print("Pass - after payment method, Status changed from " + status + " to " + status_final)
                    else:
                        print("Fail - Failed to verify Status change after payment")
                        iteration_status = False
                except Exception as Exp:
                    print(Exp)
                    print("Fail - Failed to verify Status change after payment")
                    iteration_status = False

                if iteration_status == False: testStatus = False
                str_status = "PASS" if iteration_status else "FAIL"
                print("========= " + str_status + " subscription: " + subscription + " =========")


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
                self.practitest.post(Practi_TestSet_ID, '241', '0')
                # self.logi.reportTest('pass', self.sendto)
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '241', '1')
                # self.logi.reportTest('fail', self.sendto)
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_241_API_purchase_various_plans.py', '-s'])
    # ===========================================================================
