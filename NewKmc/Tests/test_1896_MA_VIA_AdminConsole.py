'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1896_MA_VIA_AdminConsole.py
 
 @desc : this test check login to Multi account by adminConsole link 

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''

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
import reporter2
import autoitWebDriver

import Config
import Practitest

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
                self.AccountName="Kaltura internal - Moran Cohen"
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.AccountName="moran update1 (Parent Account)"
                                
            self.url    = inifile.RetIniVal(section, 'admin_url')
            self.user   = inifile.RetIniVal(section, 'AdminConsoleUser')
            self.pwd    = inifile.RetIniVal(section, 'AdminConsolePwd')
            self.Partner_ID = inifile.RetIniVal(section, 'AdminConsolePartnerID')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')
            self.admin_user = inifile.RetIniVal('admin_console_access', 'session_user')
            self.env = inifile.RetIniVal('admin_console_access', 'environment')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest()
            self.logi = reporter2.Reporter2('test_1896_MA_VIA_AdminConsole')
            self.practitest = Practitest.practitest('4586')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")   
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
        
        except:
            print('Failed Setup')
    
       
    def test_1896_MA_VIA_AdminConsole(self):
             
        global testStatus

        try:
            self.logi.initMsg('test_1896_MA_VIA_AdminConsole')
            self.logi.appendMsg("INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            if "nv" not in self.url:  # Bypass NVD console user/pass login
                ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass, self.admin_user, self.env)
            else:
                ks = False
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.url,self.user,self.pwd,ks)
            if(rc):
                self.logi.appendMsg("PASS - Admin Console login.")
            else:       
                self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + str(self.user) + " , PWD - " + str(self.pwd))
                testStatus = False
                return
                       
            # Save browser first window 
            primTab = self.Wd.window_handles[0]          
            time.sleep(2)
            self.logi.appendMsg("INFO - Going to set Publisher ID.")
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_PUBLISHER_ID).click()
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_FILTER_TEXT).clear()
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_FILTER_TEXT).send_keys(self.Partner_ID)
            self.logi.appendMsg("INFO - Going to Press on search button.")
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_SEARCH_BTN).click()
            time.sleep(1)
            self.logi.appendMsg("INFO - Going to Press on MA action.")
            self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_MALOGIN_OPTION).click()
            
            time.sleep(4)
            # Go to the second browser window
            SecondTab = self.Wd.window_handles[1]
            self.Wd.switch_to.window(SecondTab)
            time.sleep(4)
            # Open MACONSOLE_ADDNEWACCOUNT_TAB
            self.logi.appendMsg("INFO - Going to press on the MACONSOLE ADDNEWACCOUNT TAB")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_ADDNEWACCOUNT_TAB).click()
            time.sleep(2)
            res = self.Wdobj.Sync(self.Wd,DOM.MACONSOLE_ADDNEWACCOUNT_ADMINNAME)            
            if isinstance(res,bool):
                self.logi.appendMsg("FAIL - ADD NEW ACCOUNT page - NO found ADMINNAME field. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            else:       
                self.logi.appendMsg("PASS - ADD NEW ACCOUNT page - Found ADMINNAME field")
            time.sleep(2)

        # ===========================================================================
        # Next 2 steps canceled. No USAGE REPORT in testing, causes false Fail when running Regression
        # ===========================================================================
            # Open MACONSOLE_USAGEREPORT_TAB
            # self.logi.appendMsg("INFO - Going to press on the MACONSOLE USAGEREPORT_TAB")
            # self.Wd.find_element_by_xpath(DOM.MACONSOLE_USAGEREPORT_TAB).click()
            # time.sleep(3)
            # # Verify first AccountName
            # self.logi.appendMsg("INFO - Going to check first AccountName on MACONSOLE USAGEREPORT_TAB table")
            # MaConsoleUsageReportTable = self.Wd.find_element_by_xpath(DOM.MACONSOLE__USAGEREPORT_TABLE)
            # MaUSAGE_AccountName = MaConsoleUsageReportTable.find_element_by_xpath(DOM.MACONSOLE__USAGEREPORT_TABLE_ACCOUNTSNAME.replace("TEXTTOREPLACE",self.AccountName)).text
            # self.logi.appendMsg("PASS - AccountName in table: " + MaUSAGE_AccountName)
        
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)

    
    def teardown_class(self):
         
        global testStatus
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '1896','1')
                self.logi.reportTest('fail',self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '1896','0')
                self.logi.reportTest('pass',self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)
       
    #===========================================================================
    # pytest.main(args=['test_1896_MA_VIA_AdminConsole.py','-s'])
    # pytest.main('test_1896_MA_VIA_AdminConsole.py -s')    
    #===========================================================================
