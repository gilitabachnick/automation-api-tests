import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import MySelenium
import KmcBasicFuncs
import uploadFuncs
import reporter2

import Config
import Practitest
import Entrypage
import CategoryFuncs
import PlaylistFuncs

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True


class TestClass:

    # ===========================================================================
    # SETUP
    # ===========================================================================
    def setup_class(self):

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

        self.url = inifile.RetIniVal(section, 'Url')
        self.user = inifile.RetIniVal(section, 'userName5')
        self.pwd = inifile.RetIniVal(section, 'pass5')
        self.sendto = inifile.RetIniVal(section, 'sendto')
        self.basicFuncs = KmcBasicFuncs.basicFuncs()
        self.logi = reporter2.Reporter2('test_70_refine_search_metadata')
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.entryPage = Entrypage.entrypagefuncs(self.Wd)
        self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
        self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
        self.PlaylistFuncs = PlaylistFuncs.playlistfuncs(self.Wd, self.logi)
        self.practitest = Practitest.practitest('4586')
        self.active_filter_list = ["Marketing", "Product", "Engineering", "FInance", "Sales", "HR", "Management"]


    def test_70_refine_search_metadata(self):

        global testStatus
        self.logi.initMsg('test_70_refine_search_metadata')
        testStatus = True
        try:

            # Invoke and login
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 2: Going to open refine search and select Department Division")
            if self.basicFuncs.selectRefineFilter(self.Wd, pthToselection="Department Division") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to open refine search select Department Division")
                return
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to verify active filter list")
            if self.basicFuncs.verify_entrires_active_filter_selected(self.Wd, self.logi, self.active_filter_list) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to verify active filter list")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to unselect HR tag from refine search")
            if self.basicFuncs.selectRefineFilter(self.Wd, pthToselection="Department Division;HR") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to unselect HR tag from refine search")
                return
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to verify active filter list without HR")
            self.active_filter_list.remove("HR")
            if self.basicFuncs.verify_entrires_active_filter_selected(self.Wd, self.logi, self.active_filter_list) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to verify active filter list without HR")
                return
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to close active filter tag Product")
            if self.basicFuncs.closeFilterTag(self.Wd, tagText="Product") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to close active filter tag")
                return
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to verify active filter list without Product")
            self.active_filter_list.remove("Product")
            if self.basicFuncs.verify_entrires_active_filter_selected(self.Wd, self.logi, self.active_filter_list) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to verify active filter list without Product")
                return
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(1)

        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: Remove active filter / Verify active filter list / Compare active filter list")

    def teardown_class(self):
        global testStatus

        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '70', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '70', '0')
            assert True

    #===========================================================================
    # pytest.main('test_70_refine_search_metadata.py -s')
    #===========================================================================


