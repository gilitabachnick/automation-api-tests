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
            self.logi = reporter2.Reporter2('TEST1251')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
            self.PlaylistFuncs = PlaylistFuncs.playlistfuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')

            #Upload entries with relevant category for the test
            #Login KMC
            self.logi.initMsg('test 1251 - Manual Playlist > Automation Sanity')
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            # Bulk Upload
            thetime = self.uploadfuncs.bulkUpload("entry", "xml_file_uploadEntries_test1000.xml")
            rc = self.uploadfuncs.bulkMessageAndStatus("Finished successfully",thetime)
            if not rc:
                self.logi.appendMsg("FAIL - could not upload the test entries with bulk upload, can not continue this test")
                testStatus = False
                return

        except:
            pass

    def test_1251(self):
        
        global testStatus       
        try:
            entriesList = ["test 1000_1","test 1000_2","test 1000_3","test 1000_4"]
            if (self.PlaylistFuncs.CreatPlayList("Playlist for test-1251", entriesList)):
                testStatus = True
            else:
                testStatus = False


            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(3)
        except Exception as Exp:
            print(str(Exp))
            testStatus = False
            pass
        
    def teardown_class(self):

        global testStatus

        try:
            self.BasicFuncs.deleteEntries(self.Wd,"test 1000_1;test 1000_2;test 1000_3;test 1000_4",entriesSeparator=";")
        except:
            pass

        try:
            self.Wd.quit()
        except:
            pass
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1251','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1251','0')
            assert True              
            
        
    #===========================================================================
    # pytest.main('test_1251.py -s') 
    #===========================================================================
        
        
        