
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1891_ZoomNewMeeting
 
 @desc : The test created new zoom meeting by site and then login to KMC and play the entry on preview&embed.
 Verification on entryId of the meeting.
 Testing.qa - Also delete the entry of the meeting by API
 Production - NOT delete the meeting entry because It run on KINO partner

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
sys.path.insert(1,pth)


import DOM
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
                self.ZoomUser   = inifile.RetIniVal(section, 'UserZoom')
                self.ZoomPwd    = inifile.RetIniVal(section, 'PassZoom')
                self.KMCAccountName = "Kino - Kalturian Video Hub"
                self.logi = reporter2.Reporter2('test_1891_ZoomNewMeeting')
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.ZoomUrl    = "https://zoom.us/signin"
                self.ZoomUser   = inifile.RetIniVal(section, 'UserZoom')
                self.ZoomPwd    = inifile.RetIniVal(section, 'PassZoom')
                self.PublisherID = "6623"
                self.UserSecret = inifile.RetIniVal(section, 'UserSecretZoom')
                self.ServerURL = inifile.RetIniVal(section, 'ServerURL')
                self.KMCAccountName = "1testPartnerUser1604"
                self.ZOOMRegistraionPage = inifile.RetIniVal(section, 'ZOOMRegistraionPage')
                # Create client session for deleting the meeting entry just on testing.qa
                self.logi = reporter2.Reporter2('test_1891_ZoomNewMeeting')
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
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
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
    
                       
    def test_1891_ZoomNewMeeting(self):
        
        global testStatus
        global KMC_Zoom_Deletion  
        global MeetingId
        global isProd
        global entryId
        
        PreviewEmbedTYPESelectionText = "Dynamic Embed"
        PreviewEmbedHTTPSSelection = False
        meetingDuration = 2 #seconds
        PlayerVersion = 3
        
        self.logi.initMsg('test_1891_ZoomNewMeeting.py')
        
                
        try:
             ############### Registration ##########################
             if isProd == False:# if testing.qa -> Update registration page         
                self.logi.appendMsg("Going to login to ZOOM Partner Registration Page. user = " + self.user + " , pwd = " + self.pwd + " , PublisherID = " + self.PublisherID )    
                enableRecordingUpload = True # Enabled recording
                rc = self.ZoomFuncs.FullZOOMRegistration(self.Wd, self.Wdobj, self.ZOOMRegistraionPage, self.ZoomUser, self.ZoomPwd, self.user, self.pwd, self.PublisherID, enableRecordingUpload)
                if rc == False:
                    self.logi.appendMsg("FAIL - ZOOM Partner Registration Page. user = " + self.user + " , pwd = " + self.pwd + " , PublisherID = " + self.PublisherID )
                    testStatus = False
                    return            
             
                time.sleep(2)
                self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome") 
                time.sleep(5)              
             
            # Login to ZOOM web site
             self.logi.initMsg('Going to login to Zoom site')
             rc = self.ZoomFuncs.invokeZOOMLogin(self.Wd, self.Wdobj, self.ZoomUrl, self.ZoomUser, self.ZoomPwd)
             if rc == False:
                 self.logi.appendMsg("FAIL - Invoke ZOOM Login to web site" )
                 testStatus = False
                 return
                
             self.Wd.maximize_window()
                
            # Create meeting from Zoom site
             self.logi.initMsg('Going to create meeting to Zoom site')
             rc,MeetingId = self.ZoomFuncs.CreateMeetingFromZoomSite(self.Wd, self.Wdobj, self.ZoomUrl, self.ZoomUser, self.ZoomPwd)
             if rc == False:
                 self.logi.appendMsg("FAIL - Create Meeting From Zoom Site" )
                 testStatus = False
                 return    
            
             # KMC verification for the ZOOM entry
             self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
             rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
             self.Wd.maximize_window()
             # Save KMC window
             primContentTab = self.Wd.window_handles[0]
             
             #Verify KMC account 
             self.logi.appendMsg('Going to Open Change KMC Account window')
             rc =self.BasicFuncs.ChangeKMCAccount(self.Wd, self.Wdobj, self.logi , self.KMCAccountName)   
             if rc == False:
                 self.logi.appendMsg("FAIL - Change KMC account =  " + self.KMCAccountName )
                 testStatus = False
                 return    
             
             # Wait for entry creation and status - itimeout = 10min
             rc,line=self.BasicFuncs.waitForEntryCreation(self.Wd, MeetingId,600)   
             if(rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected. MeetingId = " + MeetingId)
             else:       
                self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return
            
             #Get entryId for KMC row
             self.logi.appendMsg("Going to get entryId from KMC row. MeetingId = " + MeetingId)
             entryId = str(self.BasicFuncs.get_entry_id(self.Wd))
             self.logi.appendMsg('Going to compare KMC entryid to entryCreation data')
             #Compare KMC entryid to metadata return value.
             if line.find(entryId) >= 0:
                self.logi.appendMsg("PASS - The entry id was found to MeetingId = " + MeetingId + ",  entryId = " + entryId)
                 
            # Select Entry
             self.logi.appendMsg("INFO - Going to select the entry ")          
             rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, MeetingId, True)
             if not rc:
                self.logi.appendMsg("FAIL - could not find the entry with MeetingId:" + MeetingId + " in entries table")
                     
             self.logi.appendMsg("********** INFO - Going to use player - VERSION = " + str(PlayerVersion) )
             
             try:
                time.sleep(2)   
                self.Wd.maximize_window()
             except Exception as e:
                 print(e)
                 pass    
             # Save window 
             primTab = self.Wd.window_handles[0]
         
             # Play the entry by PreviewAndEmbed
             self.logi.appendMsg("INFO - Going to play the entry on PreviewAndEmbed player")    
             rc = self.entryPage.PreviewAndEmbed(self.env,PreviewEmbedHTTPSSelection,PreviewEmbedTYPESelectionText,PlayerVersion,"Automation player_version" + str(PlayerVersion),self.Wd)
             if not rc:
                 testStatus = False
                 self.logi.appendMsg("FAIL - PreviewAndEmbed : PlayerVersion = " + str(PlayerVersion) + ", PlayerName = Automation player_version" + str(PlayerVersion))
             else:
                 self.logi.appendMsg("PASS - PreviewAndEmbed : PlayerVersion = " + str(PlayerVersion) + ", PlayerName = Automation player_version" + str(PlayerVersion))
             # meetingDuration    
             time.sleep(meetingDuration)
              
             # Close embed player tab                   
             self.Wd.close()
             time.sleep(2)
                
             # Return to previous window  
             self.Wd.switch_to.window(primTab)
             time.sleep(2)
             # Close preview&embed window   
             self.Wd.find_element_by_xpath(DOM.PREVIEWANDEMBED_CLOSE_BTN).click()
             time.sleep(2)
              
             # Close KMC            
             self.Wd.close()          
             time.sleep(2)
         
          
        except Exception as e:
            print(e)
            testStatus = False
            pass
        
        
    def teardown_class(self):
        
        global testStatus
        global KMC_Zoom_Deletion
        global MeetingId
        global isProd
        global entryId
        
        try:
           if KMC_Zoom_Deletion == True and isProd == False:#Just delete the entry on testing.qa(production run on Kino - No delete)  
               self.testTeardownclass.exeTear()
               # Delete the live entry
               self.logi.appendMsg("INFO - Going to delete the ZOOM entry. entryId = " + entryId)
               time.sleep(2)
               result = self.client.baseEntry.delete(entryId)
               print("Info - " + result) 
        except Exception as Exp:
           print(Exp)
           pass

        try:
            self.Wd.quit()
        except:
            pass

        if testStatus == False:
           self.logi.reportTest('fail',self.sendto)
           self.practitest.post(Practi_TestSet_ID, '1891','1')
           assert False
        else:
           self.logi.reportTest('pass',self.sendto)
           self.practitest.post(Practi_TestSet_ID, '1891','0')
           assert True
       
    #pytest.main(args=['test_1891_ZoomNewMeeting.py','-s'])
          
