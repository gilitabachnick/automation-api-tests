'''
@author: Moran.Cohen
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@test_name: test_1364_PreviewAndEmbedV2_HTTPIFrameEmbed
 
 @desc : this test uploading video entry and playing it with HTTP & IFrame Embed player 
 

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
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
import uploadFuncs
import reporter2

import Config
import Practitest
import Entrypage
import settingsFuncs
import QrcodeReader
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
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto') 
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('test_1364_PreviewAndEmbedV2AndV3_HTTPIFrameEmbed')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.filepth = r'\QRcodeVideo.mp4'
            self.filepthlocal = 'QRcodeVideo.mp4'
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingfuncs = settingsFuncs.settingsfuncs(self.Wd,self.logi)
            self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
            self.practitest = Practitest.practitest('4586')
            self.entryName = "QRcodeVideo"
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepthlocal
                            
                
        except:
            pass
        
    def test_1364_PreviewAndEmbedV2_HTTPDynamicEmbed(self):
        
        global testStatus
        
        PreviewEmbedTYPESelectionText = "IFrame Embed"
        PreviewEmbedHTTPSSelection = False
      
        
        self.logi.initMsg('test_1364_PreviewAndEmbedV2AndV3_HTTPIFrameEmbed.py')
        
                
        try:
            # Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()           
            

            # Upload new entry
            self.logi.appendMsg("INFO - Going to upload file - " + self.filepth)
            self.uploadfuncs.uploadFromDesktop(self.filepth)
            self.logi.appendMsg("INFO - Waiting for status ready")    
            rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.entryName)   
            if(rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
            else:       
                 self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                 testStatus = False
                 return
                                       
            
            # Select Entry
            self.logi.appendMsg("INFO - Going to select the entry ")          
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entryName, True)
            if not rc:
                self.logi.appendMsg("FAIL - could not find the entry- " + self.entryName + " in entries table")
            
            for PlayerVersion in range(2,4):
                self.logi.appendMsg("********** INFO - Going to use player - VERSION = " + str(PlayerVersion) )
                
                self.Wd.maximize_window()
                # Save window 
                primTab = self.Wd.window_handles[0]
            
                # Play the entry by PreviewAndEmbed - Version 2
                self.logi.appendMsg("INFO - Going to play the entry on PreviewAndEmbed player")    
                rc = self.entryPage.PreviewAndEmbed(self.env,PreviewEmbedHTTPSSelection,PreviewEmbedTYPESelectionText,PlayerVersion,"Automation player_version" + str(PlayerVersion))
                if not rc:
                    testStatus = False
                    self.logi.appendMsg("FAIL - PreviewAndEmbed : PlayerVersion = " + str(PlayerVersion) + ", PlayerName = Automation player_version" + str(PlayerVersion))
                else:
                    self.logi.appendMsg("PASS - PreviewAndEmbed : PlayerVersion = " + str(PlayerVersion) + ", PlayerName = Automation player_version" + str(PlayerVersion))
      
                time.sleep(10)
                
                self.QrCode.initVals()        
                rc = self.QrCode.placeCurrPrevScr()
                if rc:
                    time.sleep(4)
                    rc = self.QrCode.placeCurrPrevScr()
                    if rc:
                        rc = self.QrCode.checkProgress(4)
                        if rc:
                            self.logi.appendMsg("PASS - video played as expected")
                        else:
                            self.logi.appendMsg("FAIL - video was not progress by the qr code displayed in it")
                            testStatus = False
                                
                    else:
                            self.logi.appendMsg("FAIL - could not take second time QR code value after playing the entry")
                else:
                        self.logi.appendMsg("FAIL - could not take the QR code value after playing the entry")
            
                # Close embed player tab            
                self.Wd.close()
                
                time.sleep(2)
                
                # Return to previous window  
                self.Wd.switch_to.window(primTab)
                time.sleep(2)
                # Close preview&embed window   
                self.Wd.find_element_by_xpath(DOM.PREVIEWANDEMBED_CLOSE_BTN).click()
                time.sleep(2)
        
        except Exception as Exp:
            testStatus = False
            print(Exp)
            pass
              
        
    def teardown_class(self):
        
        global testStatus
        
        try:
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            self.BasicFuncs.deleteEntries(self.Wd,self.entryName)
        except:
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1364', '1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1364', '0')
            self.logi.reportTest('pass',self.sendto)
            assert True
        
        
            
        
    #===========================================================================
    # pytest.main('test_1364_PreviewAndEmbedV2AndV3_HTTPIFrameEmbed.py -s')    
    #===========================================================================
          