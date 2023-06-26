import browsermobproxy
import json
import os

import browsermobproxy


class clsBrowserMobCapture:
    
    LOCAL_SETTINGS_BROWSER_PROXY = "52.17.242.149:9090"
    
    #===========================================================================
    # the class allows us to capture the HTTP traffic from the remote machine that we are running the tests on.
    # we create a browser mob proxy for the remote selenium webdriver, the server is the hub and the client is the computer with the tests. 
    # need to activate the server using "./browsermob-proxy -port 9090" in the server computer.
    # we save a HAR file in specific directory for debug, and compare the expected results with the actual results we captured     
    #===========================================================================
    
    def __init__(self,testBrowser):
            
        self.testBrowser = testBrowser
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.harPath = os.path.join(pth,str(datetime.datetime.now()) + "_" + self.testBrowser + '.har')
    
    #the function creates a new client to the proxy 'browser proxy'
    def createProxyClient(self):
        
        client = browsermobproxy.Client(self.LOCAL_SETTINGS_BROWSER_PROXY)
        
        return client
    
    #the function creates new HAR file (erase the previous if exist)
    def createNewCapture(self):
        if os.path.exists(self.harPath):
            os.remove(self.harPath)
    
    #the function saves the HAR results in file (json format)
    def saveHar(self,harFile):
        self.createNewCapture()
        har_data = json.dumps(harFile, indent=4)
        save_har = open(self.harPath, 'w')
        save_har.write(har_data)
        save_har.close()

    #the function run over the HAR file, add the relevant google analytics events to a dictionary and return it.
    #===========================================================================
    # def createHttpGoogleAnalyticsDict(self,harFile):
    #     analytics   = clsAnalytics()
    #     actualHttpEvents = [] # will contain all the events parsed
    #     for ent in harFile['log']['entries']:
    #         currEvent = ent['request']['url']
    #         if('utm.gif' in currEvent): #we ensure this is a google analytics event 
    #             currEventDic = analytics.parseHTTPGoogleLine(currEvent)
    #             if(currEventDic != -1): # we don't add the packet to the dictionary if one of the values ['utme','utmhn','utmt','utmsr','utmvp','utmdt','utmac','optval'] is missing
    #                 currEventDic['Time'] = ent['startedDateTime']
    #                 actualHttpEvents.append(currEventDic)
    #     return actualHttpEvents
    #===========================================================================
    
    #The function run over the HAR file, filters the request URL, add to dictionary and return it.
    def createFilteredRequestUrlDict(self, harFile, filterString):
        actualHttpEvents = [] # will contain all the events parsed
        for ent in harFile['log']['entries']:
            currEvent = ent['request']['url']
            if(filterString in currEvent): #Filter
                    actualHttpEvents.append(currEvent)
        return actualHttpEvents
    
    
    #the function run over the HAR file, add the relevant comscore events to a dictionary and return it.
    def createHttpComscoreDict(self,harFile):
        
        requiredParams         = ['c1','c2','c3','c4','c5','c6','c7','c8','c9','c10']
        queryStringParameters  = {} 
        
        actualHttpEvents = [] # will contain all the events parsed
        for ent in harFile['log']['entries']:
            
            if('b.scorecardresearch.com/p' in ent['request']['url']): #we ensure this is comscore event
                currEvent = ent['request']['queryString']
                for param in currEvent:
                    if (param["name"] in requiredParams):
                        queryStringParameters[param["name"]] = param["value"]
                actualHttpEvents.append(queryStringParameters)
                queryStringParameters = {}
        return actualHttpEvents   
    
    
    