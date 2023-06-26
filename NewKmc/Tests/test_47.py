import os
import sys
import time

import pytest
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
            self.user   = inifile.RetIniVal(section, 'userName2')
            self.pwd    = inifile.RetIniVal(section, 'pass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST47')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        except:
            pass
        
    def test_47(self):
        
        global testStatus
        
        self.logi.initMsg('test 47')
        
        try: 
            #Login KMC
            self.Wd.maximize_window()
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            
            if rc:
                 # check first entry and check that bulk actions appear and number of selected entries=1
                self.logi.appendMsg("INFO - going to make sure that filter preferences is on: Display entries associated with the selected category only")
                self.BasicFuncs.setFilrePreferences(self.Wd, True)
                
                self.logi.appendMsg("INFO - Going to search and set category filter = MediaSpace")
                rc = self.BasicFuncs.selectCategoryFilter(self.Wd, 'MediaSpace', False)
                if not rc:
                   self.logi.appendMsg("Fail - could not find the category MediaSpace")
                   testStatus = False
                   
                # expand the media space category and check each son node is selected and disabled 
                self.logi.appendMsg("INFO - going to expand the media space category and check each son node in FIRST LEVEL is NOT selected and not disabled") 
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                mediaSpaceLine =  filtWindow.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                for ln in mediaSpaceLine:
                    if ln.text.find("MediaSpace")>=0:
                        mediaSpaceLine = ln
                        break
                mediaSpaceLine.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                time.sleep(1)
                #childrensFrame =  mediaSpaceLine.find_element_by_xpath("..")
                childrensFrame = self.Wd.find_element_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN_FRAME)
                #childrensnodes = childrensFrame.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN)
                childrensnodes = childrensFrame.find_elements_by_xpath(DOM.ENTRY_CHECKBOX)

                tmpStatus = True
                for son in childrensnodes:
                    if son.get_attribute("aria-checked").find("false")==-1:
                        self.logi.appendMsg("FAIL - sub category: " + son.find_element_by_xpath('..').text + " is selected or disable NOT as expected")
                        testStatus = False
                        tmpStatus = False
                    else:
                        # expand second level and verify it all selected and disabled
                        if son.text.find("site")!=-1:
                            self.logi.appendMsg("INFO - going to expand site category and verify that SECOND LEVEL of categories are also NOT selected and not disabled")
                            son.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                            time.sleep(1)
                            grandSonsFrame = childrensFrame.find_element_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN)
                            secondLevelNodes = grandSonsFrame.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                            for grandSon in secondLevelNodes:
                                if grandSon.get_attribute("class").find("selectable")==-1:
                                    self.logi.appendMsg("FAIL - sub category: " + grandSon.text + " is selected or disable NOT as expected")
                                    testStatus = False
                                    tmpStatus = False
                            
                if tmpStatus:
                    self.logi.appendMsg("PASS - all the sub categories on first and second level under Media space are NOT checked and NOT disabled as expected") 
                
                #verify only one filter tag was added
                self.logi.appendMsg("INFO - verifying only one filter tag was added")
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1:
                    self.logi.appendMsg("FAIL - only one filter tag should appear and actaully - " + str(len(FilterTags)) + " Appear in filter tag line")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - only one filter tag Appear in filter tag line, as expected")  
                    
                entryTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                entryRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                if entryRows == 0:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 0 and it is 0 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 0 and it is " + str(entryRows) + " NOT as expected")
                    testStatus = False 
                
                
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                filtWindow.find_element_by_xpath(DOM.CATEGORRY_CLEAR_ALL).click()
                filtWindow.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
                
                # set filter of sub-category "Media Space > Site > Galleries > Video Tools
                self.logi.appendMsg("INFO - going to set filter of sub-category Media Space > Site > Galleries > Video Tools")
                self.BasicFuncs.selectCategoryFilter(self.Wd, "Video Tools", False)
                time.sleep(3)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 17:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 4 and it is 4 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 4 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False
                    
                self.logi.appendMsg("INFO - going to type \"vid\" in the search field and verify that only the second option is enable in the auto complete list")
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys("vid")
                time.sleep(2)
                autoCopleteLines = self.Wd.find_elements_by_xpath(DOM.CATEGORY_FILTER_AUTOCOMP_LINE)
                tmpStatus = True
                for i in range (len(autoCopleteLines)):
                    if autoCopleteLines[i].get_attribute("class").find("kIsItemDisabled")!=-1:
                        if i==1:
                            continue;
                        else:
                            self.logi.appendMsg("FAIL - line number: " + str(i+1) + " should have been ENABLED and it is not")
                            testStatus = False
                            tmpStatus = False
                    else:
                        if i==1:
                            self.logi.appendMsg("FAIL - line number: " + str(i+1) + " should have been DISABLED and it is not")
                            testStatus = False
                            tmpStatus = False
                            
                if tmpStatus:
                    self.logi.appendMsg("PASS - Auto complete lines appeared enabled and disabled as expected")

                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys(Keys.CONTROL, 'a')
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys(Keys.DELETE)

                #Verify all parents of this sub-category Not changed their visibility to intermediate
                self.logi.appendMsg("INFO - going to Verify all parents of this sub-category did NOT change their visibility to intermediate")
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                mediaSpaceLine =  filtWindow.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                tmpStatus = True
                for lines in mediaSpaceLine:  # insert all intermediates fathers to array
                    if lines.text.find("site")!=-1:
                         FatherForNextStep = lines                
                    if str(lines.find_element_by_xpath(DOM.CATEGORY_CHECK_BOX).get_attribute("class")).find("minus")!=-1:
                        self.logi.appendMsg("FAIL - the father category " + lines.text + " should NOT been intermediates, and actually it is")
                        tmpStatus = False
                if tmpStatus:
                    self.logi.appendMsg("PASS - the father categories Did NOT became intermediates as expected")
                   
                # Verify a filter tag has been added for the sub-category
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1 or FilterTags[0].text != "Video Tools":
                    self.logi.appendMsg("FAIL - should have been only one filter tag \"Video Tools\" and actually there are: " + len(FilterTags) + " filter tags")
                    testStatus = False
                    if len(FilterTags)>1:
                        Thefilters = ""
                        for i in FilterTags:
                            Thefilters = Thefilters + i.text + " "
                    else:
                        Thefilters = FilterTags[0].text
                        self.logi.appendMsg("FAIL - the names of the filters tags that should not been there are: " + Thefilters)
                        testStatus = False
                else:
                    self.logi.appendMsg("PASS - there is only one filter tag name \"Video Tools\"")
                    
                # select filter name = site    
                self.logi.appendMsg("INFO - going to select a level above the \"Video Tools\", will select filter name = \"site\"")
                FatherForNextStep.click()
                time.sleep(3)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=2 or (FilterTags[0].text != "Video Tools" and FilterTags[0].text != "site"):
                    self.logi.appendMsg("FAIL - should have been 2 filter tags \"site\" and \"Video Tools\" and actually there are: " + len(FilterTags) + " filter tags")
                    testStatus = False
                    if len(FilterTags)>1:
                        Thefilters = ""
                        for i in FilterTags:
                            Thefilters = Thefilters + i.text + " "
                    else:
                        Thefilters = FilterTags[0].text
                        self.logi.appendMsg("FAIL - the names of the filters tags that should not been there are: " + Thefilters)
                        testStatus = False
                else:
                    self.logi.appendMsg("PASS - there are only two filter tags - site and Video Tools as expected")
                
                
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 21:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 21 and it is 21 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 21 and it is " + str(len(entryRows)-1) + " NOT as expected")
                    testStatus = False
                
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                filtWindow.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
                    
                # close filter tag site
                self.logi.appendMsg( "INFO - Going to remove filer tags:  site and verify Video Tools remain as it was")
                self.BasicFuncs.closeFilterTag(self.Wd, "site")
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1 or FilterTags[0].text != "Video Tools":
                     self.logi.appendMsg("FAIL - should have been 1 filter tag Video Tools and actually there are: " + len(FilterTags) + " filter tags")
                     testStatus = False
                else:
                    self.logi.appendMsg("PASS - there are only one filter tag - Video Tools as expected")

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
            self.practitest.post(Practi_TestSet_ID, '47', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '47', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True
    #===========================================================================
    #pytest.main(['test_47.py','-s'])
    #===========================================================================
                
                
                
                
                
                
                
                
                
                
                
                
                