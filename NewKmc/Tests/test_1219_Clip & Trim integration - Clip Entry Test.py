
import os
import sys
import time




pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import KmcBasicFuncs
import reporter2
import uploadFuncs
import Config
import Practitest
import Entrypage



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
            self.user   = inifile.RetIniVal(section, 'userNameIlia')
            self.pwd    = inifile.RetIniVal(section, 'passIlia')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1219')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entry = 'MOV_2.mov'
            self.entryName = '"MOV_2"'
            self.entryClipName = '"Clip of MOV_2"'
            self.entryPage = Entrypage.entrypagefuncs(self.Wd) 
            self.practitest = Practitest.practitest('4586')        
        
        except:
            pass    
        
    def test_(self):
        
        global testStatus 
        self.logi.initMsg('test 1219 Clip & Trim integration - Clip Entry Test')
        
        try:
            #Login KMC
            self.logi.appendMsg("INFO - Step 1: Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            if rc == False:
                testStatus = False
                self.logi.appendMsg("FAIL - Step 1: FAILED to login to KMC")
                return
            
            self.logi.appendMsg("INFO - Step 2: going to upload MOV file")
            self.uploadfuncs.uploadFromDesktop(self.entry)

            self.logi.appendMsg("INFO- Step 2.2: going to wait until the entry will be in status Ready")
            entryStatus, lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.entryName)
            if not entryStatus:
                self.logi.appendMsg("FAIL on step 2.2 - the entry " + self.entryName + " status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
            else:
                 self.logi.appendMsg("PASS Step 2 - the entry " + self.entryName + " uploaded successfully")

            self.logi.appendMsg("INFO  Step 3: Open entry details page")
            try:
                self.Wd.find_element_by_xpath(DOM.ENTRY_ROW_NAME).click()
                self.logi.appendMsg("PASS Step 3: Entry details page opened")

            except:
                self.logi.appendMsg("FAIL Step 3: Entry details page not opened")
                testStatus=False

            self.logi.appendMsg("INFO- Step 4 :Going to Editor")
            try:
                time.sleep(3)
                self.Wd.find_element_by_xpath(DOM.ENTRY_CLIPS).click()
                time.sleep(5)
                self.Wd.find_element_by_xpath(DOM.ENTRY_CLIPS_Trim).click()

                self.logi.appendMsg("PASS step 4 -Press on Clips and Clips and Trim")
            except Exception as Exp:
                print(Exp)
                self.logi.appendMsg("FAIL step 4-Didn't press on Clips and Clips and Trim")
                testStatus = False
            time.sleep(30)  # Waiting for KEA screen to load
            self.logi.appendMsg("INFO -Step 5: Clipping and trimming the entry...")
            timeLine = self.BasicFuncs.getTimeline(self.Wd)
            sourceDuration, sourceStringDuration = self.BasicFuncs.checkClipDuration(self.Wd)
            if not isinstance(sourceDuration, bool):
                clipFromSecond = sourceDuration / 3  # Clipping one third of entry in the middle
                clipToSecond = clipFromSecond * 2
                trimFromSecond = sourceDuration / 4  # Trimming half of entry in the middle
                trimToSecond = trimFromSecond * 3

            clipStatus, clip_duration, trim_duration = self.BasicFuncs.createClipTrim(self.Wd, timeLine, clipFromSecond, clipToSecond, trimFromSecond, trimToSecond, True, True)
            if not clipStatus:
                testStatus = False
                self.logi.appendMsg("FAIL step 5 - Could not create clip or trim!")
                return
            self.logi.appendMsg("PASS step 5-Created a clip copy")
            self.logi.appendMsg("INFO- Step 6 Search the clip and verify the clipped entry")
            time.sleep(2)
            entryStatus, lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.entryClipName)
            if not entryStatus:
                self.logi.appendMsg("FAIL on step 6.1 - the entry " + self.entryClipName + " status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                testStatus = False
                return
            else:
                 self.logi.appendMsg("PASS Step 6.1 - the entry " + self.entryClipName + " converted successfully")
            self.logi.appendMsg("PASS step 6 - Clip and trim process complete!")

            self.logi.appendMsg("INFO- Step 7 Going to verify clip and trim entries durations...")
            self.logi.appendMsg("INFO- Step 7.1 Going to verify clip entry duration...")

            clipFlag, clipDuration = self.BasicFuncs.retEntryDuration(self.Wd, self.entryClipName, clip_duration)
            if not clipFlag:
                self.logi.appendMsg("FAIL on Step 7.1 - wrong duration of clipped entry (copy)!")
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS Step 7.1 - the entry " + self.entryClipName + " has correct duration "+str(clipDuration))
            self.logi.appendMsg("Going to delete the clip...")
            try:
                self.BasicFuncs.deleteEntries(self.Wd, self.entryClipName)
            except Exception as Exp:
                print(Exp)
                self.logi.appendMsg("Failed to delete the clip! Aborting!")
                testStatus = False
                return
            self.logi.appendMsg("INFO- Step 7.2 Going to verify trim entry duration...")
            trimFlag, trimDuration = self.BasicFuncs.retEntryDuration(self.Wd, self.entryName, trim_duration, True)
            if not trimFlag:
                self.logi.appendMsg("FAIL on Step 7.2 - wrong duration of trimmed entry! Expected "+trim_duration+" and got "+trimDuration+"!")
                testStatus = False
                return
            else:
                self.logi.appendMsg("PASS Step 7.2 - the entry " + self.entryName + " has correct duration "+str(trimDuration))
        except Exception as Exp:
            print(Exp)
            testStatus = False
            pass
        
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd, self.entryName)
        except:
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1219','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1219','0')
            assert True         

    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_1219_Clip & Trim integration - Clip Entry Test.py','-s'])
    #===========================================================================
