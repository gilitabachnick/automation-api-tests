import os
import sys
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
import pytest
import time
import datetime
import pymysql
pymysql.install_as_MySQLdb()
import Practitest
import Config
import reporter
import ClienSession
import Entry
from KalturaClient.Plugins.Attachment import *

isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
testStatus = True
 #===========================================================================
# Description :   Antivirus test  
#
# Test scenario:  upload entry from clean file, add infected attachment
#                          
# Verifications:  find virusscan job status in db
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
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            if isProd:
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
            else:
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.env = 'testing'
                print('TESTING ENVIRONMENT')            
            self.PublisherID        = inifile.RetIniVal('Environment', 'iliaPublisherID')
            self.ServerURL          = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret         = inifile.RetIniVal('Environment', 'iliaUserSecret')
            self.InfectedURL            = inifile.RetIniVal('InfectedAttachment', 'URL')
            self.Message            = inifile.RetIniVal('InfectedAttachment', 'Message')
            self.connString         = inifile.RetIniVal('Environment', 'connString')
            pth                     = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            self.FileName           = inifile.RetIniVal('Entry', 'File')
            self.FileName           = os.path.join(pth, self.FileName).replace("\\", "/")  
            self.logi = reporter.Reporter('Test Antivirus')
            self.logi.appendMsg('start create session for publisher: ' + str(self.PublisherID))                 
        
            # create session
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            
            # Add new clean video entry
            currentDT = datetime.datetime.now()
            formatDate = currentDT.strftime("%Y_%m_%d__%H_%M_%S")
            self.TokenEntry = Entry.Entry(self.client, 'Antivirus '+formatDate, 'Antivirus desc '+formatDate, None, None, None, 0, file(self.FileName,'rb'))
            self.logi.initMsg('Uploading new entry...')        
            self.NewEntry = self.TokenEntry.AddNewEntryWithFile()
             
            if isinstance(self.NewEntry,bool):
                self.logi.appendMsg('FAIL - Could not create new entry')
                testStatus  = False
                assert False
            else:
                self.logi.appendMsg('New entry uploaded successfully with the name= ' + self.NewEntry.name + ' and id = ' + str(self.NewEntry.id))
            
        except:
            pass        
    #===========================================================================
    # test Antivirus
    #===========================================================================    
    def test_1449_Antivirus(self):
        global testStatus       
        try:
            #Attaching infected file
            self.logi.appendMsg('Attaching infected document to entry...')
            self.id = self.NewEntry.id
            attachmentAsset = KalturaAttachmentAsset()
            result = self.client.attachment.attachmentAsset.add(self.id, attachmentAsset)
            contentResource = KalturaUrlResource()
            contentResource.url = self.InfectedURL
            uploaded=self.client.attachment.attachmentAsset.setContent(result.id, contentResource)
            self.logi.appendMsg('Waiting 60 sec. for attachment to be ingested...')
            time.sleep(60)
            
            #Search antivirus batch job
            sql = """SELECT * FROM batch_job_sep WHERE entry_id = %s AND message LIKE %s"""
            try:
                exec(self.connString)
            except Exception as exp:
                print(exp)
                pass            
            cursor = conn.cursor()
            cursor.execute(sql, (self.NewEntry.id,'%'+self.Message+'%',))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()  
            #Check antivirus test results:
            if len(rows) != 2:
                self.logi.appendMsg("Wrong number of results - test failed!")
                testStatus  = False
                assert False
            else:
                for row in rows:
                    asset=row['object_id']
                    if row['message'] == "Scan finished - file was found to be clean":
                        self.logi.appendMsg("Asset "+asset+" scanned and found to be clean")                
                    if row['message'] == "File was found INFECTED and wasn't cleaned!":
                        self.logi.appendMsg("Asset "+asset+" scanned and found to be infected")
        except:
            testStatus=False
            pass
            
        
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        global testStatus
        
        print('#########')
        print('tear down')
        print('#########')
        
        self.logi.appendMsg('Going to delete the entry')
        
        try:
            entryDeleted = self.TokenEntry.DeleteEntry(self.NewEntry.id)
            if entryDeleted:
                self.logi.appendMsg('Entry deleted successfully')
            else:
                self.logi.appendMsg('FAIL - Could not delete the entry')
        except:
            pass
                
        if testStatus == False:
            self.logi.reportTest('fail')
            self.practitest.post(Practi_TestSet_ID, '1449','1') 
            assert False
        else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '1449','0') 
            assert True       
              
    pytest.main(args=['test_1449_Antivirus.py','-s'])
