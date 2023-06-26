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
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))


            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userBulkUpload')
            self.pwd    = inifile.RetIniVal(section, 'passBulkUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1118')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.practitest = Practitest.practitest('4586')

            #Login to KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            #Search for categories with entitlement and set them to default value "No Restriction"
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, 'nadya_auto_entitlement*')
            time.sleep(2)
            self.BasicFuncs.CheckUncheckRowInTable(self.Wd,0)
            time.sleep(1)
           #  self.BasicFuncs.CheckUncheckRowInTable(self.Wd,"2-5")
            self.BasicFuncs.bulkSelectAction(self.Wd, "Change Content Privacy")
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_YES).click()
            time.sleep(2)
            self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_NO_RESTRICTION).click()
            self.Wd.find_element_by_xpath(DOM.CATEGORY_SAVE_CHANGES).click()
            time.sleep(2)
            self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_OK).click()
            self.categoryNames = ['nadya_auto_entitlement_1', 'nadya_auto_entitlement_2', 'nadya_auto_entitlement_3', 'nadya_auto_entitlement_warning_tag']
        except:
            pass

    def test_1118_ChangeContentPrivacy(self):

        global testStatus

        self.logi.initMsg('test 1118 ChangeContentPrivacy - Categories > Bulk Operations > Change Content Privacy')
        self.logi.appendMsg("INFO - going to set different content privacy to categories with entitlements")
         
        for categoryName in self.categoryNames[:2]:
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, categoryName)
          
            if  categoryName == 'nadya_auto_entitlement_1':
                self.BasicFuncs.CheckUncheckRowInTable(self.Wd, 1)
                time.sleep(1)
                self.BasicFuncs.bulkSelectAction(self.Wd, "Change Content Privacy")
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_PRIVATE).click()             
            else:
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, 'nadya_auto_entitlement*')
                time.sleep(2)
                self.BasicFuncs.CheckUncheckRowInTable(self.Wd, "2-3")
                #self.BasicFuncs.CheckUncheckRowInTable(self.Wd, "3-4")
                time.sleep(1)
                self.BasicFuncs.bulkSelectAction(self.Wd, "Change Content Privacy")
                time.sleep(1)

                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
                time.sleep(1) 

                self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_REQUIRE_AUTH).click()
                
            self.Wd.find_element_by_xpath(DOM.TAGS_ADD_TAGS_SAVE_CHANGES).click()
            time.sleep(1)

        
        for categoryName in self.categoryNames:  
            
            if categoryName == 'nadya_auto_entitlement_1':
                self.BasicFuncs.selectEntryfromtbl(self.Wd, 'nadya_auto_entitlement_1', False)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_ENTITLEMENT_SECTION).click()
                time.sleep(1)
                activeState = self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_PRIVATE)
                 
            elif categoryName == 'nadya_auto_entitlement_2':    
                self.BasicFuncs.selectEntryfromtbl(self.Wd, 'nadya_auto_entitlement_2',False)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_ENTITLEMENT_SECTION).click()
                time.sleep(1)
                activeState = self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_REQUIRE_AUTH)
                 
            elif categoryName == 'nadya_auto_entitlement_3':
                self.BasicFuncs.selectEntryfromtbl(self.Wd, 'nadya_auto_entitlement_3', False)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_ENTITLEMENT_SECTION).click()
                time.sleep(1)
                activeState = self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_NO_RESTRICTION)
                 
            elif categoryName == 'nadya_auto_entitlement_warning_tag':
                self.BasicFuncs.selectEntryfromtbl(self.Wd, 'nadya_auto_entitlement_warning_tag', False)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.CATEGORY_ENTITLEMENT_SECTION).click()
                time.sleep(1)
                activeState = self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_REQUIRE_AUTH)

            if str(activeState.get_attribute("class")).find("label-active") > 0 :
                self.logi.appendMsg("PASS - selected content privacy parameter is active as expected")
            else:
                self.logi.appendMsg("FAIL - selected content privacy parameter is not active as expected")
                testStatus = False
                
            self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
            time.sleep(1)

        self.logi.appendMsg("INFO - going to check that notification message for category without entitlements is displayed")
        self.BasicFuncs.searchEntrySimpleSearch(self.Wd, 'nadya_auto_entitlement_noEnt')
        self.BasicFuncs.CheckUncheckRowInTable(self.Wd, 1)
        time.sleep(1)
        self.BasicFuncs.bulkSelectAction(self.Wd, "Change Content Privacy")
        time.sleep(1)
        self.Wd.find_element_by_xpath(DOM.CATEGORY_PRIVACY_PRIVATE).click()
        self.Wd.find_element_by_xpath(DOM.TAGS_ADD_TAGS_SAVE_CHANGES).click()
        time.sleep(1)
        popupMessageText = self.BasicFuncs.selectOneOfInvisibleSameObjects(self.Wd, DOM.CATEGORY_ATTENTION_MSG)
        msgtxt = popupMessageText.text
        if msgtxt.find("Some of the selected categories do not have entitlement settings and therefore will not be updated by this action")>=0:
             self.logi.appendMsg("PASS - the notification message text is displayed as expected")
        else:
            self.logi.appendMsg("FAIL - the notification message text doesn't display as expected, expected=\"Some of the selected categories do not have entitlement settings and therefore will not be updated by this action\" and actualtext= " + msgtxt)
            testStatus = False
        
        
        
        
      
    
    def teardown_class(self):
        
        global testStatus
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1118','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1118','0')
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main('test_1118_ChangeContentPrivacy.py -s')
    #===========================================================================
          