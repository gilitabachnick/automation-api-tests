###Media Repurposing 


import datetime
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

import Config
import Practitest
import autoitWebDriver


#### Jenkins params ###
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
                self.user   = inifile.RetIniVal(section,'userElla')
                self.pwd    = inifile.RetIniVal(section,'passElla')
                self.Partner_ID = inifile.RetIniVal(section, 'partnerElla')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.user   = inifile.RetIniVal(section,'AdminConsoleUser')
                self.pwd    = inifile.RetIniVal(section,'AdminConsolePwd')
                self.Partner_ID = inifile.RetIniVal(section, 'partnerId4770')
                
            self.url    = inifile.RetIniVal(section,'admin_url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')
            self.admin_user = inifile.RetIniVal('admin_console_access', 'session_user')
            self.env = inifile.RetIniVal('admin_console_access', 'environment')
           
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            
            self.practitest = Practitest.practitest()
            self.logi = reporter2.Reporter2('test_2869_MR_Create')
            self.practitest = Practitest.practitest('2869')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome",True) #true for local debugung comment for remote running
             
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()         
        except:
            pass   
        
    def test_2869_MR_Create(self):
        
        global testStatus
        self.logi.initMsg('Add new MR test_2869_MR_Create')
        
        
        try:  
            self.logi.appendMsg("INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
            ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass, self.admin_user, self.env)
            rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.url,self.user,self.pwd,ks)
            if(rc):
                self.logi.appendMsg("PASS - Admin Console login.")
            else:       
                self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                testStatus = False
                return 
        except:
            pass
        self.logi.appendMsg('Login to admin console success! Going to find partner...')
        self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_PUBLISHER_ID).click()
        time.sleep(1)
        self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_FILTER_TEXT).send_keys(self.Partner_ID)
        self.Wd.find_element_by_xpath("//button[@id='do_filter']").click() #ADMINCONSOLE_SEARCH_BTN
        self.Wd.find_element_by_xpath(DOM.MACONSOLE_ACTIONS).click()
        self.Wd.find_element_by_xpath(DOM.ADMINCONSOLE_MR_OPTION).click()
        #verify media repurposing screen opened 
        try: 
            self.Wd.find_element_by_xpath("//select[@id='filterType']").click() #MR_FILTER_BY_PARTNER
        except:
            testStatus = False
        self.logi.appendMsg('media repurposing screen opened')
        # create a function to run it for all templates
        self.logi.appendMsg('Add new MR from template')  
        self.Wd.find_element_by_xpath("//select[@id='template']").click() #MR_CHOOSE_TEMPLATE
        time.sleep(1)
        self.Wd.find_element_by_xpath(DOM.MR_SET_TEMPLATE.replace("TEXTTOREPLACE","Archive and Delete")).click() 
        time.sleep(1)
        submitbtns = self.Wd.find_elements_by_xpath("//button[@id='submit']")[1].click() #MR_CREATE_BTN_TEMPLATE
        time.sleep(1)
        try:
            self.Wd.find_element_by_xpath("//input[@id='media_repurposing_name']").clear() #MR_NAME
            self.Wd.find_element_by_xpath("//input[@id='media_repurposing_name']").send_keys("4770_create_from_template")
        except: 
            self.logi.appendMsg('create media repurposing profile screen opened')
            testStatus = False 
        self.Wd.find_element_by_xpath("//input[@id='max_entries_allowed']").clear() #MR_MAX_ENTRIES
        self.Wd.find_element_by_xpath("//input[@id='max_entries_allowed']").send_keys('5')
        time.sleep(1)
        self.Wd.find_element_by_xpath("//input[@id='FilterParams_createdAtLessThanOrEqual']").clear() #MR_CREATED_AT_LESS_THAN_OR_EQUAL
        time.sleep(1)
        theDate = str(datetime.datetime.now())[:10].replace("-",".")
        if int(theDate[-2:])<10:
           theDate = theDate.replace(theDate[-2:],theDate[-1:]) 
        self.Wd.find_element_by_xpath("//input[@id='FilterParams_createdAtLessThanOrEqual']").send_keys(theDate)
        time.sleep(5)
        self.Wd.find_element_by_xpath("//button[@id='expandFilter']").click() #MR_EXPAND_FILTER
        time.sleep(1)
        self.Wd.find_element_by_xpath("//input[@id='FilterParams_nameLike']").clear() #MR_ENTRY_NAME_LIKE
        self.Wd.find_element_by_xpath("//input[@id='FilterParams_nameLike']").send_keys("test") 
        self.Wd.find_element_by_xpath("//input[@id='mr_task_0-taskTime']").clear()
        self.Wd.find_element_by_xpath("//input[@id='mr_task_0-taskTime']").send_keys("0") 
        self.Wd.find_element_by_xpath("//input[@name='mailTo']").clear()
        self.Wd.find_element_by_xpath("//input[@name='mailTo']").send_keys("ella.lidich@kaltura.com") 
        self.Wd.find_element_by_xpath("//input[@name='sender']").clear()
        self.Wd.find_element_by_xpath("//input[@name='sender']").send_keys("sender@kaltura.com")
        self.Wd.find_element_by_xpath("//input[@name='subject']").clear()
        self.Wd.find_element_by_xpath("//input[@name='subject']").send_keys("subject")
        self.Wd.find_element_by_xpath("//textarea[@name='message']").send_keys("_message_")
        self.Wd.find_element_by_xpath("//textarea[@name='footer']").clear()
        self.Wd.find_element_by_xpath("//textarea[@name='footer']").send_keys("_footer_")
        self.Wd.find_element_by_xpath("//input[@name='link']").clear()
        self.Wd.find_element_by_xpath("//input[@name='link']").send_keys("http://{partner_id}.qakmstest.dev.kaltura.com/media/{entry_id}")
        #self.Wd.find_element_by_xpath("//input[@id='TaskData_1::link']").send_keys("http://{partner_id}.mediaspace.kaltura.com/media/{entry_id}")
        self.Wd.find_element_by_xpath("//input[@id='mr_task_1-taskTime']").clear()
        self.Wd.find_element_by_xpath("//input[@id='mr_task_1-taskTime']").send_keys("0")
        time.sleep(1)
        self.Wd.find_element_by_xpath("//span[text()='Save']").click()
        time.sleep(2)
        self.logi.appendMsg("find created MR")
        rowsArr = self.Wd.find_elements_by_xpath("//tr[*]")
        for i in (rowsArr):
            if i.text.find("4770_create_from_template")>=0:
                selectOption = i.find_element_by_xpath(".//select[@class='options']")
                selectOption.click()
                time.sleep(1)
                selectOption.find_element_by_xpath(".//option[@value='remove']").click()
                # approve alert message
                alert = self.Wd.switch_to_alert()
                alert.accept()
                time.sleep(1)
                alert.accept()
                self.Wd.switch_to.default_content()
                break
        
        try: 
            self.logi.appendMsg("created MR deleted ")
            time.sleep(1)
        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - to delete MR, MR name: 4770_create_from_template" + self.user + " , PWD - " + self.pwd)
            pass  
        
            
        
   
    def teardown_class(self):
         
        global testStatus
         
         
        self.Wd.quit()
         
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '2869','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '2869','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
    #===========================================================================
    # pytest.main(args=['test_2869_MR_Create.py','-s'])
    # pytest.main('test_2869_MR_Create.py -s')    
    #===========================================================================