import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import DOM
import MySelenium
import KmcBasicFuncs
import AdministrationFuncs
import reporter2

import Config
import Practitest
import Entrypage

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
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

        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userName5')
            self.userB = inifile.RetIniVal(section, 'userName4')
            self.pwd = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.logi = reporter2.Reporter2('TEST1124')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.adminFuncs = AdministrationFuncs.adminFuncs(self.Wd, self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            self.userEmail = 'First.Last1124@kaltura.com'
            self.invalidUserEmail = 'First.Last'
            self.firstName = 'First1124'
            self.lastName = 'Last1124'
            self.userID = 'userID_1124'

        except:
            pass

    def test_1124(self):

        global testStatus
        self.logi.initMsg('Test 1124: Administration > Edit User - publisher user ID ')

        try:
            # Invoke and login
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return

            time.sleep(1)

            try:
                self.adminFuncs.deleteUser(self.userEmail, self.firstName, self.lastName)
            except:
                pass

            self.logi.appendMsg("INFO - step 2: Going to add a user")
            # Navigate to Administration > Users
            self.logi.appendMsg("INFO - Going to navigate to Administration > Users")
            self.Wd.find_element_by_xpath(DOM.ADMIN_MAIN).click()

            time.sleep(8)

            # Define number of current and available users for triggering test and later verification
            availableUsersMsg = self.Wd.find_element_by_xpath(DOM.ADMIN_MORE_USERS_MSG).text
            availableUsersNum = availableUsersMsg.split("\n")[1].split(" ")
            time.sleep(3)
            currentUsersNum = (availableUsersMsg.split("\n")[1].split(" "))[0]

            if int(availableUsersNum[5]) >= 0:
                rc = self.adminFuncs.addUser(self.userEmail, self.firstName, self.lastName, '',
                                             currentUsersNum)
                if not rc:
                    testStatus = False

            elif int(availableUsersNum[5]) == 0:
                print(availableUsersNum[5])
                self.logi.appendMsg("INFO - Test did not start running. Available users to add in this account is 0. deleting user from list")
                rc = self.adminFuncs.deleteUser(self.userEmail, self.firstName, self.lastName)
                time.sleep(8)
                if not rc:
                    self.logi.appendMsg("FAIL - Could not delete User from list, exit test")
                    testStatus = False
                    return



            if testStatus == True:
                self.logi.appendMsg("Pass - step 2")
            else:
                self.logi.appendMsg("FAIL - problem with number of available KMC users")
                testStatus = False

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to verify userID is the same as email address")
            if self.adminFuncs.verify_user_id(self.userEmail) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to verify userID is the same as email address")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to edit user id without saving")
            if self.adminFuncs.edit_user_id(user_to_edit='First1124 Last1124' ,user_id_text_input='23', append=True, save_changes=False) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to edif user id without saving")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4.1: Going to verify userID is the same as email address")
            if self.adminFuncs.verify_user_id(self.userEmail) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4.1: FAILED to verify userID is the same as email address")
                return
            else:
                self.logi.appendMsg("Pass - step 4.1")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to edit user id with saving")
            if self.adminFuncs.edit_user_id(user_to_edit='First1124 Last1124' ,user_id_text_input='23', append=True, save_changes=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to edif user id with saving")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5.1: Going to verify userID is NOT the same as email address")
            if self.adminFuncs.verify_user_id(self.userEmail) == True:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5.1: FAILED to verify userID is the same as email address")
                return
            else:
                self.logi.appendMsg("Pass - step 5.1")

            time.sleep(1)


        except Exception as e:
            print(e)
            testStatus = False
            pass

    def teardown_class(self):

        global testStatus

        try:
            self.adminFuncs.deleteUser(self.userEmail, self.firstName, self.lastName)
        except:
            pass


        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1124', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1124', '0')
            assert True

    #===========================================================================
    # pytest.main('test_1124.py -s')
    #===========================================================================

