import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import KmcBasicFuncs
import reporter2
import settingsFuncs

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
            self.logi = reporter2.Reporter2('test_1485_Transcoding')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.transcodingOriginalName = "New Transcoding_1485"
            self.transcodingProfileName = self.transcodingOriginalName
            self.transcodingFlavors = "Source"
            self.transcodingDesc = ""
                        
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            
        except:
            pass
    #===========================================================================
    
    def test_1485_Transcoding(self):
             
        global testStatus
        self.logi.initMsg('test_1485_Transcoding - Add/Update/Delete Transcoding Profile')
        testStatus = True
        try:            
                        
            # Invoke and login
            self.logi.appendMsg("INFO - Going to login")
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            time.sleep(5)
            
        except:
            testStatus = False
            self.logi.appendMsg("FAIL - KMC login ")
        
        try:
            for profileType in range(1,3):
                
                #Initialize variables for each profile type
                if profileType == 1:
                    self.logi.appendMsg("------------- VOD TRANSCODING PROFILES -----------")
                    self.transcodingFlavors = "Source,Mobile (3GP)"
                else:
                    self.logi.appendMsg("------------ LIVE TRANSCODING PROFILES -----------")
                    self.transcodingFlavors = "Source,Ingest 2"
                
                self.transcodingProfileName = self.transcodingOriginalName
                
                #Add Transcoding Profile
                if testStatus:
                    try:
                        self.logi.appendMsg("---------- TEST ADD TRANSCODING PROFILE ----------")
                        
                        # Delete previous transcoding profiles of this test (if exist)
                        self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName,profileType)
                        
                        # Generate unique Transcoding Profile Name
                        self.transcodingProfileName = self.transcodingProfileName + " " + str(int(time.time()))
                        self.transcodingDesc = "The Description Field of " + self.transcodingProfileName + " for Testing."
                                        
                        # Add transcoding profile with flavors
                        if self.settingsFuncs.addTranscodingProfile(self.transcodingProfileName,profileType,self.transcodingFlavors,self.transcodingDesc):
                            self.logi.appendMsg("PASS - Transcoding Profile Added ")
                            if self.settingsFuncs.compareTranscodingProfile(self.transcodingProfileName, profileType, self.transcodingDesc, "" ,self.transcodingFlavors):
                                self.logi.appendMsg("PASS - Transcoding Profile added was verified properly.")
                            else:
                                testStatus = False
                                self.logi.appendMsg("FAIL - Transcoding Profile added was verified and does not match. ")
                        else:
                            testStatus = False
                            self.logi.appendMsg("FAIL - Adding Transcoding Profile")
                            
                    except:
                        testStatus = False
                        self.logi.appendMsg("FAIL -  Transcoding Profile Add")
                        
                self.logi.appendMsg("------------------------------------------------------------")
                
                # Update transcoding profile
                if testStatus:
                    self.logi.appendMsg("-------- TEST UPDATE TRANSCODING PROFILE ---------")
                    try:
                        
                        previousName = self.transcodingProfileName
                        self.transcodingProfileName =  previousName + " Update"
                        self.transcodingDesc = "The Description Field of " + self.transcodingProfileName + " for Testing."
    
                        if profileType == 1:
                            self.transcodingFlavors = "Source,SD/Large - WEB/MBL (H264/1500),HD/1080 - WEB (H264/4000)"
                        else:
                            self.transcodingFlavors = "Source,Ingest 3,SD/Small - WEB/MBL (H264/900)"
                        
                        self.logi.appendMsg("INFO - Going to update Transcoding Profile " + previousName + " with name = " + self.transcodingProfileName +  " - flavors = " + self.transcodingFlavors)
                        if self.settingsFuncs.updateTranscodingProfile(previousName,profileType,self.transcodingProfileName,self.transcodingFlavors,self.transcodingDesc):
                           self.logi.appendMsg("PASS - Transcoding Profile updated.")
                           if self.settingsFuncs.compareTranscodingProfile(self.transcodingProfileName, profileType, self.transcodingDesc, "" ,self.transcodingFlavors):
                               self.logi.appendMsg("PASS - Transcoding Profile updated was verified properly.")
                           else:
                               testStatus = False
                               self.logi.appendMsg("FAIL - Transcoding Profile updated was verified and does not match.")
                        else:
                            self.logi.appendMsg("FAIL - Transcoding Profile not updated.")
                            testStatus = False
                    except:
                        testStatus = False
                        self.logi.appendMsg("FAIL - Cannot update Transcoding Profile")
                                
                self.logi.appendMsg("------------------------------------------------------------")
                
                # Delete transcoding profile
                if testStatus:
                    self.logi.appendMsg("-------- TEST DELETE TRANSCODING PROFILE ---------")
                    try:
                        
                        # Delete specific transcoding profile
                        self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName,profileType)
                        
                    except:
                        self.logi.appendMsg("FAIL - Cannot perform Transcoding Profile deletion.")
                        testStatus = False
                    self.logi.appendMsg("------------------------------------------------------------")
                    
        except:
            self.logi.appendMsg("FAIL - Cannot perform Transcoding Profile test.")
            testStatus = False

    #===========================================================================
    
    def teardown(self):
        
        self.logi.appendMsg("-------------------------- TEAR DOWN -----------------------")
        
        global teststatus
        
        #Delete Transcoding Profiles and Close browser 
        try:
            time.sleep(0.5)
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingOriginalName,1)
            self.settingsFuncs.deleteTranscodingProfiles(self.transcodingOriginalName,2)
            self.Wd.quit()
        except:
            pass
        
                 
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1485','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1485','0')
            assert True         
            
            
    #===========================================================================
    # pytest.main('test_1485_Transcoding.py -s')
    #===========================================================================