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
            self.logi = reporter2.Reporter2('test_1190')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.transcodingProfileName = "New Transcoding_1190"
            self.default_transcoding_profile_name = "Default"
            self.transcodingFlavors = "Source,Mobile (3GP)"
            self.filepth = 'QRcodeVideo.mp4'
            self.filepthlocal = 'QRcodeVideo.mp4'
            self.entrieName = 'QRcodeVideo'

            self.mySess = ClienSession.clientSession(self.PublisherID, self.ServerURL, self.APIAdminSecret)
            self.client = self.mySess.OpenSession()
            self.myentry = Entry.Entry(self.client, "autoLive_" + str(datetime.datetime.now()), "Live Automation test",
                                       "Live tag", "Admintag", "adi category", 1, None, None)  # file(filePth,'rb')

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepthlocal
        except:
            pass

    # ===========================================================================

    def test_1190_Transcoding_Action_Menu_Set_as_default(self):

        global testStatus
        self.logi.initMsg('test_1190_Transcoding - Set default transcoding profile')
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
            else:
                self.logi.appendMsg("PASS - step 1")

            self.logi.appendMsg("INFO - step 1.1: Going to set transcoding profile to default")
            if self.settingsFuncs.setDefaultTranscodingProfile(self.default_transcoding_profile_name) == False:
                self.logi.appendMsg("INFO - step 1.1: to set transcoding profile to default OR default is already set")
            else:
                self.logi.appendMsg("PASS - step 1.1")

            time.sleep(1)

            time.sleep(1)

            self.logi.appendMsg("INFO - step 2: Going to add a transcoding profile")
            if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName, flavors="Source") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 2: FAILED to add a trandscoding profile")
                return
            else:
                self.logi.appendMsg("PASS - step 2")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3: Going to set transcoding profile to default")
            if self.settingsFuncs.setDefaultTranscodingProfile(self.transcodingProfileName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3: FAILED to set transcoding profile to default")
                return
            else:
                self.logi.appendMsg("PASS - step 3")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 3.1: Going to verify default transcoding profile")
            if self.settingsFuncs.verifyDefaultTranscodingProfile(self.transcodingProfileName) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 3.1: FAILED to verify default transcoding profile")
                return
            else:
                self.logi.appendMsg("PASS - step 3.1")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 4: Going to refresh page")
            if self.Wd.refresh() == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 4: FAILED to refresh page")
                return
            else:
                self.logi.appendMsg("PASS - step 4")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 5: Going to upload from desktop with new default transcoding profile")
            if self.basicFuncs.upload_entry_and_wait_for_status_ready(self.Wd, self.filepth, self.sendto, self.basicFuncs,
                                                                      self.logi, self.Wdobj, no_media=True) == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 5: FAILED to upload from desktop with new default transcoding profile")
                return
            else:
                self.logi.appendMsg("PASS - step 5")

            time.sleep(1)

            self.logi.appendMsg("INFO - step 6: Going to retrun previous trasnscoding profile to default")
            if self.settingsFuncs.setDefaultTranscodingProfile("Default") == False:
                testStatus = False
                self.logi.appendMsg("FAIL - step 6: FAILED to retrun previous trasnscoding profile to default")
                return
            else:
                self.logi.appendMsg("PASS - step 6")

        except Exception as e:
            self.logi.appendMsg(str(e))
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: KMC login / Transcoding Settings delete")

    # ===========================================================================

    def teardown(self):

        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")

        global teststatus

        try:
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName)
            self.basicFuncs.deleteEntries(self.Wd, self.entrieName)
        except:
            pass

        # Close browser
        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1190 ', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1190', '0')
            assert True

    #===========================================================================
    # pytest.main('test_1190.py -s')
    #===========================================================================