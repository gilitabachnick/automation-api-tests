import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','NewKmc', 'lib'))
sys.path.insert(1,pth)
import boto3
import pytest
import time
import Config
import reporter2
import ClienSession
import Entry
import hashlib
import Practitest
import datetime

#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '2040'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
    if str(isProd) == 'true':
        isProd = True
    else:
        isProd = False

testStatus = True

#===========================================================================
# Description :   S3 remote storage test  
#
# Test scenario:  Upload entry, wait for flavors to be uploaded to Amazon's S3, compare checksums
#                          
# Verifications:  get original file MD5 checksum, find S3 remote file path, compare remote file MD5 with local one.
#
#===========================================================================    

class TestClass: 
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        global testStatus
        self.practitest = Practitest.practitest('4586','APITests')

        try:
            #self.practitest = Practitest.practitest()
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
            pth                     = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            self.FileName           = inifile.RetIniVal('Entry', 'DrmPlayReadfile')
            self.FileName           = os.path.join(pth, self.FileName).replace("\\", "/")
            self.access_key         = inifile.RetIniVal('S3', 'access_key')
            self.secret_key         = inifile.RetIniVal('S3', 'secret_key')
            self.bucket_name        = inifile.RetIniVal('S3', 'bucket_name')
            
            
            #Calculating local file MD5 checksum                
            self.local_md5 = hashlib.md5(open(self.FileName,'rb+').read()).hexdigest()
                                             
            self.logi = reporter2.Reporter2('API tests')
            self.logi.initMsg('Test 1906 S3 remote storage')          
            self.logi.appendMsg('Start create session for publisher: ' + str(self.PublisherID))

            # create session
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            
            # Add new clean video entry
            currentDT = datetime.datetime.now()
            formatDate = currentDT.strftime("%Y_%m_%d__%H_%M_%S")
            self.TokenEntry = Entry.Entry(self.client, 'S3 '+formatDate, 'S3 desc '+formatDate, None, None, None, 0, open(self.FileName,'rb+'))
            self.logi.appendMsg('Uploading new entry...')        
            self.NewEntry = self.TokenEntry.AddNewEntryWithFile()
             
            if isinstance(self.NewEntry,bool):
                self.logi.appendMsg('FAIL - Could not create new entry')
                testStatus  = False              
            else:
                self.logi.appendMsg('New entry uploaded successfully with the name= ' + self.NewEntry.name + ' and id = ' + str(self.NewEntry.id))
        except:
            pass        
    #===========================================================================
    # test S3
    #===========================================================================    
    def test_1906_remote_S3(self):
        global testStatus
        self.logi.appendMsg('Waiting 90 sec to make sure flavors are uploaded...')
        time.sleep(90)
        self.logi.appendMsg('Checking if flavors uploaded to S3...')
        try:           
            #Using API client get source flavor asset ID and its path
            flavors = self.TokenEntry.flavorList(self.NewEntry.id)
            sourceFlavorId = flavors.objects[0].id
            localPath = self.client.flavorAsset.getRemotePaths(sourceFlavorId).objects[0].uri
            #Converting to S3 path
            path = 'test'+localPath
            #Connect S3 backet
            client = boto3.client(
                's3',
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_key,
            )
            #Get MD5 sum of flavor stored on S3
            response = client.head_object(Bucket = self.bucket_name, Key = path)
            remote_MD5 = response['ETag'][1:-1]
            if self.local_md5 == remote_MD5:
                print(("MD5 checksums of local uploaded file and S3 stored file match: "+self.local_md5+". Test passed!"))
            else:
                print("MD5 checksums of local uploaded file and S3 stored file DO NOT match! Test failed!")
                testStatus=False
        except Exception as Exp:
            print(Exp)
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
            self.practitest.post(Practi_TestSet_ID, '1906','1')
            self.logi.reportTest('fail')
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1906','0')
            self.logi.reportTest('pass')
            assert True
            
    pytest.main(args=['test_1906_remote_S3.py','-s'])
