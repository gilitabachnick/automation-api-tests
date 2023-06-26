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
import CategoryFuncs

import Config
import Practitest

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
                self.pwd = inifile.RetIniVal(section, 'passBulkUpload')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.pwd = inifile.RetIniVal(section, 'passBulkUploadTesting')
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userBulkUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1090_CategoriesActionDelete')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.categoryfuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            
            #Login, navigation to Categories, Delete existing categories, clear active filters
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(2)
            self.categoryfuncs.removeExistingCategory("nadya_auto_category*")
            self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
            
            #create different categories: without sub-category, with warning tag, with sub-category
            self.categoryNames = ['nadya_auto_category_no_sub_categories', 'nadya_auto_category_with_warning_tag', 'nadya_auto_category_with_sub_categories', 'nadya_auto_category_to_move']
            
            for categoryName in self.categoryNames:
                if categoryName == 'nadya_auto_category_to_move':
                    rc = self.categoryfuncs.addCategory(categoryName,"nadya_auto_category_with_sub_categories")
                else:
                    rc = self.categoryfuncs.addCategory(categoryName,"no")
                if categoryName == 'nadya_auto_category_with_warning_tag': 
                    self.categoryfuncs.updateCategory(newTags="__EditWarning", saveByButton=True)
                    time.sleep(3)
                
                time.sleep(3)
                self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                time.sleep(1)
            
        except:
            pass    
        
    def test_1090_CategoriesActionDelete(self):
        
        global testStatus
        self.logi.initMsg('test 1090_CategoriesActionDelete')

        try:
            #delete created categories: without sub-category, with warning tag, with sub-category
            #the deletion of the categories would be only for the first 3 elements of the list
            for categoryName in self.categoryNames[:3]:
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, categoryName) 
                rc = self.BasicFuncs.tblSelectAction(self.Wd, 0, "delete")
                time.sleep(4)
                self.logi.appendMsg("INFO - going to check deletion popup message")
                popupMessageText = self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE).text
                
                if categoryName == 'nadya_auto_category_no_sub_categories':
                    msgTxt = "Are you sure you want to delete this category"
                elif categoryName == 'nadya_auto_category_with_warning_tag':
                    msgTxt = "This category was created by another application and deleting it will effect this application or site.\nAre you sure you want to delete this category?"   

                else:
                    msgTxt = "This category will be deleted with its sub-categories"
                
                
                if popupMessageText.find(msgTxt) >= 0:
                    self.logi.appendMsg("PASS - the popup message contains the warning text as expected - " + msgTxt)
                else:
                    self.logi.appendMsg("FAIL - the popup message doesn't contain the expected warning text was - " + msgTxt + ", the actual message was: " + popupMessageText)
                    testStatus = False
                    
                self.logi.appendMsg("INFO - going to confirm deletion")
                
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
                time.sleep(3)
                    
               
                self.logi.appendMsg("INFO - going to check that deleted category " + categoryName + " doesn't exist")
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, categoryName)
                numOfRowsInTable = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                if numOfRowsInTable!=0:
                    self.logi.appendMsg("FAIL - should retrieve 0 entries from the search and actually got - " + str(numOfRowsInTable) + " Entries")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - retrieved 0 entries from the search as expected")

        except:
            testStatus = False
            pass
        
    
    def teardown_class(self):
        
        global testStatus
        try:
            self.Wd.quit()
        except:
            pass
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1090','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1090','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main('test_1090_CategoriesActionDelete.py -s')    
    #===========================================================================
          