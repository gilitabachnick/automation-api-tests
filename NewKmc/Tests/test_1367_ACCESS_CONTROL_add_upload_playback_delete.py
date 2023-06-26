'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@test_name: test_1367_ACCESS_CONTROL_add_upload_playback_delete
 
 @desc : this test create regular none limitation access control, upload entry, 
 set the access control to the entry, play the entry video and delete the entry and acces control
 
 
 @precondition - this test partner Id, should be included in the white list access control
 in configuration tab of admin console
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


### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True
testsMatrix = []

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
            self.user   = inifile.RetIniVal(section, 'userUpload')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto') 
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('test_1367_ACCESS_CONTROL_add_upload_playback_delete')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.filepth = r'\QRcodeVideo.mp4;' + r'\QRcodeVideo2.mp4;' + r'\QRcodeVideo3.mp4;' + r'\QRcodeVideo4.mp4' 
            self.filepthlocal = 'QRcodeVideo.mp4;QRcodeVideo2.mp4;QRcodeVideo3.mp4;QRcodeVideo4.mp4'
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")  
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.settingfuncs = settingsFuncs.settingsfuncs(self.Wd,self.logi)
            self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
            self.practitest = Practitest.practitest('4586')
            self.entryName = '"QRcodeVideo";"QRcodeVideo2";"QRcodeVideo3";"QRcodeVideo4"'
            self.entrylst = self.entryName.split(";")
            self.accessControls = ["autotest basic","autotest domain","autotest country allow","autotest country block"]
            #self.accessControls = ["autotest country block"]
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepthlocal
                
            
                
        except:
            pass
        
    def test_1367_ACCESS_CONTROL_add_upload_playback_delete(self):
        
        global testStatus
        
        self.logi.initMsg('test_1367_ACCESS_CONTROL_add_upload_playback_delete.py')
        
                
        try:
            # Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            #Upload new entries
            self.logi.appendMsg("INFO - Going to upload file - " + self.filepth)
            self.uploadfuncs.uploadFromDesktop(self.filepth)
            self.logi.appendMsg("INFO - Waiting for status ready")

            for entryName in self.entrylst:
                rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, entryName)
                if(rc):
                    self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
                else:
                    self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                    testStatus = False
                    return
            
            # adding access control
            # create 4 access controls: basic, domain, country allow, and country block
            j=0
            for i in (self.accessControls):
                
                tmptestStatus = True
                
                if i == "autotest basic":
                    rc = self.settingfuncs.addAccessControlProfile(i, "basic description")
                    shouldplay = True
                    practitest_id = '1367'
                elif i == "autotest domain":
                    rc = self.settingfuncs.addAccessControlProfile(i, "domain description", "selected", "google.com") 
                    expMsg = "sorry, this content is only available on certain domains"
                    shouldplay = False 
                    practitest_id = '1368'
                elif i == "autotest country allow":
                    rc = self.settingfuncs.addAccessControlProfile(i, "country allow description", authorizedCountries="selected", theCountries="Australia")
                    expMsg = "sorry, this content is only available in certain countries"
                    shouldplay = False
                    practitest_id = '1369'
                else:
                    rc = self.settingfuncs.addAccessControlProfile(i, "country block description", authorizedCountries="blocked", theCountries="Israel")
                    expMsg = "sorry, this content is only available in certain countries"
                    shouldplay = False  
                    practitest_id = '1370'  
                    
                if not rc:
                    testStatus = False
                    return
                
                # relate each of the access controls to the entry and play and verify it plays or not as it should        
                self.entryPage.setAccessControlToEntry(self.entrylst[j], i)
                self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entrylst[j])
                
                primTab = self.Wd.window_handles[0]
                rc = self.entryPage.PreviewAndEmbed(self.env,None,"Dynamic Embed",2,"Automation player_version2", TestPlay=shouldplay)
                if rc:
                    time.sleep(10)
            

                if i=="autotest basic":
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
                                tmptestStatus = False
                        else:
                            self.logi.appendMsg("FAIL - could not take second time QR code value after playing the entry")
                    else:
                        self.logi.appendMsg("FAIL - could not take the QR code value after playing the entry")
                        
                else:
                    self.logi.appendMsg("INFO - going to verify it is NOT played due to: " + i)
                    try:
                        messageTxt = self.Wd.find_element_by_xpath(DOM.MSG_ON_PLAYER).text
                        if messageTxt.find(expMsg) >=0:
                            self.logi.appendMsg("PASS - video received the correct message")
                        else:
                            self.logi.appendMsg("FAIL - the expected message is: " + expMsg + " and the actual is: " + messageTxt)
                    except:
                        self.logi.appendMsg("FAIL - the none authorized message did not appear on the video frame")
                        testStatus = False
                        tmptestStatus = False
 
             
                self.Wd.close()        
                self.Wd.switch_to.window(primTab)
                self.Wd.find_element_by_xpath("//i[@class='kIconclose_small kClose']").click()

                if tmptestStatus:
                    testsMatrix.append([practitest_id,'0'])
                else:
                    testsMatrix.append([practitest_id,'1'])

                j += 1
            # delete access control
            for accesctrl in self.accessControls:
                rc = self.settingfuncs.deleteAccessControl(accesctrl)
                if not rc:
                    testStatus = False
             
        
        except Exception as Exp:
            testStatus = False
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
        # report to practitest
        for i in range(len(testsMatrix)):
            self.practitest.post(Practi_TestSet_ID, str(testsMatrix[i][0]), str(testsMatrix[i][1]))

        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            assert True
            
    #==================================================================================
    # pytest.main(args=['test_1367_ACCESS_CONTROL_add_upload_playback_delete.py','-s'])
    #==================================================================================