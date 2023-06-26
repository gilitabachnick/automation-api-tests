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
import Entrypage
import CategoryFuncs


#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '1423'
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
            self.user   = inifile.RetIniVal(section, 'userName6')
            self.pwd    = inifile.RetIniVal(section, 'pass6')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1109')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome") 
            self.entryPage = Entrypage.entrypagefuncs(self.Wd)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            
            #Upload entries with relevant category for the test
            #Login KMC
            self.logi.initMsg('test 1109 Categories > View Entries')
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            time.sleep(1)
            # check if category EmptyCat - DoNotAddEntries exist if not create it
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(1)
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "EmptyCat - DoNotAddEntries")
            time.sleep(1)
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd) 
            if numOfRows==0:
                rc= self.categoryFuncs.addCategory("EmptyCat - DoNotAddEntries", "no") 
                if not rc:
                    self.logi.appendMsg("FAIL - could not upload the test categories can not continue this test")
                    return 
            
            #Bulk Upload
            thetime = self.uploadfuncs.bulkUpload("entry", "xml_file_uploadToExistingCategory_test1109.xml")
            time.sleep(1)
            rc = self.uploadfuncs.bulkMessageAndStatus("Finished Successfully",thetime)
            if not rc:
                self.logi.appendMsg("FAIL - could not upload the test entries with bulk upload, can not continue this test")
            time.sleep(1)
        except Exception as Exp:
            print(Exp)
        
    def test_1109(self):
        
        global testStatus
        
        try:
            for i in range (1,3):
                if i == 1:
                    categoryName = "EmptyCat - DoNotAddEntries"
                    entriesNum = 0
                    entriesNamesTest = False
                else:
                    categoryName = "Existing Entries - DoNotTouch"
                    entriesNum = 4
                    entriesNamesTest = True
                    
                #Search for an empty category
                self.logi.appendMsg("INFO - going to search for \"" + categoryName + "\" and select \'View Entries\' action. " + str(entriesNum) + " entries should be returned")
                self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                time.sleep(3)
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, categoryName) 
                
                # verify only one category came back from the search
                self.logi.appendMsg("INFO - going to search for \"" + categoryName + "\"")
                numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                if numOfRows!=1:
                    self.logi.appendMsg("FAIL - expected one category and actually retrieved -" + str(numOfRows))
                    testStatus = False
                    return
                       
                # verify the category name is correct
                catName = self.BasicFuncs.retTblRowName(self.Wd,1,"category")
                try:
                    if catName != categoryName:
                        self.logi.appendMsg("FAIL - expected for category name=\"" + categoryName + "\" and actually retrieved category name=\"" + catName + "\"")
                        testStatus = False
                        return

                except Exception as Exp:
                    print(Exp)
                    testStatus = False
                    self.logi.appendMsg("FAIL - could not retrieve the category name from the first row")
                    return
                
                #Click on the '...' Actions button:
                self.logi.appendMsg("INFO - going to select actions>view entries")
                if self.BasicFuncs.tblSelectAction(self.Wd,0, "View Entries")!=True:
                    self.logi.appendMsg("FAIL - could not go to \"view entries\" page")
                    testStatus = False  
                    return  
                time.sleep(2) 
                
                #Verify the number of the returned entries is correct
                self.logi.appendMsg("INFO - going to verify " + str(entriesNum) + " entries were returned")
                numOfEntries = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                if numOfEntries != entriesNum:
                    self.logi.appendMsg("FAIL - Returned entries' number is " + str(numOfEntries) + " and not " + str(entriesNum) + " as expected")
                    testStatus = False  
                else:
                    self.logi.appendMsg("PASS - " + str(entriesNum) + " entries were returned as expected")
                
                
                #Verify the filter is correct
                activeFilters = self.Wd.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
                self.logi.appendMsg("INFO - going to verify that the returned filter tag text = the category name: \"" + categoryName + "\"")
                try:
                    FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
                    if FilterTags[0].text == categoryName:
                        self.logi.appendMsg("PASS - the category filter is correct")
                    else:
                        testStatus = False
                        self.logi.appendMsg("FAIL - the category filter is wrong: " + FilterTags[0].text)

                except Exception as Exp:
                    print(Exp)
                    self.logi.appendMsg("FAIL - No active filter tag was displayed in Entries tab")
                    testStatus = False
                    
                if entriesNamesTest:
                    
                    #===============================================================
                    # Verify 4 entries are displayed as expected
                    #===============================================================
                    self.logi.appendMsg("INFO - going to verify 4 entries were returned")
                    if self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)!= 4:
                        self.logi.appendMsg("FAIL - Returned entries' number is wrong")
                        testStatus = False  
                        return    
                    else:
                           self.logi.appendMsg("PASS - Number of the returned entries is correct ")
                          
                         
                    self.logi.appendMsg("INFO - going to compare the returned entries' names with the category's entries")    
                    #List of actual entries' names that were returned from 'View Entries' action 
                    actEntryNames=[]
                    #Inserting the act entries to an array     
                    for i in range (1,5):
                        actEntryNames.append(self.BasicFuncs.retTblRowName(self.Wd, i))
                        
                    #The actual category's entries        
                    expEntryNames=['test 1109_1','test 1109_2','test 1109_3','test 1109_4' ]
            
                    #Verify returned entries' names are correct - comparing them with the uploaded entries
                    if set(actEntryNames)!=set(expEntryNames):
                        self.logi.appendMsg("FAIL - The expected entries were not returned in View Entries, The returned entries list:" + actEntryNames[0] + "," + actEntryNames[1]+ "," +actEntryNames[2]+ "," +actEntryNames[0o3] ) 
                        testStatus = False 
                    else:
                        self.logi.appendMsg("PASS - The returned entries are the expected entries")

        except Exception as Exp:
            print(Exp)
            testStatus = False

    def teardown_class(self):

        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd, "test 1109_1;test 1109_2;test 1109_3;test 1109_4",
                                          entriesSeparator=";")
        except Exception as Exp:
            print(Exp)
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
        try:
            if testStatus == False:
                self.logi.reportTest('fail', self.sendto)
                self.practitest.post(Practi_TestSet_ID, '1109', '1')
                assert False
            else:
                self.logi.reportTest('pass', self.sendto)
                self.practitest.post(Practi_TestSet_ID, '1109', '0')
                assert True
        except Exception as Exp:
            print(Exp)




    #===========================================================================
    # pytest.main('test_1109.py -s')
    if Run_locally:
        pytest.main(args=['test_1109', '-s'])
    # ===========================================================================

        
        