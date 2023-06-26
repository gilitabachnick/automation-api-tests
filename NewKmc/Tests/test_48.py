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
import Config
import KmcBasicFuncs
import Practitest
import reporter2
###########################
#
#   Test should run on prod until we add the user to testing with all the necessary data
#
###########################


### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
   isProd = True
else:
   isProd = False

testStatus = True

class TestClass:
    
    KMCURL = "http://il-kmc-ng2.dev.kaltura.com/latest/login"
        
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
            self.user   = inifile.RetIniVal(section, 'userName3')
            self.pwd    = inifile.RetIniVal(section, 'pass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST48')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        except:
            pass
        
    def test_48(self):
        
        global testStatus
        
        self.logi.initMsg('test 48')
        
        try:
            #Login KMC
            self.Wd.maximize_window()
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            
            if rc:
                 # check first entry and check that bulk actions appear and number of selected entries=1
                self.logi.appendMsg("INFO - going to make sure that filter preferences is on: Display entries associated with the selected category and its sub-categories")
                self.BasicFuncs.setFilrePreferences(self.Wd, False)
                
                self.logi.appendMsg("INFO - going to type \"sample\" in the search field and select the option sample -A")
                FilterCat = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER)
                FilterCat.click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys("sample")
                time.sleep(4)
                autoCopleteLines = self.Wd.find_elements_by_xpath(DOM.CATEGORY_FILTER_AUTOCOMP_LINE)
                autoCopleteLines[1].click()
                time.sleep(3)
                
                # verify one filter tag of Sample A and 4 entries returned
                self.logi.appendMsg("INFO - verifying only one filter tag was added")
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1:
                    self.logi.appendMsg("FAIL - only one filter tag should appear and actaully - " + str(len(FilterTags)) + " Appear in filter tag line")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - only one filter tag Appear in filter tag line, as expected") 
                    
                
                self.logi.appendMsg("INFO - verifying that 4 entries returned from the filter")    
                entryTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 4:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 4 and it is 4 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 4 and it is " + str(len(entryRows)) + " NOT as expected")
                    testStatus = False 
                
                # expand the Sample A category and check each son node is selected and disabled 
                self.logi.appendMsg("INFO - going to expand the Sample A category and verify each son node in is selected and disabled") 
                samples = self.BasicFuncs.retTreeNodeFilterlineObj(self.Wd, "Samples")
                samples.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                time.sleep(3)
                
                sampleA = self.BasicFuncs.retTreeNodeFilterlineObj(self.Wd, "Sample A")
                sampleA.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                
                bfound = False
                startTime = time.time() 
                while not bfound:
                    try:
                        childrensFrame =  samples.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN_FRAME)[1]
                        #childrensnodes = childrensFrame.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                        childrensnodes = childrensFrame.find_elements_by_xpath(DOM.ENTRY_CHECKBOX)
                        bfound = True
                        for son in childrensnodes:
                            if son.get_attribute("class").find("p-checkbox-disabled")==-1:
                                self.logi.appendMsg("FAIL - sub category: " + son.find_element_by_xpath('..').text + " is not selected or disable as it should have been")
                                testStatus = False
                                tmpStatus = False
                        if tmpStatus:
                            self.logi.appendMsg("PASS - all the sub categories on first and second level under Media space are checked and disabled as expected")
                
                    except:
                        if time.time()- startTime > 30:  # the filters did not uploaded after 30 sec
                            self.logi.appendMsg("FAIL - the filters where not loaded after 30 seconds")
                            testStatus = False 
                
                #self.Wd.find_element_by_xpath(DOM.CATEGORRY_CLEAR_ALL).click()
                #time.sleep(3)
                self.Wd.refresh()
                time.sleep(3)
                
                self.logi.appendMsg("INFO - going to type \"sample\" in the search field and select the option sample -B")
                FilterCat = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER)
                time.sleep(1)
                FilterCat.click()
                time.sleep(3)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys("sample")
                time.sleep(4)
                autoCopleteLines = self.Wd.find_elements_by_xpath(DOM.CATEGORY_FILTER_AUTOCOMP_LINE)
                autoCopleteLines[2].click()
                time.sleep(5)
                
                # verify one filter tag of Sample A and 4 entries returned
                self.logi.appendMsg("INFO - verifying only one filter tag was added")
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags) != 1:
                    self.logi.appendMsg("FAIL - only one filter tag should appear and actaully - " + str(len(FilterTags)) + " Appear in filter tag line")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - only one filter tag Appear in filter tag line, as expected") 
                    
                
                self.logi.appendMsg("INFO - verifying that 13 entries returned from the filter")    
                entryTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 13:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 13 and it is 13 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 13 and it is " + str(len(entryRows)) + " NOT as expected")
                    testStatus = False 
                
                # expand the Sample B category and verify the unable loading message appear due to more than 500 sub categories 
                self.logi.appendMsg("INFO - going to expand the Sample B category and verify that get \"unable to load\" message due to > 500 sub categories") 
                samples = self.BasicFuncs.retTreeNodeFilterlineObj(self.Wd, "Samples")
                samples.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                time.sleep(3)
                
                sampleB = self.BasicFuncs.retTreeNodeFilterlineObj(self.Wd, "Sample B")
                sampleB.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                time.sleep(3)
                
                try:
                    err = sampleB.find_element_by_xpath(DOM.CATEGORY_FILTER_ERROR_LOADING)
                    if err.text.lower().find("number of categories exceeds 500") != -1:
                        self.logi.appendMsg("PASS - the sub categories were not loaded and got the message \"" + err.text + "\"")
                    else:
                        self.logi.appendMsg("FAIL - searched for a message contain \"number of categories exceeds 500\" and the actual message was: " + err.text)
                        testStatus = False 
                except:
                     self.logi.appendMsg("FAIL - could not find the message contain \"number of categories exceeds 500\", might be due to sub categories actually loaded")
                
                
                # selecting sub category test-100 from auto complete and verify it is select able and 4 entries returned
                self.logi.appendMsg("INFO - going to select sub category test-100 from auto complete and verify it is select able and 4 entries returned")
                self.Wd.refresh()
                time.sleep(5)

                FilterCat = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER)
                FilterCat.click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys("test-100")
                time.sleep(4)
                autoCopleteLines = self.Wd.find_elements_by_xpath(DOM.CATEGORY_FILTER_AUTOCOMP_LINE)
                autoCopleteLines[1].click()
                time.sleep(3)
                
                # verify one filter tag of Sample A and 4 entries returned
                self.logi.appendMsg("INFO - verifying only one filter tag was added")
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1:
                    self.logi.appendMsg("FAIL - only one filter tag should appear and actaully - " + str(len(FilterTags)) + " Appear in filter tag line")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - only one filter tag Appear in filter tag line, as expected") 
                    
                
                self.logi.appendMsg("INFO - verifying that 4 entries returned from the filter")    
                entryTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 4:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 4 and it is 4 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 4 and it is " + str(len(entryRows)) + " NOT as expected")
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
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '48', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '48', '0')
            assert True



    #===========================================================================
    # pytest.main(args=['test_48.py', '-s'])
    #===========================================================================
            
            
            