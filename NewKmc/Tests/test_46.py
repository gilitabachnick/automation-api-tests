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


#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
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
            
            self.logi = reporter2.Reporter2('TEST46')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

        except Exception as Exp:
            print(Exp)
        
    def test_46(self):
        
        global testStatus
        try:
            self.logi.initMsg('test 46')
            #Login KMC
            self.Wd.maximize_window()
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            if not rc:
                self.logi.appendMsg("FAIL - Failed Login")
                testStatus = False
            else:
                # check first entry and check that bulk actions appear and number of selected entries=1
                self.logi.appendMsg("INFO - going to make sure that filter preferences is on: Display entries associated with the selected category and its sub-categories")
                self.BasicFuncs.setFilrePreferences(self.Wd, False)
                time.sleep(2)
                
                self.logi.appendMsg("INFO - Going to search and set category filter = MediaSpace")
                rc = self.BasicFuncs.selectCategoryFilter(self.Wd, 'MediaSpace', False)
                if not rc:
                   self.logi.appendMsg("Fail - could not find the category MediaSpace")
                   testStatus = False
                # expand the media space category and check each son node is selected and disabled 
                self.logi.appendMsg("INFO - going to expand the media space category and check each son node in FIRST LEVEL is selected and disabled") 
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                mediaSpaceLine =  filtWindow.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                for ln in mediaSpaceLine:
                    if ln.text.find("MediaSpace")>=0:
                        mediaSpaceLine = ln
                        break
                mediaSpaceLine.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                time.sleep(1)
                childrensFrame = self.Wd.find_element_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN_FRAME)
                childrensnodes = childrensFrame.find_elements_by_xpath(DOM.ENTRY_CHECKBOX)
                tmpStatus = True
                for son in childrensnodes:
                    if son.get_attribute("class").find("p-checkbox-disabled")==-1:
                        self.logi.appendMsg("FAIL - sub category: " + son.find_element_by_xpath('..').text + " is not selected or disable as it should have been")
                        testStatus = False
                        tmpStatus = False
                    else:
                        # expand second level and verify it all selected and disabled
                        if son.text.lower().find("site")!=-1:
                            self.logi.appendMsg("INFO - going to expand site category and verify that SECOND LEVEL of categories are also selected and disabled")
                            son.find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
                            time.sleep(1)
                            grandSonsFrame = childrensFrame.find_element_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN)
                            secondLevelNodes = grandSonsFrame.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                            for grandSon in secondLevelNodes:
                                if grandSon.get_attribute("class").find("selectable")!=-1:
                                    self.logi.appendMsg("FAIL - sub category: " + grandSon.text + " is not selected or disable as it should have been")
                                    testStatus = False
                                    tmpStatus = False
                            
                if tmpStatus:
                    self.logi.appendMsg("PASS - all the sub categories on first and second level under Media space are checked and disabled as expected") 
                    
                #verify only one filter tag was added
                self.logi.appendMsg("INFO - verifying only one filter tag was added")
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1:
                    self.logi.appendMsg("FAIL - only one filter tag should appear and actaully - " + str(len(FilterTags)) + " Appear in filter tag line")
                else:
                    self.logi.appendMsg("PASS - only one filter tag Appear in filter tag line, as expected")
                
                entryTbl = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 28:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 28 and it is 28 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 28 and it is " + str(len(entryRows)) + " NOT as expected")
                    testStatus = False
                
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                filtWindow.find_element_by_xpath(DOM.CATEGORRY_CLEAR_ALL).click()
                filtWindow.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
                
                
                # set filter of sub-category "Media Space > Site > Galleries > Video Tools
                self.logi.appendMsg("INFO - going to set filter of sub-category Media Space > Site > Galleries > Video Tools")
                self.BasicFuncs.selectCategoryFilter(self.Wd, "Video Tools", False)
                time.sleep(3)
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 21:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 21 and it is 21 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 21 and it is " + str(len(entryRows)) + " NOT as expected")
                    testStatus = False
                    
                self.logi.appendMsg("INFO - going to type \"video\" in the search field and verify that only the first, fifth and sixth option are enable in the auto complete list")
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys("video")
                time.sleep(2)
                autoCopleteLines = self.Wd.find_elements_by_xpath(DOM.CATEGORY_FILTER_AUTOCOMP_LINE)
                tmpStatus = True
                for i in range (len(autoCopleteLines)):
                    if autoCopleteLines[i].get_attribute("class").find("kIsItemDisabled")!=-1:
                        if 1<=i<=3:
                            continue;
                        else:
                            self.logi.appendMsg("FAIL - line number: " + str(i+1) + " should have been ENABLED and it is not")
                            testStatus = False
                            tmpStatus = False
                    else:
                        if 1<=i<=3:
                            self.logi.appendMsg("FAIL - line number: " + str(i+1) + " should have been DISABLED and it is not")
                            testStatus = False
                            tmpStatus = False
                            
                if tmpStatus:
                    self.logi.appendMsg("PASS - Auto complete lines appeared enabled and disabled as expected")

                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys(Keys.CONTROL, 'a')
                self.Wd.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys( Keys.DELETE)
                
                #Verify all parents of this sub-category change their visibility to intermediate
                self.logi.appendMsg("INFO - going to Verify all parents of this sub-category change their visibility to intermediate")
                filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
                mediaSpaceLine =  filtWindow.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
                expFathersArr = ['MediaSpace\n5', 'site\n3', 'galleries\n3']
                Fathersarr=[]
                for lines in mediaSpaceLine:  # insert all intermediates fathers to array
                    if str(lines.find_element_by_xpath(DOM.CATEGORY_CHECK_BOX).get_attribute("class")).find("minus")!=-1:
                        if len(Fathersarr)==1:
                            FatherForNextStep = lines
                        Fathersarr.append(lines.text)
                
                if set(expFathersArr)==set(Fathersarr):
                    self.logi.appendMsg("PASS - the father categories became intermediates")
                else:
                    self.logi.appendMsg("FAIL - the father categories Media Space , Site , Galleries should have been intermediates, and actually the intermediates are: " + ','.join(Fathersarr))
                    testStatus = False
                    
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
                
                
                self.logi.appendMsg("INFO - going to select a level above the \"Video Tools\", will select filter name = \"site\"")
                FatherForNextStep.click()
                time.sleep(3)
                FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                if len(FilterTags)!=1 or FilterTags[0].text != "site":
                    self.logi.appendMsg("FAIL - should have been only one filter tag \"site\" and actually there are: " + len(FilterTags) + " filter tags")
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
                    self.logi.appendMsg("PASS - there is only one filter tag name \"site\"")
                
                
                entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                if len(entryRows) == 28:
                    self.logi.appendMsg("PASS - the number of entries in the table should have been 28 and it is 28 as expected")
                else:
                    self.logi.appendMsg("FAIL - the number of entries in the table should have been 28 and it is " + str(len(entryRows)) + " NOT as expected")
                    testStatus = False
                
                
                self.logi.appendMsg("INFO - going to UNSELECT the father filter \"site\", no filter should remain active afterwards")
                FatherForNextStep.click()
                time.sleep(3)
                try:
                    FilterTags = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                    self.logi.appendMsg("FAIL - there should not be any activate filters, but there are NOT as expected")
                    testStatus = False
                except:   
                    self.logi.appendMsg("PASS - no activate filters are set as expected")

        except Exception as Exp:
            print(Exp)
            testStatus = False
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        global testStatus
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
        try:
            if testStatus == False:
                self.logi.reportTest('fail', self.sendto)
                self.practitest.post(Practi_TestSet_ID, '46', '1')
                assert False
            else:
                self.logi.reportTest('pass', self.sendto)
                self.practitest.post(Practi_TestSet_ID, '46', '0')
                assert True
        except Exception as Exp:
            print(Exp)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_46', '-s'])
    # ===========================================================================

