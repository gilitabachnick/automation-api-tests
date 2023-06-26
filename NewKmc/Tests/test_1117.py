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
            self.logi = reporter2.Reporter2('TEST1117')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome") 
            self.entryPage = Entrypage.entrypagefuncs(self.Wd)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            
            #Upload entries with relevant category for the test
            #Login KMC
            self.logi.initMsg('test 1117 Categories > Bulk Operations > Move Category')
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
           
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            
                  
            # check if any category starts with 'Lihi_test_1117' exists - if yes - delete it and them recreate it
            self.catsArr=["Lihi_test_1117_parent","Lihi_test_1117_child"]
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "Lihi_test_1117*")
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd) 
            if numOfRows!=0:
                self.BasicFuncs.deleteCategories(self.Wd, "Lihi_test_1117*") 
            
            #Creating 2 categories for the test 
            for cat in self.catsArr:
                rc= self.categoryFuncs.addCategory(cat, "no")
                if not rc:
                    self.logi.appendMsg("FAIL - could not upload the categories for the test can not continue this test")
                    return  
                self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                time.sleep(3)
        
        except:
            pass
        
        
    def test_1117(self):
        
        global testStatus
        
        try:
            #Go to Categories tab
            self.logi.appendMsg("INFO - going to open Categories tab")
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            
            #Search for the category we want to move
            self.logi.appendMsg("INFO - going to search for the category we want to move: \"Lihi_test_1117_child\" ")
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, 'Lihi_test_1117_child')
            
            #verify only one category came back from the search
            self.logi.appendMsg("INFO - going to verify only one category came back from the search")
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            if numOfRows!=1:
                self.logi.appendMsg("FAIL - expected one category and actually retrieved -" + str(numOfRows))
                testStatus = False
                       
            #verify the category name is correct
            self.logi.appendMsg("INFO - going to verify the returned category is the correct one: \"Lihi_test_1117_child\" ")
            catName = self.BasicFuncs.retTblRowName(self.Wd,0,"Lihi_test_1117_child")
            try:
                if catName != "Lihi_test_1117_child":
                    self.logi.appendMsg("FAIL - expected for category name=\"Lihi_test_1117_child\" and actually retrieved category name=\"" + catName + "\"")
                    testStatus = False
            except:
                testStatus = False
                self.logi.appendMsg("FAIL - could not retrieve the category name from the first row")
            
            #Check the first category's checkbox in the table for bulk actions
            self.logi.appendMsg("INFO - going to check the category\'s checkbox ")
            if self.BasicFuncs.CheckUncheckRowInTable(self.Wd,1) == False:
                 self.logi.appendMsg("FAIL - category was not checked")
                 testStatus = False
            
            #Click on Bulk Actions menu and select 'Move Categories'
            self.logi.appendMsg("INFO - going to click on the bulk actions menu-> and choose \'Move Categories ")
            if self.BasicFuncs.bulkSelectAction(self.Wd, "Move Categories")==False:
                self.logi.appendMsg("FAIL - could not go to \"Move Categories\" pop-up window")
                testStatus = False 
            
            #Search for the parent category we want to add the child category to
            self.logi.appendMsg("INFO - going to add the child category: \"Lihi_test_1117_child\" under the parent category:\"Lihi_test_1117_parent\"")
            time.sleep(1)        
            
            
            rc = self.categoryFuncs.moveCategory("Lihi_test_1117_parent")
            if not rc:
                self.logi.appendMsg("FAIL - Could not move the category under parent category: \"Lihi_test_1117_parent\"")
                testStatus = False 
                
            self.logi.appendMsg("INFO - going to verify the child category: \"Lihi_test_1117_child\" is now placed under the parent category:\"Lihi_test_1117_parent\"")
    
            #open categories tree
            FilterCat = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER)
            FilterCat.click()
            time.sleep(2)
            filtWindow = self.Wd.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
            #insert all parent (1st level) categories to an array
            catfiterLines =  filtWindow.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
            
            #loop on catfiterLines and return my parent category line
            ind = 0
            for myline in catfiterLines:
                if myline.text.find("Lihi_test_1117_parent") < 0:
                    ind+=1
                    continue
                else:                
                    break       
            
            catfiterLines[ind].find_element_by_xpath(DOM.CATEGORY_TREE_EXPAND).click()
            time.sleep(1)
            childrensFrame = myline.find_element_by_xpath("..")
            childrensFrame = childrensFrame.find_element_by_xpath(DOM.CATEGORY_TREE_NODE_CHILDREN)
            childrensnodes = childrensFrame.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
            tmpStatus = False
            for son in childrensnodes:
                if son.text != "Lihi_test_1117_child":
                    continue
                else:
                    self.logi.appendMsg("PASS - child category: \"Lihi_test_1117_child\" moved under the parent category:\"Lihi_test_1117_parent\" as expected") 
                    tmpStatus = True      
                    break
            
            if not tmpStatus:
                self.logi.appendMsg("FAIL - could not find child category: \"Lihi_test_1117_child\" under the parent category:\"Lihi_test_1117_parent\"")
        
        except:
            testStatus= False
            pass
        
        
    def teardown_class(self):
        
            
        global testStatus
        self.Wd.quit()
        
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1117','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1117','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
                   
        
    #===========================================================================
    # pytest.main('test_1117.py -s')        
    #===========================================================================
        
        
        