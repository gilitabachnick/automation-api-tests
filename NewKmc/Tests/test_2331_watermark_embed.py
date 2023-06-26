# '''
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# @author: ilia.vitlin
#
# @test_name: test_2331_watermark_embed
#
# @desc : Automated test for converting file with single QR code watermark embedding and verification of watermark by checking QR with Zbar
#
#  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# '''

import glob
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
import uploadFuncs
from pyzbar.pyzbar import decode
from PIL import Image

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

            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userNameIlia')
            self.pwd    = inifile.RetIniVal(section, 'passIlia')
            self.WmConversionProfileName = inifile.RetIniVal(section, 'WmConversionProfileName')
            self.WmEntryName  = 'WmEmbedQR'
            self.WmFilePth    = r'\Wildlife.wmv'
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_2331_watermark_embed')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.WmFilePth = self.WmFilePth[1:]


        except Exception as Exp:
            print(Exp)
            pass


    def test_2331_watermark_embed(self):

        global testStatus
        self.logi.initMsg('test_2331_watermark_embed')

        try:
            #invoke and login
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            #Upload file from desktop
            self.logi.appendMsg("INFO - Going to upload file - " + self.WmFilePth)
            #self.uploadfuncs.uploadFromDesktop(self.DistributionfilePth,"url","https://qa-apache-php7.dev.kaltura.com/content/output_video/out.mp4")
            self.uploadfuncs.uploadFromDesktop(self.WmFilePth,transcodingProfile=self.WmConversionProfileName, Fname=self.WmEntryName)

            #Waiting for ready status
            self.logi.appendMsg("INFO - Waiting for status ready")
            rc,line=self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.WmEntryName, itimeout=900)
            if(rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
            else:
                self.logi.appendMsg("FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return
            #Drilldown to entry by name.
            self.logi.appendMsg("INFO - Going to Drilldown to entry - " + self.WmEntryName)
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.WmEntryName, True)
            if rc:
                self.logi.appendMsg("PASS - Drilldown to entry - " + self.WmEntryName )
            else:
                self.logi.appendMsg("FAIL - could NOT Drilldown to entry - " + self.WmEntryName )
                testStatus = False
                return

            time.sleep(2)
            #Preview flavor (faster than with player embed)
            self.logi.appendMsg("INFO - Going to preview flavor of entry - " + self.WmEntryName)
            self.Wd.find_elements_by_xpath(DOM.FLAVORS)[0].click()
            self.Wd.find_elements_by_xpath(DOM.FLAVORS_FIRST_MENU)[0].click()
            self.Wd.find_elements_by_xpath(DOM.FLAVORS_PREVIEW)[0].click()
            time.sleep(5)
            self.logi.appendMsg("PASS - Preview of flavor available - " + self.WmEntryName )
            self.logi.appendMsg("INFO - Going to capture and analyze 3 screenshots - at the beginning, middle and the end")
            #Find video preview location and size
            video_preview = self.Wd.find_element_by_tag_name("video")
            location = video_preview.location
            size = video_preview.size
            x = location['x']
            y = location['y']
            w = x + size['width']
            h = y + size['height']
            screensize = (self.Wd.execute_script("return document.body.clientWidth"), self.Wd.execute_script("return window.innerHeight"))
            playTime = 0
            #Checking embedded watermark in beginning, middle and end of 0:30 video
            for i in range(3):
                #Jump to different times
                self.Wd.execute_script('document.getElementsByTagName("video")[0].currentTime += '+str(playTime)+';')
                time.sleep(2)
                #Save page screenshot
                self.Wd.save_screenshot("fullPageScreenshot.png")
                #Crop image to video
                fullImg = Image.open("fullPageScreenshot.png")
                fullImg = fullImg.resize(screensize)
                cropImg = fullImg.crop((x, y, w, h))
                cropImg.save("cropImage_"+str(i)+".png")
                #Analyze image, find QR message
                QR_image = Image.open("cropImage_"+str(i)+".png")
                barcode = decode(QR_image)
                if format(barcode[0].data.decode("utf-8")) == "Watermark":
                    self.logi.appendMsg("INFO - Image #"+str(i)+" at play time "+str(playTime)+" has correct watermark!")
                else:
                    self.logi.appendMsg("FAIL - Image #"+str(i)+" at play time "+str(playTime)+" has wrong watermark!")
                    testStatus = False
                    break
                playTime = playTime+15

            self.logi.appendMsg("PASS - All 3 screenshots from different times had correct watermark!")
            #Back to content tab
            self.Wd.refresh()
            time.sleep(3)
        except Exception as Exp:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following KMC login | UPLOAD | WaitForReady | DrillDown | Flavor Preview | Watermark QR code check")
            print(Exp)
            


    def teardown(self):
        global teststatus
        self.logi.appendMsg('Cleaning up...')
        #Delete entry
        try:
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            self.logi.appendMsg('INFO - Deleting entry...')
            self.BasicFuncs.deleteEntries(self.Wd,self.WmEntryName)
        except Exception as Exp:
            print(str(Exp))
            pass

        #Close browser
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(str(Exp))
            pass

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '2331','1')
            assert False
        else:
            #In case test passes, delete saved screenshots, just in case
            self.logi.appendMsg('INFO - Deleting screenshots...')
            fileList = glob.glob('*.png')
            for filePath in fileList:
                try:
                    os.remove(filePath)
                except:
                    print("Error while deleting file : ", filePath)

            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '2331','0')
            assert True

    #===========================================================================
    # pytest.main('test_2331_watermark_embed.py -s')
    # pytest.main(args=['test_2331_watermark_embed.py','-s'])
    #===========================================================================
