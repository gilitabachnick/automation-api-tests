import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
import myDropFolder
import ClienSession
import reporter
import Config
import tearDownclass
import Practitest


Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')


 #===========================================================================
# Description :   Drop folder test  
#
# test scenario:  validate the creation of drop folder
#                 for now with out upload file to it.
#                 Create transcoding profile name Drmautotest,
#                 get play ready access control default,
#                 upload new entry with the transcoding profile just created,
#                 get user KS,
#                 play the DRM from a player page,
#                 sniff player packates.
#                 
# verifications:  video play (QRcode)
#                 manifest and license packets retrieve OK reply
#===========================================================================
    

class TestClass:
    
    status = True
   
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.AdminSecret =  inifile.RetIniVal('Environment', 'AdminSecret')  
        self.testTeardownclass = tearDownclass.teardownclass()
        self.logi = reporter.Reporter('DropFolder')
        
        self.practitest = Practitest.practitest()
        
        
    #===========================================================================
    # CREATE DROP FOLDER TEST     
    #===========================================================================
    def test_createDropFolder(self):
        self.logi.initMsg('Create Drop Folder')
        
        print('#############################')
        print('TEST NAME: CREATE DROP FOLDER')
        print('#############################')
        
        # create -2 KS
        mySess = ClienSession.clientSession(-2, self.ServerURL,self.AdminSecret)
        self.client = mySess.OpenSession()
        
        self.logi.appendMsg('creating drop folder for partner: ' + self.PublisherID + ', folder name=autotest dropfolder, folder desc=autotest dropfolder desc, folderType=Local, folderDirectory=0, folderPth=/incoming/ella, filePolicy=ADD_NEW')
        self.drpFolder = myDropFolder.myDropFolder(self.client, self.PublisherID)
        
        self.newFolder = self.drpFolder.addDropFolder(0)
        if isinstance(self.newFolder,bool):
           self.logi.appendMsg('Failed to create new drop folder')
           self.logi.reportTest('fail')
           self.status = False
           self.practitest.post(Practi_TestSet_ID, '2358','1')
           assert False
        else:
            self.logi.appendMsg('succeed in create new drop folder')
            self.testTeardownclass.addTearCommand(self.drpFolder,'deleteDropFolder(' + str(self.newFolder.id) + ')')
            self.practitest.post(Practi_TestSet_ID, '2358','0')
         
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        
        print('#############')
        print(' Tear down')
        print('#############')
        
        if self.status == True:
            try:
                self.testTeardownclass.exeTear()
            except Exception as exep:
                print((str(exep)))
                self.logi.appendMsg('could not delete the drop folder')
                self.logi.reportTest('fail')
                assert False
           
        
        
        
        
        
        
        
        
        
        
        