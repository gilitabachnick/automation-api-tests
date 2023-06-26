import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

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
        self.user = inifile.RetIniVal(section, 'userName6')
        self.pwd = inifile.RetIniVal(section, 'pass6')
        self.sendto = inifile.RetIniVal(section, 'sendto')
        self.basicFuncs = KmcBasicFuncs.basicFuncs()
        self.logi = reporter2.Reporter2('test_1001_playlist_move_entries')
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
        self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
        self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
        self.PlaylistFuncs = PlaylistFuncs.playlistfuncs(self.Wd, self.logi)
        self.practitest = Practitest.practitest('4586')
        self.playlist_name = "Playlist for test-1001"


    def test_1001_playlist_move_entries(self):

        global testStatus
        self.logi.initMsg('test_1001_playlist_move_entries')
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

            # delete entries
            try:
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                self.basicFuncs.deleteEntries(self.Wd, "test 1000_1;test 1000_2;test 1000_3;test 1000_4",
                                              entriesSeparator=";")
            except:
                pass

            time.sleep(1)

            self.logi.appendMsg("INFO - step 2: Going to bulk upload entries for playlist")
            thetime = self.uploadfuncs.bulkUpload("entry", "xml_file_uploadEntries_test1000.xml")
            rc = self.uploadfuncs.bulkMessageAndStatus("Finished successfully", thetime)
            if not rc:
                self.logi.appendMsg("FAIL - step 2: could not upload the test entries with bulk upload, can not continue this test")
                testStatus = False
                return
            else:
                self.logi.appendMsg("Pass - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to create playlist")
            # Use same file from test 1000
            entriesList = ["test 1000_1", "test 1000_2", "test 1000_3", "test 1000_4"]

            if self.PlaylistFuncs.CreatPlayList(self.playlist_name, entriesList) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to create playlist")
                return
            else:
                self.logi.appendMsg("Pass - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to move entry 1000_3 up")
            if self.PlaylistFuncs.verify_entry_position_and_move(move_diraction='Move Up', entry_name='test 1000_3') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to move entry 1000_3 up")
            else:
                self.logi.appendMsg("Pass - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to move entry 1000_2 to top")
            if self.PlaylistFuncs.verify_entry_position_and_move(move_diraction='Move to Top', entry_name='test 1000_2') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to move entry 1000_2 to Top")
            else:
                self.logi.appendMsg("Pass - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to move entry 1000_2 to bottom")
            if self.PlaylistFuncs.verify_entry_position_and_move(move_diraction='Move to Bottom', entry_name='test 1000_2') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to move entry 1000_2 to bottom")
            else:
                self.logi.appendMsg("Pass - step 6")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to move entry 1000_1 down")
            if self.PlaylistFuncs.verify_entry_position_and_move(move_diraction='Move Down', entry_name='test 1000_1') == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to move entry 1000_1 down")
            else:
                self.logi.appendMsg("Pass - step 7")

            time.sleep(1)

        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: Create playlist / move entries in playlist")

    def teardown_class(self):
        global testStatus
        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_YES).click()
            time.sleep(3)
            self.basicFuncs.deleteEntries(self.Wd, "test 1000_1;test 1000_2;test 1000_3;test 1000_4",
                                          entriesSeparator=";")
            self.logi.appendMsg("INFO - entries where deleted successfully")

            time.sleep(1)

            self.Wd.find_element_by_xpath(DOM.PLAYLISTS_TAB).click()
            self.PlaylistFuncs.delete_playlist(self.Wd, self.playlist_name)
            self.logi.appendMsg("INFO - playlists where deleted successfully")
        except Exception as e:
            print(e)
            pass

        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1001', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1001', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_1001_playlist_move_entries.py -s')
    #===========================================================================


