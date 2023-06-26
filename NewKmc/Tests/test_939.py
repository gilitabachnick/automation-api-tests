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
import uploadFuncs
import Config
import Practitest
import autoitWebDriver
import pytest

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '1418'
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
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST939')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entriesName = "Home;Companies to watch;Creating together;Titanic in 5 Seconds"
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
        except Exception as Exp:
            print(Exp)
         
    def test_939(self):
        
        global testStatus
        self.logi.initMsg('test 939')
        
        try:
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
              
            self.logi.appendMsg("INFO - going to do bulk upload")
            self.logi.appendMsg("INFO - going to upload csv file - test939.csv")

            self.uploadfuncs.bulkUpload("entry", 'test939.csv')
            self.logi.appendMsg("INFO - going to verify the bulk upload message window appear with the correct text in it")

            the_time = str(datetime.datetime.time(datetime.datetime.now()))[:5]
            rc = self.uploadfuncs.bulkMessageAndStatus("Finished successfully", the_time,900)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAILED - bulk upload message window failed to appear with the correct text in it")
                return
            
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            entryList = self.entriesName.split(";")
            self.logi.appendMsg("INFO- going to verify that the entries uploaded and in status Ready")
            for i in entryList:
                entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,i)
                if not entryStatus:
                    self.logi.appendMsg("FAIL - the entry \"" + i + "\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                    testStatus = False
                    return
                else:
                     self.logi.appendMsg("PASS - the entry \"" + i + "\"  uploaded successfully")

            # verify entry meta data
            self.logi.appendMsg("INFO- going to verify that the entries metadata uploaded correct")
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, entryList[0])
            
            try:
                permissionVal = self.Wd.find_element_by_xpath(DOM.METADATA_WATCHPERMISSION).text
                if permissionVal == "":
                    self.logi.appendMsg("PASS - The watch permission rule field in custom meta data is empty as expected")
                else:
                    self.logi.appendMsg("FAIL - The watch permission rule field in custom meta data is Not empty as expected and has the value- " + permissionVal)
                    testStatus = False
            except Exception as e:
                print(e)
                self.logi.appendMsg("FAIL - could not find the custom meta data field name: watch permission rule in custom meta data page")
                testStatus = False

        except Exception as e:
            print(e)
            testStatus = False
    
    
    def teardown_class(self):
        
        global testStatus
        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(1)
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName)
        except Exception as e:
            self.logi.appendMsg("Teardown - failed to delete entries")
            print(e)

        try:
            self.Wd.quit()
        except Exception as e:
            print(e)

        try:
            if testStatus == False:
                self.logi.reportTest('fail',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '939','1')
                assert False
            else:
                self.logi.reportTest('pass',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '939','0')
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_939', '-s'])
    # ===========================================================================
