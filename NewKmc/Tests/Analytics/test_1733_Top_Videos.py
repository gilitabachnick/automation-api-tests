import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs
import MyCsv
import General

import Config
import Practitest
import autoitWebDriver
import analyticsFuncs

### Jenkins params ###
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')

testStatus = True
class TestClass:
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.url    = inifile.RetIniVal(section, 'Url')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.url    = inifile.RetIniVal(section, 'AnalyticsUrl')


            self.user = inifile.RetIniVal(section, 'userAnalytics')
            self.pwd = inifile.RetIniVal(section, 'passAnalytics')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1391_Analytics_Verify_Highlights_Metrics')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome",False)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.analyticsFuncs = analyticsFuncs.analyticsFuncs(self.Wd, self.logi, self.Wdobj)
            self.general = General.general(self.Wd, self.logi, self.Wdobj)
                                    
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD = self.autoitwebdriver.retautoWebDriver()
                self.filePath = self.remoteFile
        except:
            pass
    #===========================================================================
    def test_1733_Top_Videos(self):

        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'UploadData'))
        csvObj = MyCsv.MyCsv(os.path.join(pth, 'csv_analytics_top_videos.csv'))
        itter = csvObj.retNumOfRowsinCsv()

        global testStatus
        # self.logi.initMsg('test_1391_Analytics_Audience_Engagement_Tooltips')
        # Invoke and login
        self.logi.appendMsg("INFO - Going to login")
        if self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd) == False:
            self.logi.appendMsg("FAIL - Login")
            testStatus = False

        for testNum in range(1, itter):
            try:
                if csvObj.readValFromCsv(testNum, 0) == "yes":  # this test should run
                    testStatus = True
                    self.logi = reporter2.Reporter2("ANALYTICS_" + str(testNum))
                    self.logi.initMsg('TEST ' + csvObj.readValFromCsv(testNum, 1))

                    self.general.waitForLoadingToDisappear()

                    # Go To Menu / Sub Menu in analytics
                    menuTab = csvObj.readValFromCsv(testNum, 2)
                    subMenuTab = csvObj.readValFromCsv(testNum, 3)
                    navigateToTab = self.general.convertStrToBool(csvObj.readValFromCsv(testNum, 4))
                    if self.analyticsFuncs.goAnalytics(menuTab, subMenuTab, navigateToTab) == False:
                        testStatus = False

                    if testStatus == True:
                        if self.analyticsFuncs.iframeInit() == False:
                            testStatus = False
                        self.general.waitForSpinnerToFinish()

                    if testStatus == True:
                        preset = int(csvObj.readValFromCsv(testNum, 5))
                        isCompareMode = self.general.convertStrToBool(csvObj.readValFromCsv(testNum, 6))
                        comparePeriod = int(csvObj.readValFromCsv(testNum, 7))
                        # Check specific date range
                        if preset == 9:
                            startdate = self.analyticsFuncs.createCustomCompareDate()
                            # Specific date range with compare mode with custom date
                            if isCompareMode and comparePeriod == 2:
                                compareStartDate = self.analyticsFuncs.createCustomCompareDate(preset, customDelta=30)
                                if self.analyticsFuncs.setDateCustom(dateFrom=startdate, compareMode=isCompareMode,comparePeriod=comparePeriod,compareStart=compareStartDate) == False:
                                    testStatus = False
                            # Specific date range normal mode and compare mode last year
                            elif self.analyticsFuncs.setDateCustom(dateFrom=startdate,compareMode=isCompareMode) == False:
                                testStatus = False
                        # Check Preset dates
                        else:
                            # Check preset with compare mode and custom date
                            if isCompareMode and comparePeriod == 2:
                                compareStart = self.analyticsFuncs.createCustomCompareDate(preset)
                                if self.analyticsFuncs.setDatePreset(preset, isCompareMode, comparePeriod,compareStart) == False:
                                    testStatus = False
                            # Check preset normal mode and preset compare mode last year
                            elif self.analyticsFuncs.setDatePreset(preset, isCompareMode) == False:
                                testStatus = False

                    self.general.waitForSpinnerToFinish()

                    if testStatus == True:
                        # Check date for specific range
                        if preset == 9:
                            if not self.analyticsFuncs.isDate(preset, dateFrom=startdate):
                                testStatus = False
                        # Check date for preset
                        elif not self.analyticsFuncs.isDate(preset):
                            testStatus = False

                    # Collect highlights data and graph data and compare them for each metric
                    if testStatus == True:
                        if self.analyticsFuncs.verifyTopVideos(isCompareMode) == False:
                            testStatus = False

                    if testStatus == True:
                        if self.analyticsFuncs.iframeEnd() == False:
                            testStatus = False

                    testNumber = csvObj.readValFromCsv(testNum, 8)
                    if testStatus == False:
                        self.practitest.post(Practi_TestSet_ID, testNumber, '1')
                        self.logi.reportTest('fail', self.sendto)
                    else:
                        self.practitest.post(Practi_TestSet_ID, testNumber, '0')
                        self.logi.reportTest('pass', self.sendto)

                    self.Wd.refresh()
                    time.sleep(3)

            except:
                self.logi.appendMsg("TEST FAILED")
                testStatus = False
    #===========================================================================
    
    def teardown(self):
        global testStatus

        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")
        # Close browser                
        self.Wd.quit()

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1733', '1')
            assert False
        else:
            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1733', '0')
            assert True

    #pytest.main('test_1733_Top_Videos.py -s')
