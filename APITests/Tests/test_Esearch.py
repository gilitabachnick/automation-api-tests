import os
import re
import sys

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import Practitest
import Config
import reporter
import ClienSession
import MyCsv
from KalturaClient.Plugins.ElasticSearch import *

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
    
    def phpToPython(self,phpcode):
        
        arr = phpcode.split("\r\n")
        
        for i in range(0,len(arr)):
            arr[i] =  arr[i].replace("$","").replace("array()","[]").replace(";","").replace("->",".").replace("::",".")
            arr[i] =  re.sub('\[[0-9]\] = new ',".append(",arr[i])
            arr[i] = arr[i].replace("new","")
        
        #=======================================================================
        # result =  phpcode.replace("$","").replace("array()","[]").replace(";","").replace("->",".").replace("::",".")
        # result = re.sub('\[[0-9]\] = new ',".append(",result)
        #=======================================================================
        #arr = result.split("\r\n")
        
        result = ""
        for i in (arr):
            numofopen = i.count("(")
            numofclose = i.count(")")
            if numofopen > numofclose:
                result= result + "searchParams." + i + ")" + "\n"
            else:
                result= result + "searchParams." + i + "\n"
            
        result = "searchParams = KalturaESearchEntryParams() \n" + result
        print(result)
        return result
        
    
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
            
        
        self.PublisherID = inifile.RetIniVal('Esearch', 'PublisherID')
        self.UserSecret =  inifile.RetIniVal('Esearch', 'UserSecret') 
       
        self.testsetId = Practi_TestSet_ID
        #self.testTeardownclass = tearDownclass.teardownclass()
                
        # create session
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession('a@kaltura.com',2,'disableentitlement')
        self.practitestStatus = "0"
        
    #===========================================================================
    # test 
    #===========================================================================
    
    def test_Esearch(self):
        
        print('#######################') 
        print('TEST NAME: Esearch')
        print('#######################')
        
        # take the number of rows to run
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        if isProd:
            csvObj = MyCsv.MyCsv(os.path.join(pth,'esearch.csv'))
        else:
            csvObj = MyCsv.MyCsv(os.path.join(pth,'qa_esearch.csv'))
        
        itter = csvObj.retNumOfRowsinCsv()
       
        for testNum in range(1,itter):
            if csvObj.readValFromCsv(testNum,0) == "yes": #this test should run
                testStatus = True
                self.logi = reporter.Reporter("ESEARCH_" + str(testNum))
                self.logi.initMsg('TEST ' + csvObj.readValFromCsv(testNum,1))
                            
                query = csvObj.readValFromCsv(testNum,2)
                pyQuery = self.phpToPython(query)
                expResult = csvObj.readValFromCsv(testNum,3)
                expResarr = expResult.split(";")
                if expResarr[0] == "None":
                    expResarr.remove("None")
                else:
                    try:
                        expResult2 = csvObj.readValFromCsv(testNum,4)
                        if expResult2 != "":
                            expResarr2 = expResult2.split(";")
                            bmore = True
                        else:
                            bmore = False
                    except:
                        bmore = False 
                
                self.logi.appendMsg('Going to do a new search')
             
                exec(pyQuery, globals())
                pager = None
                                                
                res = self.client.elasticSearch.eSearch.searchEntry(searchParams, pager)
                
                numofentries = len(res.objects)
                if len(expResarr) == numofentries:
                    self.logi.appendMsg("PASS - the number of returned entries is: " + str(numofentries) + " as expected")
                else:
                    self.logi.appendMsg("FAIL - Expected return of " + str(len(expResarr)) + " entries and actually returned: " + str(numofentries))
                    testStatus = False
                    
                actResarr = []
                for i in (res.objects):
                    actResarr.append(str(i.object.id))
                
                i=0
                
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
                        
                       
                        if bmore:
                            # verify the number of item data retrieved is ok
                            captExpArr = expResarr2[i].split("$")
                            numofasstesId = len(res.objects[indInlist].itemsData[0].items)
                            if numofasstesId != len(captExpArr):
                                self.logi.appendMsg("Fail - the expected number of items data should have been: " + str(len(captExpArr)) + " and actually retrieved " +  str(numofasstesId) + " items data")
                                testStatus = False
                            else:
                                self.logi.appendMsg("Pass - the number of items data that found are : " + str(numofasstesId) + " as expected")
                            
                            
                            # verify the items data value are correct
                            # go through act result arr against exp result arr and check each found there - no order meaning
                            captActArr = res.objects[indInlist].itemsData[0].items
                            
                            capActtStr=[]
                            if len(captActArr)>0:
                                for capt in (captActArr):
                                    if testNum<30:
                                        capActtStr.append("line=" + str(capt.line) + ":startsAt=" + str(capt.startsAt) + ":endsAt=" + str(capt.endsAt) + ":language=" + str(capt.language) + ":captionAssetId=" + str(capt.captionAssetId))
                                    elif 30<testNum<93:
                                        if testNum == 85:
                                            capActtStr.append("xpath=" + str(capt.xpath) + ":metadataProfileId=" + str(capt.metadataProfileId) + ":valueInt=" + str(capt.valueInt))
                                        else:    
                                            capActtStr.append("xpath=" + str(capt.xpath) + ":metadataProfileId=" + str(capt.metadataProfileId) + ":valueText=" + str(capt.valueText))
                                    else:
                                        capActtStr.append("id=" + str(capt.id))
                                    
                                foundInActAndNotInExp = [capt for capt in capActtStr if not capt in captExpArr]
                                foundInActAndInExp = [capt for capt in capActtStr if capt in captExpArr]
                                foundInExpAndNotInAct = [capt for capt in captExpArr if not capt in capActtStr]  
                                
                                for j in (foundInActAndInExp):
                                    self.logi.appendMsg("Pass - find the item data : " + j + " looked for in entry ")
                                for j in (foundInActAndNotInExp):
                                    self.logi.appendMsg("Fail - the item data - " + j + " found in the entry and should not been there")
                                    testStatus = False
                                for j in (foundInExpAndNotInAct):
                                    self.logi.appendMsg("Fail - the item data - " + j + " should have been found in the entry and was not found there")
                                    testStatus = False
                             
                        i+=1
                        
                elif numofentries == 0 == len(expResarr):
                    self.logi.appendMsg("Pass - No entries found as expected")
                else:
                    testStatus = False
                             
                if testStatus:
                    self.logi.reportTest('pass','Esearch')
                else:
                    self.logi.reportTest('fail','Esearch')
                    self.practitestStatus = "1"
                    
        self.practitest.post(self.testsetId, '3548',self.practitestStatus)        
                        
    pytest.main(args=["test_Esearch.py","-s"])
    