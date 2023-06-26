# ===============================================================================================================
#  @Author: Zeev Shulman 12/05/2022
#
#  @description:
#      Leader Board: Create new user and 'confirm' it in the Leaderboard
#       - Single user - validate points given & NO bonus, assuming max bonus users already exist
#
# ===============================================================================================================

import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)


# # ========================================================================

import LeaderBoard
import LeaderBoardFuncs
# ========================================================================


import MySelenium
import KmcBasicFuncs
import reporter2

import Config
import Practitest
import RDOM

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

            if isProd:
                section = "Production"
                self.env = 'prod'
                print('===== PRODUCTION ENVIRONMENT =====')

                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.serviceUrl = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
                self.user_secret = inifile.RetIniVal('Environment', 'LeaderBoardUserSecret')
                self.analyticsUrl = inifile.RetIniVal('Environment', 'analyticsUrl')
                self.Partner_ID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
                self.url = inifile.RetIniVal('Environment', 'KMC_URL')
                self.user = "inbal.bendavid@kaltura.com"
                self.pwd = "1q2w3e$R"
            else:
                section = "Testing"
                self.env = 'testing'
                print('===== TESTING ENVIRONMENT =====')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.privileges = "*privacycontext:MediaSpace,enableentitlement"
            self.practitest = Practitest.practitest('17888')
            self.logi = reporter2.Reporter2('test_416_Confirmation_no_Bonus_YouTube')
            self.Leader_board = LeaderBoard.LeaderBoard("prod", "LB_usr1")

            self.excluded_users = []
            exc_user_list = self.Leader_board.retGroupUserList("LBexclude")
            for i in range(0, len(exc_user_list.objects)):
                self.excluded_users.append(exc_user_list.objects[i].userId)

        except Exception as Exp:
            print(Exp)

    def test_416_Confirmation_no_Bonus_YouTube(self):
        global testStatus
        self.logi.initMsg('test_416_Confirmation_no_Bonus_YouTube')
        print("-------------SINGLE USER------------------")
        print("INFO - add a user to PID and 'confirm' it in the Leaderboard")

        # ===========================================================================
        # Login to KMC, KMC_USERS, add n users
        # ===========================================================================
        try:
            # create user in KMC
            self.logi.appendMsg("INFO - login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL -  FAILED to login to KMC")
                return
            time.sleep(1)
            self.Wd.find_element_by_xpath(RDOM.KMC_USERS).click()
            time.sleep(3)

            self.Wd.find_element_by_xpath(RDOM.KMC_USERS_ADD).click()
            time.sleep(1)

            userID_str = str(int(time.time())) # unique name based on time
            name =["Regestree", userID_str[-4:]]

            self.Wd.find_element_by_xpath(RDOM.USERS_ADD_EMAIL).send_keys(userID_str + "@mailinator.com")
            self.Wd.find_element_by_xpath(RDOM.USERS_ADD_FIRSTN).send_keys(name[0])
            self.Wd.find_element_by_xpath(RDOM.USERS_ADD_LASTN).send_keys(name[1])
            self.Wd.find_element_by_xpath(RDOM.PUSER_ID).send_keys(userID_str)
            self.Wd.find_element_by_xpath("//*[text()='Save']").click()
            time.sleep(3)
            print(userID_str + " created")
            if createPass(self, userID_str):
                print(userID_str + " has password")
        except Exception as Exp:
            print(Exp)
            testStatus = False
            return

        # === base line for validation ===
        lbId = 5
        confirm_points = 50
        bonus_points = 50
        try:
            r = LeaderBoardFuncs.register_to_LB(self, userID_str, False) # register_to_LB(self, usr, register_twice=False)
            if r == False:
                print("FAIL - register_to_LB")
                testStatus = False
            time.sleep(1)
            print("INFO - validate user created and score equals confirmation points")
            time.sleep(10)
            confirmation_after = self.Leader_board.getLeaderBoardList(lbId, userID_str)
            if len(confirmation_after.objects) != 0:
                print("After  - " + userID_str + " rank:" + str(confirmation_after.objects[0].rank) + ", score:" + str(
                    confirmation_after.objects[0].score))
                if confirmation_after.objects[0].score == confirm_points:
                    print("PASS")
                else:
                    print("FAIL")
                    testStatus = False
                    if confirmation_after.objects[0].score == confirm_points + bonus_points:
                        print("REMARK: ** score == confirmation + bonus ** check if LB exhausted the bonus")

        except Exception as Exp:
            print(Exp)
            self.logi.appendMsg("FAIL - FAILED to register")
            testStatus = False
            return

    #===========================================================================
    # TEARDOWN
    #===========================================================================
    def teardown_class(self):
        global testStatus
        print("")
        print("---------- Teardown ---------")
        try:
            self.Wd.quit()
        except Exception as Exp:
            print("Teardown quit() Exception")
            print(Exp)

        try:
            if testStatus == True:
                print("  *** PASS ***")
                self.practitest.post(Practi_TestSet_ID, '416', '0')
                assert True
            else:
                print("  *** FAIL ***")
                self.practitest.post(Practi_TestSet_ID, '416', '1')
                assert False
        except Exception as Exp:
            print("Teardown Test Status Exception")
            print(Exp)


    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_416_Confirmation_no_Bonus_YouTube.py', '-s'])
    # ===========================================================================


def createPass(self, usr):
    try:
        self.logi.appendMsg("INFO - opening email massage")
        self.Wd.get("https://www.mailinator.com/v4/public/inboxes.jsp?to=" + usr)
        rc = self.BasicFuncs.wait_element(self.Wd, "//*[contains(text(),'account')]", 180)
        if rc:
            time.sleep(1)
            self.Wd.find_element_by_xpath("//*[contains(text(),'account')]").click()
            self.logi.appendMsg("PASS - opening email massage")
            time.sleep(4)
        else:
            #testStatus = False
            self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find the email massage"))
            return False
    except Exception as Exp:
        print(Exp)
        self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to find the email massage"))
        return False

    try:
        self.logi.appendMsg("INFO - extracting link")
        self.Wd.find_element_by_xpath(RDOM.JASON_TAB).click()
        time.sleep(3)
        txt = str(self.Wd.find_element_by_xpath(RDOM.EMAIL_MSG_JSON).text)
        # Extracting the link from Kaltura's automated response
        txt_chunks = txt.split("https://kmc.kaltura.com")
        txt_chunks_chunks = txt_chunks[1].split("<br")
        link = "https://kmc.kaltura.com"+txt_chunks_chunks[0]
        print(link)
        self.Wd.get(link)
        time.sleep(3)
        self.logi.appendMsg("PASS - extracted link")
        self.logi.appendMsg("INFO - New password")
        PASS1 = '//*[@id="appContainer"]/k-area-blocker/kkmclogin/div/div/div[1]/kkmcrestorepassword/form/div[1]/input'
        PASS2 = '//*[@id="appContainer"]/k-area-blocker/kkmclogin/div/div/div[1]/kkmcrestorepassword/form/div[2]/input'
        self.Wd.find_element_by_xpath(PASS1).send_keys("Dnd!ido202")
        self.Wd.find_element_by_xpath(PASS2).send_keys("Dnd!ido202")
        time.sleep(2)
        self.Wd.find_element_by_xpath("//*[text()='Send']").click()
        self.logi.appendMsg("PASS - New password")
        return True
    except Exception as Exp:
        print(Exp)
        self.logi.appendMsg(self.logi.appendMsg("FAIL -  FAILED to create password"))
        return False
