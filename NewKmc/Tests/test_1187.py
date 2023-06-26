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
            self.logi = reporter2.Reporter2('test_1187')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.transcodingProfileName = "New Transcoding_1187"
            self.transcodingFlavors = "Source,Mobile (3GP)"
            self.remoteFile = r'\TranscodingSettings1187.mp4'

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

    def test_1187_Transcoding_add_and_delete_profiles(self):

        global testStatus
        self.logi.initMsg('test_1187_Transcoding - Bulk Actions')
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

            self.logi.appendMsg("INFO - step 2: Going to add less then 5 transcoding profiles")
            for i in range(3):
                if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName) == False:
                    testStatus = False
                    self.logi.appendMsg("FAIL - step 2: FAILED to add less then 5 trandscoding profiles")
                    return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to select less then 5 transcoding profiles and cancel delete")
            if self.settingsFuncs.deleteTranscodingProfiles(profileName=self.transcodingProfileName, confirmDelete=False) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to cancel delete confirmation")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3.1: Going to select less then 5 transcoding profiles and delete")
            if self.settingsFuncs.deleteTranscodingProfiles(profileName=self.transcodingProfileName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3.1: FAILED to delete less then 5 transcoding profiles")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to select add more then 5 transcoding profiles")
            for i in range(7):
                if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName) == False:
                    testStatus = False
                    self.logi.appendMsg("FAIL - step 4: FAILED to add more then 5 trandscoding profiles")
                    return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to select more then 5 transcoding profiles and delete")
            if self.settingsFuncs.deleteTranscodingProfiles(profileName=self.transcodingProfileName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to delete more then 5 transcoding profiles")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to add less then 5 live transcoding profiles")
            for i in range(3):
                if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName, profileType=2) == False:
                    testStatus = False
                    self.logi.appendMsg("FAIL - step 6: FAILED to add less then 5 live trandscoding profiles")
                    return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7: Going to select less then 5 live transcoding profiles and cancel delete")
            if self.settingsFuncs.deleteTranscodingProfiles(profileName=self.transcodingProfileName, profileType=2, confirmDelete=False) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7: FAILED to cancel delete confirmation")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 7.1: Going to select less then 5 live transcoding profiles and delete")
            if self.settingsFuncs.deleteTranscodingProfiles(profileName=self.transcodingProfileName, profileType=2) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 7.1: FAILED to delete less then 5 live transcoding profiles")
                return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 8: Going to add more then 5 transcoding profiles")
            for i in range(7):
                if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName, profileType=2) == False:
                    testStatus = False
                    self.logi.appendMsg("FAIL - step 8: FAILED to add more then 5 trandscoding profiles")
                    return

            time.sleep(1)

            self.logi.appendMsg("INFO - step 9: Going to select more then 5 transcoding profiles and delete")
            if self.settingsFuncs.deleteTranscodingProfiles(profileName=self.transcodingProfileName, profileType=2) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 9: FAILED to delete more then 5 transcoding profiles")
                return

            time.sleep(1)


        except:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: KMC login / Transcoding Settings Add")

    # ===========================================================================

    def teardown(self):

        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")

        global teststatus

        # Close browser
        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1187', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1187', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True

    #===========================================================================
    # pytest.main('test_1187.py -s')
    #===========================================================================
