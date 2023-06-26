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
            self.logi = reporter2.Reporter2('TEST1360 Verify Moderation Player')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.practitest = Practitest.practitest('4586')
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            
                      
            #Login to KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            
            #Bulk upload for testing the moderation
            fileName = "xml_file_uploadEntries_moderation_test1360.xml"
            expstatus = "Almost Done"
            theTime = str(datetime.datetime.time(datetime.datetime.now()))[:5]

            self.uploadfuncs.bulkUpload("entry", fileName)
            self.uploadfuncs.bulkMessageAndStatus(expstatus, theTime)
            if not expstatus:
                self.logi.appendMsg("FAIL - the xml \"xml_file_uploadEntries_moderation_test1360.xml\" status was not changed to Finished Successfully after 5 minutes")
                testStatus = False
            else:
                self.Wd.find_element_by_xpath(DOM.MODERATION_TAB).click()
                time.sleep(2)
                    
        except:
            pass    
               
            
    def test_1360(self):
        
        global testStatus
        
        if testStatus == True:
        
            self.entryNames = ["\"test 1000_1\"", "\"test 1000_2\""]
              
            try:
                self.logi.initMsg('test 1360 Moderation > Verify Moderation Player')
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "\"test 1000_1\"")
                self.logi.appendMsg("INFO - going to open moderation player window")
                self.Wd.find_element_by_xpath(DOM.ENTRY_ROW_NAME).click()
                time.sleep(2)
                self.logi.appendMsg("INFO - going to check that moderation player window opens")     

                try:       
                    self.Wd.find_element_by_xpath(DOM.MODERATION_PLAYER_WINDOW)
                    time.sleep(2)
                    self.logi.appendMsg("PASS - moderation player window is open as expected")
                except:
                    self.logi.appendMsg("FAIL - moderation player window didn't open as expected")
                    testStatus = False 
                time.sleep(2)
                
                try:
                    self.logi.appendMsg("INFO - going to approve media, entry - test 1000_1")
                    self.Wd.find_element_by_xpath(DOM.MODERATION_APPROVE_ENTRY).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.MODERATION_YES_BUTTON).click()
                    time.sleep(2)
                    self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "\"test 1000_2\"")
                    self.Wd.find_element_by_xpath(DOM.ENTRY_ROW_NAME).click()
                    time.sleep(2)
                    self.logi.appendMsg("INFO - going to reject media, entry - test 1000_2")
                    self.Wd.find_element_by_xpath(DOM.MODERATION_REJECT_ENTRY).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.MODERATION_YES_BUTTON).click()
                    time.sleep(2)    
                except:
                   self.logi.appendMsg("FAIL - fail in approved or rejected one or both of the medias")
                   testStatus = False 
                time.sleep(2) 
                    
                self.logi.appendMsg("INFO - going to check that approved media is displayed in Entries table")
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                
                #Search both entries in entries table, one that was approved should appear and the rejected one should not appear
                for entryName in self.entryNames:
                    self.BasicFuncs.searchEntrySimpleSearch(self.Wd, entryName)
                    time.sleep(2)
                    currEntryName = self.BasicFuncs.retTblRowName(self.Wd, 1)
                    if entryName == 'test 1000_1':
                        if not isinstance(currEntryName,bool):
                            self.logi.appendMsg("PASS - approved media - " + entryName + " is displayed in Entries table as expected")
                        else:
                            self.logi.appendMsg("FAIL - approved media - " + entryName + " is not displayed in Entries table")
                    if entryName == 'test 1000_2':
                        self.logi.appendMsg("INFO - going to check that rejected media is not displayed in Entries table")
                        if isinstance(currEntryName,bool):
                            self.logi.appendMsg("PASS - rejected media - " + entryName + " is NOT displayed in Entries table as expected")
                        else:
                            self.logi.appendMsg("FAIL - rejected media - " + entryName + " is displayed in Entries table")
            
               
            except:
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
            self.practitest.post(Practi_TestSet_ID, '1360', '1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1360', '0')
            self.logi.reportTest('pass',self.sendto)
            assert True
        
        
            
        
    #===========================================================================
    # pytest.main(args=['test_1360_Moderation_Player.py','-s'])
    #===========================================================================
        
        