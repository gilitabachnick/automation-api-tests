import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


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
    
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile     = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile     = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userName2')
            self.userB  = inifile.RetIniVal(section, 'userName4')
            self.pwd    = inifile.RetIniVal(section, 'pass')
            self.pwdB   = inifile.RetIniVal(section, 'pass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.logi = reporter2.Reporter2('TEST1387')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome",True)
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.adminFuncs = AdministrationFuncs.adminFuncs(self.Wd, self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.practitest = Practitest.practitest('4586')
            self.userEmail = str(self.userB)
            self.firstName = 'FirstN_t1387'
            self.lastName  = 'LastN_t1387'
            self.userID    = ''
            
            #self.accountNameB = 'KMC.Kaltura Account'  
            if isProd:
                self.accountNameA = 'AdiKaltu Ra'
            else:
                self.accountNameA = 'AdiKaltu Ra'
                  
            
            # Login to OwnerA account & Delete user from previous run 
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            time.sleep(3)
            self.Wd.find_element_by_xpath(DOM.ADMIN_MAIN).click()
            time.sleep(2)
            self.logi.appendMsg("INFO - Going to identify the test user " + self.userB + " in the Users list and delete it, as a precondition to test run")
            self.adminFuncs.deleteUser(self.userEmail,self.firstName,self.lastName)
            time.sleep(3)
        
        except:
            pass
      
                 
    def test_1387_Admin_AddRegisteredUser (self):
   
        global testStatus
        self.logi.initMsg('Test 1387: Administration > Users > Add a registered user')
        
        try:
            
            # Define number of current and available users for triggering test and later verification
            availableUsersMsg = self.Wd.find_element_by_xpath(DOM.ADMIN_MORE_USERS_MSG).text
            availableUsersNum = availableUsersMsg.split("\n")[1].split(" ")
            currentUsersNum = (availableUsersMsg.split("\n")[1].split(" "))[0]
             
            if int(availableUsersNum[5])>0:
                rc = self.adminFuncs.addUser(self.userEmail,self.firstName,self.lastName,self.userID,currentUsersNum,True)
                if not rc:
                    testStatus = False
                    return
                if self.adminFuncs.verify_user_id(str(self.userEmail)) == False:
                    self.logi.appendMsg("FAIL - user id does not appear in the list as expected (should be same as email address")
                    testStatus = False
                
                                
            elif int(availableUsersNum[5])==0:
                self.logi.appendMsg("INFO - Test did not start running. Available users to add in this account is 0. exiting the test without adding a user")
                testStatus = False
                return
            
            else:
                self.logi.appendMsg("FAIL - The number of available KMC users " + str(availableUsersNum[5]) + " that appears on this page is invalid")
                testStatus = False
                return
             
        except:
               testStatus = False
               return                          

        # Logout  
        self.logi.appendMsg("INFO - Going to Logout OwnerA")
        self.Wd.find_element_by_xpath(DOM.ACCOUNT_USERNAME).click()
        time.sleep(1)
        self.Wd.find_element_by_xpath(DOM.ACCOUNT_LOGOUT).click()
        time.sleep(3)
        
        # Login with UserB and verify it has access to OwnerA's account
        self.logi.appendMsg("INFO - Going to login with userB credentials")
        self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.userB, self.pwdB)
        time.sleep(3)
        self.logi.appendMsg("INFO - Going to switch to "+ self.accountNameA + "'s account")
        self.adminFuncs.change_account(self.accountNameA)

        # Verify Owner and Logged-in User are listed in Users table 
        self.logi.appendMsg("INFO - Going to navigate to Administration > Users")
        self.Wd.find_element_by_xpath(DOM.ADMIN_MAIN).click()
        time.sleep(3)
        
        self.logi.appendMsg("INFO - Going to identify the account OwnerA : " + self.user + " and the logged-in user: "+ self.userB +" in the Admin Users list")
        usersRows = len(self.Wd.find_elements_by_xpath(DOM.ADMIN_USERS_ROW_NAME))
         
        ownerExists = None
        userExists = None
        for u in range(usersRows):
                userInRow = self.basicFuncs.retTblRowName(self.Wd, u+1, tableItem="user")
                if userInRow.find(self.accountNameA)>=0:
                    ownerExists = True
                    self.logi.appendMsg("PASS - Account owner " + self.accountNameA + "'s details were found in Users list")
                elif userInRow.find(self.firstName)>=0 and userInRow.find(self.lastName)>=0:
                    userExists = True
                    self.logi.appendMsg("PASS - Added (logged in) user " + self.firstName + " " + self.lastName + " exists in Users list")
                else:
                    continue
                
                 
        if userExists and ownerExists:  
            self.logi.appendMsg("PASS - Both the account owner and the added user " + self.firstName + " " + self.lastName + " appear in Users list")
            testStatus = True
        else:         
            self.logi.appendMsg("FAIL - Details of Account owner and added user were not found in Users list as expected")
            testStatus = False
            
    
               
        

        
    def teardown_class(self):
        
        global testStatus
        
        
        try:
            # Logout UserB and login back to OwnerA's account again
            self.logi.appendMsg("INFO - Going to Logout userB")
            self.Wd.find_element_by_xpath(DOM.ACCOUNT_USERNAME).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.ACCOUNT_LOGOUT).click()
            time.sleep(3)           
            # Deleting the new user that was added during the test:
            self.logi.appendMsg("INFO - Going to login with OwnerA credentials again and delete the new user that was added during the test ")
            self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            time.sleep(3)
            rc = self.adminFuncs.deleteUser(self.userEmail,self.firstName,self.lastName)
            
            self.Wd.quit()
            
        except:
            pass
            
            
        
       
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1387','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1387','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main(['test_1387_Admin_AddRegisteredUser.py -s'])
    #===========================================================================
    
    
                