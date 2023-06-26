# ===============================================================================================================
# @Author: Zeev Shulman 17/01/22
#
# 1. Enter valid credit card with status changed to: active
# 2. Change credit card to one wth insufficient funds
#
# result: credit card is changed and status remains active
#  - despite the no funds, payment was already done during step 1 so status is active and not pending
#  - problems might come up next billing cycle and status can be changed then

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
            self.practitest = Practitest.practitest('20271')
            # unique email based on time
            self.eMail = str(int(time.time())) + "@mailinator.com"
            self.pwd = SelfServeClient.PASSWORD
            self.logi = reporter2.Reporter2('test_258_API_change_card_insufficient_funds ')
        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

    def test_258_API_change_card_insufficient_funds(self):
        global testStatus
        self.logi.initMsg('test_258_API_change_card_insufficient_funds ')
        plan = SelfServeClient.dict_plan["classroom-pro"]
        subscription_json = SelfServeClient.dict_subscription_json["classroom-pro"]
        card_json = SelfServeClient.dict_card_json["card_ok"]
        card_json_no_funds = SelfServeClient.dict_card_json["card_no_funds"]

        try:
            print("Info - postEmailValidation: valid email format and existing package")
            rc = SelfServeClient.email_validation_form1(self, self.eMail, plan)
            if rc:
                print("Pass - postEmailValidation")
            else:
                print("Fail - postEmailValidation")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - postEmailValidation")
            return

        try:
            print("Info - putPartnerRegister")
            ui_hash = SelfServeClient.get_ui_hash(self, self.eMail)
            rc2 = self.PurcheseManager.putPartnerRegister_UIhash("Finn", "Underwood", self.eMail, "API Testing KPF",
                                                                 "CFO", self.pwd, ui_hash)
            if rc2:
                print("Pass - putPartnerRegister")
            else:
                print("Fail - putPartnerRegister")
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - putPartnerRegister")
            return

        try:
            print("Info - postPartnerLogin")
            rc3 = self.PurcheseManager.postPartnerLogin(self.eMail, self.pwd)
            if rc3:
                will_be_token = rc3.json()
                is_token = will_be_token["access_token"]
                path = rc3.url
                print("Pass - postPartnerLogin")
            else:
                print("Fail - postPartnerLogin")
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - postPartnerLogin")
            return

        try:
            # packageManager.PostSubscription{hash}
            print("Info - post Subscription")
            rc4 = self.PackageManager.postSubscription_UIhash(ui_hash, subscription_json, is_token)
            if rc4:
                print("Pass - Subscription created")
                is_dict = json.loads(rc4.text)
                pid = str(is_dict["partner_id"])
                product = is_dict["product"]
                product_type = is_dict["type"]
                status = is_dict["status"]
                print("     PID: " + pid + ", Subscription: " + product + " " + product_type + ", Status: " + status)
                print("         Full Json: " + subscription_json)
            else:
                print("Fail - Failed to create Subscription")
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - Failed to create Subscription")
            return

        try:
            print("Info - PUT credit card data")
            rc5 = self.PurcheseManager.putPartnerCard_UIhash(card_json, is_token)
            if rc5:
                is_dict2 = json.loads(rc5.text)
                status_card = is_dict2["payment_source"]["status"]
                l4 = is_dict2["payment_source"]["card"]["last4"]
                print("Pass - The card ending with the digits: " + l4 + " status is: " + status_card)
            else:
                print("Fail - credit card validation")
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - credit card validation")
            return

        try:
            # wait 5 sec increments for status to update
            for num in range(6):
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
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - Failed to verify Status change after payment")

        # ===========================================================================
        # PUT Partner Card - Insufficient Fuds
        # ===========================================================================
        try:
            print("Info - PUT credit card with Insufficient Fuds")
            rc6 = self.PurcheseManager.putPartnerCard_UIhash(card_json_no_funds, is_token)
            if rc6.status_code == 406 and "insufficient funds" in rc6.text:
                print("   "+rc6.text)
                print("Pass - insufficient funds credit card detected")
            else:
                print("   " + rc6.text)
                print("Fail - insufficient funds credit card NOT detected")
                testStatus = False

            # if rc6:
            #     is_dict2 = json.loads(rc6.text)
            #     status_card = is_dict2["payment_source"]["status"]
            #     l4 = is_dict2["payment_source"]["card"]["last4"]
            #     print("Pass - The card ending with the digits: " + l4 + " status is: " + status_card)
            # else:
            #     print("Fail - credit card validation")
            #     testStatus = False
            #     return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - credit card validation")
            return

        try:
            # wait 15 sec to verify status did not change - usual time is 5-10 sec
            time.sleep(15)
            print("Info - get subscription status after change to credit card with Insufficient Fuds")
            rc7 = self.PackageManager.getSubscriptionPartner(pid, is_token)
            if rc7:
                is_dict3 = json.loads(rc7.text)[0]
                status_final = is_dict3["status"]
            if status_final == "active":
                print("PASS - Status: " + status_final + " as it should be")
            else:
                print("Fail - Status: " + status_final + " Status should be: active")
                testStatus = False
                return
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - Failed to verify Status not changed after card change")
            return

        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - Failed to create Subscription")
            return
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
                self.practitest.post(Practi_TestSet_ID, '258', '0')
                # self.logi.reportTest('pass', self.sendto)
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '258', '1')
                # self.logi.reportTest('fail', self.sendto)
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_258_API_change_card_insufficient_funds .py', '-s'])
    # ===========================================================================