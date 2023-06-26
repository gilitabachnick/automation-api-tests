import os
import sys
import time

import pytest
from KalturaClient.Plugins.Core import *

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','NewKmc', 'lib'))
sys.path.insert(1,pth)

import Category
import Practitest
import Config
import tearDownclass
import reporter2
import ClienSession

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


 #===========================================================================
# Description :   Category test  
#
# test scenario:  add token
#                 upload file to token
#                 add document entry
#                 validate document converted
#                 
# verifications:  try actions that are not permitted and verify it is forbidden for the user
#
#===========================================================================

class TestClass:
    
    status = True
    status1= True
    status2= True
    status3= True
    
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
            
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret =  inifile.RetIniVal('Environment', 'UserSecret') 
       
        self.testsetId = Practi_TestSet_ID
        self.testTeardownclass = tearDownclass.teardownclass()
                
        self.logi = reporter2.Reporter2('API tests')
        self.logi.initMsg('Test Category setup')
        self.logi.appendMsg('start create session for publisher: ' + str(self.PublisherID))
        
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession('a@kaltura.com',2,'disableentitlement')
        
    #===========================================================================
    # test category
    #===========================================================================
    def test_1440_Category(self):
        
        print('#######################') 
        print('TEST NAME: CATEGORIES')
        print('#######################')
        
        self.logi.initMsg('Category test')
        
        # add new category
        self.logi.appendMsg('Going to add new category')        
        cat = Category.category(self.client)
        
        ''' Check if the category exsit and if yes delete it before test run '''
        catExistId = cat.getCategoryByName('CategoryTest')
        if not isinstance(catExistId,bool):
            cat.deleteCategory(catExistId)
            
        newCat = cat.addCategory()
        if isinstance(newCat, KalturaCategory):
            self.logi.appendMsg('new category created succesfully with the name= ' + newCat.name + ' and id= ' + str(newCat.id))
            self.testTeardownclass.addTearCommand(cat,'deleteCategory(' + str(newCat.id) + ')')
        else:
            self.logi.appendMsg('FAIL - Could not create new category')
            self.status = False
        try:    
            if self.status == False:
                self.practitest.post(Practi_TestSet_ID, '1439','1')
            else:
                self.practitest.post(Practi_TestSet_ID, '1439','0')
        except:
            print('no such pratitest ID')
        
            
        # add sub category name subCat
        if self.status != False:
            self.logi.appendMsg('Going to add new sub category name subCat')
            subcat = cat.addCategory(newCat.id, 'SubCat')
            if isinstance(subcat, KalturaCategory):
                self.logi.appendMsg('new category created succesfully with the name= ' + subcat.name + ' and id= ' + str(subcat.id))
                rc = cat.getCategory(subcat.id,True)
                if rc.parentId == newCat.id:
                    self.logi.appendMsg('new category created under it parent- ' + newCat.name + ' as it should been')
                else:
                    self.logi.appendMsg('new category created but not as sub category under the parent it should have been created- ' + newCat.name)
            else:
                self.logi.appendMsg('FAIL - Could not create new sub category')
                self.status1 = False 
        try:        
            if self.status1 == False:
                self.practitest.post(Practi_TestSet_ID, '1456','1')
            else:
                self.practitest.post(Practi_TestSet_ID, '1456','0')
        except:
            print('no such pratitest ID')
                
        # add sub sub category name subsubCat
        if self.status1 != False:
            self.logi.appendMsg('Going to add new sub sub category name subsubCat')
            subsubcat = cat.addCategory(subcat.id, 'SubSubCat')
            if isinstance(subsubcat, KalturaCategory):
                self.logi.appendMsg('new category created succesfully with the name= ' + subsubcat.name + ' and id= ' + str(subsubcat.id))
                rc = cat.getCategory(subsubcat.id,True)
                if rc.parentId == subcat.id:
                    self.logi.appendMsg('new category created under it parent- ' + subcat.name + ' as it should been')
                else:
                     self.logi.appendMsg('new category created but not as sub category under the parent it should have been created- ' + subcat.name)
            else:
                self.logi.appendMsg('FAIL - Could not create new sub SUB category')
                self.status = False 
        try:
            if self.status == False:
                self.practitest.post(Practi_TestSet_ID, '1457','1')
            else:
                self.practitest.post(Practi_TestSet_ID, '1457','0')
        except:
            print('no such pratitest ID')
                 
        
        # move category to under parent category
        if self.status != False:
            parentId = newCat.id
            self.logi.appendMsg('Going to move sub sub category to be under parent category id= ' + str(parentId))
            rc = cat.movecategory(subsubcat.id,parentId)
            movedCat = cat.getCategory(subsubcat.id)
            if movedCat.parentId == parentId:
                self.logi.appendMsg('Category succssefully moved under the parent category')
            else:
                self.logi.appendMsg('FAIL - Move the category under parent category')
                self.status2 = False 
        try:        
            if self.status2 == False:
                self.practitest.post(Practi_TestSet_ID, '1458','1')
            else:
                self.practitest.post(Practi_TestSet_ID, '1458','0')
        except:
            print('no such pratitest ID')
        
        # update category name by id  
        if self.status != False:  
            self.logi.appendMsg('Going to update category name by id to new name= updated_category')
            movedCat = cat.updateCategoryNamebyId(movedCat.id, 'updated_category')
            if movedCat.name == 'updated_category':
                self.logi.appendMsg('Category name was successfully updated')
            else:
                self.logi.appendMsg('FAIL - Move the category under parent category')
                self.status2 = False
            
       # delete category
        if self.status!=False :
            self.logi.appendMsg('Going to delete the category')
            cat.deleteCategory(movedCat.id)
            time.sleep(1)
            rc = cat.getCategory(movedCat.id,True)
            if isinstance(rc, KalturaCategory) or rc==False:
                self.logi.appendMsg('FAIL - category was not deleted')
                self.status2 = False
            else:
                self.logi.appendMsg('category was deleted successfully')
        try:
            if self.status2==False:
                self.practitest.post(Practi_TestSet_ID, '1440','1') 
            else:
                self.practitest.post(Practi_TestSet_ID, '1440','0')
        except:
            print('no such pratitest ID')   
     
        if self.status==False and self.status2==False:
            self.logi.reportTest('fail')
            assert False
        else:
            self.logi.reportTest('pass')
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
        

    pytest.main(args=['test_1440_Category.py', '-s'])