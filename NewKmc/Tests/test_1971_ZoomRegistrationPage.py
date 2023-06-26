
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1971_ZoomRegistrationPage
 
 @desc : The test update the registration page and verify Saved Successfully. 
 Testing.qa - Supported on partner:
 Production - It is NOT Supported because we works on Kino partner
 
 ##### Prior condition on testing.qa env ########:
 MAP Name= vendor
 https://qa-apache-php7.dev.kaltura.com/admin_console/index.php/plugin/ConfigurationMapListAction:
 
 [ZoomAccount_Prod]
ZoomBaseUrl = https://zoom.us
redirectUrl = https://qa-apache-php7.dev.kaltura.com/api_v3/service/vendor_zoomvendor/action/oauthValidation

[ZoomAccount]
ZoomBaseUrl = https://zoom.us
redirectUrl = https://qa-apache-php7.dev.kaltura.com/api_v3/service/vendor_zoomvendor/action/oauthValidation  

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''


import os
import sys

# API
import ClienSession
import tearDownclass

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1, pth)

import MySelenium
import KmcBasicFuncs
import uploadFuncs
import reporter2

import Config
import Practitest
import Entrypage
import settingsFuncs
import QrcodeReader
import ZoomFuncs


import time

#######
#import json
#from zoomus import ZoomClient
########

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
    KMC_Zoom_Deletion = False
else:
    isProd = False
    KMC_Zoom_Deletion = True

testStatus = True
isProd = False # It's Supported only on testing.qa env

MeetingId = "Empty"
entryId = "Empty"

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
                self.ZoomUrl    = "https://zoom.us/signin"
                self.ZoomUser   = inifile.RetIniVal('Zoom', 'ZoomUser')
                self.ZoomPwd    = inifile.RetIniVal('Zoom', 'ZoomPwd')
                self.logi = reporter2.Reporter2('test_1971_ZoomRegistrationPage')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.ZoomUrl    = "https://zoom.us/signin"
                self.ZoomUser   = inifile.RetIniVal('Zoom', 'ZoomUser1971')
                self.ZoomPwd    = inifile.RetIniVal('Zoom', 'ZoomPwd1971')
                self.PublisherID = "6623"
                self.UserSecret = inifile.RetIniVal(section, 'UserSecretZoom')
                self.ServerURL = inifile.RetIniVal(section, 'ServerURL')
                # Create client session for deleting the meeting entry just on testing.qa
                self.logi = reporter2.Reporter2('test_1971_ZoomRegistrationPage')
                self.logi.appendMsg('start create session for partner: ' + self.PublisherID)
                mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
                self.client = mySess.OpenSession()
                time.sleep(2)     
                #=======================================================================
                self.testTeardownclass = tearDownclass.teardownclass()
                #=======================================================================
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'UserZoom')
            self.pwd    = inifile.RetIniVal(section, 'PassZoom')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.ZOOMRegistraionPage = inifile.RetIniVal(section, 'ZOOMRegistraionPage')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            ########## Registration page details #######
            self.enableRecordingUpload = True
            self.defaultUserId = "moran.cohen@kaltura.com"
            self.zoomCategory = "regular category"
            self.zoomWebinarCategory = "webinar category"
            self.createUserIfNotExist = True
            self.enableWebinarUpload = True
            self.participantHandler = "AddasCoViewers"
            self.userMatchingHandler  = "AddPostfix"
            self.zoomUserPostfix = "@KALTURA.com"
            #############################################
            self.Wdobj = MySelenium.seleniumWebDrive()                            
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")        
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingfuncs = settingsFuncs.settingsfuncs(self.Wd,self.logi)
            self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
            self.practitest = Practitest.practitest('4586')
            self.ZoomFuncs  = ZoomFuncs.ZoomFuncs(self.Wd,self.logi)
            
                       
            #===================================================================
            # if self.Wdobj.RUN_REMOTE:
            #     self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
            #     self.AWD =  self.autoitwebdriver.retautoWebDriver()
            # else:
            #     self.filepth = self.filepthlocal
            #                 
            #===================================================================
                
        except Exception as e:
            print(e)
            pass
    
                       
    def test_1971_ZoomRegistrationPage(self):
        
        global testStatus
        global KMC_Zoom_Deletion  
        global MeetingId
        global isProd
        global entryId
        
        PreviewEmbedTYPESelectionText = "Dynamic Embed"
        PreviewEmbedHTTPSSelection = False
        meetingDuration = 2 #seconds
        PlayerVersion = 3
        
        self.logi.initMsg('test_1971_ZoomRegistrationPage.py')
        
                
        try:             
            
            # Login to ZOOM web site
             self.logi.appendMsg('Going to open ZOOM RegistraionPage and login to zoom site')
             rc = self.ZoomFuncs.invokeZOOMLogin(self.Wd, self.Wdobj, self.ZOOMRegistraionPage, self.ZoomUser, self.ZoomPwd)
             if rc == False:
                 self.logi.appendMsg("FAIL - Invoke ZOOM Login to web site" )
                 testStatus = False
                 return
                
             #self.Wd.maximize_window()
             time.sleep(2)
             self.logi.appendMsg('Going to perform ZOOM Authrize')
             rc = self.ZoomFuncs.AuthorizeZOOMPage(self.Wd)
             if rc == False:
                 self.logi.appendMsg("INFO - NO Authorize ZOOM page" )  
             time.sleep(1)
             self.logi.appendMsg("Going to login to ZOOM Partner Registration Page. user = " + self.user + " , pwd = " + self.pwd + " , PublisherID = " + self.PublisherID )    
             rc = self.ZoomFuncs.SetPartnerZOOMRegistration(self.Wd, self.user, self.pwd, self.PublisherID)
             if rc == False:
                 self.logi.appendMsg("FAIL - ZOOM Partner Registration Page. user = " + self.user + " , pwd = " + self.pwd + " , PublisherID = " + self.PublisherID )
                 testStatus = False
                 return
             
             time.sleep(1)
             self.logi.appendMsg("Going to Update Registration Page" )
             # participantHandler option values - None/AddasCoPublishers/AddasCoViewers/IgnoreParticipants.
             # userMatchingHandler - None/DoNotModify/AddPostfix/RemovePostfix
             rc = self.ZoomFuncs.UpdateZOOMRegistrationPage(self.Wd, self.enableRecordingUpload, self.defaultUserId, self.zoomCategory, self.zoomWebinarCategory, self.createUserIfNotExist, self.enableWebinarUpload, self.participantHandler, self.userMatchingHandler, self.zoomUserPostfix)
             if rc == False:
                 self.logi.appendMsg("FAIL - Update Registration Page. user = " + self.user + " , pwd = " + self.pwd + " , PublisherID = " + self.PublisherID )
                 testStatus = False
                 return
         
          
        except Exception as e:
            print(e)
            testStatus = False
            pass
        
        
    def teardown_class(self):
        
        global testStatus
        global isProd

        try:
            self.Wd.quit()
        except:
            pass

        if testStatus == False:
           self.logi.reportTest('fail',self.sendto)
           self.practitest.post(Practi_TestSet_ID, '1971','1')
           assert False
        else:
           self.logi.reportTest('pass',self.sendto)
           self.practitest.post(Practi_TestSet_ID, '1971','0')
           assert True
       
    #pytest.main(args=['test_1971_ZoomRegistrationPage.py','-s'])
          
