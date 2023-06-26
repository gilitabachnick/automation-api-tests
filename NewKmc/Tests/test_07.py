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
import Entrypage

## Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

class TestClass:
    
    #===========================================================================
    # KMCURL = "http://il-kmc-ng2.dev.kaltura.com/latest/login"
    #===========================================================================
    KMCURL = "http://il-kmc-ng.dev.kaltura.com/new-scroll/login"
        
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
            self.user   = inifile.RetIniVal(section, 'userName1')
            self.pwd    = inifile.RetIniVal(section, 'pass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        
        
            self.logi = reporter2.Reporter2('TEST07')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome") 
            self.entrypagefuncs = Entrypage.entrypagefuncs(self.Wd) 
            self.practitest = Practitest.practitest('4586')
        except:
            pass
        
         
    def test_07(self):


        testStatus = True
        
        try:
            self.logi.initMsg('test 07')
            
            '''
            @Login KMC 
            '''
            
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
           
           
            if rc:
                # check first entry and check that bulk actions appear and number of selected entries=1
                self.logi.appendMsg("INFO - going to select one entry and verify that bulk actions object appears")
                            
                if self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg( 'FAIL - Bulk actions appeared before checking an entry')
                    testStatus = False
                    
                self.entrypagefuncs.selectEntries("1")
                if self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg('PASS - Bulk actions appeared after checking an entry')
                else:
                    self.logi.appendMsg('FAIL - Bulk actions DID NOT appeared after checking an entry')
                    testStatus = False
                
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==1:
                    self.logi.appendMsg('PASS - the number of selected entries is 1 as expected')
                else:
                    self.logi.appendMsg('FAIL - the number of selected entries should have been 1 and actually it is: ' + str(selectedEntriesNum)) 
                    testStatus = False
                
                # check 3 more entries and check that and number of selected entries=4
                self.logi.appendMsg('INFO - going to select 3 more entries and check that and number of selected entries=4')
                self.entrypagefuncs.selectEntries("2,5")
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==4:
                    self.logi.appendMsg('PASS - the number of selected entries is: ' + str(selectedEntriesNum)  + ' as expected')
                else:
                    self.logi.appendMsg('FAIL - the number of selected entries is: ' + str(selectedEntriesNum)  + ' and should have been 4') 
                    testStatus = False
                
                
                # select show rows=25 check that no entry selected ,select all and check all selected 
                self.logi.appendMsg('INFO - going to select show rows=25, check that no entry selected ,select all and check all selected')
                self.entrypagefuncs.selectNumOfRowsToShowInTbl(25)
                time.sleep(3)
                
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum!=0:
                    self.logi.appendMsg("FAIL - the selected entries did not disappear after changing the number of rows to show to 25")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - the selected entries disappeared after changing the number of rows to show to 25 as expected")
                     
                self.logi.appendMsg("INFO - going to select all entries")
                self.entrypagefuncs.selectAll()
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==25:
                    self.logi.appendMsg("PASS - the number of selected Entries is 25 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of selected Entries is " + str(selectedEntriesNum) + " NOT as expected")
                    testStatus = False
                    
                time.sleep(5)    
                
                # unselect 3 entries and check number of check change accordingly 
                self.logi.appendMsg('INFO - unselect 3 entries and check number of check change accordingly')
                self.entrypagefuncs.selectEntries("1,4")
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==22:
                    self.logi.appendMsg('PASS - the number of selected entries is 22 as expected') 
                else:
                    self.logi.appendMsg('FAIL - the number of selected entries should have been 22 and actually it is: ' + str(selectedEntriesNum))
                    testStatus = False
                    
                
                # click specific check box multiple times (4) and remain it unselected and check total number is correct
                self.logi.appendMsg('INFO - click specific check box multiple times (4) and remain it unselected and check total number is correct')
                for i in range(1,5):
                    self.entrypagefuncs.selectEntries("1")
                    
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==22:
                    self.logi.appendMsg('PASS - the number of selected entries is 22 as expected') 
                else:
                    self.logi.appendMsg('FAIL - the number of selected entries should have been 22 and actually it is: ' + str(selectedEntriesNum)) 
                    testStatus = False     
                
               
                # uncheck chekAll check box and verify none selected and bulk actions not appear and the find category elements exist
                self.logi.appendMsg('INFO - uncheck chekAll check box and verify none selected and bulk actions not appear and the find category elements exist')
                self.entrypagefuncs.selectAll()
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                self.entrypagefuncs.selectAll()
                
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==0:
                    self.logi.appendMsg('PASS - the selected entries disappear after pressing the UNCHECK ALL check box as expected')
                else:
                   self.logi.appendMsg('FAIL - the selected entries did not disappeared after pressing the UNCHECK ALL check box')
                   testStatus = False
                
                # verify bulk actions disapper
                if not self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg('PASS - Bulk Actions list disappear as expected')
                else:
                    self.logi.appendMsg('FAIL - Bulk Actions list DID NOT disappear as expected after uncheck all entries')
                    testStatus = False
                    
                #verify search options appear
                try:
                    filtobj = self.Wd.find_element_by_xpath(DOM.ENTRIES_FILTER_DIV)
                    if filtobj.get_attribute('class').find('kHidden')==-1:
                        self.logi.appendMsg('PASS - The search option appears as expected after uncheck all entries')
                    else:
                        self.logi.appendMsg('FAIL - The search option DID NOT appear as expected after uncheck all entries')
                        testStatus = False
                except:
                    self.logi.appendMsg('PASS - The search option appears as expected after uncheck all entries')
                    
                 
                # check All and move to next page - verify nexct page entries not selected
                self.entrypagefuncs.selectAll()
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                self.logi.appendMsg('INFO - selected all entries in page total = ' + str(selectedEntriesNum))
                
                # go to next page and check no entries selected
                self.logi.appendMsg('INFO - go to next page and check no entries selected')
                try:
                    self.Wd.find_element_by_xpath(DOM.ENTRIES_PAGING_RIGHT).click()
                    time.sleep(3)
                    self.Wdobj.Sync(self.Wd, "//div[@class='kFilters']")
                except:
                    self.logi.appendMsg('FAIL - Could not move to next page')
                    testStatus = False
                    
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==0:
                    self.logi.appendMsg('PASS - none of the entries is selected after moving to next page as expected')
                else:
                    self.logi.appendMsg('FAIL - ' + str(selectedEntriesNum) + ' entries are still selected after moving to next page NOT AS expected') 
                    testStatus = False
                
                
                 # go to prev page and check no entries selected
                self.logi.appendMsg('INFO - go to prev page and check no entries selected')
                try:
                    self.Wd.find_element_by_xpath(DOM.ENTRIES_PAGING_LEFT).click()
                    self.Wdobj.Sync(self.Wd, "//div[@class='kFilters']")
                except:
                    self.logi.appendMsg('FAIL - Could not move to next page')
                    testStatus = False
                    
                selectedEntriesNum = self.BasicFuncs.retNumberOfSelectedEntries(self.Wd)
                if selectedEntriesNum==0:
                    self.logi.appendMsg('PASS - none of the entries is selected after moving to first page back as expected')
                else:
                    self.logi.appendMsg('FAIL - ' + str(selectedEntriesNum) + ' entries are still selected after moving to first page back, NOT AS expected')
                    testStatus = False 
                    
            else:
                self.logi.appendMsg('FAIL - Kmc did not invoke or could not login correctly with user = ' + self.user + ' and password = ' + self.pwd)
                testStatus = False
        
        except:
            testStatus = False
            pass        
            
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '7','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '7','0')
            assert True       
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        self.Wd.quit()
           
        
            
        
            
        
    # pytest.main(['test_07.py','-s'])
 
        