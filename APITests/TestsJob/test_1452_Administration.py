import os
import sys
import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','NewKmc', 'lib'))
sys.path.insert(1,pth)
import ClienSession
import Config
import userRole
import tearDownclass
import reporter2
import User
import Transcoding
import uiconf
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
# Description :   Administration test  
#
# test scenario:  create user role with not much previliges
#                 create new user and set the role for him,
#                 
#                 
# verifications:  try actions that are not permitted and verify it is forbidden for the user
#
#===========================================================================

class TestClass:  
    status = True
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
            
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret =  inifile.RetIniVal('Environment', 'UserSecret') 
        self.UseruserSecret = inifile.RetIniVal('Environment', 'UseruserSecret')
        #self.testsetId = Practi_TestSet_ID
              
        self.testTeardownclass = tearDownclass.teardownclass()
                
        self.logi = reporter2.Reporter2('API Tests')
        self.logi.initMsg('Test 1452 Administration setup')
        self.logi.appendMsg('start create session for publisher: ' + str(self.PublisherID))
        
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession('a@kaltura.com')
        self.logi.appendMsg('adding new role')
        
        # Create Role with low permissions
        self.Krole = userRole.userRole(self.client)
        rc = self.Krole.retUserRoleIdByName('autoTestRole')
        if not isinstance(rc,bool):
            self.Krole.DeleteUserRole(rc)
        try:    
            newRole = self.Krole.AddUserRole('autoTestRole', 'autoTestRoleSys', 'autoTestRoleDesc', 0, 'KMC_ACCESS,KMC_READ_ONLY,BASE_USER_SESSION_PERMISSION,WIDGET_SESSION_PERMISSION,CONTENT_INGEST_BASE,CONTENT_INGEST_UPLOAD,CONTENT_INGEST_BULK_UPLOAD,CONTENT_INGEST_EXTERNAL_SEARCH')
        except Exception as Exp:
            print(Exp)
        if isinstance(newRole,bool):
            self.logi.appendMsg('Fail to add new role')
            self.logi.reportTest('fail')
            assert False
            
        self.logi.appendMsg('new role created name- autoTestRole , id: ' + str(newRole.id))
        self.testTeardownclass.addTearCommand(self.Krole,'DeleteUserRole(' + str(newRole.id) + ')')
        
        # Create new user with the above role permissions
        self.logi.appendMsg('adding new user')
        self.usrInst = User.User(self.client)
        self.firstnewUser = self.usrInst.addUser('sububu@kaltura.com', 'subuser', 'sububu@kaltura.com', 'autotest', 'user', newRole.id)
        if isinstance(self.firstnewUser,bool):
            self.logi.appendMsg('Fail to add new user')
            self.logi.reportTest('fail')
            assert False
        
        self.logi.appendMsg('new user created with the name: autotest role and id= ' + str(self.firstnewUser.id))
        self.testTeardownclass.addTearCommand(self.usrInst,'deleteUser(\'' + str(self.firstnewUser.id) + '\')')
        
    #===========================================================================
    # test permissions
    #===========================================================================
    def test_1452_Administration(self):
        
        print('#######################') 
        print('TEST NAME: PERMISSIONS')
        print('#######################')
                        
        # create session
        self.logi.appendMsg('creating session for the new user')
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession(userID='sububu@kaltura.com')
        self.Krole = userRole.userRole(self.client)
        self.usrInst = User.User(self.client)
        
        # try to add transcoding profile
        self.logi.appendMsg('trying to add transcoding profile - should be forbidden')
        Trans = Transcoding.Transcoding(self.client,'NotSupposeToSucceed')
        
        if isProd == True:
            profile = Trans.addTranscodingProfile(0, '487041', isNegative=True)
        else:
            profile = Trans.addTranscodingProfile(0, '2', isNegative=True)
        
        if isinstance(profile,Exception): 
            if str(profile.code)== 'SERVICE_FORBIDDEN':
                self.logi.appendMsg('The access to transcoding service is forbidden as expected')
            else:
                self.logi.appendMsg('FAIL - The access to transcoding service is Not forbidden as expected')
                self.status = False
        else:
            self.logi.appendMsg('FAIL - The access to transcoding service is Not forbidden as expected')
            self.status = False
        
         
        # try to add role
        self.logi.appendMsg('trying to add Role - should be forbidden')
        newRole = self.Krole.AddUserRole('autoTesttryRole', 'autoTesttryRoleSys', 'autoTesttryRoleDesc', 0, 'KMC_ACCESS,KMC_READ_ONLY,BASE_USER_SESSION_PERMISSION', isNegative=True)
        if isinstance(newRole, Exception):
            if str(newRole.code)== 'SERVICE_FORBIDDEN':
                self.logi.appendMsg('The access to Role service is forbidden as expected')
            else:
                self.logi.appendMsg('FAIL - The access to Roles service is Not forbidden as expected')
                self.status = False
        else:
            self.logi.appendMsg('FAIL - The access to Roles service is Not forbidden as expected')
            self.testTeardownclass.addTearCommand(self.Krole,'DeleteUserRole(' + str(newRole.id) + ')')
            self.status = False
            
        
        # try to add user
        self.logi.appendMsg('trying to add User - should be forbidden')
        newUser = self.usrInst.addUser('subi@kaltura.com', 'subiuser', 'subi@kaltura.com', 'autotest', 'user',isNegative=True)
        if isinstance(newUser, Exception):
            if str(newUser.code)== 'SERVICE_FORBIDDEN':
                self.logi.appendMsg('The access to Users service is forbidden as expected')
            else:
                self.logi.appendMsg('FAIL - The access to Users service is Not forbidden as expected')
                self.status = False
        else:
            self.logi.appendMsg('FAIL - The access to Users service is Not forbidden as expected')
            self.testTeardownclass.addTearCommand(self.usrInst,'deleteUser(\'' + str(newUser.id) + '\')')
            self.status = False
            
       
        #=======================================================================
        # # try to access access Control service
        # self.logi.appendMsg('trying to access access Control service - should be forbidden')
        # accControl = accessControl.accessControl(self.client)
        # accTry = accControl.getaccessControlIdBySysName('Default')
        # if isinstance(accTry, Exception):
        #     if str(accTry.code)== 'SERVICE_FORBIDDEN':
        #         self.logi.appendMsg('The access to access Control service is forbidden as expected')
        #     else:
        #         self.logi.appendMsg('FAIL - The access to access Control service is Not forbidden as expected')
        #         self.status = False
        # else:
        #     
        #     self.logi.appendMsg('FAIL - The access to access Control Users is Not forbidden as expected')
        #     self.logi.appendMsg('Due to the Failure could retrieve the id of access control - \"Default\" and it is: ' + str(accTry))
        #     self.status = False
        #=======================================================================
       
         # try to add player
        self.logi.appendMsg('trying to add player - should be forbidden')    
        player = uiconf.uiconf(self.client)
        playerTry = player.addPlayer(None,self.env, True)
        if isinstance(playerTry, Exception):
            if str(playerTry.code)== 'SERVICE_FORBIDDEN':
                self.logi.appendMsg('The access to confUI service is forbidden as expected')
            else:
                self.logi.appendMsg('The access to confUI service is Not forbidden as expected')
                self.status = False
        else:
            self.logi.appendMsg('The access to confUI Users is Not forbidden as expected')
            self.status = False
            
       
        if self.status == False:
            self.logi.reportTest('fail')
            self.practitest.post(Practi_TestSet_ID, '1452','1')
            assert False
            
        else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '1452','0')
            assert True          
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        print('#########')
        print('tear down')
        print('#########')
        if self.status == True:
            self.testTeardownclass.exeTear()
            
#===============================================================================
    pytest.main(args=['test_1452_Administration.py', '-s'])
#===============================================================================


