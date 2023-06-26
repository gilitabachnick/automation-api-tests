'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1893_FacebookAuthenticationForDistribution.py
 
 @desc : this test perform Facebook Authentication for Distribution

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import reporter2

import Config
import Practitest
import autoitWebDriver
import distributionFuncs
import Entrypage
import uploadFuncs
import KmcBasicFuncs


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
                self.Facebook_authentication_url = "http://www.kaltura.com/index.php/extservices/facebookoauth2/partner_id/MjQ1ODgzMQ==/provider_id/NDE0MDIzMg==/page_id/MTY4NTQ4MjY1MTY5NzMxMA==/permissions/cGFnZXNfbWFuYWdlX3Bvc3Rz/re_request_permissions/ZmFsc2U="
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.Facebook_authentication_url   = "http://qa-apache-php7.dev.kaltura.com/index.php/extservices/facebookoauth2/partner_id/NjI3NA==/provider_id/MTI0Mg==/page_id/MTY4NTQ4MjY1MTY5NzMxMA==/permissions/cGFnZXNfbWFuYWdlX3Bvc3Rz/re_request_permissions/ZmFsc2U="
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'KMCuserDistribution')
            self.pwd    = inifile.RetIniVal(section, 'KMCpwdDistribution')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.DistributionProfileSelectionText    = inifile.RetIniVal(section, 'DistributionProfileSelectionFacebook')
            self.DistributionEntryName  = 'Wildlife'   
            self.DistributionfilePth    = r'\Wildlife.wmv' 
            self.EntryDescription  = "EntryDescriptionFacebook" +  str(datetime.datetime.now())
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1893_FacebookAuthenticationForDistribution')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.distribusionsFuncs = distributionFuncs.distributefuncs(self.Wd,self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            #FACEBOOK ACCOUNT
            self.Facebook_url    = "https://www.facebook.com/Kaltura-Is-Funny-1685482651697310/"
            self.Facebook_user   = "qacorekaltura@gmail.com"
            self.Facebook_pwd    = "Kaltura12#"

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.DistributionfilePth = self.DistributionfilePth[1:]
                
                
        except Exception as Exp:
            print(Exp)
            pass
    
    
    
            
     def test_1893_FacebookAuthenticationForDistribution(self):
             
        global testStatus
        
        self.logi.initMsg('test_1893_FacebookAuthenticationForDistribution')
        
        try:            
            
            # Login to FaceBook Authentication screen.
            self.logi.appendMsg("INFO - Going to login to Authentication Facebook screen.")                
            rc = self.distribusionsFuncs.invokeFacebookAuthenticationLogin(self.Wd, self.Wdobj, self.logi, self.Facebook_authentication_url, self.user, self.pwd)           
            if(rc):
                self.logi.appendMsg("PASS - Login to Authentication Facebook.")
            else:       
                self.logi.appendMsg("FAIL - Login to Authentication Facebook.")
                testStatus = False
                return           
            self.Wd.maximize_window()
            time.sleep(4)
            
            # Verify entry description on facebook site
            self.logi.appendMsg("INFO - Going to Verify Authentication text on Facebook screen.")
            rc = self.distribusionsFuncs.verifyFacebookAuthentication(self.Wd,self.Wdobj, self.logi, self.Facebook_user, self.Facebook_pwd)
            if(rc):
                self.logi.appendMsg("PASS - verifyFacebookAuthentication.User = " + self.user + " , PWD = " + self.pwd )
            else:       
                self.logi.appendMsg("FAIL - verifyFacebookAuthentication.User = " + self.user + " , PWD = " + self.pwd )
                testStatus = False
                return
        except:
            testStatus = False
            self.logi.appendMsg("FAIL - on one of the following: invokeFacebookAuthenticationLogin | verifyFacebookAuthentication")
              
        
          
        
     def teardown(self):
        
        
        global teststatus
       
        # Close browser                
        self.Wd.quit()
            
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1893','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1893','0')
            assert True         
            
            
     #==========================================================================
     # pytest.main(args=['test_1893_FacebookAuthenticationForDistribution.py','-s'])
     #==========================================================================