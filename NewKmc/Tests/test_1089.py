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
import reporter2
import CategoryFuncs

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
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1089')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')    
            
            #Login KMC and create a new category name adi_category
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            self.categoryFuncs.removeExistingCategory("adi_category")
            rc = self.categoryFuncs.addCategory("adi_category","no")   
            if rc==True:
                self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                time.sleep(3)
            else:
                self.logi.appendMsg("FAIL - the creation of the new category for the test fail, therefore can NOT continue this test")
                testStatus= False
                return
            
        except:
            pass    
            
    def test_1089(self):
        
        global testStatus 
        self.logi.initMsg('test 1089 Action Menu > Edit')
        
        try:
            self.logi.appendMsg("INFO - going to search for \"adi_category\" should retrieve one category named: adi_category")
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            
            self.logi.appendMsg("INFO - going to edit the category by adding description= autotest desc, tags=autotest tag, referenceId=autotest ref and discard changes, changes should not be save")
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "adi_category")
            rc = self.BasicFuncs.tblSelectAction(self.Wd, 0, "edit")
            if not rc:
                testStatus = False
                return
            self.categoryFuncs.updateCategory(None, "autotest desc", "autotest tag", "autotest ref", False)
            
            self.logi.appendMsg("INFO - going to verify the changes where not saved")
            self.BasicFuncs.selectEntryfromtbl(self.Wd, "adi_category",False)
            try: # check if there is tag it means it was saved
                self.Wd.find_elements_by_xpath(DOM.ENTRY_CATEGORIES_LABELS).text
                tagsField = True
            except:
                tagsField = False
                
            if self.Wd.find_element_by_xpath(DOM.CATEGORY_DESC).get_attribute("value")!="" or self.Wd.find_element_by_xpath(DOM.CATEGORY_REFERENCE_ID).get_attribute("value")!="" or tagsField:
                self.logi.appendMsg("FAIL - at least one of the fields saved the value edited although the edit action discard")
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - all changes where not saved after discard as expected")
                 
            # adding tag "_EditWarning" to the category
            self.logi.appendMsg("INFO - going to addg tag \"_EditWarning\" to the category: adi_category")
            self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
            time.sleep(3)
            rc = self.BasicFuncs.tblSelectAction(self.Wd, 0, "edit")
            if not rc:
                testStatus = False
                return
            time.sleep(3)
            self.categoryFuncs.updateCategory(newTags="__EditWarning", saveByButton=True)
            self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
            time.sleep(3)
            
            # going to select the category, pop up should appear and select the \"no\" option, page would be categories table and not category edit
            self.logi.appendMsg("INFO - going to select the category, pop up should appear and select the \"no\" option, page would be categories table and not category edit")
            self.BasicFuncs.selectEntryfromtbl(self.Wd, "adi_category",False)
            try:
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_EDIT)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_NO_BUTTON).click()
                time.sleep(1)
            except:
                self.logi.appendMsg("FAIL - the \"Edit Category\" popup warning did not appear")
                testStatus = False
            try:
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                self.logi.appendMsg("PASS - the system did not entered to category page as expected")
            except:
                self.logi.appendMsg("FAIL - the system entered to category page NOT as expected")
                testStatus = False
            
            # going to select the category, pop up should appear and select the \"Yes\" option, page would be category edit    
            self.logi.appendMsg("INFO - going to select the category, pop up should appear and select the \"Yes\" option, page would be category edit")
            self.BasicFuncs.selectEntryfromtbl(self.Wd, "adi_category",False)
            try:
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_EDIT)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
                time.sleep(1)
            except:
                self.logi.appendMsg("FAIL - the \"Edit Category\" popup warning did not appear")
                testStatus = False
            try:
                self.Wd.find_element_by_xpath(DOM.CATEGORY_NAME)
                self.logi.appendMsg("PASS - the system did not entered to category page as expected")
            except:
                self.logi.appendMsg("FAIL - the system entered to category page NOT as expected")
                testStatus = False
            
            # updating the category and save it
            self.logi.appendMsg("INFO - going to edit the category by adding description= autotest desc, tags=autotest tag, referenceId=autotest ref and save it this time")
            time.sleep(5)
            self.categoryFuncs.updateCategory(newName=None, newDesc="autotest desc", newTags="autotest tag", newReference="autotest ref")
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            self.BasicFuncs.selectEntryfromtbl(self.Wd, "adi_category",False)
            time.sleep(1)
            try:
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_EDIT)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
                time.sleep(1)
            except:
                self.logi.appendMsg("FAIL - the \"Edit Category\" popup warning did not appear")
                testStatus = False
            try: # check if there is tag and its text equal to what should have been
                tags = self.Wd.find_elements_by_xpath(DOM.ENTRY_CATEGORIES_LABELS)
                for tag in tags:
                    if tag.text == "autotest tag":
                        tagsField = False
                    else:
                        continue
            except:
                tagsField = True
                
            if self.Wd.find_element_by_xpath(DOM.CATEGORY_DESC).get_attribute("value")!="autotest desc" or tagsField or self.Wd.find_element_by_xpath(DOM.CATEGORY_REFERENCE_ID).get_attribute("value")!="autotest ref":
                self.logi.appendMsg("FAIL - at least one of the fields did not had the expected value after moving to categories table and enter to the category again")
                testStatus = False
            else:
                 self.logi.appendMsg("PASS - all changes saved as expected")
        
        except:
            testStatus = False
            pass     
       
    
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteCategories(self.Wd, "adi_category")
        except:
            pass     

        try:
            self.Wd.quit()
        except:
            pass
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1089','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1089','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main('test_1089.py -s')        
    #===========================================================================
        
        
        