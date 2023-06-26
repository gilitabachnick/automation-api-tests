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
    isProd = True
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
            
            self.logi = reporter2.Reporter2('TEST943')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")   
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)

        except Exception as e:
            print(e)

            
    def test_943(self):
        
        global testStatus
        self.logi.initMsg('test 943')
        
        try:
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            self.logi.appendMsg("INFO - going to do bulk upload csv")
            self.logi.appendMsg("INFO - going to upload 3 different files with wrong data - entries should not created")

            for i in range(0,4):
                    
                if i==0:
                    fname = "csv_file_with_invalid_url.csv"
                    entries = "Home"
                    expstatus = "Failed"
                elif i==1:
                    fname = "csv_file_without_url_-_entries.csv"
                    entries = "Home,Companies to watch,Creating together,Titanic in 5 Seconds,Humor,Big Buck Bunny Trailer" 
                    expstatus = "Failed"
                elif i==2:
                    fname = "csv_invalid_file_entries.csv"
                    entries = ""
                    expstatus = "Failed"
                else:
                    fname = "csv_empty_file_entries.csv" 
                    entries = ""
                    expstatus = "Finished Successfully"
                    
                   
                self.logi.appendMsg("INFO - going to upload " + fname)
                theTime = str(datetime.datetime.time(datetime.datetime.now()))[:5]
                
                self.uploadfuncs.bulkUpload("entry", fname)
                time.sleep(10)
                self.logi.appendMsg("INFO - going to verify the bulk upload message window appear with the correct text in it")
                rc = self.uploadfuncs.bulkMessageAndStatus(expstatus, theTime)
                if not rc:
                    self.logi.appendMsg(
                        "FAIL - failed to verify the bulk upload message window appear with the correct text in it")
                    testStatus = False
                    return

                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                
                if entries != "":
                    entryList = entries.split(",")
                    for i in entryList:
                        self.logi.appendMsg("INFO- going to verify that no entries uploaded")
                        entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,i)
                        if not entryStatus and lineText=="NoEntry":
                            self.logi.appendMsg("PASS - the entry \"" + i + "\" was not created as expected")
                        else:
                             self.logi.appendMsg("FAIL - the entry \"" + i + "\"  uploaded and should not be!!")
                             testStatus = False
                

            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(3)

        except Exception as e:
            print(e)
            testStatus = False

    def teardown_class(self):
        
        global testStatus

        try:
            self.BasicFuncs.deleteEntries(self.Wd,"Home;Companies to watch;Creating together;Titanic in 5 Seconds;Humor;Big Buck Bunny Trailer",entriesSeparator=";")
        except Exception as e:
            print(e)

        try:
            self.Wd.quit()
        except Exception as e:
            print(e)

        try:
            if testStatus == False:
                self.logi.reportTest('fail',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '943','1')
                assert False
            else:
                self.logi.reportTest('pass',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '943','0')
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    # pytest.main('test_943.py -s')    
    if Run_locally:
        pytest.main(args=['test_943', '-s'])
    # ===========================================================================