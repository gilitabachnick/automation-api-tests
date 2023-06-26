# ===============================================================================================================
# @Author: Zeev Shulman 16/01/22
#
# combines 2 validation tests:
#    1. Unique email required for registration
#       111 - KPF - Purchase Flow - Unique Email Validation - Free Trial - New Partner
#    2. invalid Credit Card fails PUT Partner Card
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
            self.logi = reporter2.Reporter2('test_243_API_unique_email_and_credit_fail')

        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

    def test_243_API_unique_email_and_credit_fail(self):
        global testStatus
        self.logi.initMsg('test_243_API_unique_email_and_credit_fail')
        subscription_json = SelfServeClient.dict_subscription_json["classroom-pro"]
        # plan = SelfServeClient.dict_plan["classroom-pro"]
        card_json = SelfServeClient.dict_card_json["card_fail"]

        try:
            print("Info - postEmailValidation: valid email format and existing package")
            rc = SelfServeClient.email_validation_form1(self, self.eMail, SelfServeClient.dict_plan["classroom-pro"])
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
            #ui_hash = self.PurcheseManager.createMD5Hash(self.eMail, plan, "EmailValidation", ui_hash)
            rc2 = self.PurcheseManager.putPartnerRegister_UIhash("Finn", "Underwood", self.eMail, "API Testing KPF", "CFO", self.pwd, ui_hash)
            if rc2:
                print("Pass - putPartnerRegister")
            else:
                print("Fail - putPartnerRegister")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - putPartnerRegister")
            return

        try:
            print("Info - unique Email, try validating already used eMail")
            # rc = email_validation_form1(self, self.eMail, "kme-virtual-classroom-free-trial")
            rc = SelfServeClient.email_validation_form1(self, self.eMail, SelfServeClient.dict_plan["classroom-free"])
            # Fail email_validation_form1 is the expected result
            if rc:
                print("Fail - not unique Email was validated")
            else:
                print("Pass - As expected, non unique Email failed to validate")
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
                # path = rc3.url
                print("Pass - postPartnerLogin")
            else:
                print("Fail - postPartnerLogin")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - postPartnerLogin")
            return

        try:
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
            else:
                print("Fail - Failed to create Subscription")
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
                print("Fail - The card ending with the digits: " + l4 + " status is: " + status_card)
                print("    The test FAILED as credit card number entered was not valid")
                testStatus = False
                return
            else:
                print("Pass - As expected, credit card validation failed")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - failed to check credit card validation")
            return

        try:
            # wait 10 sec for status to update
            time.sleep(10)
            print("Info - get subscription status")
            rc6 = self.PackageManager.getSubscriptionPartner(pid, is_token)
            status_changed = False
            if rc6:
                is_dict3 = json.loads(rc6.text)[0]
                status_final = is_dict3["status"]
                if status_final != status:
                    status_changed = True
            if status_changed:
                print("Fail - After failed payment method, Status should not change from " + status + " to " + status_final)
                testStatus = False
            else:
                print("Pass - As expected, status not changed after failed payment method")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - Failed to verify Status not changed after payment")

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus
        print("---------- Teardown ---------")
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '243', '0')
                # self.logi.reportTest('pass', self.sendto)
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '243', '1')
                # self.logi.reportTest('fail', self.sendto)
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_243_API_unique_email_and_credit_fail.py', '-s'])
    # ===========================================================================
