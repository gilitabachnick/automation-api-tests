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
import Config
import Practitest
import Entrypage
import paramiko

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
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'dropfldruser')
            self.pwd    = inifile.RetIniVal(section, 'dropfldrpass')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.sftpserver = inifile.RetIniVal('ftp', 'sftpserver')
            self.sftpuser = inifile.RetIniVal('ftp', 'sftpuser')
            self.sftppass = inifile.RetIniVal('ftp', 'sftppass')
            self.serverpth = inifile.RetIniVal('ftp', 'sftpfolder')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST_1428_DROPFOLDERSFTP')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
            self.practitest = Practitest.practitest('4586')
            self.entriesName = "P123510"
            
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName,",")
        except:
            pass    
            
        
    def test_1428_dropFolderSFTP(self):
        
        global testStatus
        
        try:
            currtime = datetime.datetime.now()
            self.logi.initMsg('test drop folder')
            self.logi.appendMsg("INFO - going start test SFTP remote content - Add as new - Delete Auto")
            self.logi.appendMsg("INFO - going to upload file  \"P123510.mp4\" to remote drop folder: " + self.serverpth + " on server: " + self.sftpserver)
           
            # uploading file to ftp server via sftp
            
            
            port = 22
            transport = paramiko.Transport((self.sftpserver, port))
            transport.connect(username = self.sftpuser, password = self.sftppass)
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            fPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData' ,'P123510.mp4'))
            try:
                #===============================================================
                # sftp.put(fPath,'/TESTING/QACoreAutomationDropFolder3/SFTPRemoteContentAddAsNew/P45678.mp4')
                #===============================================================
                sftp.put(fPath,os.path.join(self.serverpth,'P123510.mp4'))
                self.logi.appendMsg("PASS - file was sent by sftp to the ftp server")
            except:
                self.logi.appendMsg("FAIL - file was NOT sent by ftp to the ftp server, can not continue this test")
                testStatus = False
                return
            
            sftp.close()
            transport.close()

            time.sleep(5)
            
           # wait for entry to upload in KMC
            rc = self.entryPage.dropFolderWaitForUploadAndEntry("P123510")
            if not rc:
               testStatus = False
        except:
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
            self.practitest.post(Practi_TestSet_ID, '1428','1')
            assert False
        else:
            self.logi.reportTest('pass',self.sendto)
            self.practitest.post(Practi_TestSet_ID, '1428','0')
            assert True         
        
        
            
        
    #===========================================================================
    # pytest.main(args=['test_1428_dropFolderSFTP.py','-s'])
    #===========================================================================
          