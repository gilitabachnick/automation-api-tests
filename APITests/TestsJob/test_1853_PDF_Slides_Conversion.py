import datetime
import os
import sys

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','NewKmc', 'lib'))
sys.path.insert(1,pth)

import Practitest
import Config
import tearDownclass
import reporter2
import ClienSession
import Entry



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
# Description :   PDF to slides (JPEG) conversion test
#
# test scenario:  Upload PDF file, convert it with preset conversion profile
#                
# verifications:  Folder with slides created
#
#===========================================================================

class TestClass:   
    global testStatus
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        self.practitest = Practitest.practitest('4586','APITests')
        
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
        self.CoversionProfile   = inifile.RetIniVal('DocConver', 'pdfConversionProfile')
        pth                     = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.FileName           = inifile.RetIniVal('DocConver', 'pdfFile')
        self.FileName           = os.path.join(pth, self.FileName).replace("\\", "/")
        #self.testsetId = Practi_TestSet_ID
        currentDT = datetime.datetime.now()
        formatDate = currentDT.strftime("%Y_%m_%d__%H_%M_%S")
        EntryName = 'PDF conversion_'+formatDate
              
        self.testTeardownclass = tearDownclass.teardownclass()
                
        self.logi = reporter2.Reporter2('API tests')
        self.logi.initMsg('Test 1853 PDF Slides Conversion')
        self.logi.appendMsg('Start create session for publisher: ' + str(self.PublisherID))
        
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        
        # add new document entry
        currentDT = datetime.datetime.now()
        formatDate = currentDT.strftime("%Y_%m_%d__%H_%M_%S")
        self.TokenEntry = Entry.Entry(self.client, EntryName, 'PDF to slides conversion entry '+formatDate, None, None, None, 3, open(self.FileName,'rb+'), self.CoversionProfile)
        
        self.logi.appendMsg('Going to add new token and upload a document file to the token')
        Tokenfile =  self.TokenEntry.UploadFileToNewEntry(self.TokenEntry, True)
        print((' from the test - Token file id= ' + Tokenfile.id))
        self.logi.appendMsg('Going to create a document entry and set the file token uploaded to the entry')
        self.NewEntry = self.TokenEntry.AddDocumentEntry(Tokenfile.id)
        
        if isinstance(self.NewEntry,bool):
            self.logi.appendMsg('FAIL - Could not create new document entry from a document uploaded')
            testStatus=False
            self.logi.appendMsg('General error, test failed!')
            pass
        else:
            self.logi.appendMsg('New document entry from a document uploaded created successfully with the name= ' + self.NewEntry.name + ' and id= ' + str(self.NewEntry.id) + ' . Waiting for it to become ready...')
        
        
        
    #===========================================================================
    # Test of Document conversion  - PDF to folder of JPEG - one picture per PDF page
    #===========================================================================
    
    def test_1853_PDF_Slides_Conversion(self):    
        global testStatus

        try:
            timeout = 300
            DocEntryStatus = self.TokenEntry.WaitForEntryReady(self.NewEntry.id, timeout)
        except:
            testStatus=False
            self.logi.appendMsg('Fail! Could not check entry status!')
            pass
        if DocEntryStatus == 'error' or DocEntryStatus == 'timeout':
            testStatus=False
            self.logi.appendMsg('Fail! Entry conversion ' + DocEntryStatus + '!')
            pass
        else:
            self.logi.appendMsg('Entry converted successfully!')
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        print('#########')
        print('tear down')
        print('#########')
        
        global testStatus
        #=======================================================================
        # if self.status == True:
        #     self.testTeardownclass.exeTear()    
        #=======================================================================
        self.logi.appendMsg('Going to delete the document entry')
        entryDeleted = self.TokenEntry.DeleteEntry(self.NewEntry.id)
        if entryDeleted:
            self.logi.appendMsg('Document Entry deleted successfully')
        else:
            self.logi.appendMsg('FAIL - Could not delete the document entry')
            self.status = False 
        
        if testStatus==False:
            self.practitest.post(Practi_TestSet_ID, '1853','1')
            self.logi.reportTest('fail')
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1853','0')
            self.logi.reportTest('pass')
            assert True
#===============================================================================
    pytest.main(args=['test_1853_PDF_Slides_Conversion.py','-s'])
#===============================================================================
