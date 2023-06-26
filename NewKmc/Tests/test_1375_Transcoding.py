import os
import subprocess
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
from uploadFuncs import uploadfuncs
import Config
import Practitest
import autoitWebDriver


# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '1418'
else:
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
            self.logi = reporter2.Reporter2('test_1375_Transcoding')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadFuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingsFuncs = settingsFuncs.settingsfuncs(self.Wd, self.logi)
            self.entryPageFuncs = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.transcodingEntryName = "TranscodingSettings1375"
            self.transcodingProfileName = "New Transcoding_1375"
            self.transcodingFlavors = "Source,Mobile (3GP)"
            self.filePath = self.transcodingEntryName+".mp4"
            self.remoteFile = r'\TranscodingSettings1375.mp4'
                        
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
                self.filePath = self.remoteFile
        except:
            pass
    #===========================================================================
    
    def test_1375_Transcoding(self):
             
        global testStatus
        self.logi.initMsg('test_1375_Transcoding - Add/Update/Delete With File')
        testStatus = True
        try:            
                        
            # Invoke and login
            self.logi.appendMsg("INFO - Going to login")
            rc = self.basicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            time.sleep(5)
            self.logi.appendMsg("---------- TEST ADD TRANSCODING PROFILE WITH FILE ----------")
            
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
                    entryStatus,lineText = self.basicFuncs.waitForEntryStatusReady(self.Wd, self.transcodingEntryName)
                    if not entryStatus:
                        self.logi.appendMsg("FAIL - The entry " + self.transcodingEntryName + " was not uploaded - error message:" + lineText)
                        testStatus = False
                        return False
                    else:
                        self.logi.appendMsg("PASS - The entry " + self.transcodingEntryName + " was Uploaded successfully")
                except:
                    self.logi.appendMsg("FAIL - Uploading entry" + self.transcodingEntryName)
                    testStatus = False
                    return False
            else:
                testStatus = False
                return False
        except:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following: KMC login / Transcoding Settings Add/ Entry upload")
            
        # Check flavors on entry after transcoding
        if testStatus:
            testStatus = self.entryPageFuncs.compareFlavors(self.Wd, self.transcodingEntryName,self.transcodingFlavors)
            
                
        self.logi.appendMsg("------------------------------------------------------------")
        
        # Test Update transcoding with file
        if testStatus:
            self.logi.appendMsg("-------- TEST UPDATE TRANSCODING PROFILE WITH FILE ---------")
            try:
                previousName = self.transcodingProfileName
                self.transcodingProfileName = previousName + " Update"
                self.transcodingFlavors = "Source,Mobile (3GP),SD/Large - WEB/MBL (H264/1500)"
                self.logi.appendMsg("INFO - Going to update Transcoding Profile " + previousName + " with name = " + self.transcodingProfileName +  " - flavors = " + self.transcodingFlavors)
                if self.settingsFuncs.updateTranscodingProfile(previousName,1,self.transcodingProfileName,self.transcodingFlavors):
                   self.logi.appendMsg("PASS - Transcoding Profile updated.")
                   self.Wd.refresh()
                else:
                    self.logi.appendMsg("FAIL - Transcoding Profile not updated.")
                    testStatus = False
                    return False
            except:
                testStatus = False
                self.logi.appendMsg("FAIL - Cannot update Transcoding Profile")
                return False

        # Upload file with the updated Transcoding Profile
        if testStatus:
            self.logi.appendMsg("INFO - Going to add new Entry")
            try:
                self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
                time.sleep(5)
                self.uploadFuncs.uploadFromDesktop(self.filePath,"desktop","none",self.transcodingProfileName)
                self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
                time.sleep(3)
                entryStatus,lineText = self.basicFuncs.waitForEntryStatusReady(self.Wd, self.transcodingEntryName)
                if not entryStatus:
                    self.logi.appendMsg("FAIL - The entry " + self.transcodingEntryName + " was not uploaded - error message:" + lineText)
                    testStatus = False
                    return False
                else:
                    self.logi.appendMsg("PASS - The entry " + self.transcodingEntryName + " was Uploaded successfully")
            except:
                self.logi.appendMsg("FAIL - Uploading entry" + self.transcodingEntryName)
                testStatus = False
                return False
        
        # Check flavors on entry after transcoding
        if testStatus:
            testStatus = self.entryPageFuncs.compareFlavors(self.Wd, self.transcodingEntryName,self.transcodingFlavors)
                        
        self.logi.appendMsg("------------------------------------------------------------")
        
        # Test Delete transcoding with file
        if testStatus:
            self.logi.appendMsg("-------- TEST DELETE TRANSCODING PROFILE WITH FILE ---------")
            try:
                
                # Delete transcoding profile
                self.settingsFuncs.deleteTranscodingProfiles(self.transcodingProfileName,1)

                self.Wd.refresh()

                # Go to Upload from Desktop screen
                self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
                time.sleep(5)
                #
                # # Select file to upload in order to close Open File window
                time.sleep(3)
                if self.Wdobj.RUN_REMOTE:
                    pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                else:
                    pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pthstr = str(os.path.abspath(os.path.join(pth, self.filePath)))
                self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
                self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP).click()
                time.sleep(2)
                uploadfuncs.windows_upload_dialog(self, pthstr)
                # Check Transcoding Profile does not exst on Upload from Desktop
                if self.uploadFuncs.uploadTPCheck(self.transcodingProfileName):
                    self.logi.appendMsg("FAIL - Transcoding Profile present on Upload screen.")
                    testStatus = False
                else:
                    self.logi.appendMsg("PASS - Transcoding Profile not present on Upload screen as expected.")
                
                # Close Upload settings window
                self.logi.appendMsg("INFO - Closing Upload settings window.")
                self.Wd.find_element_by_xpath(DOM.UPLOAD_CANCEL).click()
                
            except Exception as Exp:
                print(Exp)
                self.logi.appendMsg("FAIL - Cannot perform Transcoding Profile deletion with upload check.")
                testStatus = False
                return False
            self.logi.appendMsg("------------------------------------------------------------")
        

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
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1375','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1375','0')
            assert True         
            
            
    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_1375_Transcoding.py', '-s'])
    #===========================================================================