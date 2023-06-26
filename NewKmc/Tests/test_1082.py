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
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1082')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.practitest = Practitest.practitest('4586')        
        
        except:
            pass    
        
    def test_1082(self):
        
        global testStatus 
        self.logi.initMsg('test 1082 Categories > Search Field ')
        
        try:
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            
            self.logi.appendMsg("INFO - going to search for \"Education\" should retrieve one category named: Education")
            self.Wd.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
            time.sleep(3)
            
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "Education")
            
            # verify only one category came back from the search
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            if numOfRows!=1:
                self.logi.appendMsg("FAIL - expected one category and actually retrieved -" + str(numOfRows))
                testStatus = False
            else:
                self.logi.appendMsg("PASS - expected one category and actually retrieved it")
            
            # verify the category name is correct
            catName = self.BasicFuncs.retTblRowName(self.Wd, 1, "category")
            try:
                if catName == "Education":
                    self.logi.appendMsg("PASS - expected for category name=\"Education\" and retrieved it as expected")
                else:
                    self.logi.appendMsg("FAIL - expected for category name=\"Education\" and actually retrieved category name=\"" + catName + "\"")
                    testStatus = False
            except:
                testStatus = False
                self.logi("FAIL - could not retrieve the category name from the first row")
            
            
            self.logi.appendMsg("INFO - going to search for \"unlisted1\" should retrieve No Results")
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, "unlisted1")    
            # verify no results came back from the search
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            if numOfRows!=0:
                self.logi.appendMsg("FAIL - expected None categories to retrieve and actually retrieved -" + str(numOfRows))
                testStatus = False
            else:
                self.logi.appendMsg("PASS - expected None categories to retrieve and that's what happened")
            
           
            self.logi.appendMsg("INFO - going to search for \"player\" tag should retrieve one category named: Video Player")
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, 'player')
            
            # verify only one category came back from the search
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            if numOfRows!=1:
                self.logi.appendMsg("FAIL - expected one category and actually retrieved -" + str(numOfRows))
                testStatus = False
            else:
                self.logi.appendMsg("PASS - expected one category and actually retrieved it")
            
            # verify the category name is correct
            catName = self.BasicFuncs.retTblRowName(self.Wd, 1, "category")
            try:
                if catName == "Video Player":
                    self.logi.appendMsg("PASS - expected for category name=\"Video Player\" and retrieved it as expected")
                else:
                    self.logi.appendMsg("FAIL - expected for category name=\"Video Player\" and actually retrieved category name=\"" + catName + "\"")
                    testStatus = False
            except:
                testStatus = False
                self.logi.appendMsg("FAIL - could not retrieve the category name from the first row")
            
            
            self.logi.appendMsg("INFO - going to search for \"located\" description should retrieve one category named: Tutorials")
            self.BasicFuncs.searchEntrySimpleSearch(self.Wd, 'located')
            
            # verify only one category came back from the search
            numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            if numOfRows!=1:
                self.logi.appendMsg("FAIL - expected one category and actually retrieved -" + str(numOfRows))
                testStatus = False
            else:
                self.logi.appendMsg("PASS - expected one category and actually retrieved it")
            
            # verify the category name is correct
            catName = self.BasicFuncs.retTblRowName(self.Wd, 1, "category")
            try:
                if catName == "Tutorials":
                    self.logi.appendMsg("PASS - expected for category name=\"Tutorials\" and retrieved it as expected")
                else:
                    self.logi.appendMsg("FAIL - expected for category name=\"Tutorials\" and actually retrieved category name=\"" + catName + "\"")
                    testStatus = False
            except:
                testStatus = False
                self.logi.appendMsg("FAIL - could not retrieve the category name from the first row")
        
        except:
            testStatus = False
            pass
        
    def teardown_class(self):
        
        global testStatus
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1082','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1082','0')
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main('test_1082.py -s')        
    #===========================================================================
        
        
        