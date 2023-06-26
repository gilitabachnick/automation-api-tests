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
            self.logi = reporter2.Reporter2('test_1188')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.transcodingProfileName = "New Transcoding_1188"
            self.transcodingFlavors = "Source,Mobile (3GP)"
            self.defaultMetadataSettingsEntry = "0_gx41ku23"
            self.remoteFile = r'\TranscodingSettings1188.mp4'

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

    def test_1188_Transcoding_Action_Menu_Edit(self):

        global testStatus
        self.logi.initMsg('test_1188_Transcoding - Action Menu Edit')
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

            self.logi.appendMsg("INFO - step 2: Going to add a transcoding profile with a non exsiting entry id Default Metadata Settings")
            if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName, defaultMetadata=self.defaultMetadataSettingsEntry) == False:
                self.logi.appendMsg("PASS - step 2")
            else:
                testStatus = False
                self.logi.appendMsg(
                    "FAIL - step 2: FAILED to trandscoding profile with a non exsiting entry id Default Metadata Settings was added")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to add a transcoding profile")
            if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to add a trandscoding profile")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to update transcoding description of profile")
            if self.settingsFuncs.updateTranscodingProfile(self.transcodingProfileName, profileDesc="This is a test") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to update transcoding profile")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to update transcoding metadate profile")
            if self.settingsFuncs.updateTranscodingProfile(self.transcodingProfileName, defaultMetadata="This is a test 23", exitWithoutSaving=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to update transcoding profile")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to add a LIVE transcoding profile with a non exsiting entry id Default Metadata Settings")
            if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName, profileType=2,defaultMetadata=self.defaultMetadataSettingsEntry) == False:
                self.logi.appendMsg("PASS - step 6")
            else:
                testStatus = False
                self.logi.appendMsg(
                    "FAIL - step 6: FAILED to add a LIVE trandscoding profile with a non exsiting entry id Default Metadata Settings was added")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to add a live transcoding profile")
            if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName, profileType=2) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to add a trandscoding profile")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 8: Going to update transcoding description of profile")
            if self.settingsFuncs.updateTranscodingProfile(self.transcodingProfileName, profileType=2, profileDesc="This is a test") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 8: FAILED to update transcoding profile")


            time.sleep(1)

            self.logi.appendMsg("INFO - step 9: Going to update transcoding metadate profile")
            if self.settingsFuncs.updateTranscodingProfile(self.transcodingProfileName, profileType=2, defaultMetadata="This is a test 23", exitWithoutSaving=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 9: FAILED to update transcoding profile")


        except:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: KMC login / Transcoding Settings Add")

    # ===========================================================================

    def teardown(self):

        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")

        global teststatus

        try:
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName)
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName, profileType=2)
        except:
            pass

        # Close browser
        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1188', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1188', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_1187.py -s')
    #===========================================================================
