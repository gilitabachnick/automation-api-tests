import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import uploadFuncs
import DOM
import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs
import Entrypage

import Config
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
            self.user   = inifile.RetIniVal(section, 'userTranscoding')
            self.pwd    = inifile.RetIniVal(section, 'passTranscoding')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.basicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1418_Upload_WM_from_Desktop_Different_Transcoding_Profile')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.transcodingEntryName = "Wildlife"
            self.transcodingProfileName = "New Transcoding_1418"
            self.transcodingFlavors = "Source,Mobile (3GP)"
            self.filePath = self.transcodingEntryName+".wmv"
            self.remoteFile = r'\Wildlife.wmv'
                        
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
                self.filePath = self.remoteFile
        except:
            pass
    #===========================================================================
    
    def test_1418_Upload_WM_from_Desktop_Different_Transcoding_Profile(self):
             
        global testStatus
        self.logi.initMsg('test_1418_Upload_WM_from_Desktop_Different_Transcoding_Profile')
        testStatus = True
        try:            
                        
            # Invoke and login
            self.logi.appendMsg("INFO - Going to login")
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            time.sleep(5)
            self.logi.appendMsg("---------- UPLOAD WMV FROM DESKTOP WITH TRANSCODING PROFILE ----------")
            
            # Delete previous transcoding profiles of this test (if exists)
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName,1)
            
            # Add transcoding profile with flavors
            if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName,1,self.transcodingFlavors):
                
                # Upload file with the added Transcoding Profile 
                self.logi.appendMsg("INFO - Going to add new Entry")
                try:
                    self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
                    time.sleep(5)
                    self.uploadFuncs.uploadFromDesktop(self.filePath,"desktop","none",self.transcodingProfileName)
                    entryStatus,lineText = self.basicFuncs.waitForEntryStatusReady(self.Wd, self.transcodingEntryName,itimeout=500)
                    if not entryStatus:
                        self.logi.appendMsg("FAIL - The entry " + self.transcodingEntryName + " was not uploaded - error message:" + lineText)
                        testStatus = False
                    else:
                        self.logi.appendMsg("PASS - The entry " + self.transcodingEntryName + " was Uploaded successfully")
                except Exception as exp:
                    self.logi.appendMsg("FAIL - Uploading entry" + self.transcodingEntryName)
                    testStatus = False
                    return
            else:
                testStatus = False
        except:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: KMC login / Transcoding Settings Add/ Entry upload")
            
        # Check flavors on entry after transcoding
        if testStatus:
            testStatus = self.entryPageFuncs.compareEntryFlavors(self.transcodingEntryName,self.transcodingFlavors)
            
                
        self.logi.appendMsg("------------------------------------------------------------")
        
       
        
        # Check flavors on entry after transcoding
        if testStatus:
            testStatus = self.entryPageFuncs.compareEntryFlavors(self.transcodingEntryName,self.transcodingFlavors)
                             

    #===========================================================================
    
    def teardown(self):
        
        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")
        
        global teststatus
        
        #Delete entry
        try: 
            self.logi.appendMsg("INFO - Deleting entries")
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click() 
            time.sleep(3) 
            self.basicFuncs.deleteEntries(self.Wd,self.transcodingEntryName)
        except:
            pass
        
        #Delete Transcoding Profiles
        try:
            time.sleep(0.5)
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName,1)
        except:
            pass
        
        #Close browser                
        self.Wd.quit()
        
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1418', '1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1418', '0')
            self.logi.reportTest('pass',self.sendto)
            assert True
            
            
    #===========================================================================
    # pytest.main('test_1418_Upload_WM_from_Desktop_Different_Transcoding_Profile.py -s')
    #===========================================================================