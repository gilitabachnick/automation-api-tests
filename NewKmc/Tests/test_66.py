'''
Updated on May 12, 2021

@author: Zeev.Shulman
'''
import os
import sys
import time

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
            self.user   = inifile.RetIniVal(section, 'userName8')
            self.pwd    = inifile.RetIniVal(section, 'pass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            
            self.logi = reporter2.Reporter2('TEST66')
            
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.Wd.maximize_window()
        except Exception as Exp:
            print(Exp)

    def test_66(self):
        global testStatus
        try:
            self.logi.initMsg('test 66')
            # Login KMC
            self.Wd.maximize_window()
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            if not rc:
                self.logi.appendMsg("FAIL - Failed Login")
                testStatus = False
            else:
                # open refine filter and Check [Access control] "parent" filter checkbox
                # Repetition acts as double-click fix focus problem. If stops working try 1 "Access Control Profiles" instead.
                rc = self.BasicFuncs.selectRefineFilter(self.Wd, "Access Control Profiles", True)
                time.sleep(5)

                if rc == False:
                    self.logi.appendMsg(
                        "FAIL - could not find filter name ""Access Control Profiles"" , can not continue this test")
                    testStatus = False
                else:
                    # going to verify all access control filters
                    self.logi.appendMsg("INFO - verifying all access control filters tag were added")
                    # activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                    FilterTags = self.Wd.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)

                    if len(FilterTags) != 10:
                        self.logi.appendMsg("FAIL - 10 filter tags should appear and actually - " + str(
                            len(FilterTags)) + " Appear in filter tag line")
                        testStatus = False
                    else:
                        self.logi.appendMsg("PASS - 10 filter tags Appear in filter tag line, as expected")

                        # going to check all sub categories are selected
                    self.logi.appendMsg("INFO- going to check all sub filters are selected")
                    AccessControlFilt = self.BasicFuncs.retTreeNodeFilterlineObj(self.Wd, "Access Control Profiles")
                    AccessControlFilt.find_element_by_xpath(DOM.REFINE_EXPAND).click()
                    time.sleep(3)

                    FilterWin = self.Wd.find_element_by_xpath(DOM.REFIN_POP)
                    childrensFrame = FilterWin.find_element_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN)
                    childrensnodes = childrensFrame.find_elements_by_xpath(DOM.REFINE_LEAF_SUBJECT_ROW)
                    tmpStatus = True
                    for son in childrensnodes:
                        if son.get_attribute("class").find("selectable") != -1:
                            self.logi.appendMsg(
                                "FAIL - sub filter: " + son.text + " is not selected or disable as it should have been")
                            testStatus = False
                            tmpStatus = False
                    if tmpStatus:
                        self.logi.appendMsg("PASS - all the sub filters of ""access control"" are selected as expected")

                    FilterWin.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
                    expFilterTags = ["Access2-Domain_BlockKaltura", "Access8-IP_AllowOfficeRange",
                                     "Access7-IP_BlockOfficeRange", "Access6-Cntry_BlockIsrael",
                                     "Access5-Cntry_AllowMany_NoIsrael", "Access9-SecureKS_With12sPreview",
                                     "Access3-Flavors_Only3GP", "Access4-Flavors_BlockMany",
                                     "Access1-Domain_OnlyKaltura", "Default"]
                    actFilterTags = []
                    # FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)

                    for i in range(0, len(FilterTags)):

                        if FilterTags[i].text == "":  # or i==9:
                            scrolRight = self.Wd.find_element_by_xpath(DOM.ENTRY_TAGS_RIGHT_SCROLL)
                            scrolRight.click()
                            time.sleep(1)

                        actFilterTags.append(str(FilterTags[i].text))

                    if set(actFilterTags) == set(expFilterTags):
                        self.logi.appendMsg("PASS - 10 filter tags TEXT Appear correct in filter tag line, as expected")
                    else:
                        self.logi.appendMsg("FAIL - the expected filter tags are: " + str(
                            expFilterTags) + " and actually it is: " + str(actFilterTags))
                        testStatus = False

                    while self.Wd.find_element_by_xpath(DOM.ENTRY_TAGS_LEFT_SCROLL).get_attribute("class").find(
                            "disable") < 0:
                        self.Wd.find_element_by_xpath(DOM.ENTRY_TAGS_LEFT_SCROLL).click()
                        time.sleep(1)
                    # ===========================================================
                    # self.Wd.find_element_by_xpath(DOM.ENTRY_TAGS_LEFT_SCROLL).click()
                    # time.sleep(2)
                    # ===========================================================
                    self.BasicFuncs.closeFilterTag(self.Wd, "Default")
                    time.sleep(5)

                    entryRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                    if len(entryRows) == 30:
                        self.logi.appendMsg(
                            "PASS - the number of entries in the table should have been 30 and it is 30 as expected")
                    else:
                        self.logi.appendMsg(
                            "FAIL - the number of entries in the table should have been 30 and it is " + str(
                                len(entryRows)) + " NOT as expected")
                        testStatus = False

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
                self.practitest.post(Practi_TestSet_ID, '66', '1')
                self.logi.reportTest('fail', self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '66', '0')
                self.logi.reportTest('pass', self.sendto)
                assert True
        except Exception as Exp:
            print(Exp)

    #===========================================================================
    # pytest.main('test_66.py -s')
    if Run_locally:
        pytest.main(args=['test_66', '-s'])
    # ===========================================================================
            