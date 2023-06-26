import os
import sys
import time

from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import Config
import KmcBasicFuncs
import Practitest
import reporter2


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
            self.user   = inifile.RetIniVal(section, 'userName1')
            self.pwd    = inifile.RetIniVal(section, 'pass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST80')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        except:
            pass
        
    def test_80(self):
        
        self.logi.initMsg('test 80')

        global testStatus
        
        try:
            #Login KMC
            self.Wd.maximize_window()
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            
            if rc:
                
                # make sure no filter is set, press the clear all if exist
                try:
                    self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
                    time.sleep(2)
                except:
                    pass
                
                self.logi.appendMsg("INFO - Going to set category filter = MainCategory1")
                rc = self.BasicFuncs.selectCategoryFilter(self.Wd, 'MainCategory1')
                if not rc:
                   self.logi.appendMsg("Fail - could not find the category MainCategory1")
                    
                
                entryTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 13:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 13 and it is 13 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 13 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False
                     
                           
                # Refine filter to media->video only exp result = 3 entry 
                self.logi.appendMsg("INFO -Going to add Refine filter of Media Types-> Audio")
                self.BasicFuncs.selectRefineFilter(self.Wd,'Media Types;Audio')
                time.sleep(2)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 3:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 3 and it is 3 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 3 and it is " + str(len(entryRows)-1) + " NOT as expected") 
                    testStatus = False
                             
                
                #going to add search filter of AudioAdmin 
                self.logi.appendMsg("INFO - going to add search filter of AudioAdmin")
                search = self.Wd.find_element_by_xpath(DOM.SEARCH_ENTRIES)
                search.send_keys('AudioAdmin' + Keys.RETURN)
                time.sleep(3)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 2:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 2 and it is 2 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 2 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False
                    
                
                # take the tags that table is filtered with before replacing the text
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                                       
                
                # replace text filter with other text filter
                self.logi.appendMsg("INFO -Going to replace the free text filter with the value - ReplaceTag")
                search.clear()
                search.send_keys('ReplaceTag' + Keys.RETURN)
                time.sleep(3)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 3:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 3 and it is 3 as expected")
                else:
                    self.logi.appendMsg("FAIL -the number of entries in the table should have been 3 and it is " + str(len(entryRows)-1) + " NOT as expected") 
                    testStatus = False
                    
                # verify that filters tags remain as they were and only the last one changed
                FilterTags2 = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags2)!=len(FilterTags):
                    self.logi.appendMsg("FAIL -the number of filter tags should have been 3 same as before and it is " + str(len(FilterTags2)))
                
                tempStatus = True
                for i in range(0,len(FilterTags2)):   
                    if i<len(FilterTags2)-1:
                        if FilterTags[i].text == FilterTags2[i].text:
                            continue
                        else:
                            self.logi.appendMsg("FAIL - the filter tag #" + str(i) + " should have been " + FilterTags[i].text + " and it is: " + FilterTags2[i].text)
                            tempStatus = False
                    else:
                        if FilterTags2[i].text != "ReplaceTag":
                            self.logi.appendMsg("FAIL - the filter text tag value was NOT replaced ok")
                            tempStatus = False      
                # both conditions occur
                if tempStatus:
                    self.logi.appendMsg("PASS - The free text filter was replaced OK")
                else:
                    testStatus = False
                    
                    
                # add refine filters and verify tags scroll
                scrollTags = self.Wd.find_element_by_xpath(DOM.ENTRY_FILTERS_TAG_SCROLL)
                isVisible = str(scrollTags.get_attribute('style'))
                if isVisible.find("visible")!=-1:
                    self.logi.appendMsg("WARNING -  the tags scroll was visible when when it only have 3 filter tags")
                    
                self.logi.appendMsg('INFO - Going to add Refine filters of ingestion Statuses and Durations')
                self.BasicFuncs.selectRefineFilter(self.Wd,'Ingestion Statuses')
                self.BasicFuncs.selectRefineFilter(self.Wd,'Durations')
                time.sleep(2)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 3:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 3 and it is 3 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 3 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False 
                             
                # check that scroll arrows appear and there are 12 tags
                FilterTags3 = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags3)==12:
                    self.logi.appendMsg("PASS - there are 12 filter tags as expected")
                else:
                    self.logi.appendMsg( "FAIL - should have been 12 filter tags and actually there are: " + str(len(FilterTags3)))
                    testStatus = False
                    
                isVisible = str(scrollTags.get_attribute('style'))
                if isVisible.find("visible")!=1:
                    self.logi.appendMsg( "PASS -  the tags scroll is visible as expected")
                else:
                    self.logi.appendMsg( "FAIL - the tags scroll is NOT visible as should have been")
                    testStatus = False
                    
                    
                #verify scroll right and left are clickable
                self.logi.appendMsg( "INFO - going to check that scroll right and left are click able")
                scrolRight = self.Wd.find_element_by_xpath(DOM.ENTRY_TAGS_RIGHT_SCROLL) 
                scrolLeft = self.Wd.find_element_by_xpath(DOM.ENTRY_TAGS_LEFT_SCROLL)
                tmpStatus = True
                if 'disable' not in str(scrolLeft.get_attribute('class')) or 'disable' in str(scrolRight.get_attribute('class')):
                    tmpStatus = False

                scrolRight.click()
                time.sleep(5)
                if 'disable' in str(scrolLeft.get_attribute('class')) or 'disable' not in str(scrolRight.get_attribute('class')):
                    tmpStatus = False
                
                if tmpStatus:
                    self.logi.appendMsg( "PASS - the scroll left and right are click able as expected")
                else:
                    self.logi.appendMsg( "FAIL - the scroll left and right are NOT click able as it should be")
                    testStatus = False
                    
                scrolLeft.click()
                time.sleep(2)
                    
                # remove filer tags  "Media Type: Audio" "MainCategory1", verify there are 17 entries
                self.logi.appendMsg( "INFO - Going to remove filer tags  Media Type: Audio MainCategory1, verify there are 12 entries")
                self.BasicFuncs.closeFilterTag(self.Wd, "MainCategory1")
                time.sleep(2)
                self.BasicFuncs.closeFilterTag(self.Wd, "Audio")
                time.sleep(2)
                
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 13:
                    self.logi.appendMsg( "PASS - the number of entries in the table should have been 12 and it is 12 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 12 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False 
                
                # clear all filters and set them again
                self.logi.appendMsg( "INFO - going to clear all table filters and set new ones (MainCategory1, Media Types-> Audio ,AudioAdmin)")
                self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
                time.sleep(3)
                
                rc = self.BasicFuncs.selectCategoryFilter(self.Wd, 'MainCategory1')
                time.sleep(1)
                self.BasicFuncs.selectRefineFilter(self.Wd,'Media Types;Audio')
                time.sleep(1)
                search.send_keys('AudioAdmin' + Keys.RETURN)
                time.sleep(3)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 2:
                    self.logi.appendMsg( "PASS - after setting filters again, the number of entries in the table should have been 2 and it is 2 as expected")
                else:
                    self.logi.appendMsg("FAIL - after setting filters again, the number of entries in the table should have been 2 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False
                                 
                
                # select the entry
                self.logi.appendMsg( 'INFO - going to select the entry in the table')
                entriesTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                uncheckedEntries = self.Wd.find_elements_by_tag_name('tr')
                numOfUncheckedEntries = len(uncheckedEntries)
                chk = uncheckedEntries[1].find_element_by_xpath(DOM.ENTRY_CHECKBOX)
                chk.click()
                if self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg('PASS - selected the entry in the table')
                else:
                    self.logi.appendMsg('FAIL - could not select the entry in the table')
                    testStatus = False
                
                # sort the table by creation date
                self.logi.appendMsg( 'INFO - going to sort by creation date')    
                self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_COLUMN_TITLE).click()
                time.sleep(3)    
                if self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg('FAIL - the sort did not uncheck the entry in the table')
                    testStatus = False
                else:
                    self.logi.appendMsg('PASS - the sort unchecked the entry in the table as expected')
                
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 2:
                    self.logi.appendMsg( "PASS - the filters that set before sorting the table remain after sorting as expected")
                else:
                    self.logi.appendMsg("FAIL - the filters that set before sorting the table DID NOT remain after sorting NOT as expected" )
                    testStatus = False
                             
                
                #refresh the table and verify filters disappear
                #first select an entry
                self.logi.appendMsg( 'INFO - going to select an entry in the table')
                entriesTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                uncheckedEntries = self.Wd.find_elements_by_tag_name('tr')
                numOfUncheckedEntries = len(uncheckedEntries)
                chk = uncheckedEntries[0].find_element_by_xpath(DOM.ENTRY_CHECKBOX)
                chk.click()
                if self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg("PASS - selected the entry in the table")
                else:
                    self.logi.appendMsg("FAIL - could not select the entry in the table")
                    testStatus = False
                
                # verify entry was unselected     
                self.logi.appendMsg('INFO - going to refresh the entries table and verify filters remain and selected entries unselect')
                self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
                time.sleep(3)
                if self.BasicFuncs.isBulkActionsExsit(self.Wd):
                    self.logi.appendMsg("FAIL - the refresh did not uncheck the entry in the table")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - the refresh unchecked the entry in the table as expected")
                    
                # verify filters remain
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                numOfFilters = len(activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG))
                if numOfFilters == 3:
                    print('PASS - the filters remain as they were before refreshing the table')
                else:
                    print('FAIL - the filters DID NOT remain as they were before refreshing the table, before were 3 and after - ' +  str(numOfFilters))
                    testStatus = False 
                
            
            else:
                testStatus = False
        
        except:
            testStatus = False
            pass
    
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        global testStatus
        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '80','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '80','0')
            self.logi.reportTest('pass',self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_80.py -s')
    #===========================================================================
