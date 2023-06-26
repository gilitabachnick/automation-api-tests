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
        
        self.PublisherID = inifile.RetIniVal('EsearchUnified', 'PublisherID')
        self.UserSecret =  inifile.RetIniVal('EsearchUnified', 'UserSecret') 
       
        self.testsetId = Practi_TestSet_ID
        self.practitestStatus = "0"
        #self.testTeardownclass = tearDownclass.teardownclass()
                
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession('a@kaltura.com',2,'disableentitlement')
               
    #===========================================================================
    # test 
    #===========================================================================
        
    def test_EsearchUnified(self):
        
        print('#######################') 
        print('TEST NAME: EsearchUnified')
        print('#######################')
        
        # take the number of rows to run
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        
        if isProd:
            csvObj = MyCsv.MyCsv(os.path.join(pth,'esearchUnified.csv'))
        else:
            csvObj = MyCsv.MyCsv(os.path.join(pth,'qa_esearchUnified.csv'))
        
        itter = csvObj.retNumOfRowsinCsv()
        
       
        for testNum in range(1,itter):
            if csvObj.readValFromCsv(testNum,0) == "yes": #this test should run
                testStatus = True
                self.logi = reporter.Reporter("ESEARCH_UNIFIED_" + str(testNum))
                self.logi.initMsg('TEST ' + csvObj.readValFromCsv(testNum,1))
                
                expResult = csvObj.readValFromCsv(testNum,3)
                expResarr = expResult.split(";")
                expMoreItems = [False for iElem in range(3)]
                expItemResult  = ["" for iElem in range(3)]
                if expResarr[0] == "None":
                    expResarr.remove("None")
                else:
                    for testItem in range(3):
                        try:
                            expResult2 = csvObj.readValFromCsv(testNum,testItem+4)
                            if expResult2 != "":
                                expMoreItems[testItem] = True
                                expItemResult[testItem] = expResult2
                            else:
                                expMoreItems[testItem] = False
                        except:
                            expMoreItems[testItem] = False 

                self.logi.appendMsg('Going to do a new search')
                
                #prepare API query
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
                                
                pager = None
                
                # log query
                self.logi.appendMsg("Query - Unified search: " + arrParams[0] + " - " + arrParams[1])
                
                #run query
                res = self.client.elasticSearch.eSearch.searchEntry(searchParams, pager)
                
                #Evaluate entries results
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
                    indExpRes=0
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
                            
                        # Evaluation of every type of ItemData expected (caption, metadata, cue_points)
                        for testItem in range(3):
                            if expMoreItems[testItem]:
                                
                                if testItem == 0:
                                    self.logi.appendMsg("    Captions:")
                                elif testItem == 1:
                                    self.logi.appendMsg("    Metadata:")
                                else:
                                    self.logi.appendMsg("    Cue Points:")
                                
                                # Set expected content 
                                expResarr2 = expItemResult[testItem].split(";")
                                if len(expResarr)>len(expResarr2):
                                    for i in range((len(expResarr)-len(expResarr2))):
                                        expResarr2.append("")
                                captExpArr = expResarr2[indExpRes].split("$")
                                # Empty array for no-data expected
                                if len(captExpArr) == 1 and captExpArr[0] == "": 
                                    captExpArr = []
                                
                                # Concatenate all the ItemData arrays from result of the same item type
                                captActArr = []
                                for resItems in (res.objects[indInlist].itemsData):
                                    if (testItem == 0 and resItems.itemsType == "caption") or (testItem == 1 and resItems.itemsType == "metadata") or (testItem == 2 and resItems.itemsType == "cue_points"):
                                        captActArr = captActArr + resItems.items
                                numofasstesId = len(captActArr)
                                
                                # verify the number of item data retrieved is ok
                                if (numofasstesId != len(captExpArr)):
                                    self.logi.appendMsg("        Fail - the expected number of items data should have been: " + str(len(captExpArr)) + " and actually retrieved " +  str(numofasstesId) + " items data")
                                    testStatus = False
                                else:
                                    self.logi.appendMsg("        Pass - the number of items data that found are : " + str(numofasstesId) + " as expected")
                                                                
                                # verify the items data value are correct
                                # go through act result arr against exp result arr and check each found there - no order meaning
                                capActtStr=[]
                                if len(captActArr)>0:
                                    for capt in (captActArr):
                                        if testItem == 0:
                                            capActtStr.append("startsAt=" + str(capt.startsAt) + ":endsAt=" + str(capt.endsAt) + ":captionAssetId=" + str(capt.captionAssetId))
                                        elif testItem == 1:
                                            capActtStr.append("xpath=" + str(capt.xpath))
                                        else:
                                            capActtStr.append("id=" + str(capt.id))
                                        
                                    foundInActAndNotInExp = [capt for capt in capActtStr if not capt in captExpArr]
                                    foundInActAndInExp = [capt for capt in capActtStr if capt in captExpArr]
                                    foundInExpAndNotInAct = [capt for capt in captExpArr if not capt in capActtStr]  
                                    
                                    for j in (foundInActAndInExp):
                                        self.logi.appendMsg("        Pass - find the item data : " + j + " looked for in entry ")
                                    for j in (foundInActAndNotInExp):
                                        self.logi.appendMsg("        Fail - the item data - " + j + " found in the entry and should not been there")
                                        testStatus = False
                                    for j in (foundInExpAndNotInAct):
                                        self.logi.appendMsg("        Fail - the item data - " + j + " should have been found in the entry and was not found there")
                                        testStatus = False
                        indExpRes+=1
                        
                elif numofentries == 0 == len(expResarr):
                    self.logi.appendMsg("Pass - No entries found as expected")
                else:
                    testStatus = False
                             
                if testStatus:
                    self.logi.reportTest('pass','Esearch')
                   
                else:
                    self.logi.reportTest('fail','Esearch')
                    self.practitestStatus = "1"
                                        
        self.practitest.post(self.testsetId, '3552',self.practitestStatus)
    
    pytest.main(args=["test_EsearchUnified.py","-s"])
    