# ===============================================================================================================
# @Author: Zeev Shulman 15/12/21
# @description: SSRV API's - PurcheseManager post email-validation, PackageManager getPackage List
#
# 1- send incorrect eMail format and/or non existing Package - verify getting 400
# 2- send ok eMail format paired with all existing packages
# ===============================================================================================================

import os
import sys
import json
import time

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

            self.logi = reporter2.Reporter2('test_245_API_all_packages_email_validation')
        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

    def test_245_API_all_packages_email_validation(self):
        global testStatus
        self.logi.initMsg('test_245_API_all_packages_email_validation')
        try:
            print("INFO - postEmailValidation sending 3 sets of bad values")
            #print("3 bad json values: eMail Package - false false, false true, true false")
            list_of_bad_dicts = [{"email": "Scipio8@mailinator", "desiredPackageId": " f ree-trial"},
                                 {"email": "Scipio8", "desiredPackageId": "kme-virtual-classroom-free-trial"},
                                 {"email": "Scipio8@mailinator.com", "desiredPackageId": "kme-virtual"}]

            for j in list_of_bad_dicts:
                is_jason = json.dumps(j)
                if not self.PurcheseManager.postEmailValidation(is_jason):
                    print("Pass - As expected API returns err when sent bad json: " + is_jason)
                else:
                    print("Fail - API returns 201 when sent bad json: " + is_jason)
                    testStatus = False
                    return

        except Exception as Exp:
            print(Exp)
            testStatus = False
            print("Fail - failed to test bad jsons")
            return

        try:
            print("INFO - postEmailValidation sending valid Packages with proper eMail")
            eMail = str(int(time.time())) + "@mailinator.com"
            if isProd:
                plans_list = [SelfServeClient.dict_plan["classroom-free"],
                              SelfServeClient.dict_plan["webinars-free-isProd"],
                              SelfServeClient.dict_plan["vpass-free"],
                              SelfServeClient.dict_plan["vpass-6000"],
                              SelfServeClient.dict_plan["vpass-pay"]
                              ]
                for i in plans_list:
                    try:
                        recaptcha_token = "" #"see old vesions if self serve automation will be relevant again"
                        will_be_jason = {"email": eMail, "desiredPackageId": i, "recaptchaToken": recaptcha_token}
                        is_jason = json.dumps(will_be_jason)
                        rc = self.PurcheseManager.postEmailValidation(is_jason)
                        if rc:
                            print("PASS - Package: "+i + " Validated")
                        else:
                            print("FAIL Package: "+i + " Validation")
                            testStatus = False
                    except Exception as Exp:
                        print(Exp)
                        testStatus = False
            else:
                r = self.PackageManager.getPackageList()
                for i in r.json():
                    try:
                        will_be_jason = {"email": eMail, "desiredPackageId": i["name"]}
                        is_jason = json.dumps(will_be_jason)
                        rc = self.PurcheseManager.postEmailValidation(is_jason)
                        if rc:
                            print("PASS - Package: "+i["name"] + " Validated")
                        else:
                            print("FAIL Package: "+i["name"] + " Validation")
                            testStatus = False
                    except Exception as Exp:
                        print(Exp)
                        testStatus = False

        except Exception as Exp:
            print(Exp)
            testStatus = False


    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):
        global testStatus
        print("---------- Teardown ---------")
        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '245', '0')
                # self.logi.reportTest('pass', self.sendto)
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '245', '1')
                # self.logi.reportTest('fail', self.sendto)
                assert False
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_245_API_all_packages_email_validation.py', '-s'])
    # ===========================================================================



