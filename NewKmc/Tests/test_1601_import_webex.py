import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
sys.path.insert(1,pth)


import DOM
import webexFuncs
import MySelenium
import KmcBasicFuncs
import reporter2

import Config
import Practitest
import autoitWebDriver


Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    Practi_TestSet_ID = '2043'
else:
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
        global testStatus          
        try:       
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
                
            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userNameIlia')
            self.pwd = inifile.RetIniVal(section, 'passIlia')       
            self.wurl = inifile.RetIniVal(section, 'WebexURL')
            self.wuser = inifile.RetIniVal(section, 'WebexUser')
            self.wpwd = inifile.RetIniVal(section, 'WebexPass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.WebexFuncs = webexFuncs.webexFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1601_import_webex')
            self.logi.initMsg('Webex recording import setup...')
                       
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome", fakeWebcam = True)
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()

        except Exception as Exp:
            print(Exp)
            testStatus = False
            
    def test_1601_import_webex(self):
        global testStatus
        #Record webex entry
        try: 
            RecordMeeting = self.WebexFuncs.recordMeeting(self.Wd, self.wurl, self.wuser, self.wpwd, 40, 900)
            if not RecordMeeting[0]:
                self.logi.initMsg(RecordMeeting[1])
            else:
                self.EntryName = RecordMeeting[1]
        except:
            testStatus = False
            return
        #Checking if entry uploaded to Kaltura
        rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
        time.sleep(5)
        Result = self.BasicFuncs.waitForEntryCreation(self.Wd, self.EntryName , 900)
        if not Result:
            testStatus = False
            self.logi.appendMsg("ERROR! Entry not found after 300 seconds!")
            pass
        self.logi.appendMsg("Entry Found, "+Result[1])   
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown(self): 
        global testStatus
        self.logi.appendMsg('Cleaning up...')  
        try:           
            self.Wd.quit()
        except:
            pass
         
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1601','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1601','0')
            self.logi.reportTest('pass',self.sendto)
            assert True  
    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_1601_import_webex.py','-s'])
    #===========================================================================
