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


#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
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
            self.logi = reporter2.Reporter2('TEST1115')
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
            self.categoryFuncs.removeExistingCategory("test1115_category*")
            for i in range(1,3):
                rc = self.categoryFuncs.addCategory("test1115_category" + str(i),"no")   
                if rc==True:
                    self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
                    time.sleep(3)
                else:
                    self.logi.appendMsg("FAIL - the creation of the new category for the test fail, therefore can NOT continue this test")
                    testStatus= False
                    return

        except Exception as Exp:
            print(Exp)
            testStatus = False
        
            
    def test_1115(self):
        
        global testStatus 
        self.logi.initMsg('test 1115 Categories > Bulk Operations > Add / Remove Tags > Add Tags')
        
        try:
            # select the category test1115_category and cancel bulk action add tag without save
            self.logi.appendMsg("INFO - going to select the category test1115_category1 and cancel bulk action add tag without save")
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "test1115_category1")
            self.entryPage.selectEntries("1")
            self.BasicFuncs.bulkSelectAction(self.Wd, "Add / Remove Tags>add tags")
            time.sleep(1)
            closeButton = self.BasicFuncs.selectOneOfInvisibleSameObjects(self.Wd,DOM.UPLOAD_SETTINGS_CLOSE)
            closeButton.click()
            time.sleep(1)
            self.logi.appendMsg("INFO - going to verify the category is selected after closing the window")
            tblRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
            chkrow1 = tblRows[0].find_element_by_xpath(DOM.CATEGORY_TBL_CHECKBOX)
            isClicked = chkrow1.get_attribute("aria-checked")
            if isClicked == "true":
               self.logi.appendMsg("PASS - the category was selected after closing the window, as expected")
               chkrow1.click()
            else:
               self.logi.appendMsg("FAIL - the category was not selected after closing the window, NOT as expected") 
               testStatus = False
               
            for step in range(1,5): 
                
                itterStatus = True
                
                if step==1:
                    tagName = 'mediaspace'
                    self.logi.appendMsg("INFO - going to select 2 categories test1115_category1-3 and add tag \"mediaspace\" with bulk action and auto complete")
                    singleTag = None
                if step==2:
                    tagName = 'AA'
                    self.logi.appendMsg("INFO - going to select 2 categories test1115_category1-3 and add tag \"AA\" with bulk action")
                    singleTag = None
                if step==3:
                    tagName = 'autoLongTag'
                    self.logi.appendMsg("INFO - going to select 2 categories test1115_category1-3 and add long tag \"autoLongTag\" with bulk action")
                    singleTag = None
                if step==4:
                    tagName = 'first\n second\n third\n forth\n fifth'
                    self.logi.appendMsg("INFO - going to select 2 categories test1115_category1-3 and add multiple tags \"first second third forth fifth\" with bulk action")
                    singleTag = None
                self.Wd.find_element_by_xpath(DOM.ENTRY_FILTER_CLEAR_ALL).click()
                time.sleep(3)
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "test1115_category*")
                self.entryPage.selectEntries("1,3")
                self.BasicFuncs.bulkSelectAction(self.Wd, "Add / Remove Tags>add tags")
                time.sleep(1)
                addTagsWin = self.Wd.find_element_by_xpath(DOM.POPUP_WIN_ADD_TAGS)
                addTagsWin.find_element_by_xpath(DOM.TAGS_ADD_TAGS_NAME).send_keys(tagName)
                            
                if step==1:
                    time.sleep(2)
                    autoCompLst = self.Wd.find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_LIST)
                    
                    try:
                        autoCompLst.click()
                    except:
                        self.logi.appendMsg('FAIL - the autocomplete search did not find the tag \"mediaspace\"')
                        closeButton.click()
                        time.sleep(1)
                        self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_CONFIRM_DELETE_YES).click()
                        time.sleep(3)
                        testStatus = False
                        itterStatus = False
                        continue
                
                
                addTagsWin.find_element_by_xpath(DOM.TAGS_ADD_TAGS_SAVE_CHANGES).click()
                time.sleep(3)
                
                self.logi.appendMsg("INFO - going to verify the tag- " +tagName+ " was placed ok in the entries")
                
                if itterStatus:
                    for i in range(1,3):
                        self.BasicFuncs.selectEntryfromtbl(self.Wd, "test1115_category" + str(i), False)
                        
                        rc = self.categoryFuncs.verifyCategoryValues(None, None, ["first", "second", "third", "forth", "fifth"], None, singleTag)
                        if not rc:
                            testStatus = False
                            self.logi.appendMsg("FAIL - the entry: test1115_category" + str(i)+ " had not contained the tag- " + tagName)
                        else:
                            self.logi.appendMsg("PASS - the entry: test1115_category" + str(i)+ " contained the tag- " + tagName + " as expected")
                        self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
                        time.sleep(2)
        except Exception as Exp:
            print(Exp)
            testStatus = False

    
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteCategories(self.Wd, "test1115_category*")
        except Exception as Exp:
            print(Exp)

        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)

        try:
            if testStatus == False:
                self.logi.reportTest('fail',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '1115','1')
                assert False
            else:
                self.logi.reportTest('pass',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '1115','0')
                assert True
        except Exception as Exp:
            print(Exp)
        
    # ===========================================================================
    # pytest.main('test_1115.py -s')        
    if Run_locally:
        pytest.main(args=['test_1115', '-s'])
    # ===========================================================================
        
        