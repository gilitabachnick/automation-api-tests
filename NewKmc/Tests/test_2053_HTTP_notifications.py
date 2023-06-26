import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'APITests', 'lib'))
sys.path.insert(1,pth)

import time
import datetime
import Practitest
import Config
import reporter2
import ClienSession
import CustomMetaData
import Entry
from KalturaClient.Plugins.Attachment import *
import KmcBasicFuncs
import MySelenium

cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()

if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

#===========================================================================
# Description :   HTTP notifications test  
#
# Test scenario:  upload entry with add captions on partner with pre-set various HTTP notifications
#                          
# Verifications:  find HTTP job statuses in db
#
#===========================================================================

class TestClass:    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        global testStatus
        try:
            self.practitest = Practitest.practitest('4586')
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../APITests/', 'ini'))
            if isProd:
                inifile = Config.ConfigFile(os.path.join(pth, '../ini/ProdParams.ini'))
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
            else:
                inifile = Config.ConfigFile(os.path.join(pth, '../ini/TestingParams.ini'))
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
            self.PublisherID        = inifile.RetIniVal('Environment', 'iliaPublisherID')
            self.ServerURL          = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret         = inifile.RetIniVal('Environment', 'iliaUserSecret')
            pth                     = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../APITests/', 'UploadData'))
            self.JobSubType         = inifile.RetIniVal('Entry', 'SubType')
            self.MetadataProfile    = inifile.RetIniVal('Entry', 'MetadataProfile')
            self.MetaDataValue      = inifile.RetIniVal('Entry', 'Metadata')
            self.URL                = inifile.RetIniVal('Entry', 'AttachementURL')
            self.FileName           = inifile.RetIniVal('Entry', 'File')
            self.FileName           = os.path.join(pth, self.FileName).replace("\\", "/")
            self.CaptionName           = inifile.RetIniVal('Entry', 'Caption')
            self.CaptionName           = os.path.join(pth, self.CaptionName).replace("\\", "/")
            self.logi = reporter2.Reporter2('API tests')
            self.logi.initMsg('Test 2053 HTTP notifications')
            self.logi.appendMsg('start create session for publisher: ' + str(self.PublisherID))
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()

            #Pulling NewKmc ini file
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', 'ini'))
            if isProd:
                inifile = Config.ConfigFile(os.path.join(pth, '../ini/ProdParams.ini'))
                self.env = 'prod'
                section = 'Production'
                print('PRODUCTION ENVIRONMENT')
            else:
                inifile = Config.ConfigFile(os.path.join(pth, '../ini/TestingParams.ini'))
                self.env = 'testing'
                section = 'Testing'
                print('TESTING ENVIRONMENT')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')
            self.admin_user = inifile.RetIniVal('admin_console_access', 'session_user')
            self.env = inifile.RetIniVal('admin_console_access', 'environment')
            self.url = inifile.RetIniVal(section, 'admin_url')
            self.user   = inifile.RetIniVal(section, 'AdminConsoleUser')
            self.pwd    = inifile.RetIniVal(section, 'AdminConsolePwd')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            # create session
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            self.MetaData = CustomMetaData.CustomMetaData(self.client)

            # Add new video entry
            currentDT = datetime.datetime.now()
            formatDate = currentDT.strftime("%Y_%m_%d__%H_%M_%S")
            self.TokenEntry = Entry.Entry(self.client, 'HTTP notification '+formatDate, 'HTTP notification desc '+formatDate, None, None, None, 0, open(self.FileName,'rb+'))
            self.logi.appendMsg('Uploading new entry...')
            self.NewEntry = self.TokenEntry.AddNewEntryWithFile()

            if isinstance(self.NewEntry,bool):
                self.logi.appendMsg('FAIL - Could not create new entry')
                testStatus  = False
                assert False
            else:
                self.MainEntryID = str(self.NewEntry.id)
                self.logi.appendMsg('New entry uploaded successfully with the name= ' + self.NewEntry.name + ' and id = ' + self.MainEntryID)

            #Add new specific MetaData to entry
            self.logi.appendMsg('Going to change custom metadata of '+self.MainEntryID+' ...')
            try:
                self.MetaData.AddCustomMetaData(self.MetadataProfile, 0, self.MainEntryID, self.MetaDataValue)
            except Exception as Exp:
                raise Exp
            #Add attachment to the entry
            self.logi.appendMsg('Going to attach a document to entry '+self.MainEntryID+' ...')
            try:
                attachmentAsset = KalturaAttachmentAsset()
                result = self.client.attachment.attachmentAsset.add(self.MainEntryID, attachmentAsset)
                contentResource = KalturaUrlResource()
                contentResource.url = self.URL
                uploaded=self.client.attachment.attachmentAsset.setContent(result.id, contentResource)
            except Exception as Exp:
                raise Exp
            self.logi.appendMsg('Waiting 60 sec for all events to be sent...')
            time.sleep(60)
            pass
        except Exception as Exp:
            print(Exp)
            testStatus  = False
            pass        
    #===========================================================================
    # test HTTP_notifications
    #===========================================================================    
    def test_2053_HTTP_notifications(self):
        global testStatus
        self.logi.appendMsg('Going to log in to Admin Console...')
        if testStatus:
            try:
                if "nv" not in self.url:  # Bypass NVD console user/pass login
                    ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                                self.admin_user, self.env)
                else:
                    ks = False
                rc = self.BasicFuncs.invokeConsoleLogin(self.Wd, self.Wdobj, self.logi, self.url, self.user, self.pwd, ks)
                if not rc:
                    self.logi.appendMsg("FAIL - Unable to open admin console!")
                    testStatus = False
                    return
                else:
                    #Go to entry investigation page
                    self.logi.appendMsg('Success! Going to enter Batch Process Control page and search for entry ' + self.MainEntryID + ' ...')
                    result = self.BasicFuncs.getBatchJobStatus(self.Wd, self.MainEntryID, 'Event Notification')
                    if result:
                        if len(result) == 4:
                            self.logi.appendMsg('Success! Found 4 values as expected! They are as following:')
                            for i in range(len(result)):
                                self.logi.appendMsg('Job title: ' + str(result[i][0]) + ' | ' + str(result[i][1]) + ' | ' + str(result[i][2]))
                                if str(result[i][2]) == 'status : Finished':
                                    self.logi.appendMsg('Pass!')
                                else:
                                    self.logi.appendMsg('Unexpected job status - ' + str(result[i][2]) +'!')
                                    testStatus = False
                                    pass
                        else:
                            self.logi.appendMsg('Unexpected number of results - ' + str(len(result)) + ' !')
                            testStatus = False
                            pass
                    else:
                        self.logi.appendMsg('Got empty or invalid result! FAILED!')
                        testStatus = False
                        pass
            except Exception as Exp:
                print(Exp)
                testStatus = False
                pass
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        global testStatus
        
        print('#########')
        print('tear down')
        print('#########')

        # Close browser
        self.Wd.quit()

        self.logi.appendMsg('Going to delete the entry')
        
        try:
            entryDeleted = self.TokenEntry.DeleteEntry(self.MainEntryID)
            if entryDeleted:
                self.logi.appendMsg('Entry deleted successfully')
            else:
                self.logi.appendMsg('FAIL - Could not delete the entry')
        except:
            pass

        if testStatus == False:
            self.logi.reportTest('fail')
            self.practitest.post(Practi_TestSet_ID, '2053','1') 
            assert False
        else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '2053','0') 
            assert True       
    ############################################################
    # pytest.main(args=['test_2053_HTTP_notifications.py','-s'])
    ############################################################
    