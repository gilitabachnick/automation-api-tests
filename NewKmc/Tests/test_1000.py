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
import collections

import Config
import Practitest
import Entrypage
import CategoryFuncs
import PlaylistFuncs

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '1456'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()
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
        global testStatus
        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
        if isProd:
            section = "Production"
            self.env = 'prod'
            print ('PRODUCTION ENVIRONMENT')
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        else:
            section = "Testing"
            self.env = 'testing'
            print ('TESTING ENVIRONMENT')
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

        self.url = inifile.RetIniVal(section, 'Url')
        self.user = inifile.RetIniVal(section, 'userName6')
        self.pwd = inifile.RetIniVal(section, 'pass6')
        self.sendto = inifile.RetIniVal(section, 'sendto')
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        self.logi = reporter2.Reporter2('TEST1000')
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.entryPage = Entrypage.entrypagefuncs(self.Wd)
        self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
        self.categoryFuncs = CategoryFuncs.categoryfuncs(self.Wd, self.logi)
        self.PlaylistFuncs = PlaylistFuncs.playlistfuncs(self.Wd, self.logi)
        self.practitest = Practitest.practitest('4586')
        self.playlist_name = "Playlist for test-1000"

    def test_1000(self):
        global testStatus
        try:
            # Upload entries with relevant category for the test
            # Login KMC
            self.logi.initMsg(
                'test 1000 Manual Playlist Details > Content > Action Menu > Remove from Playlist & Duplicate')
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            # Bulk Upload
            thetime = self.uploadfuncs.bulkUpload("entry", "xml_file_uploadEntries_test1000.xml")
            time.sleep(5)
            rc = self.uploadfuncs.bulkMessageAndStatus("Finished successfully", thetime, 600)
            if not rc:
                self.logi.appendMsg(
                    "FAIL - could not upload the test's entries with bulk upload, can not continue this test")
                testStatus = False
                return

            entriesList = ["test 1000_1", "test 1000_2", "test 1000_3", "test 1000_4"]
            self.PlaylistFuncs.CreatPlayList(self.playlist_name, entriesList)

            # Taking the playlist's duration before removing an entry- 03:28 as integer number (3+28=31)
            PlaylsitActDuration = self.Wd.find_element_by_xpath(DOM.PLAYLIST_DURATION).text
            durArr = PlaylsitActDuration.split(":")
            durBefore = int(durArr[1]) + int(durArr[2])

            # Saving the entry name of the entry that is going to be removed
            removeEntry = self.BasicFuncs.retTblRowName(self.Wd, 1, "entry")

            # Click on the '...' Actions button for the entry in the first row:
            self.logi.appendMsg("INFO - going to select actions>Remove from Playlist for the first row entry")
            # Select 'Remove from Playlist' option
            if self.BasicFuncs.tblSelectAction(self.Wd, 0, "Remove from Playlist") != True:
                self.logi.appendMsg("FAIL - could not choose \"Remove from Playlist\" option")
                testStatus = False
                return
            time.sleep(2)

            # save changes
            self.Wd.find_element_by_xpath(DOM.CATEGORY_SAVE).click()
            time.sleep(3)

            # Taking the playlist's duration after removing an entry - 02:36 as integer (2+36=38)
            PlaylsitActDuration = self.Wd.find_element_by_xpath(DOM.PLAYLIST_DURATION).text
            durArr = PlaylsitActDuration.split(":")
            durAfter = int(durArr[1]) + int(durArr[2])

            # First validation- duration time before minus duration time after = 7 (38-31=7)
            if durAfter - durBefore == 7:
                self.logi.appendMsg("PASS - entry was removed, the duration changed to 02:36 as expected")
            else:
                self.logi.appendMsg(
                    "FAIL - entry was NOT removed, the duration was NOT changed to 02:36 as it should have been")
                testStatus = False

            # Second validation - the row of the removed entry is not displayed anymore:

            # counting rows' num in the playlist after the remove action
            numOfRows2 = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            arr2 = []
            # entering the entries' names into an array
            for i in range(1, numOfRows2 + 1):
                arr2.append(self.BasicFuncs.retTblRowName(self.Wd, i, "entry"))

            # Index function returns exception indicating the removed entry was not found - that's the PASS flow - otherwise - FAIL.
            try:
                arr2.index(removeEntry)
                self.logi.appendMsg("FAIL - The row of the removed entry is still displayed")
            except:
                self.logi.appendMsg(
                    "PASS - The removed entry row is not displayed anymore in the playlist, as expected")

            # Saving the entry name of future duplicate entry
            dupEntryName = self.BasicFuncs.retTblRowName(self.Wd, 1, "entry")

            # Click on the '...' Actions button for the entry in the first row::
            self.logi.appendMsg("INFO - going to select actions>Duplicate for the first row entry")
            # Select 'Duplicate' option
            if self.BasicFuncs.tblSelectAction(self.Wd, 0, "Duplicate") != True:
                self.logi.appendMsg("FAIL - could not choose \"Duplicate\" option")
                testStatus = False
            else:
                time.sleep(2)

                # counting rows' num in the playlist after the duplicate action
                numOfRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                arr = []
                # entering the entries' names into an array
                for i in range(1, numOfRows + 1):
                    arr.append(self.BasicFuncs.retTblRowName(self.Wd, i, "entry"))

                dupEntry = [item for item, count in collections.Counter(arr).items() if count > 1]
                if dupEntry[0] == dupEntryName:
                    self.logi.appendMsg("PASS - the entry- " + dupEntryName + " was duplicated as expected")
                else:
                    self.logi.appendMsg("FAIL - the entry- " + dupEntryName + " was NOT duplicated")
                    testStatus = False

                # save changes
                self.Wd.find_element_by_xpath(DOM.CATEGORY_SAVE).click()
                time.sleep(3)

                # Remove one of the duplicated entries:
                # Taking the playlist's duration before removing entry- 03:28 as integer number (3+28=31)
                PlaylsitActDuration = self.Wd.find_element_by_xpath(DOM.PLAYLIST_DURATION).text
                durArr = PlaylsitActDuration.split(":")
                durBefore = int(durArr[1]) + int(durArr[2])

                # Click on the '...' Actions button for the entry in the first row:
                self.logi.appendMsg("INFO - going to select actions>Remove from Playlist for the duplicated entry")
                # Select 'Remove from Playlist' option
                if self.BasicFuncs.tblSelectAction(self.Wd, 1, "Remove from Playlist") != True:
                    self.logi.appendMsg("FAIL - could not choose \"Remove from Playlist\" option")
                    testStatus = False
                    return
                time.sleep(2)

                # save changes
                self.Wd.find_element_by_xpath(DOM.CATEGORY_SAVE).click()
                time.sleep(3)

                # counting rows' num in the playlist after the removing action
                numOfRows1 = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                arr1 = []

                # entering the entries' names into an array
                for i in range(1, numOfRows1 + 1):
                    arr1.append(self.BasicFuncs.retTblRowName(self.Wd, i, "entry"))

                dupEntry1 = []

                dupEntry1 = [item for item, count in collections.Counter(arr1).items() if count > 1]
                if len(dupEntry1) == 0:
                    self.logi.appendMsg("PASS - the entry- " + dupEntryName + " was removed as expected")
                else:
                    self.logi.appendMsg("FAIL - the entry- " + dupEntryName + " was NOT removed")
                    testStatus = False
        except Exception as e:
            print(e)
            testStatus = False
            return

    def teardown_class(self):
        global testStatus
        try:
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(3)
            self.BasicFuncs.deleteEntries(self.Wd, "test 1000_*")
            print("======= Teardown =======")
            try:
                # To fix 'deleted, 'not found' entries
                if self.Wd.find_element_by_xpath("//*[contains(text(),'not found')]"):
                    self.Wd.find_element_by_xpath("//*[contains(text(),'OK') and contains(@class,'button')]").click()
                    #self.Wd.find_element_by_xpath('//*[@id="appContainer"]/p-confirmdialog[2]/div/div/div[3]/p-footer/button/span').click()
            except:
                pass

            self.logi.appendMsg("INFO - entries where deleted successfully")
            time.sleep(1)

            self.Wd.find_element_by_xpath(DOM.PLAYLISTS_TAB).click()
            self.PlaylistFuncs.delete_playlist(self.Wd, self.playlist_name)
            self.logi.appendMsg("Pass - playlists where deleted successfully")

        except Exception as e:
            print("Failed - to delete entries or playlist")
            print(e)

        try:
            self.Wd.quit()
            if testStatus == False:
                self.logi.reportTest('fail', self.sendto)
                self.practitest.post(Practi_TestSet_ID, '1000', '1')
                assert False
            else:
                self.logi.reportTest('pass', self.sendto)
                self.practitest.post(Practi_TestSet_ID, '1000', '0')
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    if Run_locally:
        pytest.main(args=['test_1000.py', '-s'])
    # ===========================================================================

