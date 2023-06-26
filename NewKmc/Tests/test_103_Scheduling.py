'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_103_Scheduling.py
 
 @desc : this test check Functionality of Scheduling Section:,KMC UI/Validation annd Preview&Embed playback (allow/block scheduling)

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
import KmcBasicFuncs
import uploadFuncs
import reporter2

import Config
import Practitest
import Entrypage
import settingsFuncs
import QrcodeReader
import SchedulingFuncs
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
            self.logi = reporter2.Reporter2('test_103_Scheduling')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.filepthVIDEO = r'\QRcodeVideo.mp4'
            self.filepthlocalVIDEO = 'QRcodeVideo.mp4'          
            self.filepthIMAGE = r'\smalljpg.jpg'
            self.filepthlocalIMAGE = 'smalljpg.mp4'
            self.filepthAUDIO = r'\Audio1.wav'
            self.filepthlocalAUDIO = 'Audio1.mp4'
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingfuncs = settingsFuncs.settingsfuncs(self.Wd,self.logi)
            self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
            self.SchedulingFuncs = SchedulingFuncs.SchedulingFuncs(self.Wd,self.logi)            
            self.practitest = Practitest.practitest('4586')
            self.entryNameVIDEO = "QRcodeVideo"
            self.entryNameIMAGE = "smalljpg"
            self.entryNameAUDIO = "Audio1"
            self.Schedulings = ["Scheduling allow","Scheduling block"]
            self.expMsg = 'Something went wrong'
            
                  
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()

            else:
                self.filepthVIDEO = self.filepthlocalVIDEO
                self.filepthIMAGE = self.filepthlocalIMAGE
                self.filepthAUDIO = self.filepthlocalAUDIO

                
        except Exception as e:
            print(e)
            pass
        
    def test_103_Scheduling(self):
        
        global testStatus
        
        self.logi.initMsg('test_103_Scheduling.py')
        
                
        try:
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
                     
            #Upload new entry VIDEO
            self.logi.appendMsg("INFO - Going to upload VIDEO file - " + self.filepthVIDEO)
            self.uploadfuncs.uploadFromDesktop(self.filepthVIDEO)
            self.logi.appendMsg("INFO - Waiting for status ready")
            rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.entryNameVIDEO)   
            if(rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
            else:       
                self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return
                  
            for i in self.Schedulings:

                # relate each of the scheduling to the entry and play and verify it plays or not as it should
                if i=="Scheduling allow":
                    StartDay="5"
                    StartMonth="June"
                    rc = datetime.date.today().year - 1
                    #StartYear= "2018"
                    StartYear= str(rc)
                    EndDay="6"
                    EndMonth="September"
                    #EndYear="2028"
                    EndYear= str(rc + 10)

                    SchedulingEnable=True
                    self.logi.appendMsg(" -------  INFO - Going to set Scheduling To Entry - ALLOW --------")
                    rc=self.SchedulingFuncs.setSchedulingToEntry(self.entryNameVIDEO, SchedulingEnable, StartDay, StartMonth, StartYear,EndDay, EndMonth, EndYear)
                    if not rc:
                        self.logi.appendMsg("FAIL - setSchedulingToEntry")
                        testStatus = False
                        return
                else: # Future scheduling/Block
                    StartDay="5"
                    StartMonth="June"
                    #StartYear= "2025"
                    StartYear= str(datetime.date.today().year + 6)
                    EndDay="6"
                    EndMonth="September"
                    #EndYear="2026"
                    EndYear= str(datetime.date.today().year + 7)
                    SchedulingEnable=True
                    self.logi.appendMsg("--------- INFO - Going to setSchedulingToEntry- BLOCK ----------")
                    rc=self.SchedulingFuncs.setSchedulingToEntry(self.entryNameVIDEO, SchedulingEnable, StartDay, StartMonth, StartYear,EndDay, EndMonth, EndYear)
                    if not rc:
                        self.logi.appendMsg("FAIL - setSchedulingToEntry")
                        testStatus = False
                        return

            self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entryNameVIDEO)
            primTab = self.Wd.window_handles[0]
            rc = self.entryPage.PreviewAndEmbed(self.env,None,"Dynamic Embed",3,"Automation player_version3")

            if rc:
                time.sleep(10)

            if i=="Scheduling allow":
                self.logi.appendMsg("INFO - going to play the entry video and verify it is played ok by detecting to QR code the video plays")
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

            else:
                self.logi.appendMsg("INFO - going to verify it is NOT played due to: " + i)
                try:
                    messageTxt = self.Wd.find_element_by_xpath(DOM.MSG_ON_PLAYERV7).text
                    if messageTxt.find(self.expMsg) >= 0:
                        self.logi.appendMsg("PASS - video received the correct message")
                    else:
                        self.logi.appendMsg("FAIL - the expected message is: " + self.expMsg + " and the actual is: " + messageTxt)
                except:
                    self.logi.appendMsg("FAIL - the none authorized message did not appear on the video frame")
                    testStatus = False


            self.Wd.close()
            self.Wd.switch_to.window(primTab)
            self.Wd.find_element_by_xpath(DOM.SCHEDULING_SCHEDULED_CLOSE).click()
                
            time.sleep(2)
         
        
        except Exception as e:
            print(e)
            testStatus = False
            pass
        
        
    def teardown_class(self):
        
        global testStatus
        
        try:
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            self.BasicFuncs.deleteEntries(self.Wd,self.entryNameVIDEO)
        except:
            pass
        
        self.Wd.quit()
        
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '103','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '103','0')
            self.logi.reportTest('pass',self.sendto)
            assert True         
        
    #===========================================================================
    #pytest.main(args=['test_103_Scheduling.py','-s'])    
    #===========================================================================
          
