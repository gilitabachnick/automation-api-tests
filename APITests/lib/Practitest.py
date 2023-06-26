import base64, datetime, json, os, shutil, time, requests, sys
from retrying import retry
import Config

#############################################################
#    This class reports practitest regarding test run
#    status.
#    post method parameters:
#    testId - the test id in practitest
#    testStatus - send 0 for pass 1 for fail
#    attachFile - if you want to attach file to the run results send the path to it
#
#############################################################

##################
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.insert(1,pth)
from integrations.static_methods import get_test_instance_from_test_set_file

'''
@CONSTANTS
'''
##################

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
PRACTITEST_API_TOKEN = inifile.RetIniVal('Practitest','PRACTITEST_API_TOKEN')
PRACTITEST_EMAIL = inifile.RetIniVal('Practitest','PRACTITEST_EMAIL')


class practitest():
    
    def __init__(self, PRACTITEST_PROJECT_ID = '1327', testsFldr='NewKmc'):
    
        self.GetInstanceURL = "https://api.practitest.com/api/v2/projects/"+ PRACTITEST_PROJECT_ID +"/instances.json"
        self.GetTestsetIdURL = "https://api.practitest.com/api/v2/projects/"+ PRACTITEST_PROJECT_ID +"/sets.json"
        self.GetTestIdURL =  "https://api.practitest.com/api/v2/projects/"+ PRACTITEST_PROJECT_ID +"/tests.json"
        self.UpdateRunURL = "https://api.practitest.com/api/v2/projects/"+ PRACTITEST_PROJECT_ID +"/runs.json"
        self.practitestProjectId = PRACTITEST_PROJECT_ID

        if testsFldr== "APITests":
            print ("********************************************** API ***************************************")
            self.TESTS_EXECUTION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'TestsToExecute'))
            self.ORIG_TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'TestsJob'))

        if testsFldr == "NewKmc":
            print("********************************************** NEWKMC ***************************************")
            self.TESTS_EXECUTION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','NewKmc', 'TestsToExecute'))
            if self.TESTS_EXECUTION_DIR.find("ReachTests")>=0:
                self.ORIG_TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc','ReachTestsJob'))
            elif self.TESTS_EXECUTION_DIR.find("SelfServe")>=0:
                self.ORIG_TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'SelfServeTests'))
            elif self.TESTS_EXECUTION_DIR.find("LeaderBoard")>=0:
                self.ORIG_TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'LeaderBoardTests'))
            else:
                self.ORIG_TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','NewKmc','Tests'))
        
        
    def post(self,testsetId, testId, testStatus, attachFile=None):
        try:
            # New method, post if test live exists in tests_to_execute.csv
            instanceId = get_test_instance_from_test_set_file(testId)
            if not instanceId:
                # get the SET system id by its display ID
                data_json = json.dumps({"display-ids":str(testsetId)})
                r= self.retryWr("get",self.GetTestsetIdURL,data_json)
                setId = r.text[:r.text.find("type")].split("\"")[5]

                # get the TEST system id by its display ID
                data_json = json.dumps({"display-ids":testId})
                r = self.retryWr("get", self.GetTestIdURL, data_json)
                tesId = r.text[:r.text.find("type")].split("\"")[5]

                # get the INSTANCE of the test id in this test set by
                data_json = json.dumps({"test-ids":tesId,"set-ids":setId})
                r = self.retryWr("get", self.GetInstanceURL, data_json)
                instanceId = r.text[:r.text.find("type")].split("\"")[5]
            try:
                # update a test run fail or pass and attach file if exist
                if attachFile is not None:
                    # upload test results with a file attachment
                    encoded_bytes = base64.b64encode(attachFile.encode("utf-8"))
                    encoded_str = str(encoded_bytes.rstrip(b"="), "utf-8")
                    data_json = json.dumps({"data": { "type": "instances", "attributes": {"instance-id": instanceId, "exit-code": testStatus}, "files": {"data": [{"filename": "log.txt", "content_encoded": encoded_str}]}}})
                else:
                    data_json = json.dumps({"data": { "type": "instances", "attributes": {"instance-id": instanceId, "exit-code": testStatus}}})
            except Exception as e:
                print(e)
                data_json = json.dumps({"data": {"type": "instances", "attributes": {"instance-id": instanceId, "exit-code": testStatus}}})

            testStatusStr = 'pass' if str(testStatus) == '0' else 'fail'
            r = self.retryWr("post", self.UpdateRunURL, data_json)
            if r.status_code == 200:
                print("PRACTITEST: Updated test: " + str(testId) + " as testStatus: '" + testStatusStr + "'")
                return True
            else:
                print("PRACTITEST: Bad response for update instances. " + r.text)
                print("PRACTITEST: FAILED to updated test: " + str(testId) + " as: " + testStatusStr + "'")

        except:
            pass
        print(("@@@@@@@@@@@@@ TEST FINISH TIME: " + str(datetime.datetime.now()) + " @@@@@@@@@@@@@@@"))




    def retryWr(self, postGet, requestURL, data_json):

        retry = True
        timesToRetry = 0
        while retry:
            try:
                if postGet=="get":
                    r = requests.get(requestURL,
                         data=data_json,
                         auth=(PRACTITEST_EMAIL, PRACTITEST_API_TOKEN),
                         headers={'Content-type': 'application/json'},
                         timeout=(5, 30))
                elif postGet == "put":
                    r = requests.put(requestURL,
                        data=data_json,
                        auth=(PRACTITEST_EMAIL, PRACTITEST_API_TOKEN),
                        headers={'Content-type': 'application/json'},
                        timeout=(5, 30))
                else:
                    r = requests.post(requestURL,
                         data=data_json,
                         auth=(PRACTITEST_EMAIL, PRACTITEST_API_TOKEN),
                         headers={'Content-type': 'application/json'},
                         timeout=(5, 30))
                if r.status_code != 200:
                    print(f'Response from PractiTest: {r.text}')
                    raise Exception("Status code is:" + str(r.status_code))
                return r
            except Exception as Exp:
                print("exception from PractiTest web request- " + str(Exp))
                timesToRetry += 1
                if timesToRetry > 5:
                    retry = False
                    print("FAIL TO REPORT PRACTITEST")
                    return False
                else:
                    time.sleep(3)

    @retry(wait_exponential_multiplier=10000, wait_exponential_max=60000,stop_max_attempt_number=7)
    def setTestSetAutomationStatusAsProcessed (self, testsetId, jobName="sanity"):
        
        if jobName=="reach":
            data = {"data": {"type": "sets", "attributes": {"custom-fields": {"---f-30327": "Processed"}}}}
        elif jobName == "leaderboard":
            data = {"data": {"type": "sets", "attributes": {"custom-fields": {"---f-135920": "Processed"}}}}
        elif jobName=="sanity":
            data = {"data": {"type": "sets", "attributes": {"custom-fields": {"---f-50308": "Processed"}}}}
        elif jobName=="selfserve":
            data = {"data": {"type": "sets", "attributes": {"custom-fields": {"---f-105928": "Processed"}}}}


        data_json = json.dumps({"display-ids":str(testsetId)})
        r = requests.get(self.GetTestsetIdURL,
            data=data_json,
            auth=(PRACTITEST_EMAIL, PRACTITEST_API_TOKEN),
            headers={'Content-type': 'application/json'},
            timeout=(5, 30))
        try:
            self.setId = str(r.content)[:str(r.content).find("type")].split("\"")[5]

        except Exception as Exp:
            print("trying again")
        
        
        practiTestSetAutomationStatusAsProcessedUrl = "https://api.practitest.com/api/v2/projects/" + str(self.practitestProjectId) + \
                                                        "/sets/" + str(self.setId) + ".json?" + \
                                                        "api_token=" + str(PRACTITEST_API_TOKEN) + \
                                                        "&developer_email=adi.miler@kaltura.com"
        
        headers = { 
            'Content-Type': 'application/json',
            'Connection':'close'
        }


        r = requests.put(practiTestSetAutomationStatusAsProcessedUrl,headers = headers, data = json.dumps(data),timeout=(5, 30))
        if (r.status_code == 200):
                print(("INFO","Session: " + str(self.setId) + " updated as processed"))
                return True
        else:
            print(("INFO","Status code: '" + str(r.status_code) + "'"))
            print(("INFO","Bad response for get sessions. " + r.text))
            return False

    @retry(wait_exponential_multiplier=10000, wait_exponential_max=60000,stop_max_attempt_number=7)
    def getPractiTestAutomationSession(self, envfieldId=43697, runonlyfail=58286):
        
        #filterId = 658612  # by Version    Automation > Pending > Host1
        filterId = os.getenv('FILTER_ID')
        practiTestGetSessionsURL = "https://api.practitest.com/api/v2/projects/" + str(self.practitestProjectId) + "/sets.json?" + \
                                    "api_token=" + str(PRACTITEST_API_TOKEN) + \
                                    "&developer_email=adi.miller@kaltura.com"  \
                                    "&filter-id=" + str(filterId)
        
       
        headers = {
            'Content-Type': 'application/json',
            'Connection':'close'
        }
        r = requests.get(practiTestGetSessionsURL, headers = headers,timeout=(5, 30))

        if (r.status_code == 200):
            dctSets = json.loads(r.text)
            env = dctSets["data"][0]["attributes"]["custom-fields"]["---f-" + str(envfieldId)]
            displayId = dctSets["data"][0]["attributes"]["display-id"]
            sessionId = dctSets["data"][0]["id"]

            print("=======  session id= " + str(sessionId) + " =============")

            try:
                dd = dctSets["data"][0]["attributes"]["custom-fields"]["---f-" + str(runonlyfail)]
                if dd == 'true' or dd == 'yes':
                    boolRunOnlyFailed = True
                else:
                    boolRunOnlyFailed = False
            except:
                dd = 'false'
                boolRunOnlyFailed = False

            print("-------------- THIS IS THE ANSWER FOR RUN ONLY FAIL 1 ------ " +dd)
            print("-------------- THIS IS THE ANSWER FOR RUN ONLY FAIL 1 ------ " + str(dd))

            print ("=============boolRunOnlyFailed= " +  str(boolRunOnlyFailed) + " ===============")
            print(('################################### THE DISLAY ID = ' + str(displayId) + ' ###########################################'))
            
            os.environ['Practi_TestSet_ID'] = str(displayId)
            if str(env).find("Testing")>=0:
                os.environ['isProd'] = 'false'
                os.popen("setx isProd false")
                os.popen("set isProd false")
            else:
                os.environ['isProd'] = 'true'
                os.popen("setx isProd true")
                os.popen("set isProd true")
       
        
            
            return sessionId, boolRunOnlyFailed

    # =============================================================================================================
    # Function that returns all instances of a specific session
    # =============================================================================================================
    @retry(wait_exponential_multiplier=10000, wait_exponential_max=60000,stop_max_attempt_number=7)
    def getPractiTestSessionInstances(self, sessionId, boolRunOnlyFailed):
        # sessionId = prSessionInfo["sessionSystemID"]
        # defaultPlatform = prSessionInfo["setPlatform"]
        # boolRunOnlyFailed = prSessionInfo["runOnlyFailed"].lower()
        sessionInstancesDct = {}
        page = 1
        testListToRun = []
        while True:
            headers = {
                'Content-Type': 'application/json',
                'Connection': 'close'
            }

            practiTestGetSessionsURL = "https://api.practitest.com/api/v2/projects/" + str(
                self.practitestProjectId) + \
                                       "/instances.json?set-ids=" + str(sessionId) + \
                                       "&developer_email=" + PRACTITEST_EMAIL + \
                                       "&page[number]=" + str(page) + \
                                       "&api_token=" + PRACTITEST_API_TOKEN


            print("======== practiTestGetSessionsURL = " + str(practiTestGetSessionsURL) + " ===============")
            # For next iteration
            page = page + 1

            r = requests.get(practiTestGetSessionsURL, headers=headers,timeout=(5, 30))
            print("getPractiTestSessionInstances--------------1")
            if (r.status_code == 200):
                dctSets = json.loads(r.text)
                if (len(dctSets["data"]) > 0):

                    for testInstance in dctSets["data"]:

                        # Run only FAILED tests:
                        if boolRunOnlyFailed:
                            if testInstance['attributes']['run-status'].lower() == 'failed':
                                print(str(testInstance['attributes']['run-status'].lower()) + " +++++++++++++++++++++++")
                                testListToRun.append(testInstance["attributes"]["test-display-id"])

                        # Run only 'No Run' test
                        else:
                            if testInstance['attributes']['run-status'].lower() == 'no run':
                                testListToRun.append(testInstance["attributes"]["test-display-id"])
                                print(("INFO - Found test with id: " + str(testInstance["attributes"]["test-display-id"]) + " with the status: " +  str(testInstance['attributes']['run-status'].lower())))
                else:
                    print(("No instances in set. " + r.text))
                    break
            else:
                print(("Status code: '" + str(r.status_code)))
                print(("Bad response for get sessions. " + r.text))
                break

        print(" this is the test in status FAILED_____________" + str(testListToRun[0]))
        return testListToRun




            #=============================================================================================================
    # Function that returns all tests sets that are located under the given filter 
    #=============================================================================================================
    def getPractiTestTestSetByFilterId(self, filterId, onlyExecuteAtNight=False):
        practiTestGetSessionsURL = "https://api.practitest.com/api/v2/projects/" + str(self.practitestProjectId) + "/sets.json?" + \
                                    "api_token=" + str(PRACTITEST_API_TOKEN) + \
                                    "&developer_email=" + str(PRACTITEST_EMAIL) + \
                                    "&filter-id=" + str(filterId)
        
        listTestSet = []    

        headers = {
            'Content-Type': 'application/json',
            'Connection':'close'
        }
        
        r = requests.get(practiTestGetSessionsURL,headers = headers,timeout=(5, 30))
        if (r.status_code == 200):
            dctSets = json.loads(r.text)
            if len(dctSets["data"]) != 0:
                for testSet in dctSets["data"]:
                    # Execute test when "Execute at Night", PractiTest TestSet field, is set to True
                    if onlyExecuteAtNight == True:
                        try:
                            #'---f-41840' = "Execute at Night"
                            if testSet['attributes']['custom-fields']['---f-54943'] == 'yes':
                                listTestSet.append(testSet)
                                print(("INFO","TestSet name: " + str(testSet['attributes']['name']) + "; ID: " + str(testSet['attributes']['display-id']) + " was added to list"))
                        # When "Execute at Night" is False        
                        except:
                            print(("INFO","TestSet name: " + str(testSet['attributes']['name']) + "; ID: " + str(testSet['attributes']['display-id']) + " was skipped"))                            
                    # Execute regardless "Execute at Night" PractiTest TestSet field
                    else:
                        listTestSet.append(testSet)
                        print(("INFO","TestSet name: " + str(testSet['attributes']['name']) + "; ID: " + str(testSet['attributes']['display-id']) + " was added to list"))                        
            else:
                print(("INFO","No Test Sets found under filter id: '" + filterId + "'"))
                return False
        else:
            print(("INFO","Status code: '" + str(r.status_code) + "'"))
            print(("INFO","Bad response for get Test Set: " + r.text))
            return False
        
        return listTestSet    
        
            
    
    
    #=============================================================================================================
    # Function that update the testsets custom fields
    # testSetList = list of testset instance id
    # EXAMPLE: customFiledsDict =  OrderedDict({'---f-30327':'Processed', '---f-38033':'yes'})
    # (Automation Status = ---f-30327
    # Automation Run Only FAILED = ---f-30327)
    #============================================================================================================= 
    def updateTestsetsCustomFields(self, testSetList, customFiledsDict):
        succ = True
        # For each Testset under cpecified filter
        for testSet in testSetList:
            # Get Testset Instance ID
            instanceId = testSet["id"]
            if self.updateInstanceCustomFields(instanceId, customFiledsDict) == False:
                succ = False
        return succ    
    
    
    #=============================================================================================================
    # Function that sets the test custom field
    # customFiledId example: "---f-38302"
    #=============================================================================================================
    def updateInstanceCustomFields(self, instanceId, customFiledsDict):
        practiTestUpdateASpecificTestsetInstanceUrl = "https://api.practitest.com/api/v2/projects/" + str(self.practitestProjectId) + \
                                                        "/sets/" + str(instanceId) + ".json?" + \
                                                        "api_token=" + str(PRACTITEST_API_TOKEN) + \
                                                        "&developer_email=" + str(PRACTITEST_EMAIL) 
        headers = { 
            'Content-Type': 'application/json',
            'Connection':'close'
        }
        data = self.createDataForTestsetMultipleCustomFileds(customFiledsDict)
        # Convert data string to variable
        data = eval(data) 
        r = requests.put(practiTestUpdateASpecificTestsetInstanceUrl,headers = headers, data = json.dumps(data),timeout=(5, 30))
        if (r.status_code == 200):
            print(("INFO","SUCCESSFULLY updated field in instance ID: '" + str(instanceId) + "'"))
            return True
        else:
            print(("INFO","Status code: '" + str(r.status_code) + "'"))
            print(("INFO","FAILED to update field in instance ID: '" + str(instanceId) + "'; Response: " + r.text))
            return False      
        
        
        
    #=============================================================================================================                
    # Creates generic data for updating multiple custom fileds in testset by sending one request
    #=============================================================================================================
    def createDataForTestsetMultipleCustomFileds(self, customFiledsDict):
        tampleteSuffix = '}}}}'
        data = '{"data": { "type": "sets", "attributes": {"custom-fields": {'
        
        for customField in customFiledsDict:
            data = data + '"' + str(customField) + '": "' + str(customFiledsDict[customField]) + '"'
            # if not last, add ',' at the end
            if customField != list(customFiledsDict.keys())[-1]:
                data = data + ','

        data = data + tampleteSuffix 
        return data

    ###################################################################################################
    # this function goes through all the tests under "Tests" folder and check which are the tests to run
    ###################################################################################################
    def copyTestsForExecution(self, testsList):

        print(("orig dir = " + self.ORIG_TESTS_DIR))
        print(("execution dir = " + self.TESTS_EXECUTION_DIR))

        print("Elements of the List:\n")
        print('\n'.join(map(str, testsList)))

        # Delete TESTS_EXECUTION_DIR folder if exists
        if os.path.exists(self.TESTS_EXECUTION_DIR) and os.path.isdir(self.TESTS_EXECUTION_DIR):
            try:
                shutil.rmtree(self.TESTS_EXECUTION_DIR)
                print(("Temp folder deleted for tests to execute: '" + str(self.TESTS_EXECUTION_DIR) + "'"))
            except Exception as exp:
                print(exp)
                print(("FAILED to delete temp folder for tests to execute: '" + str(self.ESTS_EXECUTION_DIR) + "'"))
                return False

        # Ceate the TESTS_EXECUTION_DIR
        try:
            os.makedirs(self.TESTS_EXECUTION_DIR)
            print(("Temp folder created for tests to execute: '" + str(self.TESTS_EXECUTION_DIR) + "'"))
        except Exception as exp:
            print(exp)
            print(("FAILED to create temp folder for tests to execute: '" + str(self.TESTS_EXECUTION_DIR) + "'"))
            return False

        # Go over all tests in tree under root folder ("\tests"), if test appears in the list above, then copy to temp folder
        try:
            for p, d, f in os.walk(self.ORIG_TESTS_DIR):
                for file in f:
                    if file.endswith('.py') and len(file.split('_'))>1:
                        src = os.path.abspath(os.path.join(p, file))
                        dst = os.path.abspath(os.path.join(self.TESTS_EXECUTION_DIR, file))
                        try:
                            if int(file.split('_')[1].split('.')[0]) in testsList:
                                shutil.copyfile(src, dst)
                                # Remove from list, in order save time
                                testsList.remove(int(file.split('_')[1].split('.')[0]))
                        except:
                            print("could not copy test " + str(src))
                            continue
        except Exception as Exp:
            print(Exp)
            print(("FAILED to copy temp folder for tests to execute: '" + str(self.TESTS_EXECUTION_DIR) + "'"))
            return False

        return True

        # The following function will clone test in KMC PT project and set new testset name, KMC version, BE version and Analytics version
    def cloneAutomationTestSet(self, ApiUrl, customData):
        try:
            clone_result = self.retryWr('post', ApiUrl, customData)
        except Exception as Exp:
            print(Exp)
            return False
        return clone_result.status_code, json.loads(clone_result.content)['data']['id']  # Return HTTP status and test PT id (if any)

    def getCustomFieldValue(self, projectId, fieldId):
        try:
            url = "https://api.practitest.com/api/v2/projects/" + projectId + "/custom_fields/" + fieldId + ".json"
            field_value = self.retryWr('get', url, '')
            return field_value.text
        except Exception as Exp:
            print(Exp)
            return False

    def addCustomFieldValue(self, projectId, fieldId, newValue):
        try:
            url = "https://api.practitest.com/api/v2/projects/" + projectId + "/custom_fields/" + fieldId + ".json"
            customFieldValues = json.loads(self.getCustomFieldValue(projectId, fieldId))
            possible_values = customFieldValues['data']['attributes']['possible-values']
            if isinstance(possible_values, list):  # If custom field has multiple values
                if newValue not in possible_values:
                    possible_values.append(newValue)
                    self.retryWr('put', url, json.dumps(customFieldValues))
                    return True, 'update'
                else:
                    return True, 'pass'  # No need to update field
        except Exception as Exp:
            print(Exp)
            return False
