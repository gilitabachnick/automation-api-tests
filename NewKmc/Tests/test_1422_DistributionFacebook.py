'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1422_DistributionFacebook
 
 @desc : The test performs Facebook distribution 

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import reporter2

import Config
import Practitest
import autoitWebDriver
import distributionFuncs
import Entrypage
import uploadFuncs
import KmcBasicFuncs

Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    Practi_TestSet_ID = '2043'
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
            self.user   = inifile.RetIniVal(section, 'KMCuserDistribution')
            self.pwd    = inifile.RetIniVal(section, 'KMCpwdDistribution')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.DistributionProfileSelectionText    = inifile.RetIniVal(section, 'DistributionProfileSelectionFacebook')
            self.DistributionEntryName  = 'Wildlife'   
            self.DistributionfilePth    = 'Wildlife.wmv'
            self.EntryDescription  = "EntryDescriptionFacebook" +  str(datetime.datetime.now())
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1422_DistributionFacebook')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.distribusionsFuncs = distributionFuncs.distributefuncs(self.Wd,self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            #FACEBOOK ACCOUNT
            self.Facebook_url = "https://www.facebook.com/Kaltura-Is-Funny-1685482651697310/"
            self.Facebook_user = inifile.RetIniVal('FaceBook', 'Facebook_user')
            self.Facebook_pwd = inifile.RetIniVal('FaceBook', 'Facebook_pwd')

                        
            # if self.Wdobj.RUN_REMOTE:
            #     self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
            #     self.AWD =  self.autoitwebdriver.retautoWebDriver()
            # else:
            #     self.DistributionfilePth = self.DistributionfilePth[1:]
                
                
        except Exception as Exp:
            print(Exp)
            pass
    
    
    
            
     def test_1422_DistributionMediaPCUSTOM(self):
             
        global testStatus
        
        self.logi.initMsg('test_1422_DistributionFacebook')
        
        try:            
            
            # invoke and login
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            self.logi.appendMsg("INFO - Going to upload different kind of files")

            # Upload file from desktop
            self.logi.appendMsg("INFO - Going to upload file - " + self.DistributionfilePth)
            self.uploadfuncs.uploadFromDesktop(self.DistributionfilePth)
            #self.uploadfuncs.uploadFromDesktop(self.DistributionfilePth,"url","https://qa-apache-php7.dev.kaltura.com/content/output_video/out.mp4")

            # Waiting for ready status
            self.logi.appendMsg("INFO - Waiting for status ready")
            try:
                rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.DistributionEntryName,600)
                if(rc):
                    self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
            except:
                self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return

            # Update entry's metadata for distribution
            self.logi.appendMsg("INFO - Going to update entry's metadata " + self.DistributionEntryName)

            # Open entry's drilldown
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd,self.DistributionEntryName)

            if not rc:
                self.logi.appendMsg("FAIL - Metadata update - Entry's Drilldown didn't open " + self.DistributionEntryName )
                testStatus = False
                return
            time.sleep(2)

            # Set entry basic metadata
            rc = self.entryPage.EntrySetBasicMetadata(self.DistributionEntryName,self.EntryDescription,None,None,None)
            if rc:
                self.logi.appendMsg("INFO - Updated entry's metadata - " + self.DistributionEntryName )
            else:
                self.logi.appendMsg("FAIL - Could NOT update entry's metadata - " + self.DistributionEntryName )
                testStatus = False
                return

            time.sleep(3)

            # Open Distribution tab
            self.logi.appendMsg("INFO - Going to click on distribution tab")
            self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_TAB).click()
            time.sleep(5)

            # Select distribution
            self.logi.appendMsg("INFO - Going to select distribution profile - DistributionProfile= " + self.DistributionProfileSelectionText)
            rc = self.distribusionsFuncs.Distribution_Selection(self.DistributionProfileSelectionText)
            if not rc:
                self.logi.appendMsg("FAIL - Could NOT select distribution profile in entry - DistributionProfile= " + self.DistributionProfileSelectionText )
                testStatus = False
                return
            time.sleep(3)

            # Press on EXPORT button
            self.logi.appendMsg("INFO - Going to press on the distribution EXPORT and then on export UPDATE button - DistributionProfile= " + self.DistributionProfileSelectionText)
            self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_EXPORT_BUTTON).click()
            time.sleep(5)
            self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_EXPORT_UPDATE_BUTTON).click()
            time.sleep(5)

            # Distribution waiting for ready status
            self.logi.appendMsg("INFO - Going to wait for distribution status=\"distributed\"")
            rc,line=self.distribusionsFuncs.Distribution_WaitingForReady()
            if rc:
                self.logi.appendMsg("PASS - The distribution status was changed to Ready as expected ")
            
                # Login to FaceBook site
                self.logi.appendMsg("INFO - Going to login Facebook account")                
                rc = self.distribusionsFuncs.invokeFacebookLogin(self.Wd, self.Wdobj, self.logi, self.Facebook_url, self.Facebook_user, self.Facebook_pwd)           
                if(rc):
                    self.logi.appendMsg("PASS - Login to Facebook account")
                else:       
                    self.logi.appendMsg("FAIL - Login to Facebook account")
                    testStatus = False
                    return           
                self.Wd.maximize_window()
                time.sleep(5)
                # Verify entry description on facebook site
                self.logi.appendMsg("INFO - Going to Verify description File on Facebook account")
                rc = self.distribusionsFuncs.verifyFacebookFile(self.Wd, self.logi, self.EntryDescription)
                if(rc):
                    self.logi.appendMsg("PASS - Entry description was found on facebook account.EntryDescription = " + self.EntryDescription)
                else:       
                    self.logi.appendMsg("FAIL - Entry description was NOT found on facebook account.EntryDescription = " + self.EntryDescription)
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
                self.logi.appendMsg("FAIL - The distribution status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return
            
        except Exception as EXP:
            print(EXP)
            testStatus = False
            self.logi.appendMsg("FAIL - on one of the following: KMC login | UPLOAD | WaitForReady | DrillDown | Distribution tab Failed")
              
        
          
        
     def teardown(self):
        
        
        global teststatus
        # Delete entry
        try:
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click() 
            time.sleep(3) 
            self.BasicFuncs.deleteEntries(self.Wd,self.DistributionEntryName)
        except:
            pass
        
        try:
            # Close browser                
            self.Wd.quit()
        except:
            pass    
            
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1422','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1422','0')
            assert True         
            
            
     #==========================================================================
     #pytest.main('test_1422_DistributionFacebook.py -s')
     if Run_locally:
         pytest.main(args=['test_1422_DistributionFacebook.py','-s'])
     #==========================================================================