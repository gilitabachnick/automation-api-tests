import os
import sys
import time
# TODO: check builtins

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','NewKmc', 'lib'))
sys.path.insert(1,pth)
import ClienSession
import Config
import tearDownclass
import reporter2
import Gmail
import AdminSettings
import Entry
import Practitest


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

status = True

#===========================================================================
# Description :   Email notification test  
#
# test scenario:  create email notification for upload new entry, 
#                 
#                 create new user and set the role for him,
#                 
# verifications:  try actions that are not permitted and verify it is forbidden for the user
#
#===========================================================================

class TestClass:
    
    status = True
    
    def _searchInMessage(self, msgEmail , strEntryId, strDate=None):
        if strDate != None:
            if msgEmail.find(strDate) and msgEmail.find(strEntryId):
                return True
            else:
                return False
        else:
            if msgEmail.find(strEntryId):
                return True
            else:
                return False 
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        #isProd = False
        #isProd = True
        
        self.practitest = Practitest.practitest('4586','APITests')
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            self.inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
        else:
            self.inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
  
        self.PublisherID        = self.inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL          = self.inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret         = self.inifile.RetIniVal('Environment', 'UserSecret')  
        self.FileName           = self.inifile.RetIniVal('Entry', 'File')
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.FileName           = os.path.join(pth,self.FileName)
        self.testTeardownclass  = tearDownclass.teardownclass()
                
        self.logi = reporter2.Reporter2('API tests')
        self.logi.initMsg('test 1450 Email Templates')
        
         # create event notification only in testing env
        if isProd == False:
            self.logi.appendMsg('Going to add event notification for entry ready')
            adminKmc = AdminSettings.AdminSettings(impersonateID=self.PublisherID)
            templateExist = adminKmc.searchEventTemplateBysysName('AutoTestTemplate_sys')
            
            if not isinstance(templateExist,bool):
                self.logi.appendMsg('event notification template with sys name=AutoTestTemplate_sys exist, going to delete it and recreate it')
                adminKmc.DeleteTemplateNotification(templateExist)
            
            self.timestmp = str(time.strftime("%c"))    
            eventTemplate = adminKmc.CreateEmailTemplate('AutoTestTemplate', 'AutoTestTemplate_sys', 'AutoTestTemplate desc', self.timestmp)
            if isinstance(eventTemplate,Exception):
                self.logi.appendMsg('Fail to add event notification template')
                self.logi.appendMsg(eventTemplate)
                self.logi.reportTest('fail')
                assert False
            
            self.testTeardownclass.addTearCommand(adminKmc,'DeleteTemplateNotification('+str(eventTemplate.id) + ')')
        else: # for production
            self.timestmp = None
        
    def test_1450_EmailTemplates(self):
        
        print('#############################')
        print('TEST NAME: EVENT NOTIFICATION')
        print('#############################')
        MAXTIME = 300
         
        self.logi.appendMsg('Creating session for partner: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.inifile.RetIniVal('Environment', 'PublisherID'),self.inifile.RetIniVal('Environment', 'ServerURL'),self.inifile.RetIniVal('Environment', 'UserSecret'))
        client = mySess.OpenSession()
        
        # upload new entry with the transcoding profile just created 
        self.logi.appendMsg('Going to upload new entry...')
        # TODO: check file
        myentry = Entry.Entry(client,"EventTemplateAuto", "Event Template Automatiion test", "EventTemplate tag", "Admintag", "None", 0, open(self.FileName,'rb+'))
        entry = myentry.AddNewEntryWithFile(300)
        if isinstance(entry,bool):
            self.logi.appendMsg('Entry was not uploaded after 5 minutes')
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
        else:
            self.logi.appendMsg('Finished upload file to new entry id :' + entry.id)
        
        self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(entry.id) + '\')')
        
        
        # Check gmail got the email notification
        self.logi.appendMsg('Going to Check that a new email arrived for the new entry Ready status')
        endoftime = False
        mailArrived = False
        timepassed = 0
        # wait for email to arrive
        while not endoftime and not mailArrived:
            MailObj = Gmail.gmail()
            msgMail = MailObj.retMailboxContent()
            if not isinstance(msgMail,bool):  # case no messages in the inbox
                if self._searchInMessage(msgMail, str(entry.id), self.timestmp)== True:
                    MailObj.deleteEmail()
                    self.logi.appendMsg('The email notification arrived OK for entry id = ' + str(entry.id))
                    self.logi.reportTest('pass')
                    mailArrived = True
                
                else:
                    time.sleep(10)
                    timepassed = timepassed + 10
                    if timepassed >  MAXTIME:
                        endoftime = True
            else:
                time.sleep(10)
                timepassed = timepassed + 10
                if timepassed >  MAXTIME:
                    endoftime = True
                    
    
        if not mailArrived:
            self.logi.appendMsg('The email notification did not arrive after 5 minutes- Test Fail')
            self.practitest.post(Practi_TestSet_ID, '1450','1')
            self.logi.reportTest('fail')
            self.status = False
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1450','0')
            assert True
        
                    
    def teardown_class(self):
        if self.status == True:
            print('##########')
            print('tear down')
            print('##########')
            self.testTeardownclass.exeTear()
    if Run_locally:
        pytest.main(args=['test_1450_EmailTemplates.py', '-s'])
