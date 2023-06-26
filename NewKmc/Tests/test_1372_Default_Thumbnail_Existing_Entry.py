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
            self.logi = reporter2.Reporter2('TEST1372 Set Default Thumbnail To Existing Entry')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")    
            self.practitest = Practitest.practitest('4586')
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.filepth = r'\QRcodeVideo.mp4'
            self.filepthlocal = 'QRcodeVideo.mp4'
            self.entryName = 'Lihi_Test_1372'
            
            if self.Wdobj.RUN_REMOTE:
              self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
              self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepthlocal
            
            self.logi.initMsg('TEST 1372- Set Default Thumbnail - Existing Entry')    
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
              
            
    def test_1372(self):
        
        global testStatus 
        self.logi.appendMsg("----------- TEST ------------")
        
        #Search for entry > Open 'Thumbnails' section and set to default the thumbnail
        try:
        #Select the uploaded entry
            self.logi.appendMsg("INFO - Going to open the Entry Page of the uploaded entry")       
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                self.logi.appendMsg("FAIL - could not find or open the entry- " + self.entryName + " in entries table")
                testStatus = False
                return
            time.sleep(3)
        #Move to Thumbnails section in entry details
            self.logi.appendMsg("INFO - Going to move to the 'Thumbnails' section in entry details page")
            rc = self.Wd.find_element_by_xpath(DOM.ENTRY_THUMBNAILS_SECTION)           
            if not rc:
              self.logi.appendMsg("FAIL - could not move to 'Thumbnails' section in entry details page")
              testStatus = False
              return
            rc.click()
            time.sleep(2)
            
        #Set current thumbnail to be the default thumbnail
            self.logi.appendMsg("INFO - Going to set the thumbnail to default")
            setDefault = self.Wd.find_element_by_xpath(DOM.THUMBNAIL_SET_AS_DEFAULT)
            if not setDefault:
              self.logi.appendMsg("FAIL - could not find the 'set as default' button for the thumbnail")
              testStatus = False
              return
            setDefault.click()
            time.sleep(2)
            default = self.Wd.find_element_by_xpath(DOM.DEFAULT_THUMBNAIL)
            if not default:
             self.logi.appendMsg("FAIL - could not set thumbnail as default")
             testStatus = False
             return
            self.logi.appendMsg("PASS - thumbnail was set to default")
            #Back to Content-Entries for deleting the uploaded entry    
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
                
                
        except Exception as Exp:
            testStatus = False
            pass 
    
    def teardown_class(self):
        
       global testStatus
        
       try:
           #Delete the Uploaded entry
           self.BasicFuncs.deleteEntries(self.Wd,self.entryName)
       except Exception as Exp:
           print(Exp)
           pass

       try:
           self.Wd.quit()
       except:
           pass

        
       if testStatus == False:
           self.practitest.post(Practi_TestSet_ID, '1372', '1')
           self.logi.reportTest('fail',self.sendto)
           assert False
       else:
           self.practitest.post(Practi_TestSet_ID, '1372', '0')
           self.logi.reportTest('pass',self.sendto)
           assert True
       
        
    #===========================================================================
    # pytest.main('test_1372_Default_Thumbnail_Existing_Entry.py -s')        
    #===========================================================================
        
        