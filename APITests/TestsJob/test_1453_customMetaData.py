#from pip._vendor.requests.packages.urllib3.util.connection import select
import os
import sys
import time
import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','NewKmc', 'lib'))
sys.path.insert(1,pth)
import CustomMetaData
import ClienSession
import Config
import Entry
import XmlParser
import reporter2
import Transcoding
import tearDownclass
import Practitest

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree

#======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
#======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = False
    Practi_TestSet_ID = '2160'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
    if str(isProd) == 'true':
        isProd = True
    else:
        isProd = False

class TestClass:
    
    #===========================================================================
    # @pytest.fixture(scope='module',params=[pytest.mark.t('testing'),pytest.mark.p('production')])
    # def initfix(self,request):
    #     pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
    #     if request.param=='testing':
    #         print 'TESTING ENV'
    #         return Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
    #     else:
    #         print 'PRODUCTION ENV'
    #         return Config.ConfigFile(os.path.join(pth, 'ProdParams.ini')) 
    #===========================================================================
    status = True
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        self.practitest = Practitest.practitest('4586','APITests')
        
        # retrieve environment parameters from ini file
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
                
        if isProd == True:
            inifile             = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            print(' from Prod')
            print('PRODUCTION ENVIRONMENT')
        else:
            inifile             = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            print('from Testing')
            print('TESTING ENVIRONMENT')
        
        self.PublisherID        = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL          = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret         = inifile.RetIniVal('Environment', 'UserSecret')  
        self.FileName           = inifile.RetIniVal('Entry', 'File')
        self.transcodingPrtofile= inifile.RetIniVal('Environment', 'transcodingProfile')
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.FileName           = os.path.join(pth,self.FileName)
        self.testTeardownclass  = tearDownclass.teardownclass()
        
        
        self.logi = reporter2.Reporter2('API tests')
        self.logi.initMsg('Test 1453 Custom Metadata Test')
        
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession('creator@kaltura.com')
        self.logi.appendMsg('creating new entry')

        # creating new entry
        myentry = Entry.Entry(self.client,"MetaDataTest","MetaDataTest desc","metadatatest tag","admintag","metadatatest category1",0,open(self.FileName,'rb+'))
        #myentry = Entry.Entry(self.client, "MetaDataTest", "MetaDataTest desc", "metadatatest tag", "admintag","metadatatest category1", 0, self.FileName)
        self.entry = myentry.AddEntry(creatorId='creator@kaltura.com',ownerId='not@kaltura.com')
        self.logi.appendMsg('the new entry id is:' + self.entry.id)
        self.logi.appendMsg('upload file to the entry')
        Tokken = myentry.UploadFileToNewEntry(self.entry)
        finit = myentry.WaitForEntryReady(self.entry.id,60)
        if not finit:
            self.logi.reportTest('fail')
            assert False
        
        self.logi.appendMsg('Finished upload file to entry')
        self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(self.entry.id) + '\')')
        
        # Adding Metadata profile       
        self.logi.appendMsg('Adding Metadata profile')
        self.MData = CustomMetaData.CustomMetaData(self.client)
        self.MdataProfile = self.MData.AddCustomMetaDataProfile(None)
        if type(self.MdataProfile) is str:  # happens when profile metadata already exist then take it 
            if self.MdataProfile =='exist':
                self.MdataProfile = self.MData.GetMetaDataProfileListBYname(0,'autotest').objects[0]
                self.logi.appendMsg('MetaData profile already exist- deleting it and then recreate it')
                self.MData.DeleteMetaDataProfile(self.MdataProfile.id)
                self.logi.appendMsg('Add the profile metadata again')
                self.MdataProfile = self.MData.AddCustomMetaDataProfile(None)
            elif isinstance(self.MdataProfile,bool):
                self.logi.appendMsg('Fail to add metadata profile')
                self.logi.reportTest('fail')
                self.testTeardownclass.exeTear()
                assert False
        
        self.testTeardownclass.addTearCommand(self.MData,'DeleteMetaDataProfile(' + str(self.MdataProfile.id) + ')')
        self.logi.appendMsg('The new Metadata profile ID ' + str(self.MdataProfile.id))
        
        self.logi.appendMsg('Adding custom data to new metadata fields: auto1=automation to delete  auto2=automation to stay')
        self.MData.AddCustomMetaData(self.MdataProfile.id, 0, self.entry.id,'<metadata><Auto1>automation to delete</Auto1><Auto3>automation to stay</Auto3></metadata>')
        
        # Adding transcoding code with default entry = the entry loaded
        self.logi.appendMsg('Adding Transcoding with default entry=' + str(self.entry.id))
        self.logi.appendMsg('Create transcoding profile name MetaDataautotest')
        Trans = Transcoding.Transcoding(self.client,'MetaDataautotest')
        transProfileId = Trans.getTranscodingProfileIDByName('MetaDataautotest')
        if transProfileId != None:
            print('profile exist deleting it and recreate')
            Trans.deleteTranscodingProfile(transProfileId)
            time.sleep(3)
        profile = Trans.addTranscodingProfile(0, self.transcodingPrtofile, self.entry.id)
        if isinstance(profile,bool):
            self.logi.appendMsg('Could not create the new transcoding profile')
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
       
        time.sleep(2)
        self.testTeardownclass.addTearCommand(Trans,'deleteTranscodingProfile('+str(profile.id) + ')')
        time.sleep(3)
        
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client2 = mySess.OpenSession('subi@kaltura.com')
        self.logi.appendMsg('creating new entry with users subi@kaltura.com')
        
        # upload new entry with the above transcoding, i.e the above entry as template
        self.logi.appendMsg('upload another entry with the above transcoding, i.e the above entry as template')
        myentry = Entry.Entry(self.client2,"MetaDataTest2","MetaDataTest2 desc",None,None,None,0,open(self.FileName,'rb+'),conversionProfileId=profile.id)
        self.entry2 = myentry.AddEntry() 
        self.logi.appendMsg('the new entry id is:' + self.entry2.id)
        self.logi.appendMsg('upload file to the entry')
        Tokken = myentry.UploadFileToNewEntry(self.entry2)
        finit = myentry.WaitForEntryReady(self.entry2.id,60)
        if not finit:
            self.logi.reportTest('fail')
            assert False
        
        self.logi.appendMsg('Finished upload file to entry')
        self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(self.entry2.id) + '\')')
        
    #===========================================================================
    # !!!!!Removed on 20.10.21 as not relevant anymore due to changed metadata requirements!!!!!!
    # Custom Meta data test - remove metadata field, verify the field and its value
    # removed.
    #===========================================================================
    # @pytest.mark.ready
    # def test_CustomMetadataRemove(self):
    #
    #     print('##################################')
    #     print('TEST NAME: CUSTOM METADATA REMOVE')
    #     print('##################################')
    #     self.logi.appendMsg('CustomMetadata delete metadata field test')
    #
    #     CustomDataXml = self.MData.GetMetadataListByEntryID(self.entry.id)
    #     CustomData = XmlParser.XmlParser(None,CustomDataXml.objects[0].xml)
    #     fieldVal = CustomData.retCustomDataFieldVal()
    #
    #     self.logi.appendMsg('The field that is going to be removed value=' + fieldVal)
    #     self.logi.appendMsg('Updating metadata profile- removing field name: auto1')
    #     dataProfile = self.MData.UpdateCustomMetadataProfile(self.MdataProfile.id)
    #
    #     CustomDataXml = self.MData.GetMetadataListByEntryID(self.entry.id)
    #     CustomData = XmlParser.XmlParser(None,CustomDataXml.objects[0].xml)
    #
    #     fieldVal1 = CustomData.retCustomDataFieldVal()
    #     fieldVal2 = CustomData.retCustomDataFieldVal('Auto3')
    #
    #
    #     if fieldVal1==None and fieldVal2=='automation to stay':
    #         self.logi.reportTest('pass')
    #         self.practitest.post(Practi_TestSet_ID, '1353','0')
    #         assert True
    #     else:
    #         self.logi.appendMsg('The value of the removed field still exist and it is- ' + fieldVal1)
    #         self.logi.reportTest('fail')
    #         self.status = False
    #         self.practitest.post(Practi_TestSet_ID, '1353','1')
    #         print('THE TEST FAILED')
    #         assert False

    #===========================================================================
    # TemplateEntryCustomData  test -
    #
    # upload entry with different owner and creator,
    # create transcoding profile with default entry uploaded before
    # upload new entry with the Transcoding
    # verify oner was not copied and other meta data did  
    #===========================================================================
    def test_1453_customMetaData(self):
        
        print('#########################')
        print('TEST NAME: TEMPLATE ENTRY')
        print('#########################')
        self.logi.appendMsg('Template Entry CustomData')
        self.logi.appendMsg('Going to verify all data beside entry owner copied from entry: ' + self.entry.id + ' to entry: ' + self.entry2.id)
        
        myentry = Entry.Entry(self.client,"MetaDataTest","MetaDataTest desc","MetaDataTest tag","Admintag","MetaDataTest category1",0,open(self.FileName,'r+'))
        entryxml = myentry.getEntry(self.entry2.id)
        if isinstance(entryxml,bool):
           self.logi.appendMsg('Could not retrieve entry data for entry: ' +  self.entry2.id + 'exit test')
           self.logi.reportTest('fail')
           self.status = False
           assert False
        
        testFaile = False   
        tag = str(entryxml.tags)
        if tag == '':
            tag = 'empty'
        admintag = str(entryxml.adminTags)
        if admintag == '':
            admintag = 'empty'
        category = str(entryxml.categories) 
        if category == '':
            category = 'empty'   
        creator = str(entryxml.creatorId)
        if creator == '':
            creator = 'empty'
        owner = str(entryxml.userId)
        if owner == '':
            owner = 'empty'
        
        if tag.strip() != 'metadatatest tag':
            self.logi.appendMsg('the tag of the entry should have been - metadatatest tag and it is- ' + tag)
            testFaile = True
        if admintag.strip() != 'admintag':
            self.logi.appendMsg('the admin tag of the entry should have been - admintag and it is- ' + admintag)
            testFaile = True
        if category.strip() != 'metadatatest category1':
            self.logi.appendMsg('the category of the entry should have been - metadatatest category1 and it is- ' + category)
            testFaile = True
        if creator.strip() != 'subi@kaltura.com':
            self.logi.appendMsg('the creator of the entry should have been - subi@kaltura.com and it is- ' + creator)
            testFaile = True
        # owner should be same as creator and not as it is in the template entry
        if owner.strip() != 'subi@kaltura.com':
            self.logi.appendMsg('the owner of the entry should have been - subi@kaltura.com  as the owner of the template entry, and it is- ' + owner)
            testFaile = True  
        
        
        if testFaile:
            self.status = False
        else:
            self.logi.appendMsg('all metadata copied as expected from the template entry')
            
            
        # check custom metadata copied as expected
        CustomDataXml = self.MData.GetMetadataListByEntryID(self.entry.id)
        CustomData = XmlParser.XmlParser(None,CustomDataXml.objects[0].xml)
        fieldVal2 = CustomData.retCustomDataFieldVal('Auto3')
        if fieldVal2=='automation to stay':
            self.logi.appendMsg('custom meta data values copied from template entry as expected')
        else:
            self.logi.appendMsg('custom meta data values NOT copied from template entry as expected field Auto3 value should have been: automation to stay, and it is: '+ str(fieldVal2))
            testFaile = True
            
        if testFaile:
            self.logi.reportTest('fail')
            self.status = False
            self.practitest.post(Practi_TestSet_ID, '1453','1')
            assert False
        else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '1453','0')
            assert True
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        if self.status == True:
            print('#########') 
            print('tear down')
            print('#########') 
            self.testTeardownclass.exeTear()
    if Run_locally:
        pytest.main(args=['test_1453_customMetaData.py', '-s'])
        