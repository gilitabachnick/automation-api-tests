import os
import sys

import pytest
from KalturaClient.Plugins.ElasticSearch import *

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import Practitest
import Config
import reporter
import ClienSession
import MyCsv

isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')

Server_ID = os.getenv('Server_ID')

# temporary
#isProd = True
#Server_ID = 'ServerURL'
#Practi_TestSet_ID = ""
#########


#===========================================================================
# Description :   Esearch test  
#
# test scenario:  POC of e search test
#                 
# verifications:  
#
#===========================================================================

class TestClass:
    
            
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        self.practitest = Practitest.practitest()
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
            self.ServerURL = inifile.RetIniVal('Environment', Server_ID)
        else:
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        
        self.PublisherID = inifile.RetIniVal('EsearchLanguages', 'PublisherID')
        self.UserSecret =  inifile.RetIniVal('EsearchLanguages', 'UserSecret') 
        self.AdminSecret =  inifile.RetIniVal('EsearchLanguages', 'AdminSecret')
       
        self.testsetId = Practi_TestSet_ID
        self.practitestStatus = "0"
        
        #self.testTeardownclass = tearDownclass.teardownclass()
        
        # create session
        userSecret = self.AdminSecret
        sessionType = KalturaSessionType.ADMIN
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,userSecret)
        self.client = mySess.OpenSession('a@kaltura.com',sessionType,'*,disableentitlement')
        
    #===========================================================================
    # test 
    #===========================================================================
    @pytest.mark.Esearch
    def test_EsearchLanguages(self):
        
        print('#######################') 
        print('TEST NAME: EsearchLanguages')
        print('#######################')
        
        # take the number of rows to run
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        
        if isProd:
            csvObj = MyCsv.MyCsv(os.path.join(pth,'esearchLanguages.csv'))
        else:
            csvObj = MyCsv.MyCsv(os.path.join(pth,'qa_esearchLanguages.csv'))
        
        itter = csvObj.retNumOfRowsinCsv()
        
        for testNum in range(1,itter):
            if csvObj.readValFromCsv(testNum,0) == "yes": #this test should run
                testStatus = True
                
                self.logi = reporter.Reporter("ESEARCH_LANGUAGE_" + str(testNum))
                self.logi.initMsg('TEST ' + csvObj.readValFromCsv(testNum,1))
                
                expResult = csvObj.readValFromCsv(testNum,3)
                expResarr = expResult.split(";")
                if expResarr[0] == "None":
                    expResarr.remove("None")
                
                self.logi.appendMsg('Going to do a new search')
                                         
                #setup query
                paramCSV=csvObj.readValFromCsv(testNum,2)
                arrParams=paramCSV.split(";")
                searchParams = KalturaESearchEntryParams() 
                searchParams.searchOperator =  KalturaESearchEntryOperator()
                searchParams.searchOperator.operator = KalturaESearchOperatorType.AND_OP
                searchParams.searchOperator.searchItems = []
                searchParams.searchOperator.searchItems.append(KalturaESearchUnifiedItem())
                searchParams.searchOperator.searchItems[0].searchTerm = arrParams[0]
                
                if arrParams[1] == "partial" or arrParams[1] == "p":
                    searchParams.searchOperator.searchItems[0].itemType = KalturaESearchItemType.PARTIAL
                elif arrParams[1] == "start" or arrParams[1] == "s":
                    searchParams.searchOperator.searchItems[0].itemType = KalturaESearchItemType.STARTS_WITH
                else:
                    searchParams.searchOperator.searchItems[0].itemType = KalturaESearchItemType.EXACT_MATCH
                    
                # log query
                self.logi.appendMsg("Query - Unified search: " + arrParams[0] + " - " + arrParams[1])
                
                #execute request
                pager = None
                res = self.client.elasticSearch.eSearch.searchEntry(searchParams, pager)
                                
                #expected eval
                numofentries = len(res.objects)
                if len(expResarr) == numofentries:
                    self.logi.appendMsg("PASS - the number of returned entries is: " + str(numofentries) + " as expected")
                else:
                    self.logi.appendMsg("FAIL - Expected return of " + str(len(expResarr)) + " entries and actually returned: " + str(numofentries))
                    testStatus = False
                    
                actResarr = []
                for i in (res.objects):
                    actResarr.append(str(i.object.id))
                
                # verify item data are correct
                if numofentries>0 and len(expResarr)>0:
                    
                    for eID in (expResarr):
                        if eID in (actResarr):
                            self.logi.appendMsg("PASS -  the entry ID that return is: " + eID + " as expected")
                            # find out the actual place in the list
                            for j in range(0,len(actResarr)):
                                if actResarr.__getitem__(j) == eID:
                                    indInlist = j
                                    break
                        else:
                            self.logi.appendMsg("FAIL - the expected return entry ID was: " + eID + " and it actually was not returned")
                            testStatus = False
                        
                elif numofentries == 0 == len(expResarr):
                    self.logi.appendMsg("Pass - No entries found as expected")
                    
                else:
                    testStatus = False
                
                             
                if testStatus:
                    self.logi.reportTest('pass','Esearch')     
                else:
                    self.logi.reportTest('fail','Esearch')
                    self.practitestStatus = "1"
                    
        self.practitest.post(self.testsetId, '3551',self.practitestStatus)
        
    pytest.main(args=["test_EsearchLanguages.py","-s"])
    