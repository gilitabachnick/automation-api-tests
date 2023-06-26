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
import CategoryFuncs
import reporter2

import Config
import Practitest
import Entrypage


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
            self.user   = inifile.RetIniVal(section, 'userName4')  # 'kmc.kal.tura@gmail.com'
            self.pwd    = inifile.RetIniVal(section, 'pass')
            # self.sendto = inifile.RetIniVal(section, 'sendto')
            self.sendto = 'adi.millman@kaltura.com'
            self.logi = reporter2.Reporter2('TEST1112')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd,self.logi)
            self.practitest = Practitest.practitest('4586')
    
            self.testedCategoryArr = ['Test-1112 SubCategory','Test-1112 CategoryToMove','Test-1112 CategoryWithSub','Test-1112 ParentCategory']
                   
            
            # Login & Navigating to categories section
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)


            # Check if we have left over 'Test-1112' categories from last run. if no - create categories to work with. if yes - delete all and create all.
            TestedCategoryName = 'Test-1112'
            self.logi.appendMsg("Going to search for left over 'Test-1112' categories from previous runs")   
            self.basicFuncs.searchEntrySimpleSearch(self.Wd, TestedCategoryName)
            if self.basicFuncs.retNumOfRowsInEntryTbl(self.Wd) != 0:
                self.logi.appendMsg("Going to delete left over 'Test-1112' categories")   
                self.basicFuncs.deleteCategories(self.Wd,'Test-1112')
                time.sleep(2)
                #try and catch for error message that appears when deleting both parent and child category (till bug KMCNG-1892 is fixed)
                try:
                    popup = self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE)
                    popup.find_element_by_xpath(DOM.POPUP_MESSAGE_OK).click()                       
                except:
                    print("no pop up message")

            for catName in self.testedCategoryArr:
                self.logi.appendMsg("Going to create categories to run this test with")
                self.categoryFuncs.addCategory(catName, "no")
                time.sleep(2)
                self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                time.sleep(3)
    
             
        except:
            pass        
      

    '''
    @ Test 1112 - Search and Move Category (3 scenarios)
        In Content > Categories:
        Selecting a category > Opening Actions menu
                
        1. Move a category:
        1.1 Search and move 'SubCategory'[0] to 'CategoryWithSub'[2]
        1.2 Search and move 'CategoryToMove'[1] to a category that is not displayed in the (collapsed) tree ('SubCategory') [0]
        Verify the correct category 'SubCategory' is selected in the tree - how do I do that?... is it a UI issue? 
        Verify 'CategoryToMove'  was moved correctly
        
        2. Move a category that contains sub-categories:
        Search and move 'CategoryWithSub' [2] to 'ParentCategory' [3] 
        Verify the correct category 'SubCategory' is selected in the tree
        Verify 'CategoryWithSub' was moved correctly with its sub-categories
        
        3. Try to move a category to an invalid destination:
        3.1 Try to move a category to itself > get message
        3.3 Try to move a category to one of its Sub-Categories > get message
        3.2 Try to move a category to what is already the parent of this category > get message
          
    '''
    # Defining moveCategoryToSearchedParent and verifyCategoryMovedCorrectly
    # posCheck = false for scenarios where the system should not allow moving a category to selected destination 

    def moveCategoryToSearchedParent(self,catName,catParent,posCheck=True, negExpMsg=None):
        
        global testStatus
        
        self.logi.appendMsg("INFO - Going to search for '"+catName+"' category, and click on 'Move Category' action")
        self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
        self.basicFuncs.searchEntrySimpleSearch(self.Wd,catName)
        time.sleep(3)
        self.basicFuncs.tblSelectAction(self.Wd, 0, 'move category')
        time.sleep(5)
        self.logi.appendMsg("INFO - Going to search for the 'destination' parent category = '"+ catParent +"'")        
        self.Wd.find_element_by_xpath(DOM.NEW_CATEGORY_SEARCH).send_keys(catParent)
        time.sleep(5)
        newCatWin = self.Wd.find_element_by_xpath(DOM.CATEGORY_ADD_POPUPWIN)
        time.sleep(1)
        #=======================================================================
        # newCatWin.find_element_by_xpath(DOM.NEW_CATEGORY_SEARCH).send_keys(categoryParent)
        # time.sleep(2)
        # newCatWin.find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_SELECT).click()
        #=======================================================================
        newCatWin.find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_LIST).click()
        time.sleep(1)
        self.Wd.find_element_by_xpath(DOM.CATEGORY_NEW_APPLY).click()
        time.sleep(3)             
        if posCheck:
            self.Wd.find_element_by_xpath(DOM.GLOBAL_YES_BUTTON).click()
            time.sleep(2)
            
            uiLock = True
            timeout = 0
            while uiLock and timeout < 60:    
                try:
                    self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                    uiLock = False
                except:    
                    time.sleep(1)
                    timeout = timeout+1
                    continue
            if timeout > 60:
                self.logi.appendMsg("FAIL - Categories update takes longer than 60 seconds")
                testStatus = False
                
            self.verifyCategoryMovedCorrectly(catName,catParent)
            
        else:
            self.logi.appendMsg("INFO - Verifying correct message after trying to move to an invalid parent category'"+ catParent +"'")        
            popupMessageText = self.Wd.find_element_by_xpath(DOM.GLOBAL_ERROR_POPUP_MSG_TEXT).text
            if popupMessageText.find(negExpMsg) >= 0:
                self.logi.appendMsg("PASS - the pop-up message contains the expected text: '"+ popupMessageText+"'")
                self.Wd.find_element_by_xpath(DOM.GLOBAL_ERROR_CANCEL_BUTTON).click()
                time.sleep(1)
                self.basicFuncs.selectOneOfInvisibleSameObjects(self.Wd, DOM.UPLOAD_SETTINGS_CLOSE).click()
                time.sleep(1)
            else:
                self.logi.appendMsg("FAIL - the pop-up message is not the expected one, the actual message was: '" + popupMessageText+"'")
                testStatus = False
                
        

            
    
    def verifyCategoryMovedCorrectly(self,catName,catParent):
        
        global testStatus
        

        self.logi.appendMsg("INFO - Going to open '" + catParent + "' details page, and move to its 'Sub Categories' tab")
        self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
        time.sleep(3)
        self.basicFuncs.searchEntrySimpleSearch(self.Wd, catParent)
        self.basicFuncs.tblSelectAction(self.Wd, 0, 'edit')
        time.sleep(3)
        self.Wd.find_element_by_xpath(DOM.CATEGORY_SUB_CATEGORIES_TAB).click()
        time.sleep(1)
        subCatName = self.basicFuncs.retTblRowName(self.Wd,1,'category')
        
        self.logi.appendMsg("INFO - Going to verify that the parent category '" + catParent + "' now contains '"+ catName +"'")
        if subCatName != catName:
            self.logi.appendMsg("FAIL - The moved category is not located under the parent category as expected")
            testStatus = False
        else:
            self.logi.appendMsg("PASS - The category has been moved successfully")    
            
                     
    def test_1112(self):
   
        global testStatus
        self.logi.initMsg('Test 1112: Categories > Move Category')

        # self.testedCategoryArr = ['Test-1112 SubCategory','Test-1112 CategoryToMove','Test-1112 CategoryWithSub','Test-1112 ParentCategory']
        try:
            for i in range(0,6):
                print("step: " + str(i))
                time.sleep(2)
                # 1. Move a category
                if i==0:
                    catName = self.testedCategoryArr[0]
                    catParent = self.testedCategoryArr[2]
                    self.moveCategoryToSearchedParent(catName,catParent)
                    
                    
                # 2. Move 'CategoryToMove'[1] to a category that is not displayed in the (collapsed) tree ('SubCategory') [0]
                elif i==1:
                    catName = self.testedCategoryArr[1]
                    catParent = self.testedCategoryArr[0]
                    self.moveCategoryToSearchedParent(catName, catParent)
                    
                    
                 # 2. Move a category that contains sub-categories
                elif i==2:
                    catName = self.testedCategoryArr[2]
                    catParent = self.testedCategoryArr[3]
                    self.moveCategoryToSearchedParent(catName, catParent)
                    self.verifyCategoryMovedCorrectly(self.testedCategoryArr[0],self.testedCategoryArr[2])
                                       
                # 3.1 Try to move a category to itself > get message
                elif i==3:
                    catName = self.testedCategoryArr[2]
                    catParent = self.testedCategoryArr[2]
                    self.moveCategoryToSearchedParent(catName, catParent,False, "A Category cannot be moved into itself or one of its children's categories.")
                     
                                        
                # 3.2 Try to move a category to one of its Sub-Categories > get message
                elif i==4:
                    catName = self.testedCategoryArr[2]
                    catParent = self.testedCategoryArr[0]
                    self.moveCategoryToSearchedParent(catName, catParent, False, "A Category cannot be moved into itself or one of its children's categories.")
                     
                        
                # 3.3 Try to move a category to what is already the parent of this category > get message
                elif i==5:
                    catName = self.testedCategoryArr[0]
                    catParent = self.testedCategoryArr[2]
                    self.moveCategoryToSearchedParent(catName, catParent, False, "Category is already a child of the selected parent.")
            
        except:
               testStatus = False
               pass
        
        
    def teardown_class(self):
        
        global testStatus
        
        try:
            self.basicFuncs.deleteCategories(self.Wd,'Test-1112 SubCategory')
            self.basicFuncs.deleteCategories(self.Wd,'Test-1112 CategoryToMove;Test-1112 CategoryWithSub;Test-1112 ParentCategory')
        except:
            pass
        
        self.Wd.quit()
               
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1112','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1112','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
            
        
    #===========================================================================
    #pytest.main(args=['test_1112.py','-s'])        
    #===========================================================================
        
                