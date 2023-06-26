
import datetime
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
import PlaylistFuncs
import CustomMetaData
import ClienSession
import settingsFuncs



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
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.partnerId = inifile.RetIniVal(section, 'partnerId')
            self.adminSecret = inifile.RetIniVal(section, 'adminSecret')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1159')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome") 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.PlaylistFuncs = PlaylistFuncs.playlistfuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            self.settingsfuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi) 
            
            mySess = ClienSession.clientSession(self.partnerId ,self.url, self.adminSecret)
            self.client = mySess.OpenSession('automation.upload@gmail.com')
            self.MData = CustomMetaData.CustomMetaData(self.client)
                
            fieldsEnding = str(datetime.datetime.now()).replace("-","").replace(":","").replace(" ","").split(".")[0]    
            self.fieldsarr = ['titleValue' + fieldsEnding,'Text' + fieldsEnding,'Date'+ fieldsEnding,'Entry-ID list'+ fieldsEnding,'Text select list'+ fieldsEnding]
            
        except Exception as e:
            print(e)
            pass    
        
    def test_1159(self):
        
        global testStatus 
        self.logi.initMsg('Settings - Add Custom Schema E2E - Entries')
        
        try:
            #Login KMC
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return
            
            self.logi.appendMsg("INFO - going to create a new customData profile")     
            #Go to Settings->CustomData
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()    
            self.Wd.find_element_by_xpath(DOM.CUSTOM_DATA_TAB).click()            
            
            #Click on 'Add Custom Schema' button
            try:                
                self.Wd.find_element_by_xpath(DOM.ADD_CUSTOM_SCHEMA_BUTTON).click() 
            except:           
                self.logi.appendMsg("FAIL - could not click on 'Add Custom Schema' option")
                testStatus = False  
                return
              
            time.sleep(2)
            #Add a title to the Schema
            self.Wd.find_element_by_xpath(DOM.CUSTOM_SCHEMA_TITLE).send_keys(self.fieldsarr[0]) 
            time.sleep(2)
                                   
            #Adding fields to the schema 
            self.logi.appendMsg("INFO - going to add 4 different type fields to the schema") 
            self.settingsfuncs.AddCustomField("Text",self.fieldsarr[1])
            self.settingsfuncs.AddCustomField("Date",self.fieldsarr[2])
            self.settingsfuncs.AddCustomField("Entry-ID list",self.fieldsarr[3])
            self.settingsfuncs.AddCustomField("Text select list",self.fieldsarr[4], "1,2,3,4")                             
            time.sleep(2)
            
            #Verify fields were added to the schema (table)
            
            popupWin = self.Wd.find_element_by_xpath(DOM.POPUP_WIN)
            rowsNum =  popupWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
                 
            if (len(rowsNum)-1 == 4):
                self.logi.appendMsg("PASS - all 4 fields were added to the schema")
            else:
                self.logi.appendMsg("FAIL - " +str(rowsNum) + " fields were added to the schema instead of 4 as expected")
                testStatus = False 
                                      
            #Save the schema    
            self.logi.appendMsg("INFO - going to save the new schema")
            self.Wd.find_element_by_xpath(DOM.ADD_CUSTOM_SCHEMA_SAVE_BUTTON).click()
            time.sleep(3)
            
            #Click on Content tab
            self.logi.appendMsg("INFO - going to Entries tab")

            time.sleep(2)
            
            #Go to Content-> Entries tab 
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            #Select the first entry in the table
            entryName = self.BasicFuncs.retTblRowName(self.Wd,1)
            self.BasicFuncs.selectEntryfromtbl(self.Wd, entryName, True)
        
            time.sleep(1)
            bFieldExsists,sFieldsName = self.settingsfuncs.checkCustomFieldsExist(False, self.fieldsarr)
            if not bFieldExsists:
                self.logi.appendMsg("FAIL - the following fields where not found in the entry custom meta data: " + sFieldsName)
                testStatus = False
            else:
               self.logi.appendMsg("PASS - all custom meta data scheme fields were added and appear as expected in the entry")
   
                
        except Exception as Ex:
            print(Ex)
            testStatus = False
            pass
        
    def teardown_class(self):
        
        global testStatus
        try:
            self.MData.DeleteMetaDataProfile(None,0,self.fieldsarr[0])
        except Exception as Ex:
            print(Ex)
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1159','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1159','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main(['test_1159_Settings - Add Custom Schema E2E - Entries.py'])        
    #===========================================================================
        
        