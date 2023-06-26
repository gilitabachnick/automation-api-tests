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
            self.user   = inifile.RetIniVal(section, 'uModeration')
            self.pwd    = inifile.RetIniVal(section, 'pModeration')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1236 Approve Moderation')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.practitest = Practitest.practitest('4586')
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            
                      
            #Login to KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            
            #Bulk upload for testing the moderation
            fileName = "xml_file_uploadEntries_test1000.xml"
            expstatus = "Finished Successfully"
            theTime = str(datetime.datetime.time(datetime.datetime.now()))[:5]

            self.uploadfuncs.bulkUpload("entry", fileName)
            self.uploadfuncs.bulkMessageAndStatus(expstatus, theTime)
            if not expstatus:
                self.logi.appendMsg("FAIL - the xml \"xml_file_uploadEntries_test1000.xml\" status was not changed to Finished Successfully after 5 minutes")
                testStatus = False
            else:
                self.Wd.find_element_by_xpath(DOM.MODERATION_TAB).click()
                time.sleep(2)
                    
        except:
            pass
            
    
    def test_1236(self):
        
        global testStatus
        
        if testStatus == True:
            
            self.logi.initMsg('test 1236 Moderation > Approve Moderation')
            self.entryNames = ['"test 1000_4"', '"test 1000_3"', '"test 1000_2"', '"test 1000_1"']
            
            try:               
                

                for i in range(0,2):
                    
                    time.sleep(3)
                    if i==0:
                        self.BasicFuncs.searchEntrySimpleSearch(self.Wd, self.entryNames[0])
                        time.sleep(5)
                        self.logi.appendMsg("INFO - going to select 'Approve' moderation via Action Menu for single entry")
                        self.BasicFuncs.tblSelectAction(self.Wd, 0, "Approve")
                        
                    else:
                       self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "test 1000_*")
                       time.sleep(5)
                       self.logi.appendMsg("INFO - going to select 'Approve' moderation via Bulk Action for multiple entries")
                       self.BasicFuncs.CheckUncheckRowInTable(self.Wd, 0)
                       self.BasicFuncs.bulkSelectAction(self.Wd, "Approve")
                       
                    time.sleep(3)
                    self.logi.appendMsg("INFO - going to check notification message for approve media")
                    popupMessageText = self.Wd.find_element_by_xpath(DOM.MODERATION_APPROVE_MSG)
                    msgtxt = popupMessageText.text
                    
                    if msgtxt.find("Moderation: Approve Media")>=0:
                       self.logi.appendMsg("PASS - the notification message text is displayed as expected")
                    else:
                       self.logi.appendMsg("FAIL - the notification message text is not displayed as expected" + msgtxt)
                       testStatus = False 
        
                    self.logi.appendMsg("INFO - going to approve media by pressing on 'YES' button")
                    self.Wd.find_element_by_xpath(DOM.GLOBAL_YES_BUTTON).click()
                    time.sleep(5)
                
                self.logi.appendMsg("INFO - going to check that approved media is displayed in Entries table")
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                
                
                for entryName in self.entryNames:
                    self.BasicFuncs.searchEntrySimpleSearch(self.Wd, entryName)
                    time.sleep(2)
                    currEntryName = self.BasicFuncs.retTblRowName(self.Wd, 1)
                    if not isinstance(currEntryName,bool):
                        self.logi.appendMsg("PASS - approved media - " + entryName + " is displayed in Entries table as expected")
                    else:
                        self.logi.appendMsg("FAIL - approved media - " + entryName + " is not displayed in Entries table")
                        testStatus = False

               
            except Exception as error:
                print(error)
                testStatus = False
                pass
            
        else:
            testStatus = False

    
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd, "test 1000_*")
        except:
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1236','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1236','0')
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main('test_1236_Moderation_Approve.py -s')
    #===========================================================================
        
        
