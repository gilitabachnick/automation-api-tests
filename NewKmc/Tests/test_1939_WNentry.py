'''
@author: Moran.Cohen
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@test_name: test_test_playWNentry

 @desc : this test plays WN entry verify playback on production
Download https://sourceforge.net/projects/capture2text/
path=r'C:\Program Files (x86)\Kaltura\QRCodeDetector\Capture2Text\Capture2Text.exe
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''

#import imagehash


import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import KmcBasicFuncs
import uploadFuncs
import reporter2

import Config
import Practitest
import Entrypage
import settingsFuncs
import QrcodeReader

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
#===============================================================================
# ############OLD
# isProd = os.getenv('isProd')
# if str(isProd) == 'true':
#     isProd = True
# else:
#     isProd = False
#      
# Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
# ###############
#===============================================================================

testStatus = True
# This test only run on production - WN entry
isProd = True

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
                self.existQrCode = False
                self.url    = "http://www.kaltura.com/index.php/extwidget/preview/partner_id/931702/uiconf_id/43922141/entry_id/1_oorxcge2/embed/auto?&flashvars%5bLeadWithHLSOnFlash%5d=true"
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.existQrCode = True
                self.url    = "https://qa-apache-php7.dev.kaltura.com/index.php/extwidget/preview/partner_id/231/uiconf_id/15224703/entry_id/0_k6rhb11m/embed/dynamic"
                
            self.sendto = inifile.RetIniVal(section, 'sendto')  
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('test_1939_WNentry')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.Wd.get(self.url)
            self.Wd.implicitly_wait(30)         
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingfuncs = settingsFuncs.settingsfuncs(self.Wd,self.logi)
            self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
            self.practitest = Practitest.practitest('4586')
        
                
        except Exception as Exp:
            print(Exp)
            pass
    
 
        
    def test_1939_WNentry(self):
        
        global testStatus
        
        self.logi.initMsg('test_1939_WNentry.py')  
                
        try:
            # Open WN player 
            self.Wd.get(self.url)
            self.Wd.implicitly_wait(10)
            
            self.logi.appendMsg("********** INFO - Going to use player = " + str(self.url) )
            
            # Play the entry by PreviewAndEmbed - Version 2
            self.logi.appendMsg("INFO - Going to play the entry on PreviewAndEmbed player")    
            rc = self.entryPage.PreviewAndEmbed(self.env,JustPlayOnBrowser =True)
            if not rc:
                testStatus = False
                self.logi.appendMsg("FAIL - Play WN entry = " + str(self.url))
            else:
                self.logi.appendMsg("PASS - Play WN entry")
  
            time.sleep(10)
            
            
            if self.existQrCode == False: #Production NO Qrcode - Using Capture2Text 
                self.QrCode.initVals()        
                rc = self.QrCode.placeCurrPrevScr_OnlyPlayback()               
                if rc:
                    time.sleep(4)
                    rc = self.QrCode.placeCurrPrevScr_OnlyPlayback()
                    if rc: 
                        rc = self.QrCode.checkProgress_OnlyPlayback(4)
                        if rc:
                            self.logi.appendMsg("PASS - Video played as expected.")
                        else:
                            self.logi.appendMsg("FAIL - Video was not progress by the Capture2Text displayed in it.")
                            testStatus = False
                                  
                    else:
                            self.logi.appendMsg("FAIL - could not take second time Capture2Text value after playing the entry.")
                else:
                        self.logi.appendMsg("FAIL - could not take the Capture2Text value after playing the entry.")         
            else:#self.existQrCode = True --> Testing.qa exists QrCode
                self.QrCode.initVals()        
                rc = self.QrCode.placeCurrPrevScr()
                if rc:
                    time.sleep(4)
                    rc = self.QrCode.placeCurrPrevScr()
                    if rc:
                        rc = self.QrCode.checkProgress(4)
                        if rc:
                            self.logi.appendMsg("PASS - Video played as expected.")
                        else:
                            self.logi.appendMsg("FAIL - Video was not progress by the qr code displayed in it.")
                            testStatus = False
                                 
                    else:
                            self.logi.appendMsg("FAIL - could not take second time QR code value after playing the entry.")
                else:
                        self.logi.appendMsg("FAIL - could not take the QR code value after playing the entry.")
      
           
        
        except Exception as Exp:
            testStatus = False
            print(Exp)
            pass
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):

        
        global testStatus
        
        print('#############')
        print(' Tear down')
        self.Wd.quit()
        print('#############')
        
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '1939','1') 
           self.logi.reportTest('fail',self.sendto)      
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '1939','0')
           self.logi.reportTest('pass',self.sendto)
           assert True            
            

    #pytest.main(args=['test_1939_WNentry.py','-s'])       
