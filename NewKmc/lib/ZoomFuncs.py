'''
Created on 05/08/2019

@author: moran.cohen
'''




import time
# TODO: check if builtins is in use


from selenium.webdriver.common.action_chains import ActionChains

import DOM
import KmcBasicFuncs
import MySelenium

False


class ZoomFuncs:
    
    
    def __init__(self, webdrvr, logi):
        
        self.Wd = webdrvr
        self.logi = logi
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        
        
        
    # Function that  Login to ZOOM site
    def invokeZOOMLogin(self, webdrvr, Wdobj, url, user, pwd):
        
        try: 
            webdrvr.get(url)
            webdrvr.implicitly_wait(10)
            time.sleep(3)
            rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_LOGIN_USER)
            if rc == False:
                return False
            #Wdobj.valToTextbox(webdrvr, DOM.ZOOM_LOGIN_USER, user)
            webdrvr.find_element_by_name("email").send_keys(user)
            time.sleep(1)
            #Wdobj.valToTextbox(webdrvr, DOM.ZOOM_LOGIN_PASS, pwd)
            webdrvr.find_element_by_name("password").send_keys(pwd)
            
            
            rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_LOGIN_SUBMIT)
            if rc == False:
                rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_LOGIN_SUBMIT2)
                if rc == False:
                    return False
                else:
                    webdrvr.find_element_by_xpath(DOM.ZOOM_LOGIN_SUBMIT2).click()
                    
            else:
                webdrvr.find_element_by_xpath(DOM.ZOOM_LOGIN_SUBMIT).click()
                
            return True
    
        except Exception as exp:
            print(exp)
            return False
        
         
    # Function that create zoom meeting
    def CreateZoomMeeting(self, webdrvr, meetingDuration):
        
        try: 
            # Click on Zoom recording button
            time.sleep(10) 
            self.logi.appendMsg('Going to click on Zoom recording')
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_RECORD, "Zoom recording button", 10)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Zoom recording button")
                return False
            webdrvr.find_element_by_xpath(DOM.ZOOM_RECORD).click()
            time.sleep(meetingDuration)
            self.logi.appendMsg('Going to click on Stop Recording on ZOOM meeting')
            webdrvr.find_element_by_xpath(DOM.ZOOM_STOP_RECORDING).click()
            # Dialog approve end meeting
            self.logi.appendMsg('Dialog:Going to click on Yes')
            webdrvr.find_element_by_xpath(DOM.ZOOM_DIALOG_YES).click()
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_LEAVE_MEETING, "Leave Meeting button", 10)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Leave Meeting button")
                return False
            # Click on Leave meeting
            self.logi.appendMsg('Going to click on Leave Meeting')
            webdrvr.find_element_by_xpath(DOM.ZOOM_LEAVE_MEETING).click()
            time.sleep(4) 
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_DIALOG_END_MEETING, "End Meeting button", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement End Meeting button")
                return False
            #click on End Meeting
            self.logi.appendMsg('Dialog:Going to click on End Meeting')
            webdrvr.find_element_by_xpath(DOM.ZOOM_DIALOG_END_MEETING).click()
            #Close zoom site window
            webdrvr.quit()
            
            
            return True
    
        except Exception as exp:
            print(exp)
            return False
      
        
    # Function that create zoom meeting from Zoom site
    # meetingDuration - seconds
    def CreateMeetingFromZoomSite(self, webdrvr, Wdobj, url, user, pwd, meetingDuration=2, sipUrl=None):
        
        try:           
            time.sleep(6)    
            self.logi.appendMsg('Going to click on host a meeting link')
            rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_DROPDOWN_HOSTMEETING)
            if rc == False:
                return False
            
            webdrvr.find_element_by_xpath(DOM.ZOOM_DROPDOWN_HOSTMEETING).click()
            time.sleep(1)
            webdrvr.find_element_by_xpath(DOM.ZOOM_DROPDOWN_HOSTMEETING).click()
            self.logi.appendMsg('Going to click on With Video On link')
            webdrvr.find_element_by_xpath(DOM.ZOOM_WITH_VIDEO_ON).click()
                    
            time.sleep(5)    
                    
            # Solve the Alert issue but taken the meetingId # https://zoom.us/s/834785663?status=success
            currentUrl = webdrvr.current_url
            resultStrMeetingId = currentUrl.split("zoom.us/s/")
            MeetingId = resultStrMeetingId[1]           
            webdrvr.quit()                     
            # Open ZOOM web application
            webdrvr = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            zoomUrlMeeting = "https://us02web.zoom.us/wc/" + str(MeetingId) + "/start"
            
            # Login to ZOOM web site
            self.logi.appendMsg('Going to login to Zoom site')
            rc = self.invokeZOOMLogin(webdrvr, Wdobj, zoomUrlMeeting , user, pwd)
            if rc == False:
                self.logi.appendMsg("FAIL - Invoke ZOOM Login to web site" )
                return False
            webdrvr.implicitly_wait(10)     
         
            # Handle "Do you want to end it and start this meeting?" alert
            time.sleep(4) 
            self.logi.appendMsg('Going to verify Start this Meeting button')
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_START_THIS_MEETING_BTN, "Start this Meeting", 15)
            if rc != False:
                self.logi.appendMsg("INFO - ALERT - Do you want to end it and start this meeting?")
                webdrvr.find_element_by_xpath(DOM.ZOOM_START_THIS_MEETING_BTN).click()            
            if sipUrl == None:
                #Create Zoom meeting 
                self.logi.appendMsg('Going to Create Zoom meeting.')
                rc = self.CreateZoomMeeting(webdrvr, meetingDuration)
            else:
                #Create Zoom meeting 
                self.logi.appendMsg('Going to Create Zoom meeting with SIP.')
                rc = self.CreateSIPWithZOOMMeeting(webdrvr, meetingDuration,sipUrl) 
            if rc == False:
                self.logi.appendMsg("FAIL - CreateZoomMeeting")
                return False


            return True,MeetingId
    
        except Exception as exp:
            print(exp)
            return False          
        

    # Function that create zoom with SIP meeting
    def CreateSIPWithZOOMMeeting(self, webdrvr, meetingDuration,sipUrl):
        
        try: 
            # Click on Zoom recording button
            time.sleep(8) 
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_MANAGE_PARTICIPANTS_BTN, "SIP MANAGE PARTICIPANT button", 15)    
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement SIP MANAGE PARTICIPANT button")
                return False
            
            rc = self.BasicFuncs.wait_visible(webdrvr, DOM.SIP_MANAGE_PARTICIPANTS_BTN, 15)
            if rc == False:
                self.logi.appendMsg("FAIL - wait_visible SIP MANAGE PARTICIPANT button")
                return False
            time.sleep(8) 
            self.logi.appendMsg('Going to click on SIP MANAGE PARTICIPANT button.')
            webdrvr.find_element_by_xpath(DOM.SIP_MANAGE_PARTICIPANTS_BTN).click()
            time.sleep(8)             
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_INVITE_BTN, "SIP Invite button", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement SIP Invite button")
                return False
            self.logi.appendMsg('Going to click on SIP Invite button.')
            webdrvr.find_element_by_xpath(DOM.SIP_INVITE_BTN).click()
            time.sleep(5) 
            
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_INVITE_ROOM_SYSTEM, "SIP Invite room tab", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement SIP Invite room tab")
                return False
            rc = self.BasicFuncs.wait_visible(webdrvr, DOM.SIP_INVITE_ROOM_SYSTEM, 15)
            if rc == False:
                self.logi.appendMsg("FAIL - wait_visible SIP Invite room system")
                return False                  
            self.logi.appendMsg('Going to click on Invite a Room System tab.')
            time.sleep(5) 
            webdrvr.find_element_by_xpath(DOM.SIP_INVITE_ROOM_SYSTEM).click()
            time.sleep(5)  
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_INVITE_CALL_OUT, "SIP Invite call out tab", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement SIP Invite call out tab")
                return False            
            rc = self.BasicFuncs.wait_visible(webdrvr, DOM.SIP_INVITE_CALL_OUT, 10)
            if rc == False:
                self.logi.appendMsg("FAIL - wait_visible SIP Invite call out tab")
                return False
            time.sleep(4) 
            self.logi.appendMsg('Going to click on Call Out tab.')
            webdrvr.find_element_by_xpath(DOM.SIP_INVITE_CALL_OUT).click()
            
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_RB, "SIP radio button", 10)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement SIP radio button")
                return False
            self.logi.appendMsg('Going to click on SIP radio button.')
            webdrvr.find_element_by_xpath(DOM.SIP_RB).click()
            
            self.logi.appendMsg('Going to set IP address.')
            webdrvr.find_element_by_xpath(DOM.SIP_IP_ADDRESS).send_keys(sipUrl)
            count = 0
            while webdrvr.find_element_by_xpath(DOM.SIP_CALL_BTN).get_attribute("class").find("disabled") != -1:
                time.sleep(1)
                count = count + 1
                if count == 5:#timeout
                    break 
                
            self.logi.appendMsg('Going to click on Call button.')
            webdrvr.find_element_by_xpath(DOM.SIP_CALL_BTN).click()
            time.sleep(2)
            ###### LOGIC - SIP call status after pressing on the call button ############## 
            rcRing = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_RING_STATUS, "SIP Ring status", 10)
            count = 0
            while rcRing == False:#while there is NO "Ring" status wait and check again 
                time.sleep(1)
                count = count + 1
                rcRing = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_RING_STATUS, "SIP Ring status", 10)
                if count == 3:#timeout
                    break        
            rcFailed = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_FAILD_STATUS, "SIP Failed status", 10)
            count = 0
            while rcFailed != False:#while there is NO "Failed" status wait and check again 
                time.sleep(1)
                count = count + 1
                rcFailed = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.SIP_FAILD_STATUS, "SIP Failed status", 10)
                if count == 3:#timeout
                    break 
            # Sum result of call status    
            if rcFailed != False: # If return failed ->Test failed 
                self.logi.appendMsg("FAIL - Verify SIP Failed status.")
                return False
            else: # IF No failed text but also No Ring status 
                if rcRing == False: 
                    self.logi.appendMsg("INFO - Verify SIP Ring status. - No Ring and NO Failed status")
                else:
                    self.logi.appendMsg("PASS - Verify SIP Ring status.")
            
            self.logi.appendMsg('Going to click on Invite close button.')
            webdrvr.find_element_by_xpath(DOM.SIP_INVAITE_CLOSE_BTN).click()
            time.sleep(2) 
            # Duration
            time.sleep(meetingDuration)   
            
            #Close zoom site window
            webdrvr.quit()
            
            return True
    
        except Exception as exp:
            print(exp)
            return False
        
        
        
    # Function that create zoom with SIP meeting
    def LeaveMeetingSIPZOOMMeeting(self, webdrvr, Wdobj, MeetingId,user,pwd):
        
        try:
    
            # Open ZOOM web application
            webdrvr = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            zoomUrlMeeting = "https://zoom.us/wc/" + MeetingId + "/start"
            # Login to ZOOM web site
            self.logi.appendMsg('Going to login to Zoom site. ' + zoomUrlMeeting)
            rc = self.invokeZOOMLogin(webdrvr, Wdobj, zoomUrlMeeting , user, pwd)
            if rc == False:
                self.logi.appendMsg("FAIL - Invoke ZOOM Login to web site" )
                return False
            time.sleep(18) 
            
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_LEAVE_MEETING, "Leave Meeting button", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Leave Meeting button")
                return False           
            rc = self.BasicFuncs.wait_visible(webdrvr, DOM.ZOOM_LEAVE_MEETING, 15)
            if rc == False:
                self.logi.appendMsg("FAIL - wait_visible Leave Meeting button")
                return False
            time.sleep(20)  
            
            # Click on Leave meeting
            self.logi.appendMsg('Going to click on Leave Meeting button')
            webdrvr.find_element_by_xpath(DOM.ZOOM_LEAVE_MEETING).click()
            time.sleep(15) 
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_DIALOG_END_MEETING, "Dialog End Meeting button", 15)
            if rc == False:
                rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_DIALOG_LEAVE_MEETING, "Dialog leave Meeting button", 15)
                if rc == False:
                    self.logi.appendMsg("FAIL - verifyElement leave Meeting button")
                    return False
                else:
                    time.sleep(5) 
                    self.logi.appendMsg('Going to click close on Dialog Leave Meeting')
                    webdrvr.find_element_by_xpath(DOM.ZOOM_DIALOG_CLOSE).click()
                    time.sleep(5)
                    self.logi.appendMsg('Going to click again on Leave Meeting button')
                    webdrvr.find_element_by_xpath(DOM.ZOOM_LEAVE_MEETING).click()
                    time.sleep(5)
                    rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_DIALOG_END_MEETING, "Dialog End Meeting button", 15)
                    if rc == False:
                        self.logi.appendMsg('Dialog:Going to click again on Dialog leave Meeting')
                        webdrvr.find_element_by_xpath(DOM.ZOOM_DIALOG_LEAVE_MEETING).click()
                        time.sleep(5)
                    else:
                        # Click on End Meeting
                        self.logi.appendMsg('Dialog:Going to click on end Meeting')
                        webdrvr.find_element_by_xpath(DOM.ZOOM_DIALOG_END_MEETING).click()
                        time.sleep(5) 
                            
            else:
                # Click on End Meeting
                self.logi.appendMsg('Dialog:Going to click on end Meeting')
                webdrvr.find_element_by_xpath(DOM.ZOOM_DIALOG_END_MEETING).click()
                time.sleep(5)
            
                
            time.sleep(6) 
            # Close zoom site window
            webdrvr.quit()
            
            
            return True
    
        except Exception as exp:
            print(exp)
            return False    
        
        
        
    # Function that Authrize registration ZOOM page
    def AuthorizeZOOMPage(self, webdrvr, authrize=True):
        
        try: 
            webdrvr.implicitly_wait(10)
            time.sleep(2) 
            rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_REGISTRATION_AUTHORIZE)
            if rc == False:
                return False
            if authrize == True:
                webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_AUTHORIZE).click()
            else:
                webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_DECLINE).click()
            
            return True
    
        except Exception as exp:
            print(exp)
            return False  
        
    # Function that set KMC Partner Registration
    def SetPartnerZOOMRegistration(self, webdrvr,partnerName,partnerPwd,partnerID):
        
        try: 
            webdrvr.implicitly_wait(10)
            rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_REGISTRATION_PARTNER_NAME)
            if rc == False:
                return False
            
            webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTNER_NAME).send_keys(partnerName)
            webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTNER_PWD).send_keys(partnerPwd)
            webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTNER_ID).send_keys(partnerID)
            
            
            webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_LOGIN_BTN).click()
            
            return True
    
        except Exception as exp:
            print(exp)
            return False          
        
    # Function that update ZOOM Registration Page.
    # Parameters:
    # enableRecordingUpload createUserIfNotExist enableWebinarUpload - None/True
    # defaultUserId, zoomCategory, zoomWebinarCategory, zoomUserPostfix - String.
    # participantHandler option values - None/AddasCoPublishers/AddasCoViewers/IgnoreParticipants.
    # userMatchingHandler - None/DoNotModify/AddPostfix/RemovePostfix
    def UpdateZOOMRegistrationPage(self, webdrvr,enableRecordingUpload=None,defaultUserId=None,zoomCategory=None,zoomWebinarCategory=None,createUserIfNotExist=None,enableWebinarUpload=None,participantHandler=None,userMatchingHandler=None,zoomUserPostfix=None):
        
        try:
            TestStatus = True 
            webdrvr.implicitly_wait(10)
            rc = self.BasicFuncs.wait_element(webdrvr, DOM.ZOOM_REGISTRATION_ENABLE_RECORDINGUPLOAD)
            if rc == False:
                return False
                
            if defaultUserId != None:
                self.logi.appendMsg("INFO - Going to set defaultUserId = " + defaultUserId)
                self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_DEFAULT_USERID).clear() 
                webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_DEFAULT_USERID).send_keys(defaultUserId)               
            if zoomCategory != None:
                self.logi.appendMsg("INFO - Going to set zoomCategory = " + zoomCategory)
                self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_CATEOGRY).clear() 
                webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_CATEOGRY).send_keys(zoomCategory)            
            if zoomWebinarCategory != None:
                self.logi.appendMsg("INFO - Going to set zoomWebinarCategory = " + zoomWebinarCategory) 
                self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_WEBINAR_CATEOGRY).clear()   
                webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_WEBINAR_CATEOGRY).send_keys(zoomWebinarCategory)
                
            #Check default value enableRecordingUpload - should be none - unchecked radio button.
            State_enableRecordingUpload = str(webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ENABLE_RECORDINGUPLOAD).get_attribute("checked"))
            State_enableRecordingUpload = State_enableRecordingUpload.lower()
            if State_enableRecordingUpload != "none":
                self.logi.appendMsg("FAIL - Default State enableRecordingUpload. Actual State_enableRecordingUpload = " + State_enableRecordingUpload + " , Expected State_enableRecordingUpload = none(unchecked)")
                TestStatus = False     
            # Update enableRecordingUpload
            if enableRecordingUpload != None:
                self.logi.appendMsg("INFO - Going to set enableRecordingUpload = " + str(enableRecordingUpload))
                
                if (enableRecordingUpload == True and State_enableRecordingUpload == "none") or (enableRecordingUpload == False and State_enableRecordingUpload == "true"):
                        element = webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ENABLE_RECORDINGUPLOAD)
                        actions = ActionChains(webdrvr)
                        actions.double_click(element).perform()
                        
            #Check default value createUserIfNotExist - should be true - checked radio button.
            State_createUserIfNotExist = str(webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ENABLE_CREATE_USERIDIFNOTEXIST).get_attribute("checked"))
            State_createUserIfNotExist = State_createUserIfNotExist.lower()
            if State_createUserIfNotExist != "true":
                self.logi.appendMsg("FAIL - Default State createUserIfNotExist. Actual State_createUserIfNotExist = " + State_createUserIfNotExist + " , Expected State_createUserIfNotExist = true(checked)")
                TestStatus = False        
            # Update createUserIfNotExist             
            if createUserIfNotExist != None:
                self.logi.appendMsg("INFO - Going to set createUserIfNotExist = " + str(createUserIfNotExist))
                if (enableRecordingUpload == True and State_createUserIfNotExist == "none") or (createUserIfNotExist == False and State_createUserIfNotExist == "true"):
                        element = webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ENABLE_CREATE_USERIDIFNOTEXIST)
                        actions = ActionChains(webdrvr)
                        actions.double_click(element).perform()
                        
            #Check default value enableWebinarUpload - should be none - unchecked radio button.
            State_enableWebinarUpload = str(webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ENABLE_RECORDINGWEBINARUPLOAD).get_attribute("checked"))
            State_enableWebinarUpload = State_enableWebinarUpload.lower()
            if State_enableWebinarUpload != "none":
                self.logi.appendMsg("FAIL - Default State State_enableWebinarUpload. Actual State_enableWebinarUpload = " + State_enableWebinarUpload + " , Expected State_enableWebinarUpload = none(unchecked)")
                TestStatus = False
            # Update enableWebinarUpload                        
            if enableWebinarUpload != None:
                self.logi.appendMsg("INFO - Going to set enableWebinarUpload = " + str(enableWebinarUpload))
                if (enableWebinarUpload == True and State_enableWebinarUpload == "none") or (enableWebinarUpload == False and State_enableWebinarUpload == "true"):
                        element = webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ENABLE_RECORDINGWEBINARUPLOAD)
                        actions = ActionChains(webdrvr)
                        actions.double_click(element).perform()                        
            
            # Check default values of participantHandler             
            rc = [None, None, None] 
            for i in range(0,3):
                rc[i] = str(self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTICIPANT_HANDLER.replace("TEXTTOREPLACE",str(i))).get_attribute("checked"))
                rc[i] = rc[i].lower()
            if rc[0] != "true":
                self.logi.appendMsg("FAIL - Default participantHandler. Actual Add as Co publishers = " + str(rc[0]) + " , Expected Add as Co publishers = TRUE ")
                TestStatus = False
            if rc[1] != "none":
                self.logi.appendMsg("FAIL - Default participantHandler. Actual Add as Add as Co viewers = " + str(rc[0]) + " , Expected Add as Co viewers = None ")
                TestStatus = False
            if rc[2] != "none":    
                self.logi.appendMsg("FAIL - Default participantHandler. Actual Add as Ignore participants = " + str(rc[0]) + " , Expected Ignore participants = None ")
                TestStatus = False
            # Update radio button participantHandler option values(AddasCoPublishers/AddasCoViewers/IgnoreParticipants)     
            if participantHandler != None: 
                self.logi.appendMsg("INFO - Going to set participantHandler = " + str(participantHandler))                       
                if participantHandler == "AddasCoPublishers":
                    element = self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTICIPANT_HANDLER.replace("TEXTTOREPLACE","0"))
                    actions = ActionChains(webdrvr)
                    actions.double_click(element).perform()  
                if participantHandler == "AddasCoViewers":
                    element = self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTICIPANT_HANDLER.replace("TEXTTOREPLACE","1"))
                    actions = ActionChains(webdrvr)
                    actions.double_click(element).perform()  
                if participantHandler == "IgnoreParticipants":
                    element = self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_PARTICIPANT_HANDLER.replace("TEXTTOREPLACE","2"))
                    actions = ActionChains(webdrvr)
                    actions.double_click(element).perform()  
            
            rc = [None, None, None]        
            # Check radio button default values of userMatchingHandler
            for i in range(0,3):
                rc[i] = str(self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_USERMATCHING_HANDLER.replace("TEXTTOREPLACE",str(i))).get_attribute("checked"))
                rc[i] = rc[i].lower()
            if rc[0] != "true":
                self.logi.appendMsg("FAIL - Default userMatchingHandler. Actual Do not modify = " + str(rc[0]) + " , Expected Do not modify = TRUE ")
                TestStatus = False
            if rc[1] != "none":
                self.logi.appendMsg("FAIL - Default userMatchingHandler. Actual Add postfix = " + str(rc[0]) + " , Expected Add postfix = None ")
                TestStatus = False
            if rc[2] != "none":    
                self.logi.appendMsg("FAIL - Default userMatchingHandler. Actual Remove postfix = " + str(rc[0]) + " , Expected Remove postfix = None ")
                TestStatus = False
            # Update userMatchingHandler option values(DoNotModify/AddPostfix/RemovePostfix)     
            if userMatchingHandler != None: 
                self.logi.appendMsg("INFO - Going to set userMatchingHandler = " + str(userMatchingHandler))                       
                if userMatchingHandler == "DoNotModify":
                    element = self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_USERMATCHING_HANDLER.replace("TEXTTOREPLACE","0"))
                    actions = ActionChains(webdrvr)
                    actions.double_click(element).perform()  
                if userMatchingHandler == "AddPostfix":
                    element = self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_USERMATCHING_HANDLER.replace("TEXTTOREPLACE","1"))
                    actions = ActionChains(webdrvr)
                    actions.double_click(element).perform()  
                if userMatchingHandler == "RemovePostfix":
                    element = self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_USERMATCHING_HANDLER.replace("TEXTTOREPLACE","2"))
                    actions = ActionChains(webdrvr)
                    actions.double_click(element).perform()                  
       
            if zoomUserPostfix != None:
                self.logi.appendMsg("INFO - Going to set zoomUserPostfix = " + zoomUserPostfix)
                self.Wd.find_element_by_xpath(DOM.ZOOM_REGISTRATION_USER_POSTFIX).clear()      
                webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_USER_POSTFIX).send_keys(zoomUserPostfix)
                    
            # Test status according to default registration values
            if TestStatus == False:
                self.logi.appendMsg("FAIL - Wrong Default ZOOM registration values ")
                return False
            #Press on the submit button
            self.logi.appendMsg("INFO - Going to click on the Submit button")
            webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_SUBMIT_BTN).click()
            
            time.sleep(2)
            rc = self.BasicFuncs.verifyElement(webdrvr, self.logi,DOM.ZOOM_REGISTRATION_ALERT_SUCCESS, "Zoom Registration success alert", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Zoom Registration success alert")
                return False
            # Check the registration page status alert - SUCCESS or FAIL
            self.logi.appendMsg('INFO - Going to Verify alert status of registration page')
            if str(webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ALERT_SUCCESS).get_attribute("style")) == "" and str(webdrvr.find_element_by_xpath(DOM.ZOOM_REGISTRATION_ALERT_FAIL).get_attribute("style")) == "display: none;":
                self.logi.appendMsg("PASS - Alert status of registration page - Saved Successfully.")
            else:
                self.logi.appendMsg("FAIL - Alert status of registration page - Data was Not Saved.")
                return False
            
            return True
    
        except Exception as exp:
            print(exp)
            return False     
        
        
    def FullZOOMRegistration(self, webdrvr,Wdobj,ZOOMRegistraionPage,ZoomUser,ZoomPwd,user,pwd,PublisherID,enableRecordingUpload=None,defaultUserId=None,zoomCategory=None,zoomWebinarCategory=None,createUserIfNotExist=None,enableWebinarUpload=None,participantHandler=None,userMatchingHandler=None,zoomUserPostfix=None):
        
        try:
            
            # Login to ZOOM web site
            self.logi.appendMsg('Going to open ZOOM RegistraionPage and login to zoom site')
            rc = self.invokeZOOMLogin(webdrvr, Wdobj, ZOOMRegistraionPage, ZoomUser, ZoomPwd)
            if rc == False:
                self.logi.appendMsg("FAIL - Invoke ZOOM Login to web site" )
                #testStatus = False
                return False
                
            self.Wd.maximize_window()
            time.sleep(2)       
            self.logi.appendMsg('Going to perform ZOOM Authrize')
            rc = self.AuthorizeZOOMPage(webdrvr)
            if rc == False:
                self.logi.appendMsg("INFO - NO ZOOM Authorize page" )
                           
            time.sleep(2) 
            self.logi.appendMsg("Going to login to ZOOM Partner Registration Page. user = " + user + " , pwd = " + pwd + " , PublisherID = " + PublisherID )    
            rc = self.SetPartnerZOOMRegistration(webdrvr, user, pwd, PublisherID)
            if rc == False:
                self.logi.appendMsg("FAIL - ZOOM Partner Registration Page. user = " + user + " , pwd = " + pwd + " , PublisherID = " + PublisherID )
                #testStatus = False
                return False
            time.sleep(2) 
            self.logi.appendMsg("Going to Update Registration Page" )
            # participantHandler option values - None/AddasCoPublishers/AddasCoViewers/IgnoreParticipants.
            # Enabled recording
            rc = self.UpdateZOOMRegistrationPage(webdrvr, True)
            if rc == False:
                self.logi.appendMsg("FAIL - Update Registration Page. user = " + user + " , pwd = " + pwd + " , PublisherID = " + PublisherID )
                return False
            
            time.sleep(2)
            webdrvr.quit()
                       
            return True
    
        except Exception as exp:
            print(exp)
            return False    
                 