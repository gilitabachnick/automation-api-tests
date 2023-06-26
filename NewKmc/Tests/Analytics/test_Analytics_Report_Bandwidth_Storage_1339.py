import datetime
import os
import sys
import time
from datetime import datetime

from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'..','..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'..','..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import DOM
import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs

import MyCsv
import Config
import Practitest
import autoitWebDriver
import analyticsFuncs
import General

### Jenkins params ###
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')

testStatus = True

#Temp
#isProd = True

class TestClass:
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'ini'))
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
            
            self.user   = inifile.RetIniVal(section, 'userAnalytics')
            self.pwd    = inifile.RetIniVal(section, 'passAnalytics')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.logi = reporter2.Reporter2('test_Bandwidth_Storage_1339')
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.analyticsFuncs = analyticsFuncs.analyticsFuncs(self.Wd, self.logi, self.Wdobj)
            self.general = General.general(self.Wd, self.logi, self.Wdobj)
            self.kmcDateFormat = "MM/DD/YYYY"
            self.testSetId = Practi_TestSet_ID
            self.practitest = Practitest.practitest(self.testSetId)
                                    
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
                self.filePath = self.remoteFile
        except:
            pass
    #===========================================================================
    
    
    def test_Analytics_Bandwidth_Storage(self):
             
        global testStatus
        testStatus = True
        self.logi.initMsg('TEST - Usage - Bandwidth & Storage Report')
        
        # Invoke and login
        try: 
            self.logi.appendMsg("INFO - Going to login")
            testStatus = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            time.sleep(5)
        except:
            self.logi.appendMsg("FAIL - Login")
            testStatus = False
        
        # open CSV with test cases
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'UploadData'))
            csvObj = MyCsv.MyCsv(os.path.join(pth, 'analytics_usage_publisher_bandwidth_storage_report.csv'))
            itter = csvObj.retNumOfRowsinCsv()
        except:
            self.logi.appendMsg("FAIL - CSV file")
            testStatus = False
        
        if testStatus:
            
            try:
                
                self.logi.appendMsg('Going to start CSV tests cases...')
                # Iterates CSV test cases
                rContainers = []
                sectionTabs = "Bandwidth Consumption,Average Storage,Peak Storage,Added Storage,Deleted Storage,BW and Storage Consumption,Transcoding Consumption"
                
                for testNum in range(1,itter):
                    if csvObj.readValFromCsv(testNum, 0) == "yes":  # this test should run
                        
                        testStatus = True
                        testType = csvObj.readValFromCsv(testNum, 6)
                        testNumber = csvObj.readValFromCsv(testNum,7)
                        self.logi = reporter2.Reporter2("ANALYTICS_" + str(testNumber))
                        testName = csvObj.readValFromCsv(testNum, 1)
                        self.logi.initMsg('TEST ' + testName)
                        
                        try:
                            
                            if testType == "Defaults":
                                
                                if not self.analyticsFuncs.iframeEnd():
                                    testStatus = False
                                self.general.waitForLoadingToDisappear()
                                time.sleep(5)
                                
                                # Get KMC date format
                                self.kmcDateFormat = self.analyticsFuncs.getKMCDateFormat()
                                if self.kmcDateFormat == "":
                                    self.kmcDateFormat= "MM/DD/YYYY"
                                    self.logi.appendMsg("INFO - Using default date format MM/DD/YYYY")
                                    
                                # Go To Analytics section
                                if not self.analyticsFuncs.goAnalytics("USAGE","PUBLISHERS BANDWIDTH & STORAGE"):
                                   testStatus = False
                                
                                self.general.waitForLoadingToDisappear()
                                time.sleep(2)
                                    
                                # Checking page components & defaults
                                self.logi.appendMsg("INFO - Going to check page components")
                            
                                # Switch webdriver to iframe 
                                if not self.analyticsFuncs.iframeInit():
                                    testStatus = False
                                self.general.waitForSpinnerToFinish()
                                time.sleep(2)
                                
                                # Check components
                                if not self.analyticsFuncs.isPageTitle("Publishers Bandwidth & Storage"):
                                    testStatus = False
                                
                                # Verify default date range on current quarter
                                if not self.analyticsFuncs.isDate(7):
                                    testStatus = False
                                                               
                                # Verify report sections
                                time.sleep(2)
                                rContainers = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_REPORT_CONTENT)
                                
                                sectionContainer = rContainers[0]
                                       
                                # Verify Title section Highlights
                                if not self.analyticsFuncs.isReportTitle(sectionContainer, "Highlights"):
                                    testStatus = False
                                
                                # Check Monthly graph period by default
                                if not self.analyticsFuncs.isGraphPeriod("Monthly", rContainer = sectionContainer):
                                    testStatus = False
                                
                                # Verify tabs names present
                                if not self.analyticsFuncs.isReportTabSet(sectionContainer, sectionTabs):
                                    testStatus = False
                                
                                self.logi.appendMsg('INFO - Going to open View Details toggle...')
                                sectionContainer.find_element_by_xpath(DOM.ANALYTICS_TABLE_TOGGLE.replace('TEXTTOREPLACE', "View Details")).click()
                                
                                self.general.waitForLoadingToDisappear()
                                time.sleep(3)
                                
                            elif testType == "DateTable":
                                
                                preset = int(csvObj.readValFromCsv(testNum,2))
                                isCompareMode = self.general.convertStrToBool(csvObj.readValFromCsv(testNum, 3))
                                comparePeriod = int(csvObj.readValFromCsv(testNum, 4))
                                
                                startDate = self.analyticsFuncs.createCustomCompareDate()
                                endDate = datetime.today().strftime("%Y-%m-%d")
                                
                                self.Wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
                                time.sleep(2)
                                
                                #Check specific date range
                                if preset == 9:
                                    compareStart = self.analyticsFuncs.createCustomCompareDate(preset, customDelta = 30)
                                    testStatus = self.analyticsFuncs.setDateCustom(dateFrom=startDate, compareMode=isCompareMode, comparePeriod=comparePeriod, compareStart=compareStart)
                                #Check Preset dates
                                else:
                                    compareStart = self.analyticsFuncs.createCustomCompareDate(preset)
                                    testStatus = self.analyticsFuncs.setDatePreset(preset, isCompareMode, comparePeriod, compareStart)
                                    
                                self.general.waitForSpinnerToFinish()
                                time.sleep(2)
                                
                                if testStatus:
                                    testStatus = self.analyticsFuncs.isDate(preset, startDate, endDate)
                                
                                #===============================================
                                # if testStatus and isCompareMode:
                                #     testStatus = self.analyticsFuncs.isCompareMode(comparePeriod, compareStart, self.kmcDateFormat)
                                #===============================================
                                    
                                if testStatus:
                                    graphPeriod = csvObj.readValFromCsv(testNum, 5)
                                    testStatus = self.analyticsFuncs.setGraphPeriod(graphPeriod, rContainer = sectionContainer)
                                
                                if testStatus:
                                    dataT= self.analyticsFuncs.getDataTable(sectionContainer, isCompareMode)
                                    testStatus = self.analyticsFuncs.compareGraphDateTable(sectionContainer, sectionTabs, dateTable = dataT, threshold = 5, compareMode = isCompareMode, kmcDateFormat = self.kmcDateFormat)
                                
                                if testStatus:
                                    testStatus = self.analyticsFuncs.compareAccumulativeDateTable(sectionContainer, "Accumulative Storage,Accumulative Bandwidth & Storage", "1:2,2:6", compareMode = isCompareMode, dateTable = dataT)
                                
                        except:
                            self.logi.appendMsg('FAIL Testing ' + testName)
                            testStatus = False
                        
                        if testStatus == False:
                            self.logi.reportTest('fail',self.sendto)
                            #self.practitest.post(self.testSetId, testNumber,'1')
                        else:
                            self.logi.reportTest('pass',self.sendto)
                            #self.practitest.post(self.testSetId, testNumber,'0')
                            
                                             
                # Switch webdriver back to default
                self.analyticsFuncs.iframeEnd()
                            
            except:
                self.logi.appendMsg("FAIL - Running the tests CSV file")
                testStatus = False
                    
    #===========================================================================
    
    def teardown(self):
        
        global teststatus
        
        # Close browser                
        self.Wd.quit()
        
            
    #pytest.main('test_Analytics_Report_Bandwidth_Storage_1339.py -s')
    
    