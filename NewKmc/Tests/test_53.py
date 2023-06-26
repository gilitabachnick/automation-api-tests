import os
import sys
import time

import pytest

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
        self.user   = inifile.RetIniVal(section, 'userName4')
        self.pwd    = inifile.RetIniVal(section, 'pass')
        self.sendto = inifile.RetIniVal(section, 'sendto')
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        self.practitest = Practitest.practitest('4586')
        
        self.logi = reporter2.Reporter2('TEST53')
        
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        
    def test_53(self):
        global testStatus
        
        self.logi.initMsg('test 53')
        
        #Login KMC
        self.Wd.maximize_window()
        rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
        
        if rc:
            # open refine filter and verify Custom metadata filters appear
            self.logi.appendMsg("INFO - going to open refine filter and verify Custom metadata filters appear")
            try:
                time.sleep(5)
                self.Wd.find_element_by_xpath(DOM.REFINE_BUTTON).click()
            except:
                self.logi.appendMsg("FAIL - could not find the ""Refine Filter"" button, can not continue the test")
                assert False
            
            expTitles = ['ADDITIONAL FILTERS','2ND CUSTOM METADATA SCHEMA','ENTRIESSCHEMA4AUTO -31CHARMAX','DEPARTMENT INFO']
            actTitles = []    
            refineWin = self.Wd.find_element_by_xpath(DOM.REFIN_POP)
            grpTitles = refineWin.find_elements_by_xpath(DOM.REFINE_GROUP_TITLE)
            if len(grpTitles)!=4:
                self.logi.appendMsg("FAIL - should have been 4 refine filter group titles and actually there are: " + str(len(grpTitles)))
                testStatus = False
                
            else:
                for i in range(0,4):
                    actTitles.append(grpTitles[i].text)
                    
                if set(expTitles) == set(actTitles):
                    self.logi.appendMsg("PASS - the group titles, of the Refine filters appeared as expected")
                else:
                    self.logi.appendMsg("FAIL - the group titles, of the Refine filters should have been: " + '[%s]' % ', '.join(map(str, expTitles)) + " and the actaull titles are: " + '[%s]' % ', '.join(map(str, actTitles)))
                
            
            self.logi.appendMsg("INFO - going to expand the custom metadata filter name \"Field4Auto-TextSelectList\" and verify all sub filters there")
            filterFathers = self.Wd.find_elements_by_xpath(DOM.REFINE_SUBJECT_ROW)
            theOneToExpand = None
            for filt in(filterFathers):
                if filt.text.find("Field4Auto-TextSelectList")!=-1:
                    theOneToExpand = filt
                    break
                
            if theOneToExpand==None:
                self.logi.appendMsg("FAIL - could not find father filter name ""Field4Auto-TextSelectList""")
                testStatus = False
            else:
                expLeafs = ['Value1_4Auto','Select Single Value form this list','Val4scroll1','Val4scroll2','Val4scroll3']
                actLeafs = []
                theOneToExpand.find_element_by_xpath(DOM.REFINE_EXPAND).click()
                leafs = theOneToExpand.find_elements_by_xpath(DOM.REFINE_LEAF_SUBJECT_ROW)
                for i in(leafs):
                    actLeafs.append(i.text)
                if set(expLeafs) == set(actLeafs):
                    self.logi.appendMsg("PASS - the sun filters appeared as expected")
                else:
                    self.logi.appendMsg("FAIL - the sun filters should have been: " + '[%s]' % ', '.join(map(str, expLeafs)) + " and the actual titles are: " + '[%s]' % ', '.join(map(str, actLeafs)))
                    testStatus = False

    
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        global testStatus
        try:
            self.Wd.quit()
        except:
            pass
        try:
            if testStatus == False:
                self.practitest.post(Practi_TestSet_ID, '53','1')
                self.logi.reportTest('fail',self.sendto)
                assert False
            else:
                self.practitest.post(Practi_TestSet_ID, '53','0')
                self.logi.reportTest('pass',self.sendto)
                assert True
        except:
            pass



    #===========================================================================
    #pytest.main(['test_53.py','-s'])
    #===========================================================================
