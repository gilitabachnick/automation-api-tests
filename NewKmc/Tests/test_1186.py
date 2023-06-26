import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import uploadFuncs
import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs
import Entrypage
import datetime
import ClienSession
import DOM

import Config
import Entry
import Practitest
import autoitWebDriver

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

            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userTranscoding')
            self.pwd = inifile.RetIniVal(section, 'passTranscoding')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1186')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.transcodingEntryName = "TranscodingSettings1186"
            self.transcodingProfileName = "New Transcoding_1186"
            self.transcodingProfileNameWithoutFlavors = 'Transcoding_1186 - no flavors'
            self.vodEntryDefaultMetadataSettings = ''
            self.liveEntryDefaultMetadataSettings = ''
            self.transcodingFlavors = "Source,Mobile (3GP)"
            self.filePath = self.transcodingEntryName + ".mp4"
            self.remoteFile = r'\TranscodingSettings1375.mp4'

            self.PublisherID = inifile.RetIniVal(section, 'PublisherID')
            self.ServerURL = inifile.RetIniVal(section, 'ServerURL')
            self.APIAdminSecret = inifile.RetIniVal(section, 'APIAdminSecret')

            self.mySess = ClienSession.clientSession(self.PublisherID, self.ServerURL, self.APIAdminSecret)
            self.client = self.mySess.OpenSession()
            self.myentry = Entry.Entry(self.client, "autoLive_" + str(datetime.datetime.now()), "Live Automation test",
                                       "Live tag", "Admintag", "adi category", 1, None, None)  # file(filePth,'rb')

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
                self.filePath = self.remoteFile
        except:
            pass

    # ===========================================================================

    def test_1186_Transcoding_profiles(self):

        global testStatus
        self.logi.initMsg('test_1186_Transcoding - Validation Tests')
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

            self.logi.appendMsg("INFO - step 2: Going to upload vod entry and verify upload")
            try:
                entryStatus = self.basicFuncs.upload_entry_and_wait_for_status_ready(self.Wd, 'MPEG_5.mpg',
                                                                       self.sendto, self.basicFuncs, self.logi, self.Wdobj)
                if not entryStatus:
                    self.logi.appendMsg("FAIL - the entry \"MPEG_5.mpg\" status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - the entry \"MPEG_5.mpg\" uploaded successfully")

            except Exception as e:
                self.logi.appendMsg(e)
                testStatus = False
                pass

            self.logi.appendMsg("INFO - step 2.1: Going to get entry id")
            self.vodEntryDefaultMetadataSettings = self.basicFuncs.get_entry_id(self.Wd)
            if self.vodEntryDefaultMetadataSettings == '':
                testStatus = False
                self.logi.appendMsg("FAIL - step 2.1: FAILED to get entry id")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to create live stream entry")
            if self.myentry.AddEntryLiveStream(None, None, 0, 0) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to create live stream entry")
                return

            time.sleep(2)

            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()

            time.sleep(2)

            self.logi.appendMsg("INFO - step 3.1: Going to get live entry id")
            self.liveEntryDefaultMetadataSettings = self.basicFuncs.get_entry_id(self.Wd)
            if self.liveEntryDefaultMetadataSettings == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3.1: FAILED to get live entry id")
                return

            time.sleep(5)

            self.logi.appendMsg("INFO - step 4: Going to add 2 profiles with the same name")
            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileName) is False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to add 2 profiles with the same name")


            time.sleep(5)

            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileName) is False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4.1: FAILED to add 2 profiles with the same name")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to add vod profile without flavors")
            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileNameWithoutFlavors, profileType = 1, flavors="No flavor") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to add vod profile without flavors")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 5.1: Going to add live profile without flavors")
            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileNameWithoutFlavors, profileType = 2, flavors="No flavor") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5.1: FAILED to add live profile without flavors")


            time.sleep(5)

            self.logi.appendMsg("INFO - step 6: Going to add vod profile with same entry ID")
            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileName, profileType = 1, defaultMetadata=self.vodEntryDefaultMetadataSettings) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to add vod profile with same entry ID")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 6.1: Going to add live profile with same entry ID")
            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileName, profileType = 2, defaultMetadata=self.vodEntryDefaultMetadataSettings) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6.1: FAILED to add live profile with same entry ID")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to add live profile with offline entry")
            if self.settingsFuncs.addTranscodingProfile(profileName=self.transcodingProfileName, profileType = 2, defaultMetadata=self.liveEntryDefaultMetadataSettings) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to add live profile with offline entry")


            time.sleep(1)

        except:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: KMC login / Transcoding Settings Add")

    # ===========================================================================

    def teardown(self):

        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")

        global teststatus

        # Delete transcoding profiles
        try:
            profiles_list = [self.transcodingProfileName, self.transcodingProfileNameWithoutFlavors]
            for profile in profiles_list:
                self.settingsFuncs.deleteTranscodingProfiles(profile)
                time.sleep(2)
                self.settingsFuncs.deleteTranscodingProfiles(profile, profileType=2)

        except:
            pass

        # Close browser
        try:
            self.Wd.quit()
        except:
            pass

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1186', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1186', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_1186.py -s')
    #===========================================================================
