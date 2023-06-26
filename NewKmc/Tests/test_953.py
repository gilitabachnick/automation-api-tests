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
import uploadFuncs
import reporter2

import Config
import Practitest

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
            
        
            self.logi = reporter2.Reporter2('TEST953')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")   
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entriesName = "Speical chars,Special chars"

        except Exception as e:
            print(e)
        
    def test_953(self):
        
        global testStatus
        self.logi.initMsg('test 953')
        
        try:
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            
            self.logi.appendMsg("INFO - going to do bulk upload xml")
            self.logi.appendMsg("INFO - going to upload a file with entries names contain special characters")
            
            fname = "xml_file_specialCharacters_entries.xml"
            entries = "Special chars *()_+{}:;,Special chars'?/.>"
            expstatus = "Finished Successfully"
       
            self.logi.appendMsg("INFO - going to upload " + fname)
                    
            theTime = self.uploadfuncs.bulkUpload("entry", fname)
            
            self.logi.appendMsg("INFO - going to verify the bulk upload message window appear with the correct text in it")
            rc = self.uploadfuncs.bulkMessageAndStatus(expstatus, theTime, 900)
            if not rc:
                self.logi.appendMsg("FAILED - bulk upload message window failed to appear with the correct text in it")
                testStatus = False
                return
            
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(3)
            
            entryList = entries.split(",")
            self.logi.appendMsg("INFO- going to verify 2 out of 4 entries because of bug in search for the first 2 entries!!!!")
            for i in entryList:

                self.logi.appendMsg("INFO- going to verify that the entries uploaded and in status Ready")
                entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,i)
                if not entryStatus:
                    self.logi.appendMsg("FAIL - the entry \"" + i + "\"  was not uploaded and should have been!!")
                    testStatus = False
                else:
                     self.logi.appendMsg("PASS - the entry \"" + i + "\" was Uploaded Successfully as expected")
                     
            
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(3)

        except Exception as e:
            print(e)
            testStatus = False
        
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName,",")
        except Exception as e:
            print(e)

        try:
            self.Wd.quit()
        except Exception as e:
            print(e)

        try:
            if testStatus == False:
                self.logi.reportTest('fail',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '953','1')
                assert False
            else:
                self.logi.reportTest('pass',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '953','0')
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    # pytest.main('test_953.py -s')    
    if Run_locally:
        pytest.main(args=['test_953', '-s'])
    # ===========================================================================