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

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import DOM
import MySelenium
import KmcBasicFuncs
import reporter2

import Config
import Practitest
import autoitWebDriver
import uploadFuncs
from pyzbar.pyzbar import decode
from PIL import Image, ImageFilter

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

class TestClass:
    # ===========================================================================
    # SETUP
    # ===========================================================================
    def setup_class(self):
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'userNameIlia')
            self.pwd = inifile.RetIniVal(section, 'passIlia')
            self.ThumbnailEntryName = 'Thumb and player preview'
            self.ThumbnailFilePth = r'\QR.mp4'
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_2411_thumbnail_preview')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()

            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                self.AWD = self.autoitwebdriver.retautoWebDriver()
            else:
                self.ThumbnailFilePth = self.ThumbnailFilePth[1:]


        except Exception as Exp:
            print(Exp)
            pass

    def test_2411_thumbnail_preview(self):

        global testStatus
        self.logi.initMsg('test_2411_thumbnail_preview')

        try:
            # invoke and login
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            # Upload file from desktop
            self.logi.appendMsg("INFO - Going to upload file - " + self.ThumbnailFilePth)
            self.uploadfuncs.uploadFromDesktop(self.ThumbnailFilePth, Fname=self.ThumbnailEntryName)

            # Waiting for ready status
            self.logi.appendMsg("INFO - Waiting for status ready")
            rc, line = self.BasicFuncs.waitForEntryStatusReady(self.Wd, self.ThumbnailEntryName, itimeout=900)
            if (rc):
                self.logi.appendMsg("PASS - The entry status was changed to Ready as expected ")
            else:
                self.logi.appendMsg(
                    "FAIL -  The entry status was NOT changed to Ready as expected, the actual status was: " + line)
                testStatus = False
                return
            time.sleep(5)
            self.logi.appendMsg("INFO - Taking screenshot of small list thumbnail...")
            # Find the div of thumbnail in list, take its screenshot
            self.Wd.find_element_by_class_name("kThumbnailHolder").screenshot("cropImg.png")
            # Quadruple thumbnail size and sharpen it for successful QR decoding
            QrImg = Image.open("cropImg.png")
            #QrImg.show()
            barcode = decode(QrImg)
            if format(barcode[0].data.decode("utf-8")) == "123456":
                self.logi.appendMsg(
                    "INFO - Thumbnail in list is shown correctly!")
            else:
                self.logi.appendMsg(
                    "FAIL - Thumbnail in list is NOT shown correctly!")
                testStatus = False

            # Drilldown to entry by name.
            self.logi.appendMsg("INFO - Going to Drilldown to entry - " + self.ThumbnailEntryName)
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.ThumbnailEntryName, True)
            if rc:
                self.logi.appendMsg("PASS - Drilldown to entry - " + self.ThumbnailEntryName)
            else:
                self.logi.appendMsg("FAIL - could NOT Drilldown to entry - " + self.ThumbnailEntryName)
                testStatus = False
                return

            time.sleep(10)
            self.logi.appendMsg("INFO - Taking screenshot of preview player...")
            player = self.Wd.find_elements_by_xpath("//iframe")[0].screenshot("BigImg.png")
            QrPlayerImg = Image.open("BigImg.png")
            #QrPlayerImg.show()
            playerBarcode = decode(QrPlayerImg)
            if format(playerBarcode[0].data.decode("utf-8")) == "123456":
                self.logi.appendMsg(
                    "INFO - Player preview is loaded successfully!")
            else:
                self.logi.appendMsg(
                    "FAIL - Player preview is NOT loaded successfully!")
                testStatus = False
            self.Wd.refresh()
            time.sleep(3)
        except Exception as Exp:
            testStatus = False
            self.logi.appendMsg("FAIL - on of the following KMC login | UPLOAD | WaitForReady | DrillDown | Flavor Preview | QR code check")
            testStatus = False
            print(Exp)

    def teardown(self):
        global teststatus
        self.logi.appendMsg('Cleaning up...')
        # Delete entry
        try:
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            self.logi.appendMsg('INFO - Deleting entry...')
            self.BasicFuncs.deleteEntries(self.Wd, self.ThumbnailEntryName)
        except Exception as Exp:
            print(str(Exp))
            pass

        # Close browser
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(str(Exp))
            pass

        if testStatus == False:
            self.logi.reportTest('fail', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '2411', '1')
            assert False
        else:
            # In case test passes, delete saved screenshots, just in case
            self.logi.appendMsg('INFO - Deleting screenshots...')
            fileList = glob.glob('*.png')
            for filePath in fileList:
                try:
                    os.remove(filePath)
                except:
                    print("Error while deleting file : ", filePath)

            self.logi.reportTest('pass', self.sendto)
            self.practitest.post(Practi_TestSet_ID, '2411', '0')
            assert True

    # ===========================================================================
    # pytest.main(args=['test_2411_thumbnail_preview.py', '-s'])
    # ===========================================================================
