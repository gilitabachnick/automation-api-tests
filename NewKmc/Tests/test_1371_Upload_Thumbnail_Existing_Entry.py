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
import uploadFuncs
import reporter2

import Config
import Practitest
import autoitWebDriver

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
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
        
        global testStatus
    
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
            self.user   = inifile.RetIniVal(section, 'userUpload')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST1371 Upload Thumbnail for Existing Entry')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.practitest = Practitest.practitest('4586')
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.filepth = r'\QRcodeVideo.mp4'
            self.filepthlocal = 'QRcodeVideo.mp4'
            self.entryName = 'Lihi_Test_1371'
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepthlocal

            self.logi.initMsg('TEST 1371- Upload Thumbnail - Existing Entry')    
            self.logi.appendMsg("----------- SETUP -----------")  
                             
            #Login to KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()                     
                          
            #Upload new entry
            self.logi.appendMsg("INFO - Going to upload an entry - " + self.filepth)
            self.uploadfuncs.uploadFromDesktop(filePth=self.filepth, Fname=self.entryName)
            self.logi.appendMsg("INFO - Waiting for status ready")
             
            rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.entryName)   
            if(rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
            else:       
                self.logi.appendMsg("FAIL - The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return                         
         
        except Exception as Exp:
            testStatus = False
            pass          
            
    def test_1371_Upload_Thumbnail_Existing_Entry(self):
    #Upload thumbnail test 
        global testStatus 
        self.logi.appendMsg("----------- TEST ------------")
       
        self.logi.appendMsg("INFO - Going to upload a thumbnail for existing entry")
        #Select the uploaded entry
        try:
            self.logi.appendMsg("INFO - Going to open the Entry Page of the uploaded entry")       
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                self.logi.appendMsg("FAIL - could not find or open the entry- " + self.entryName + " in entries table")
                testStatus = False
                return
            time.sleep(3)
            #Moving to Thumbnails section in entry details
            self.logi.appendMsg("INFO - Going to move to the 'Thumbnails' section")
            rc = self.Wd.find_element_by_xpath(DOM.ENTRY_THUMBNAILS_SECTION)           
            if not rc:
              self.logi.appendMsg("FAIL - could not move to 'Thumbnails' section")
              testStatus = False
              return
            rc.click()
            self.uploadfuncs.UploadThumbnail('smalljpg.jpg')
#===============================================================================        
#            #Click on the Upload (thumbnail) button
#             
#             #Verify -comparing the rows num in the Thumbnails' table to 3 (1- default thumbnail, 2 - the uploaded thumbnail, 3- titles row)
#             
#===============================================================================
 
            
            #Back to Content-Entries for deleting the uploaded entry    
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            
        except Exception as Exp:
            testStatus = False
            pass 
        self.logi.appendMsg("Test:)")         
    
    def teardown_class(self):
        
        global testStatus
        
        try:
            #Delete the Uploaded entry
            self.BasicFuncs.deleteEntries(self.Wd,self.entryName)
        except Exception as Exp:
            print(Exp)
             
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1371','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1371','0')
            assert True         
       
        
    #===========================================================================
    if Run_locally:
        pytest.main(args=['test_1371_Upload_Thumbnail_Existing_Entry.py', '-s'])
    #===========================================================================
        
        