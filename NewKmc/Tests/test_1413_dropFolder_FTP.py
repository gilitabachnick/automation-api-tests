import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import MySelenium
import KmcBasicFuncs
import reporter2
import myFtp

import Config
import Practitest
import Entrypage

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
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

            self.serverpth = inifile.RetIniVal('ftp', 'folder')
            self.url = inifile.RetIniVal(section, 'Url')
            self.user = inifile.RetIniVal(section, 'dropfldruser')
            self.pwd = inifile.RetIniVal(section, 'dropfldrpass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.ftpserver = inifile.RetIniVal('ftp', 'ftpserver')
            self.ftpuser = inifile.RetIniVal('ftp', 'ftpuser')
            self.ftppass = inifile.RetIniVal('ftp', 'ftppass')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST_1413_DROPFOLDER_FTP')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.practitest = Practitest.practitest('4586')
            self.ftp = myFtp.myFtp(self.ftpserver, self.ftpuser, self.ftppass)
            self.entriesName = "P123509"

            # Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            self.BasicFuncs.deleteEntries(self.Wd, self.entriesName, ",")
        except:
            pass

    def test_1413_dropFolder_FTP(self):

        global testStatus

        try:
            currtime = datetime.datetime.now()
            self.logi.initMsg('test drop folder')
            self.logi.appendMsg("INFO - going start test FTP remote content - Add as new - Delete Auto")
            self.logi.appendMsg(
                "INFO - going to upload file  \"P123509.mp4\" to remote drop folder: \"FTPRemoteContentAddAsNew\" on server: " + self.ftpserver)

            # uploading file to ftp server
            fPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData', 'P123509.mp4'))
            rc = self.ftp.uploadFile(fPath, self.serverpth, "P123509.mp4")
            if rc:
                self.logi.appendMsg("PASS - file was sent by ftp to the ftp server")
            else:
                self.logi.appendMsg("FAIL - file was NOT sent by ftp to the ftp server, can not continue this test")
                testStatus = False
                return

            time.sleep(5)

            # wait for entry to upload in KMC
            rc = self.entryPage.dropFolderWaitForUploadAndEntry("P123509")
            if not rc:
                testStatus = False
        except Exception as Exp:
            print(Exp)
            testStatus = False
            pass
    
    def teardown_class(self):
        
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName,",")
        except:
            pass
        self.Wd.quit()
        
        if testStatus == False:
            self.logi.reportTest('fail',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1413','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1413','0')
            assert True

    #===========================================================================
    # pytest.main(args=['test_1413_dropFolder_FTP.py','-s'])
    #===========================================================================
          