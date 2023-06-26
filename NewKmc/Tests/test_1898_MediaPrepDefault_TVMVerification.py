'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1898_MediaPrepDefault_TVMVerification
 
 @desc : The test performs mediPrep default distribution and then go to TVM app and perform files verification 

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''



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

import Config
import Practitest
import autoitWebDriver
import distributionFuncs
import uploadFuncs
import datetime
import Entrypage
import random


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
            self.user   = inifile.RetIniVal(section, 'KMCuserDistribution')
            self.pwd    = inifile.RetIniVal(section, 'KMCpwdDistribution')
            self.tvm_url    = "http://ec2-54-202-106-218.us-west-2.compute.amazonaws.com:9090/adm_media_files.aspx?media_id=769386"
            self.tvm_user = inifile.RetIniVal('Tvm', 'tvm_user')
            self.tvm_pwd = inifile.RetIniVal('Tvm', 'tvm_pwd')
            self.DistributionProfileSelectionText    = inifile.RetIniVal(section, 'DistributionProfileSelectionText')
            self.DistributionEntryName  = 'Wildlife'
            self.DistributionfilePth    = r'\Wildlife.wmv' 
            #self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1898_MediaPrepDefault_TVMVerification')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.distribusionsFuncs = distributionFuncs.distributefuncs(self.Wd,self.logi)
                        
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.DistributionfilePth = self.DistributionfilePth[1:]
            
                
            #self.distribusionsFuncs.DistributionCreateMovie()         
        
        except:
            pass
    
       
      
    def test_1898_MediaPrepDefault_TVMVerification(self):
             
        global testStatus
        self.logi.initMsg('test_1898_MediaPrepDefault_TVMVerification')
        

        try:            
      
              
             # Invoke login to KMC
             rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
             if rc == False:
               self.logi.appendMsg("FAIL - invokeLogin to KMC" )
               testStatus = False
               return
              
             self.Wd.maximize_window()            
          
             # Upload file from desktop
             self.logi.appendMsg("INFO - Going to upload file - " + self.DistributionfilePth)
             self.uploadfuncs.uploadFromDesktop(self.DistributionfilePth,transcodingProfile='widevine+h264+clear ism')
                                          
             # Waiting for ready status 
             self.logi.appendMsg("INFO - Waiting for status ready")
             rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.DistributionEntryName,600)  
             if(rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
             else:       
                self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return
                                                        
            # Drilldown to entry by name.   
             self.logi.appendMsg("INFO - Going to Drilldown to entry - " + self.DistributionEntryName)
             rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.DistributionEntryName, True)
             if rc:
                 self.logi.appendMsg("PASS - Drilldown to entry - " + self.DistributionEntryName )
             else:
                 self.logi.appendMsg("FAIL - could NOT Drilldown to entry - " + self.DistributionEntryName )
                 testStatus = False
                 return
                  
             time.sleep(5)
              
             # Update entry name
             x = datetime.datetime.now()
             self.DistributionEntryName = 'Wildlife_automation_mediaPrepDefault_' + str(random.randint(1,101)) + "_" + x.strftime("%x")
             self.logi.appendMsg("INFO - Going to update entry name - " + self.DistributionEntryName)
             rc = self.entryPage.EntrySetBasicMetadata(self.DistributionEntryName)
             if rc == False:
                self.logi.appendMsg("FAIL - EntrySetBasicMetadata - Update entry name to " + self.DistributionEntryName)
                testStatus = False
                return
              
             time.sleep(5)
              
             # Open Distribution tab
             rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.DISTRIBUTION_TAB, "Distribution tab", 10)
             if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Entry name")
                return False    
             self.logi.appendMsg("INFO - Going to click on distribution tab")  
             self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_TAB).click()
              
             time.sleep(2)            
             # Select distribution
             self.logi.appendMsg("INFO - Going to select distribution profile - DistributionProfile= " + self.DistributionProfileSelectionText)
              
             # Function that select distribution
             rc = self.distribusionsFuncs.Distribution_Selection(self.DistributionProfileSelectionText)
             if not rc:
                 self.logi.appendMsg("FAIL - Could NOT select distribution profile in entry - DistributionProfile= " + self.DistributionProfileSelectionText )
                 testStatus = False
                 return
              
             time.sleep(3)
              
             # Press on EXPORT button
             self.logi.appendMsg("INFO - Going to press on the distribution EXPORT and then on export UPDATE button - DistributionProfile= " + self.DistributionProfileSelectionText)
             rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.DISTRIBUTION_EXPORT_BUTTON, "Distribution export button", 10)
             if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Distribution export button field")
                return False 
             self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_EXPORT_BUTTON).click()
             time.sleep(4)
             rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.DISTRIBUTION_EXPORT_UPDATE_BUTTON, "Distribution export update button", 15)    
             if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Distribution export update button")
                return False 
             self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_EXPORT_UPDATE_BUTTON).click()
             time.sleep(6)
               
             # Distribution waiting for ready status
             self.logi.appendMsg("INFO - Going to wait for distribution status=\"distributed\"")
             rc,line=self.distribusionsFuncs.Distribution_WaitingForReady()
          
             if rc:
                 self.logi.appendMsg("PASS - The distribution status was changed to Ready as expected ")
                
                # Login to TVM app
                 self.logi.appendMsg("INFO - Going to perform TVM login")                
                 rc = self.distribusionsFuncs.invokeTVMLogin(self.Wd, self.Wdobj, self.logi, self.tvm_url, self.tvm_user, self.tvm_pwd)           
                 if(rc):
                    self.logi.appendMsg("PASS - Login to TVM")
                 else:       
                    self.logi.appendMsg("FAIL - Login to TVM")
                    testStatus = False
                    return           
                 self.Wd.maximize_window()
                 self.logi.appendMsg("INFO - Going to Verify TVM FilesNumber")
                 # Verify TVM Files Number - Expected 5 files on default mediaPrep case
                 rc = self.distribusionsFuncs.verifyTVMFilesNumber(self.Wd, self.logi, self.DistributionEntryName, 5)
                 if(rc):
                    self.logi.appendMsg("PASS - Verify TVM Files Number")
                 else:       
                    self.logi.appendMsg("FAIL - Verify TVM Files Number")
                    testStatus = False
                    return              
                 
                 time.sleep(3)
                 
                 # Invoke login to KMC
                 rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
                 if rc == False:
                     self.logi.appendMsg("FAIL - invokeLogin to KMC" )
                     testStatus = False
                     return
                 
                 time.sleep(3)
             else:       
                 self.logi.appendMsg("FAIL -  The distribution status was NOT changed to Ready as expected, the actual status was: " + line)
                 testStatus = False
                 return
 
        except Exception as exp:
             print(exp)        
             testStatus = False
             self.logi.appendMsg("FAIL - on of the following KMC login | UPLOAD | WaitForReady | DrillDown | Distribution tab Failed")
               
                  
        
    def teardown(self):
        
        
        global teststatus
        #Delete entry
        
        try:
             self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click() 
             time.sleep(3) 
             self.BasicFuncs.deleteEntries(self.Wd,self.DistributionEntryName)
        except:
             pass 
        
        #Close browser                
        self.Wd.quit()
        
        
        if testStatus == False:
            self.logi.reportTest('fail',"moran.cohen@kaltura.com")
            self.practitest.post(Practi_TestSet_ID, '1898','1')
            assert False
        else:
            self.logi.reportTest('pass',"moran.cohen@kaltura.com")
            self.practitest.post(Practi_TestSet_ID, '1898','0')
            assert True         
            
            
    #===========================================================================
    # pytest.main('test_1898_MediaPrepDefault_TVMVerification.py -s')
    #===========================================================================
