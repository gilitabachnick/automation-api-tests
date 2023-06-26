################################################################
#
# This function library contain all Atomic reusable
#
# functions related to the Webex Meeting Recording
#
# date created: 3.11.19
#
# author: Ilia Vitlin
#
################################################################
import time
from selenium.webdriver.common.by import By
import WDOM

class webexFuncs:
    # Login Webex Kaltura site
    def webexLogin(self, webdrvr, wurl, wuser, wpwd):
        webdrvr.get(wurl)
        try:
            webdrvr.find_element(By.CSS_SELECTOR, WDOM.SIGNIN_BTN).click()
            webdrvr.find_element(By.ID, WDOM.EMAIL_FIELD).send_keys(wuser)
            webdrvr.find_element(By.ID, WDOM.EMAIL_SUBMIT).click()
            webdrvr.find_element(By.ID, WDOM.PASSWORD_FIELD).send_keys(wpwd)
            webdrvr.find_element(By.ID, WDOM.PASSWORD_SUBMIT).click()
            # Start meeting
            time.sleep(2)
            # Getting rid of various banners
            if len(webdrvr.find_elements_by_xpath(WDOM.SPLASH_SCREEN_OFF)) > 0:
                print('Found splash screen, skipping...')
                webdrvr.find_element_by_xpath(WDOM.SPLASH_SCREEN_OFF).click()
            else:
                print('Splash screen not found')
            if len(webdrvr.find_elements_by_xpath(WDOM.COOKIES_ACCEPT)) > 0:
                print('Accepting cookies...')
                webdrvr.find_element_by_xpath(WDOM.COOKIES_ACCEPT).click()
            else:
                print('Cookies dialog not found')
            if len(webdrvr.find_elements_by_xpath(WDOM.HELP_OK)) > 0:
                print('Skipping help message...')
                webdrvr.find_element_by_xpath(WDOM.HELP_OK).click()
            else:
                print('Help dialog not found')
            if len(webdrvr.find_elements_by_xpath(WDOM.START_MTG_BTN)) > 0:
                return True, "Login successful!"
        except Exception as Exp:
            return False, Exp

    # Initiate meeting
    def startMeeting(self, webdrvr):
        try:
            webdrvr.find_element(By.CSS_SELECTOR, WDOM.MTG_MODE_SELECT).click()
            time.sleep(2)
            webdrvr.find_element_by_xpath(WDOM.WEB_APP).click()
            time.sleep(2)
            webdrvr.find_element_by_xpath(WDOM.START_MTG_BTN).click()
            time.sleep(5)
            # Skip welcome screen
            try:
                webdrvr.switch_to.frame(3)
                SkipButton = webdrvr.find_element(By.CSS_SELECTOR, WDOM.SKIP_WELCOME)
                print("Found welcome screen, skipping...")
                SkipButton.click()
            except:
                print("Welcome screen not found")
        except:
            return False, "Meeting start fail!"
        return True, "Meeting started successfully!"

    # Start and stop recording from meeting window, gets recTime provided in seconds
    def record(self, webdrvr, recTime=40):
        # Start recording
        try:
            webdrvr.switch_to.frame("thinIframe")
            #webdrvr.find_element_by_xpath(WDOM.START_VIDEO).click()
            #time.sleep(3)
            webdrvr.find_element_by_xpath(WDOM.START_MTG).click()
            time.sleep(10)
            if not isinstance(webdrvr.find_element_by_xpath(WDOM.WHITEBOARD_POPUP), bool):
                print("Found whiteboard welcome screen, skipping...")
                webdrvr.find_element_by_xpath(WDOM.WHITEBOARD_POPUP).click()
            else:
                print("Whiteboard welcome screen not found")
            webdrvr.find_element_by_xpath(WDOM.RECORD_MENU).click()
            time.sleep(2)
            webdrvr.find_element_by_xpath(WDOM.START_RECORDING).click()
            # Wait for requested time and stop recording
            time.sleep(recTime)
            try:
                webdrvr.find_element_by_xpath(WDOM.STOP_RECORDING).click()
                time.sleep(2)
                webdrvr.find_element_by_xpath(WDOM.CONFIRM_STOP).click()
            except Exception as Exp:
                return False, Exp
        except Exception as Exp:
            return False, Exp
        return True, "Recording successful!"

    # End meeting and return to Webex Kaltura dashboard home page
    def endMeeting(self, webdrvr):
        try:
            webdrvr.find_element_by_xpath(WDOM.END_MENU).click()
            time.sleep(2)
            webdrvr.find_element_by_xpath(WDOM.END_BTN).click()
            time.sleep(2)
            webdrvr.find_element_by_xpath(WDOM.CONFIRM_END).click()
            time.sleep(5)
        except Exception as Exp:
            return False, Exp
        return True, "Meeting ended successfully!"

    # Goes to recording page and waits till the recorded meeting appears in list as done.
    # Gets timeOut(number of seconds to wait for recorded entry to appear in recordings list, default is 5 minutes (300 seconds))
    def findRecording(self, webdrvr, timeOut=900):
        i = 0
        webdrvr.find_element_by_xpath(WDOM.MEETINGS).click()
        time.sleep(2)
        webdrvr.find_element_by_xpath(WDOM.RECORDED_LIST).click()
        time.sleep(3)
        while i < timeOut:
            try:
                webdrvr.find_element_by_xpath(WDOM.GENERATING)  # Find row with "Generating..."
            except:
                try:
                    FoundEntry = webdrvr.find_element_by_xpath(WDOM.ENTRY_NAME)
                except:
                    return False, 'ERROR! No entry found'
                else:
                    EntryName = FoundEntry.text
                    # Cleaning up EntryName
                    EntryName = EntryName[:-2]
                    return True, EntryName
            else:
                i += 15
                time.sleep(15)
                webdrvr.find_element_by_xpath(WDOM.MEETINGS).click()  # Refreshing list of recorded meetings
                webdrvr.find_element_by_xpath(WDOM.RECORDED_LIST).click()
                time.sleep(3)
        else:
            return False, 'ERROR! No entry found'

    # Global function that runs all other webex functions step by step. Gets recTime (desired meeting duration to record, in seconds, default is 40)
    # and timeOut(number of seconds to wait for recorded entry to appear in recordings list, default is 5 minutes (300 seconds))
    def recordMeeting(self, webdrvr, wurl, wuser, wpwd, recTime=40, timeOut=900):
        try:
            LoginResult = webexFuncs.webexLogin(self, webdrvr, wurl, wuser, wpwd)
        except:
            return False, "Login error!"
        else:
            if LoginResult[0]:
                print((LoginResult[1]))
            else:
                return False, LoginResult[1]
        try:
            StartMeeting = webexFuncs.startMeeting(self, webdrvr)
        except:
            return False, "Start Meeting error!"
        else:
            if StartMeeting[0]:
                print((StartMeeting[1]))
            else:
                return False, StartMeeting[1]
        try:
            WebexRec = webexFuncs.record(self, webdrvr, recTime)
        except:
            return False, "Recording error!"
        else:
            if WebexRec[0]:
                print((WebexRec[1]))
            else:
                return False, WebexRec[1]
        try:
            EndMeeting = webexFuncs.endMeeting(self, webdrvr)
        except:
            return False, "End meeting error!"
        else:
            if EndMeeting[0]:
                print("Meeting ended successfully! Waiting for recording to appear...")
                RecName = webexFuncs.findRecording(self, webdrvr, timeOut)
                if not RecName[0]:
                    return False, "Record not found - timeout!"
                else:
                    print(("Found recorded Webex entry: " + RecName[1] + ". Checking if uploaded to Kaltura..."))
                    return True, RecName[1]
            else:
                return False, EndMeeting[1]
