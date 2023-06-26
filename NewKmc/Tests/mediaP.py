'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_2584_MAConsoleDirect.py
 
 @desc : this test check the Multi acount login  

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''

import os
import sys
import time

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import KmcBasicFuncs
import reporter2

import Config
import Practitest

### Jenkins params ###
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')


testStatus = True

isProd = True

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
                self.AccountName="kaltura update111 (Parent Account)"
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.AccountName="moran update1 (Parent Account)"
                
            self.url    = inifile.RetIniVal(section, 'MaConsoleUrl')
            self.user   = inifile.RetIniVal(section, 'MaConsoleUser')
            self.pwd    = inifile.RetIniVal(section, 'MaConsolePwd')
            self.sendto = inifile.RetIniVal(section, 'sendto') 
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest()
            self.logi = reporter2.Reporter2('test_2584_MAConsoleDirect')
            self.practitest = Practitest.practitest('4586')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")   
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
        
        except:
            pass
    
       
    def test_2584_MAConsoleDirect(self):
             
        global testStatus
        self.logi.initMsg('test_2584_MAConsoleDirect')
        
        
        try:  
            self.logi.appendMsg("INFO - Going to login to MACONSOLE login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.url,self.user,self.pwd)
            if(rc):
                self.logi.appendMsg("PASS - MACONSOLE login (Exist MACONSOLE_ENTRIES_TAB)")
            else:       
                self.logi.appendMsg("FAIL - MMACONSOLE login - NO ADMINCONSOLE_ENTRIES_TAB. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                testStatus = False
                return
                       
            # Open MACONSOLE_ADDNEWACCOUNT_TAB
            self.logi.appendMsg("INFO - Going to press on the MACONSOLE ADDNEWACCOUNT TAB")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_ADDNEWACCOUNT_TAB).click()
            time.sleep(2)
            res = self.Wdobj.Sync(self.Wd,DOM.MACONSOLE_ADDNEWACCOUNT_ADMINNAME)            
            if isinstance(res,bool):
                self.logi.appendMsg("FAIL - ADD NEW ACCOUNT page - NO found ADMINNAME field. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            else:       
                self.logi.appendMsg("PASS - ADD NEW ACCOUNT page - Found ADMINNAME field")
            
            # Open MACONSOLE_USAGEREPORT_TAB
            self.logi.appendMsg("INFO - Going to press on the MACONSOLE USAGEREPORT_TAB")
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_USAGEREPORT_TAB).click()
            
            # Verify first AccountName
            self.logi.appendMsg("INFO - Going to check first AccountName on MACONSOLE USAGEREPORT_TAB table")     
            MaConsoleUsageReportTable = self.Wd.find_element_by_xpath(DOM.MACONSOLE__USAGEREPORT_TABLE)
            MaUSAGE_AccountName = MaConsoleUsageReportTable.find_element_by_xpath(DOM.MACONSOLE__USAGEREPORT_TABLE_ACCOUNTSNAME.replace("TEXTTOREPLACE",self.AccountName)).text
            self.logi.appendMsg("PASS - AccountName in table: " + MaUSAGE_AccountName)
                      
            time.sleep(2)
        
        
        
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - MMACONSOLE login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            pass  
        
          
        
    #===========================================================================
    def teardown_class(self):
         
        global testStatus
         
         
        self.Wd.quit()
         
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '2584','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '2584','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
                    
        
    pytest.main('test_2584_MAConsoleDirect.py -s')    
            
