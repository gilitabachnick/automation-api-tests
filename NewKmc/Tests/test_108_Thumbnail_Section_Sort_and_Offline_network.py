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
import Entrypage
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
            self.logi = reporter2.Reporter2('TEST108 Functionality of Thumbnail Section')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome", True)
            self.practitest = Practitest.practitest('4586')
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.entrypagefuncs = Entrypage.entrypagefuncs(self.Wd, self.logi ) 
            self.filepth = r'\QRcodeVideo.mp4'
            self.filepthlocal = 'QRcodeVideo.mp4'
            self.entryName = 'Lihi_Test_108'
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepthlocal

            self.logi.initMsg('TEST 108- Thumbnail Section Sort and Offline network')    
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
            
    def test_108_Thumbnail_Section_Sort_and_Offline_network(self):
    #Upload thumbnail test 
        global testStatus 
        self.logi.appendMsg("----------- TEST ------------")
       
        self.logi.appendMsg("INFO - Going to sort entry's thumbnails and verify offline message")
        #Select the uploaded entry
        try:
            self.logi.appendMsg("INFO - Going to open the Entry Page of the uploaded entry")       
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                self.logi.appendMsg("FAIL - could not find or open the entry- " + self.entryName + " in entries table")
                testStatus = False
            time.sleep(3)
        #Moving to Thumbnails section in entry details
            self.logi.appendMsg("INFO - Going to move to the 'Thumbnails' section")
            rc = self.Wd.find_element_by_xpath(DOM.ENTRY_THUMBNAILS_SECTION)           
            if not rc:
              self.logi.appendMsg("FAIL - could not move to 'Thumbnails' section")
              testStatus = False
              return
            rc.click()

            self.uploadfuncs.delete_thumbnail()
            time.sleep(2)
            
        #Upload 6 thumbnails for the uploaded entry
            counter = 0
            for i in range(1,7):
                uploadSuccess = self.uploadfuncs.UploadThumbnail("Thumbnail_" + str(i) + ".jpg")
                if uploadSuccess:                
                    counter += 1  #'Counter' counts the actual uploaded thumbnails
                    
            if counter<2:
              self.logi.appendMsg("FAIL - Sort is not relevant for less than 2 thumbnails")
              testStatus = False
              return
        
        #Sort function
            rc = self.entrypagefuncs.SortEntryThumbnailsTable()
            if not rc:
                testStatus = False
                return               
        
        #offline steps will be added after upgrading to python 3.5.0
        #    time.sleep(2)
        #    self.Wd.set_network_conditions({'offline':True,'latency':5,'throughput':500*1024})
        
            
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
             
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '108','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '108','0')
            assert True         
       
        
    #===========================================================================
    # pytest.main('test_108_Thumbnail_Section_Sort_and_Offline_network.py -s')
    #===========================================================================
        
        