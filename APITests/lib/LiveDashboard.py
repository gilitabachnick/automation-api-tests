'''
Created on May 6, 2020

@author: Moran.Cohen

this lib includes reusable functions for liveDashboard tests on LIVENG 

Primary State:
case -1: return "N/A";
case 0: return "Stopped";
case 3: return "Authenticated";
case 2: return "Broadcasting";
case 1: return "Playable";
case 100: return "Suspended";
Health state(Will be change by DEV):
   case 10:
        return "Debug";
    case 20:
        return "Info";
    case 30:
        return "Warn";
    case 40:
        return "Error";
}
return `N/A ${severity}`

'''
import os
import sys
import time
import MySelenium
import datetime

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)
import DOM
import KmcBasicFuncs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

class LiveDashboard():
    
    def __init__(self,Wd, logi):
        self.Wd = Wd
        self.logi = logi
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()  
        
    # This function login to LiveDashboard
    def invokeLiveDashboardLogin(self,webdrvr,wdobj,logi,url,env='testing'):
        self.Wd = webdrvr
        self.logi = logi
        self.Wdobj = wdobj
   
        self.Wd.get(url)
        webdrvr.implicitly_wait(10)
        time.sleep(2) 
        # Searching LIVE_DASHBOARD_ALERTS_TAB - Channels tab
        #=======================================================================
        # res = self.Wdobj.Sync(self.Wd,DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE","Channels"))            
        # if isinstance(res,bool):
        #     return False
        # else:       
        #     return True
        #=======================================================================
        if env == 'prod':
            timeout = 180
            #rc = self.BasicFuncs.wait_element(self.Wd, DOM.LIVE_DASHBOARD_TAB_PROD.replace("TEXTTOREPLACE", "Channels"),timeout=timeout)
        else:
            timeout = 60
        rc = self.BasicFuncs.wait_element(self.Wd, DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE","Channels"),timeout=timeout)
        if rc == False:
            return False
        else:
            return True
    
    # Moran.cohen
    # This function navigates to selected tab     
    # Parameter:
    # NavigateTo = Channels / Investigate / Alerts / Maps 
    def navigateToLiveDashboardTabs(self,webdrvr,navigateTo = "Channels",env='testing'):
        try:
            if env == 'prod':
                timeout = 80
                #rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.LIVE_DASHBOARD_TAB_PROD.replace("TEXTTOREPLACE", navigateTo),"LiveDashboard tab - " + navigateTo, timeout)
            else:
                timeout = 30
            rc = self.BasicFuncs.verifyElement(self.Wd,self.logi,DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE",navigateTo), "LiveDashboard tab - " + navigateTo, timeout)
            if rc == False:
                 self.logi.appendMsg("FAIL - verifyElement LiveDashboard tab - " + navigateTo)
                 return False
            #if env == 'prod':
                #webdrvr.find_element_by_xpath(DOM.LIVE_DASHBOARD_TAB_PROD.replace("TEXTTOREPLACE",navigateTo)).click()
            #else:
            webdrvr.find_element_by_xpath(DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE", navigateTo)).click()
    
            time.sleep(5)
            return True
          
        except Exception as exp:
            print(exp)   
            return False

    # Moran.cohen
    # This function return tow data of liveDahsboard table by entryId
    # Return from Channels tab --> str: #3 0_ljyy9qvz N/A 3LivNG_last2704 231 Playable (qa1@qa1) N/A 0 0 Disabled (3) 1970-01-01T02:00:00+02:00        
    # Return from Alerts tab --> str: #2 Info 231 0_6udadn7n 2020-05-05T08:43:18+03:00 N/A ChannelStoppedAlert 1 Channel 0_6udadn7n has been stopped      
    def ReturnRowDataLiveDashboardByEntryId(self,webdrvr,entryId,navigateTo = "Channels", DselectFilterStoppedChanels=False,env="testing"):
        try:
            try:
                # Uncheck the show stopped chanels filter
                if DselectFilterStoppedChanels and navigateTo == "Channels":
                    #self.Wd.refresh()
                    #time.sleep(2)
                    self.Wd.find_element_by_xpath(DOM.LIVE_FILTER_STOPPED_CHANELS).click()
                    time.sleep(2)
            except Exception as exp:
                print(exp)
                pass
            RowEntryDataArr=[]       
            rc = self.BasicFuncs.verifyElement(self.Wd,self.logi,DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE",entryId), "LiveDashboard table row by entryId - " + entryId, 10)    
            if rc == False and navigateTo == "Channels" :
                self.logi.appendMsg("INFO - No Channels - verifyElement LiveDashboard table row by entryId - " + entryId)
                return False,RowEntryDataArr
            elif rc == False and navigateTo == "Alerts" :
                self.logi.appendMsg("INFO - NO Alerts - verifyElement LiveDashboard table row by entryId - " + entryId)
                return True,RowEntryDataArr #empty

            ###############Add search by entryid in filter of live dashboard
            if not (DselectFilterStoppedChanels==True and env =='prod'):#on Production with filterStopped removed we have problem in search->then don't do the search entryid filter
                self.logi.appendMsg("INFO - Going to SEARCH by entry in LiveDashboard table by entryId - " + entryId + "navigateTo = " + navigateTo)
                rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE", entryId),"LiveDashboard table row by entryId - " + entryId, 25)
                if rc == False:
                    self.logi.appendMsg("FAIL - SEARCH - No entryId on live dashboard - entryId = " + entryId + "navigateTo = " + navigateTo)
                    return False, RowEntryDataArr#empty
                else:
                    #webdrvr.find_element_by_xpath("//div[contains(@class,'MuiGrid-root')]//input[contains(@class,'MuiInputBase-input')]").send_keys(entryId)
                    webdrvr.find_element_by_xpath(DOM.LIVE_DASHBOARD_SEARCH_ENTRYID).send_keys(entryId)
                time.sleep(5)
            ################WORKING ON
            #webdrvr.find_element_by_xpath("//button[contains(@class,'MuiIconButton-root')]").click()
            #webdrvr.find_element_by_xpath("//tbody[contains(@class,'MuiTableBody-root')]//tr[contains(@class,'MuiTableRow-root')]//button[contains(@class,'MuiButtonBase-root')]//svg[contains(@class,'MuiSvgIcon-root')]").click()
            ################
            # Return row data of table according to entryId
            rowsNum = len(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE",entryId)))
            if rowsNum != 1 and navigateTo == "Channels":
                self.logi.appendMsg("FAIL - There is NO 1 entry row on Channels table.entryId =  " + entryId + ", Tab = " + navigateTo + " , Actual rowsNum = " + str(rowsNum))
                return False,RowEntryDataArr  
            if rowsNum < 1 and navigateTo == "Alerts":
                self.logi.appendMsg("INFO - NO Alerts - LiveDashboard table by entryId - " + entryId)
                return False,RowEntryDataArr  
            previousRowData = ""
            #Setup loop for Channels/Alerts tabs
            if navigateTo == "Channels":
                MaxResult=rowsNum
                start_i=0
            else:#alerts
                MaxResult=len(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ROWS))
                #start_i=1#Removed                 
            start_i=0#added
            for i in range(start_i, MaxResult):
                try:    
                    currentRowData = str(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE",entryId))[i].find_element_by_xpath('..').text)   
                    #webdrvr.find_elements_by_xpath("//td[contains(text(),'0_nprmqgos')]")[0].find_element_by_xpath('..')          
                    if currentRowData != "" and currentRowData != previousRowData:
                        # Set current rowData in array
                        RowEntryDataArr.append(currentRowData)
                        previousRowData = currentRowData 
                    if currentRowData == "" or rowsNum == i-1 or currentRowData == previousRowData :
                        timeout = 0
                        Page = 0     
                        
                        while currentRowData == "" or currentRowData != previousRowData:
                            currentRowData = str(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE",entryId))[i].find_element_by_xpath('..').text)
                            if currentRowData !="" and navigateTo == "Channels":#If it's "Channels" return just one row and break the loop - remove
                                RowEntryDataArr.append(currentRowData)
                                break
                            elif currentRowData !="" and navigateTo == "Alerts":
                                RowEntryDataArr.append(currentRowData)
                                break
    
                            if timeout == 5:#timeout
                                #timeout = timeout + 1
                                break
                            if Page==9 and currentRowData =="":
                                #Press page down on key                                           
                                body = webdrvr.find_element_by_xpath('/html/body')
                                body.click()
                                ActionChains(webdrvr).send_keys(Keys.SPACE).perform() 
                                time.sleep(1) 
                                Page = 0
                                timeout=timeout+1#add - timout for trying to get alert->End of alert page
                            else:
                                Page = Page + 1
                                
                                                
                   
                except Exception as exp:
                    #Press page down on key
                    body = webdrvr.find_element_by_xpath('/html/body')
                    body.click()
                    ##ActionChains(webdrvr).send_keys(Keys.PAGE_DOWN).perform()
                    ActionChains(webdrvr).send_keys(Keys.SPACE).perform()
                    pass       
                
                
            time.sleep(1)
            if RowEntryDataArr==[]:
                self.logi.appendMsg("INFO - NO Alerts - LiveDashboard table row by entryId - " + entryId)
            
            #Verify that we catch all the alerts by entryid
            if navigateTo == "Alerts":
                if len(RowEntryDataArr) != rowsNum:
                    self.logi.appendMsg("INFO - Different alerts catch count between start to end fuction.entryId =  " + entryId + ", Tab = " + navigateTo + " , ExpectedRowEntriesCount =" + str(rowsNum) + " , ActualRowEntriesCount= " + str(len(RowEntryDataArr)))
            
            return True,RowEntryDataArr
          
        except Exception as exp:
            print(exp)   
            return False,RowEntryDataArr


    
    
    # Moran.cohen  
    # This function return results analysis of live dashboard for each alert by entry+partner
    # PrimaryState = Broadcasting/playable/Stopped/ (case insensitivity )
    # Removed meaning live entry should be removed from channels tab(for example after stop streaming)
    # ServersStreaming=Only_Primary/Only_Backup/Both_Primary_Backup
    #def VerifyReturnRowDataLiveDashboard(self,webdrvr,entryId,PublisherID,RowData,navigateTo = "Alerts",PrimaryState="Broadcasting;playable",ServersStreaming="Only_Primary",env = "testing",errorAlertRemoved = None):
    def VerifyReturnRowDataLiveDashboard(self,webdrvr,entryId,PublisherID,RowData,navigateTo="Alerts",PrimaryState="Broadcasting;playable", ServersStreaming="Only_Primary",env="testing",errorAlertRemoved=None,Live_Cluster_Primary=None):
        try:
            flagTestStatus=True
            if env == 'testing':
                clusterName = "- 1-a.live.nvq1"
                if Live_Cluster_Primary !=None:
                    clusterName = clusterName.replace("1-a",Live_Cluster_Primary)
                timeout = 60
                #rc = self.BasicFuncs.wait_element(self.Wd, DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE", "Channels"),timeout=60)
            else:#prod
                time.sleep(8)# added
                #clusterName = "- 1-a.live.nvp1"
                clusterName = "- 1-e.live.nvp1"
                if Live_Cluster_Primary !=None:
                    clusterName = clusterName.replace("1-a",Live_Cluster_Primary)
                timeout = 120
            rc = self.BasicFuncs.wait_element(self.Wd, DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE", "Channels"),timeout)
            if rc == False:
                 return False
            rowsNum=len(RowData)
            if (navigateTo == "Alerts"):
                self.logi.appendMsg("INFO - Going to verify alerts data: entryId = " + str(entryId))
                for i in range(0, rowsNum):
                    currentRowData=str(RowData[i])                    
                    if currentRowData.find(" Error " + PublisherID)>=0:
                        self.logi.appendMsg("FAIL - entryId = " + str(entryId) + " , RowData-" + str(i) + " = " + currentRowData)
                        if currentRowData.find("AllFlavorManifestsMissingAlert")<=0 or currentRowData.find("MissingMasterManifestAlert") <=0:#bug of alert-if it doesn't exist ->fail all tests #####ADDED
                            flagTestStatus=False #will remove after fix alerts
                        if errorAlertRemoved!=None:
                            if currentRowData.find(errorAlertRemoved) >= 0:#if error alert exists -> flagTestStatus = True
                                flagTestStatus = True  # will remove after fix alerts
                    elif currentRowData.lower().find("error")>=0 and currentRowData.lower().find("info")>=0:
                        self.logi.appendMsg("INFO with Error - entryId = " + str(entryId) + " , RowData-" + str(i) + " = " + currentRowData)
                        #flagTestStatus=False #will remove after fix alerts
                    else:    
                        self.logi.appendMsg("INFO - entryId = " + str(entryId) + " , RowData-" + str(i) + " = " + currentRowData)
                        
            if (navigateTo == "Channels" and PrimaryState=="removed"):   #ADDED for removed entry from channels test  
                if rowsNum != 0:
                    self.logi.appendMsg("FAIL - Entry is NOT removed from  Channels tab - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData)
                    flagTestStatus=False
                    return False        
                
            if (navigateTo == "Channels"):
                if rowsNum !=1:#Verify that there is just one row in channels tabs for each entry
                    self.logi.appendMsg("FAIL - Entry is NOT one row in Channels tab - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData)
                    flagTestStatus=False
                    return False 
                #Verify Channel date
                flagPrimaryState=False
                i=0
                currentRowData=str(RowData[i])
                self.logi.appendMsg("INFO - Going to verify channels data: entryId = " + str(entryId))
                if PrimaryState.find(";") >=0: #Multi status options     
                    arrPrimaryState=PrimaryState.split(";")  
                    for currentState in arrPrimaryState:  
                        if ServersStreaming=="Only_Primary": #Only_Primary state - > Expected: 2930571 Playable N/A
                            if currentRowData.lower().find(PublisherID + " " + currentState.lower() + " " + clusterName + " n/a") >=0:
                                flagPrimaryState=True #One of the state were found
                                self.logi.appendMsg("PASS - Only_Primary State - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + currentState)
                                break
                        if ServersStreaming=="Only_Backup": #Only_Backup state -> Expected: 2930571 N/A Playable
                            if currentRowData.lower().find(PublisherID + " n/a " + currentState.lower()) >=0:
                                flagPrimaryState=True #One of the state were found
                                self.logi.appendMsg("PASS - Only_Backup State - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + currentState)
                                break                            
                        if ServersStreaming=="Both_Primary_Backup":
                            if currentRowData.lower().find(PublisherID + " " + currentState.lower() + " " + clusterName + " " + currentState.lower()) >=0: 
                                flagPrimaryState=True #One of the state were found
                                self.logi.appendMsg("PASS - Both_Primary_Backup State - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + currentState)
                                break            
                            
                    if flagPrimaryState==False:
                        self.logi.appendMsg("FAIL - Primary State - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + currentState)
                        flagTestStatus=False #Fail the test        
                else:#Just one status option
                    if currentRowData.lower().find(PublisherID + " " + PrimaryState.lower()) <=0:
                        self.logi.appendMsg("FAIL - Primary State - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + PrimaryState)
                        flagTestStatus=False #Fail the test
                    else:
                        self.logi.appendMsg("PASS - Primary State - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + PrimaryState)
                        
                if currentRowData.lower().find("poor")>=0 :
                    self.logi.appendMsg("FAIL - Health with poor - entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + PrimaryState) 
                    #flagTestStatus=False #will remove after fix alerts
                else:    
                    self.logi.appendMsg("PASS - CHANNEL STATE -  entryId = " + str(entryId) + " , RowData-" + str(rowsNum) + " = " + currentRowData + " , Expected_PrimaryState = " + PrimaryState)
            
            
            if flagTestStatus == False:        
                return False         
                          
            return True
          
        except Exception as exp:
            print(exp)   
            return False

    # This function verify alerts and Channels LiveDashboard
    # Flag_Transcoding(Just for kubernetes use) - Meaning the transcoding is running or NOT (false)--> avoid transcoding alert/err if needed
    def Verify_LiveDashboard(self, logi,LiveDashboardURL,entryId,PublisherID,ServerURL,UserSecret,env="testing",Flag_Transcoding=False,Live_Cluster_Primary=None,ServersStreaming="Only_Primary",First_navigateTo="Alerts"):
        try:
            Wdobj = MySelenium.seleniumWebDrive()
            Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")

            # **** Login LiveDashboard
            self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
            rc = self.invokeLiveDashboardLoginByKS(Wd, Wdobj, logi, LiveDashboardURL,PublisherID,ServerURL,UserSecret,env)
            if (rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + LiveDashboardURL)
                # Close LiveDashboard window
                try:
                    self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                    Wd.quit()
                    time.sleep(2)
                except Exception as Exp:
                    print(Exp)
                    pass
                return False
            time.sleep(4)
            if env=="prod":
                time.sleep(10)
            # LiveDashboard - Alerts tab
            navigateTo = "Alerts"
            self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo= " + First_navigateTo)
            #rc = self.navigateToLiveDashboardTabs(webdrvr=Wd, navigateTo=navigateTo, env=env)
            rc = self.navigateToLiveDashboardTabs(webdrvr=Wd, navigateTo=First_navigateTo, env=env)#update First_navigateTo instead of navigateTo
            if (rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + First_navigateTo)
            else:
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + First_navigateTo + ",  entryId: " + entryId + ", ************ENTRY")
                # Close LiveDashboard window
                try:
                    self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                    Wd.quit()
                    time.sleep(2)
                except Exception as Exp:
                    print(Exp)
                    pass
                return False

            ######################
            '''time.sleep(5)
            if env=="prod":
               time.sleep(10)'''
            # Timout for row data on Alerts tab
            locator = DOM.LIVE_DASHBOARD_ROWS
            timeout = 15
            if env == "prod":
                timeout = 55
            element = self.wait_element(Wd, locator=locator, timeout=timeout)
            if element == False:
                logi.appendMsg("INFO: Element   was NOT found; Locator by: " + locator)
                Wd.quit()
                time.sleep(2)
                return False
            time.sleep(2)
            if env=="prod":
             time.sleep(2)
            #####################
            # Return row data from Alerts
            rc, RowData = self.ReturnRowDataLiveDashboardByEntryId(Wd, entryId, navigateTo)
            rowsNum = len(RowData)
            if (rc):
                self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                rc = self.VerifyReturnRowDataLiveDashboard(Wd, entryId, PublisherID,RowData, navigateTo, env=env,Live_Cluster_Primary=Live_Cluster_Primary)
                if (rc!=True and Flag_Transcoding==True):
                    CntError = 0
                    CntError_TranscodingFailedAlert=0
                    flag_TranscodingFailedAlert = False
                    for j in range(0, len(RowData)):
                        if RowData[j].find("TranscodingFailedAlert")> 0:
                            flag_TranscodingFailedAlert = True
                            CntError_TranscodingFailedAlert = CntError_TranscodingFailedAlert+1
                        if RowData[j].find("Error") > 0:
                            CntError = +1
                    if CntError >= 1 and flag_TranscodingFailedAlert != True:  # Many Errors - Not just DuplicateInputAlert
                        self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - There are Error alerts, without TranscodingFailedAlert. entryId: " + entryId + ", ************ENTRY" )
                        # Close LiveDashboard window
                        try:
                            self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                            Wd.quit()
                            time.sleep(2)
                        except Exception as Exp:
                            print(Exp)
                            pass
                        return False
                    if CntError >= 1 and flag_TranscodingFailedAlert == True:
                        if CntError_TranscodingFailedAlert < CntError:
                            self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - TranscodingFailedAlert verification. entryId: " + entryId + ", ************ENTRY")
                            # Close LiveDashboard window
                            try:
                                self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                                Wd.quit()
                                time.sleep(2)
                            except Exception as Exp:
                                print(Exp)
                                pass
                            return False
                elif(rc!=True and Flag_Transcoding==False):
                    self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - There are Error alerts. entryId: " + entryId + ", ************ENTRY")
                    # Close LiveDashboard window
                    try:
                        self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                        Wd.quit()
                        time.sleep(2)
                    except Exception as Exp:
                        print(Exp)
                        pass
                    return False

            # ****** Livedashboard - Channels tab
            navigateTo = "Channels"
            self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo = " + navigateTo)
            rc = self.navigateToLiveDashboardTabs(Wd, navigateTo, env=env)
            if (rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
            else:
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                # Close LiveDashboard window
                try:
                    self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                    Wd.quit()
                    time.sleep(2)
                except Exception as Exp:
                    print(Exp)
                    pass
                return False


            ######################
            #Timout for row data on channel tab
            locator=DOM.LIVE_DASHBOARD_ROWS
            timeout = 10
            if env == "prod":
                timeout = 50
            element = self.wait_element(Wd, locator=locator, timeout=timeout)
            if element == False:
                logi.appendMsg("INFO: Element   was NOT found; Locator by: " + locator)
                return False
            # time.sleep(5)
            #if env=="prod":
                #time.sleep(12)
            #####################
            # Return row data from Channels
            rc, RowData = self.ReturnRowDataLiveDashboardByEntryId(Wd, entryId, navigateTo)
            rowsNum = len(RowData)
            if (rc):
                self.logi.appendMsg("INFO - Going to verify the Channels of return RowData:")
                rc = self.VerifyReturnRowDataLiveDashboard(Wd, entryId, PublisherID, RowData,navigateTo, env=env,Live_Cluster_Primary=Live_Cluster_Primary,ServersStreaming=ServersStreaming)
                if (rc):
                    self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + entryId + ", ************ENTRY")
                else:
                    self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on Channels tab livedashboard. entryId: " + entryId + ", ************ENTRY")
                    if env == 'testing':
                        # Close LiveDashboard window
                        try:
                            self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                            Wd.quit()
                            time.sleep(2)
                        except Exception as Exp:
                            print(Exp)
                            pass
                        return False
            else:
               self.logi.appendMsg("FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + entryId + ", ************ENTRY" )
               # Close LiveDashboard window
               try:
                   self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                   Wd.quit()
                   time.sleep(2)
               except Exception as Exp:
                   print(Exp)
                   pass
               return False
            time.sleep(2)
            '''if env=="prod":
                time.sleep(10)'''
            ######################
            # Timout for row data on channel tab
            locator = DOM.LIVE_DASHBOARD_ROWS
            timeout = 10
            if env == "prod":
                timeout = 50
            element = self.wait_element(Wd, locator=locator, timeout=timeout)
            if element == False:
                logi.appendMsg("INFO: Element   was NOT found; Locator by: " + locator)
                return False
            #####################
            self.logi.appendMsg("INFO - Going to verify if there are Disconnected on Channels DrillDown of entryID = " + str(entryId))
            rc, RowData = self.LiveDashboard_SearchTextOnEntryDrillDown(Wd, entryId, navigateTo, env=env)
            if (rc == True):# return disconnected stream on live dashbarod
                 self.logi.appendMsg("FAIL -Channels LiveDashboard_SearchTextOnEntryDrillDown - Found Disconnected on Entry Drilldown. entryId: " + entryId )
                 for i in range(0,len(RowData)):
                     self.logi.appendMsg("FAIL -LiveDashboard_SearchTextOnEntryDrillDown - Found Disconnected on Entry Drilldown.Details RowData =" + str(RowData[i]))
                 # Close LiveDashboard window
                 try:
                     self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                     Wd.quit()
                     time.sleep(2)
                 except Exception as Exp:
                     print(Exp)
                     pass
                 return False
            else:
                self.logi.appendMsg("PASS -Channels LiveDashboard_SearchTextOnEntryDrillDown - No Disconnected on Entry Drilldown. entryId: " + entryId + ", ************ENTRY")

            #Close LiveDashboard window
            try:
                self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                Wd.quit()
                time.sleep(2)
            except Exception as Exp:
                print(Exp)
                pass

            return True

        except Exception as exp:
            # Close LiveDashboard window
            try:
                self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                Wd.quit()
                time.sleep(2)
            except Exception as Exp:
                print(Exp)
                pass
            print(exp)
            return False



    # Moran.cohen
    # This function return result for search text("Disconnected") from Outputs liveDahsboard drilldown of entryId
    # SearchText - Set the search text for searching on Outputs section of liveDahsboard drilldown
    # filterByEntryID - Is the entryId need to be filtered(TRUE) on live dashboard or already is(FALSE - default).
    def LiveDashboard_SearchTextOnEntryDrillDown(self, webdrvr, entryId, navigateTo="Channels",DselectFilterStoppedChanels=False, env="testing",SearchText="Disconnected",filterByEntryID=False):
        try:
            if env == "prod":
                time.sleep(20)
            else:
                time.sleep(2)
            try:
                # Uncheck the show stopped chanels filter
                if DselectFilterStoppedChanels and navigateTo == "Channels":
                    # self.Wd.refresh()
                    # time.sleep(2)
                    self.Wd.find_element_by_xpath(DOM.LIVE_FILTER_STOPPED_CHANELS).click()
                    time.sleep(2)
            except Exception as exp:
                print(exp)
                pass
            RowEntryDataArr = []
            rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE", entryId),"LiveDashboard table row by entryId - " + entryId, 10)
            if rc == False and navigateTo == "Channels":
                self.logi.appendMsg("INFO - No Channels - verifyElement LiveDashboard table row by entryId - " + entryId)
                return False, RowEntryDataArr
            elif rc == False and navigateTo == "Alerts":
                self.logi.appendMsg("INFO - NO Alerts - verifyElement LiveDashboard table row by entryId - " + entryId)
                return True, RowEntryDataArr  # empty

            ###############Add search by entryid in filter of live dashboard
            time.sleep(2)
            if filterByEntryID == True:
                if not (DselectFilterStoppedChanels == True and env == 'prod'):  # on Production with filterStopped removed we have problem in search->then don't do the search entryid filter
                    self.logi.appendMsg("INFO - Going to SEARCH by entry in LiveDashboard table by entryId - " + entryId + "navigateTo = " + navigateTo)
                    rc = self.BasicFuncs.verifyElement(self.Wd, self.logi,DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE", entryId),"LiveDashboard table row by entryId - " + entryId, 25)
                    if rc == False:
                        self.logi.appendMsg("FAIL - SEARCH - No entryId on live dashboard - entryId = " + entryId + "navigateTo = " + navigateTo)
                        return False, RowEntryDataArr  # empty
                    else:
                        webdrvr.find_element_by_xpath(DOM.LIVE_DASHBOARD_SEARCH_ENTRYID).send_keys(entryId)
                    time.sleep(5)
            time.sleep(2)
            # Return row data of table according to entryId
            rowsNum = len(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRYID.replace("TEXTTOREPLACE", entryId)))
            if rowsNum != 1 and navigateTo == "Channels":
                self.logi.appendMsg("FAIL - There is NO 1 entry row on Channels table.entryId =  " + entryId + ", Tab = " + navigateTo + " , Actual rowsNum = " + str(rowsNum))
                return False, RowEntryDataArr
            if rowsNum < 1 and navigateTo == "Alerts":
                self.logi.appendMsg("INFO - NO Alerts - LiveDashboard table by entryId - " + entryId)
                return False, RowEntryDataArr
            # Open the drilldown window of the entry
            self.logi.appendMsg("INFO - Going to OPEN LiveDashboard Drilldown of entryId - " + entryId)
            webdrvr.find_element(By.CSS_SELECTOR, ".MuiTableCell-root .MuiIconButton-label > .MuiSvgIcon-root").click()
            time.sleep(4)
            if env=="prod":
                time.sleep(20)
            #RowData=len(webdrvr.find_elements_by_xpath("//table[contains(@class,'MuiTable-root')]//tr[contains(@class,'MuiTableRow-root')]//td[contains(@class,'MuiTableCell-root MuiTableCell-body')]"))
            RowData = len(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRY_DRILLDOWN_OUTPUTS_TABLE))
            IsMatch = False
            for i in range(0,RowData):
                #CurrrentValue=str(webdrvr.find_elements_by_xpath("//table[contains(@class,'MuiTable-root')]//tr[contains(@class,'MuiTableRow-root')]//td[contains(@class,'MuiTableCell-root MuiTableCell-body')]")[i].text)
                CurrrentValue = str(webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRY_DRILLDOWN_OUTPUTS_TABLE)[i].text)
                RowEntryDataArr.append(CurrrentValue)
                if CurrrentValue.find(SearchText)>-1:#Found disconnected
                    self.logi.appendMsg("FAIL - LiveDashboard_SearchTextOnEntryDrillDown  - Found Disconnected on drilldown table of entryId - " + entryId + " , CurrrentValue = " + CurrrentValue + ",CurrentDate = " + str(datetime.datetime.now()))
                    IsMatch=True
            #Close drill down window
            time.sleep(2)
            self.logi.appendMsg("INFO - Going to Close LiveDashboard Drilldown of entryId - " + entryId)
            #element =webdrvr.find_elements_by_xpath("//table[contains(@class,'MuiTable-root')]//tr[contains(@class,'MuiTableRow-root')]//td[contains(@class,'MuiTableCell-root MuiTableCell-body')]")[i]
            element = webdrvr.find_elements_by_xpath(DOM.LIVE_DASHBOARD_ENTRY_DRILLDOWN_OUTPUTS_TABLE)[i]
            actions = ActionChains(webdrvr)
            actions.double_click(element).perform()
            time.sleep(2)
            if IsMatch==True:
                self.logi.appendMsg("FAIL - LiveDashboard_SearchTextOnEntryDrillDown  - Found Disconnected on drilldown table of entryId - " + entryId + ",CurrentDate = " + str(datetime.datetime.now()))
                return True, RowEntryDataArr
            else:
                return False, RowEntryDataArr


        except Exception as exp:
            print(exp)
            return False, RowEntryDataArr

    # this function set implicitly_wait to default
    def setImplicitlyWaitToDefault(self, webdrvr):
        webdrvr.implicitly_wait(30)
    # Moran.cohen
    # This function waits for the element to appear
    def wait_element(self, webdrvr, locator, timeout=10, multipleElements=False):
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        webdrvr.implicitly_wait(0)
        while True:
            try:
                if multipleElements == True:
                    elements = webdrvr.find_element_by_xpath(locator)
                    for el in elements:
                        if el.size['width'] != 0 or el.size['height'] != 0:
                            self.setImplicitlyWaitToDefault(webdrvr)
                            return el

                    if wait_until < datetime.datetime.now():
                        self.setImplicitlyWaitToDefault(webdrvr)
                        return False
                else:
                    el = webdrvr.find_element_by_xpath(locator)
                    self.setImplicitlyWaitToDefault(webdrvr)
                    return el
            except:
                if wait_until < datetime.datetime.now():
                    self.setImplicitlyWaitToDefault(webdrvr)
                    return False
                pass

    # This function login to LiveDashboard by partner ks
    #QA env:https://dashboard-manager-1.live.nvq1.ovp.kaltura.com/dashboard/channels
    #PROD env:https://dashboard-manager-1.live.nvp1.ovp.kaltura.com/dashboard/channels
    #PROD old IP http://52.90.42.173/dashboard/channels
    #QA old IP http://34.229.47.42/dashboard/channels
    def invokeLiveDashboardLoginByKS(self, webdrvr, wdobj, logi, url,PublisherID,ServerURL,UserSecret,env='testing'):#url,BE_env,partnerId
        try:
            self.Wd = webdrvr
            self.logi = logi
            self.Wdobj = wdobj
            import ClienSession

            # create client session
            self.logi.appendMsg('INFO - start create session for partner: ' + PublisherID)
            mySess = ClienSession.clientSession(PublisherID, ServerURL, UserSecret)
            client = mySess.OpenSession()
            partner_ks = client.requestConfiguration.get('ks')#Get ks of the partner
            time.sleep(2)
            #env options
            if env == 'prod':
                self.Wd.get(url + "?access_token=Kaltura_nvp1_" + partner_ks)
            elif ServerURL.find('nvd1') >= 0 : # env == 'nvd1'
                self.Wd.get(url + "?access_token=Kaltura_nvd1_" + partner_ks)
            elif ServerURL.find('nvq2') >= 0 : # env == 'nvq2'
                self.Wd.get(url + "?access_token=Kaltura_nvq2_" + partner_ks)
            else: # env is nvq1 testing
                self.Wd.get(url + "?access_token=Kaltura_nvq1_" + partner_ks)

            #self.Wd.get(url + "?access_token=Kaltura_" + partner_ks)
            webdrvr.implicitly_wait(10)
            time.sleep(2)

            if env == 'prod':
                timeout = 180
            else:
                timeout = 60
            rc = self.BasicFuncs.wait_element(self.Wd, DOM.LIVE_DASHBOARD_TAB.replace("TEXTTOREPLACE", "Channels"),timeout=timeout)
            if rc == False:
                return False
            else:
                return True

        except Exception as exp:
            print(exp)
            return False
