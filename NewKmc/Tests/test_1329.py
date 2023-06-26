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
                inifile  = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile     = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.userB   = inifile.RetIniVal(section, 'userName4')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.logi = reporter2.Reporter2('TEST1329')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.adminFuncs = AdministrationFuncs.adminFuncs(self.Wd, self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.practitest = Practitest.practitest('4586')     
            self.userEmail = 'First.Last1330@kaltura.com'
            self.firstName = 'First1330'
            self.lastName  = 'Last1330'
            self.userID    = 'userID_1330'
            
            
            self.logi.appendMsg("INFO - Going to identify the test user " +self.firstName +" "+ self.lastName+" in the Users list and delete it, as a precondition to test run")
            # Login to OwnerA account
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            time.sleep(3)
            
            # Navigate to Administration > Users
            self.logi.appendMsg("INFO - Going to navigate to Administration > Users")
            self.Wd.find_element_by_xpath(DOM.ADMIN_MAIN).click()
            time.sleep(2)
            rc = self.adminFuncs.deleteUser(self.userEmail,self.firstName,self.lastName)
        
        except:
            pass
      
                 
    def test_1329(self):
   
        global testStatus
        self.logi.initMsg('Test 1329: Administration > Add User (non existing)')
    
        try:
            
            # Define number of current and available users for triggering test and later verification
            availableUsersMsg = self.Wd.find_element_by_xpath(DOM.ADMIN_MORE_USERS_MSG).text
            availableUsersNum = availableUsersMsg.split("\n")[1].split(" ")
            currentUsersNum = (availableUsersMsg.split("\n")[1].split(" "))[0]
            
            if int(availableUsersNum[5])>0:
                rc = self.adminFuncs.addUser(self.userEmail,self.firstName,self.lastName,self.userID,currentUsersNum)
                if not rc:
                    testStatus = False
               
            elif int(availableUsersNum[5])==0:
                print(availableUsersNum[5])
                self.logi.appendMsg("INFO - Test did not start running. Available users to add in this account is 0. exiting the test without adding a user")
                testStatus = False
            
            else:
                self.logi.appendMsg("FAIL - problem with number of available KMC users")
                testStatus = False
             
        except:
               testStatus = False
               pass                          
        
        
    def teardown_class(self):
        
        global testStatus
        
        # Deleting the new user that was added during last/previous test:
        try:
            self.adminFuncs.deleteUser(self.userEmail,self.firstName,self.lastName)
        except:
            pass
            
            
        self.Wd.quit()
       
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1329','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1329','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main('test_1329.py -s')
    #===========================================================================
        
                