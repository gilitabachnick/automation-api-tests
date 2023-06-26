import datetime
import os
import sys
import time

from selenium.webdriver.common.by import By

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import KmcBasicFuncs
import reporter2
import Config
import Practitest
import autoitWebDriver


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
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.env = 'prod'
                section = 'Production'
                print('PRODUCTION ENVIRONMENT')
            else:
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.env = 'testing'
                section = 'Testing'
                print('TESTING ENVIRONMENT')            
            self.url = inifile.RetIniVal(section, 'admin_url')
            self.user = inifile.RetIniVal(section, 'AdminConsoleUser')
            self.pwd = inifile.RetIniVal(section, 'AdminConsolePwd')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')
            self.admin_user = inifile.RetIniVal('admin_console_access', 'session_user')
            self.env = inifile.RetIniVal('admin_console_access', 'environment')
            
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
      
            self.logi = reporter2.Reporter2('1448_CREATE_NEW_PARTNER')
            self.logi.initMsg('Add new partner setup')
                       
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
             
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()         
        except:
            pass   
        
    def test_1448_new_partner(self):
        
        global testStatus
         
        try:
            if "nv" not in self.url:  # Bypass NVD console user/pass login
                ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                            self.admin_user, self.env)
            else:
                ks = False
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj, self.logi,self.url, self.user, self.pwd, ks)
            if not rc:   
                self.logi.appendMsg("FAIL - Unable to open admin console!")
                testStatus = False
                return
            try:
                NewPublisher = self.Wd.find_element_by_xpath("//a[contains(text(),'Add New Publisher')]")
            except:
                self.logi.appendMsg('Login to admin console failed')
                testStatus = False
            else:
                self.logi.appendMsg('Login to admin console success! Going to create new partner...')
                currentDT = datetime.datetime.now()
                formatDate = currentDT.strftime("%Y_%m_%d__%H_%M_%S")
                NewPublisher.click()
                self.Wd.find_element_by_id("name").send_keys("AutoNewPartner " + formatDate)
                self.Wd.find_element_by_id("company").send_keys("AutoCompany " + formatDate)
                self.Wd.find_element_by_id("admin_email").send_keys(formatDate + "@mailinator.com")
                self.Wd.find_element_by_id("phone").send_keys("12345678")
                self.Wd.find_element_by_xpath("//select[@id='partner_package']/option[text()='Free Trial Edition']").click()
                self.Wd.find_element_by_id("submit").click()
                #Searching for new partner
                table_id = self.Wd.find_element_by_xpath("//table[@class='clear']")
                rows = table_id.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    if formatDate in row.text:
                        partnerId = row.find_elements(By.TAG_NAME, "td")[1].text
                        userName = row.find_elements(By.TAG_NAME, "td")[2].text
                        
                if 'partnerId' in locals():
                    self.logi.appendMsg('Found partner '+partnerId+' ,going to log in...')
                    time.sleep(20)
                    self.Wd.find_element_by_xpath("//select[@onchange='doAction(this.value, "+partnerId+")']/option[text()='Manage - KMCNG']").click()
                else:
                    self.logi.appendMsg('Partner not found, test FAILED')
                    testStatus = False
                #Checking if log in successful
                self.Wd.switch_to.window(self.Wd.window_handles[1])
                time.sleep(10)
                try:
                    UName = self.Wd.find_element_by_xpath("//div[@class='kUserInitials']").text
                    NumOfEntries = self.Wd.find_element_by_xpath("//span[@class='kSelectedEntriesNum ng-star-inserted']").text
                except:
                    testStatus = False  
                else:
                    self.logi.appendMsg('Logged in to correct new partner with user initals '+UName+' successfully! It has '+NumOfEntries+'entries!')
        except:
            testStatus = False
            pass
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        
        global testStatus 
        
        self.logi.appendMsg('Cleaning up...')  
        try:           
            self.Wd.quit()
        except:
            pass
         
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1448','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1448','0')
            assert True        
    #===========================================================================
    # pytest.main(args=['test_1448_new_partner.py','-s'])
    #===========================================================================
