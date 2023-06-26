'''
@desc : this lib contains distribution function including login to media prep TVM

@author: moran.cohen
'''

import subprocess
import time

import DOM
import KmcBasicFuncs
import MySelenium


class distributefuncs:

    def __init__(self, webdrvr, logi):

        self.Wd = webdrvr
        self.logi = logi
        self.KmcBasicFuncs = KmcBasicFuncs.basicFuncs()
        self.Wdobj = MySelenium.seleniumWebDrive()

    # This function checks if Facebook page is in English and switches to it if the page was initially in Hebrew
    def switchToEngish(self, webdrvr):
        # See if page isn't in English
        if not webdrvr.find_elements_by_xpath(DOM.FACEBOOK_LOGIN):
            webdrvr.find_element_by_xpath(DOM.FACEBOOK_ENGLISH).click()
            time.sleep(2)
        if webdrvr.find_elements_by_xpath(DOM.FACEBOOK_LOGIN):
            return True
        else:
            return False

    # this function select distribution profile - send one of the profiles name
    def Distribution_Selection(self, DistributionProfileSelectionText):
        try:
            self.Wd.find_element_by_xpath(
                DOM.DISTRIBUTION_CHECKBOX_SELECTION.replace("TEXTTOREPLACE", DistributionProfileSelectionText)).click()
            return True
        except:
            return False

    # this function waits till the distribution status changes to distributed
    # Optional sending TimeOut -  Default TimeOut 5min for youtube distribution 20min
    def Distribution_WaitingForReady(self, TimeOut=300):
        self.Wd.execute_script("window.scrollTo(0, 0)")  # Jumping to top to make sure refresh button is in focus
        time.sleep(0.5)
        bStatusReady = False
        itimeout = TimeOut
        startTime = time.time()
        while not bStatusReady:
            rc = self.KmcBasicFuncs.verifyElement(self.Wd, self.logi, DOM.DISTRIBUTION_REFRESH_STATUS,
                                                  "Distribution refresh status", 15)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement Distribution refresh status")
                return False

            self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_REFRESH_STATUS).click()
            time.sleep(3)
            try:
                rc = self.KmcBasicFuncs.verifyElement(self.Wd, self.logi, DOM.DISTRIBUTION_STATUS,
                                                      "Distribution status", 15)
                if rc == False:
                    self.logi.appendMsg("FAIL - verifyElement Distribution status")
                    return False
                lineText = self.Wd.find_element_by_xpath(DOM.DISTRIBUTION_STATUS).text
                if lineText.find("Distributed") >= 0:
                    bStatusReady = True
                elif lineText.find("Distribution Failed") >= 0:
                    return False, lineText
                else:
                    time.sleep(1)
            except:
                return False, "NoDistirbution"

            if startTime + itimeout < time.time():
                return False, lineText

        return True, lineText

    # This function generates unique video entry from slide show of random number of images and uploads it to external site accessible both from testing and production
    # Current implementation designed to run on Windows 10 VM, folder c:\distribution_files\
    def DistributionCreateMovie(self):

        process = subprocess.Popen('c:\distribution_files\generate_youtube.sh', shell=True, stdout=subprocess.PIPE)
        process.wait()
        print(process.returncode)
        # =======================================================================
        # rc = subprocess.call(['/home/ubuntu/Be-Automation/distribution_files/generate_youtube.sh'])
        # print str(rc)
        # =======================================================================

    # this function login to TVM    
    def invokeTVMLogin(self, webdrvr, Wdobj, logi, url, user, pwd):

        try:
            webdrvr.get(url)
            webdrvr.implicitly_wait(10)

            time.sleep(3)
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.TVM_LOGIN_USER, "User login field", 10)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement user login field")
                return False

            Wdobj.valToTextbox(webdrvr, DOM.TVM_LOGIN_USER, user)
            time.sleep(1)
            Wdobj.valToTextbox(webdrvr, DOM.TVM_LOGIN_PASS, pwd)
            webdrvr.find_element_by_xpath(DOM.TVM_LOGIN).click()

        except Exception as exp:
            print(exp)
            return False

        return True

        # this function verify TVM Files Number by entryName

    def verifyTVMFilesNumber(self, webdrvr, logi, entryName, expectedFilesNumber):

        try:

            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.TVM_KALTURA_MUS_PRIMARY,
                                                  "Kaltura Mus - Primary link", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Kaltura Mus - Primary link")
                return False
            logi.appendMsg("INFO - Going to click on Kaltura Mus - Primary -> Inner groups.")
            childlCell = webdrvr.find_element_by_xpath(DOM.TVM_KALTURA_MUS_PRIMARY)
            parent = childlCell.find_element_by_xpath('..')
            parent.find_element_by_xpath(DOM.TVM_INNER_GROUPS).click()
            logi.appendMsg("INFO - Click on Kaltura Mus - Primary -> Inner groups.")
            time.sleep(5)
            logi.appendMsg("INFO - Going to click on Kaltura Mus Regular -> Browse as.")
            childlCell = webdrvr.find_element_by_xpath(DOM.TVM_KALTURA_MUS_PRIMARY_PAGE2)
            parent = childlCell.find_element_by_xpath('..')
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.TVM_BROWSE_AS, "Browser as link", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Browser as link")
                return False

            try:
                logi.appendMsg("INFO - Click on Kaltura Mus Regular -> Browse as.")
                webdrvr.set_page_load_timeout(30)
                parent.find_element_by_xpath(DOM.TVM_BROWSE_AS).click()
            except Exception as exp:
                if exp == "timeout":
                    pass
            time.sleep(5)

            try:
                logi.appendMsg("INFO - Going to search to media local category.")
                webdrvr.get("https://tvm-preprod.ott.kaltura.com/adm_media.aspx")
                webdrvr.implicitly_wait(10)
            except Exception as exp:
                if exp == "timeout":
                    pass
            time.sleep(5)
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.TVM_ENTRY_NAME.replace("TEXTTOREPLACE", entryName),
                                                  "EntryName on TVM", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement entryName on TVM")
                return False
            self.logi.appendMsg("INFO - Going to verify entry name in the list.")
            childlCell = webdrvr.find_element_by_xpath(DOM.TVM_ENTRY_NAME.replace("TEXTTOREPLACE", entryName))
            self.logi.appendMsg("INFO - Going to verify file number.")
            parent = childlCell.find_element_by_xpath('..')
            actualParentFilesNumber = parent.find_element_by_xpath(DOM.TVM_FILES)
            actualFilesNumber = str(actualParentFilesNumber.find_element_by_xpath('..').text)
            expectedFilesNumberDefault = "Files (" + str(expectedFilesNumber) + ")"
            if actualFilesNumber == expectedFilesNumberDefault:
                logi.appendMsg(
                    "PASS - File number actualFilesNumber = " + actualFilesNumber + " , expectedFilesNumberDefault = " + expectedFilesNumberDefault)
            else:
                logi.appendMsg(
                    "FAIL - File number actualFilesNumber = " + actualFilesNumber + " , expectedFilesNumberDefault = " + expectedFilesNumberDefault)
                testStatus = False
                return False

        except Exception as e:
            print(e)
            logi.appendMsg("FAIL - Verify TVM file.")
            return False

        return True

    # This function login to FaceBook account    
    def invokeFacebookLogin(self, webdrvr, Wdobj, logi, url, user, pwd):

        try:
            webdrvr.get(url)
            webdrvr.implicitly_wait(10)

            time.sleep(3)
            language = webdrvr.find_element_by_xpath('//*[@id="pageFooter"]/ul/li[1]').text  # Checking page's language
            if language == 'English (US)':
                loginUser = DOM.FACEBOOK_LOGIN_USER_US
                loginButton = DOM.FACEBOOK_LOGIN_US
            if language == 'English (UK)':
                loginUser = DOM.FACEBOOK_LOGIN_USER_UK
                loginButton = DOM.FACEBOOK_LOGIN_UK
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, loginUser, "User login field", 10)
            if rc == False:
                self.logi.appendMsg("FAIL - verifyElement user login field")
                return False
            # English = self.switchToEngish(webdrvr)
            # if English == False:
            #     self.logi.appendMsg("FAIL - Facebook page isn't in English, can't proceed")
            #     return False

            Wdobj.valToTextbox(webdrvr, loginUser, user)
            time.sleep(1)
            Wdobj.valToTextbox(webdrvr, DOM.FACEBOOK_LOGIN_PASS, pwd)
            webdrvr.find_element_by_xpath(loginButton).click()

        except Exception as exp:
            print(exp)
            return False

        return True

    # This function verify Facebook file description 
    def verifyFacebookFile(self, webdrvr, logi, entryDescription):

        try:
            for i in range(1, 4):
                rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi,
                                                      DOM.FACEBOOK_FILE_DESCRIPTION.replace("TEXTTOREPLACE",
                                                                                            entryDescription),
                                                      "Entry description on Facebook", 10)
                if rc == False and i == 4:
                    return False
                elif rc == False and i < 4:
                    webdrvr.refresh()
                    time.sleep(4)
                else:
                    return True

        except Exception as e:
            print(e)
            logi.appendMsg("FAIL - verify Facebook File.")
            return False

        return True

        # This function login to FaceBook authentication site

    def invokeFacebookAuthenticationLogin(self, webdrvr, Wdobj, logi, url, user, pwd):

        try:
            webdrvr.get(url)
            webdrvr.implicitly_wait(10)

            time.sleep(3)
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.FACEBOOK_AUTHENTICATION_LOGIN_USER,
                                                  "User login field", 10)
            if rc == False:
                self.logi.appendMsg("FAIL - FacebookAuthentication - verifyElement user login field")
                return False
            Wdobj.valToTextbox(webdrvr, DOM.FACEBOOK_AUTHENTICATION_LOGIN_USER, user)
            time.sleep(1)
            Wdobj.valToTextbox(webdrvr, DOM.FACEBOOK_AUTHENTICATION_LOGIN_PASS, pwd)
            webdrvr.find_element_by_xpath(DOM.FACEBOOK_AUTHENTICATION_LOGIN_BTN).click()

        except Exception as exp:
            print(exp)
            return False

        return True

    # This function verify Facebook Authentication text
    def verifyFacebookAuthentication(self, webdrvr, Wdobj, logi, Facebook_user, Facebook_pwd):

        try:
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.FACEBOOK_AUTHENTICATION_PROCEED,
                                                  "Proceed to Facebook for authorization", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Proceed to Facebook for authorization link")
                return False
            logi.appendMsg("INFO - Going to click on the Authentication proceed.")
            webdrvr.find_element_by_xpath(DOM.FACEBOOK_AUTHENTICATION_PROCEED).click()
            # Login to facebook account
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.FACEBOOK_AUTHENTICATION_LOGIN_USER,
                                                  "Facebook login user", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Facebook login user")
                return False
            logi.appendMsg("INFO - Going to set facebook login details.")
            Wdobj.valToTextbox(webdrvr, DOM.FACEBOOK_AUTHENTICATION_SITE_LOGIN_USER, Facebook_user)
            time.sleep(1)
            Wdobj.valToTextbox(webdrvr, DOM.FACEBOOK_AUTHENTICATION_SITE_LOGIN_PASS, Facebook_pwd)
            logi.appendMsg("INFO - Going to click on Login button.")
            webdrvr.find_element_by_xpath(DOM.FACEBOOK_AUTHENTICATION_SITE_LOGIN).click()
            time.sleep(10)
            logi.appendMsg("INFO - Going to click on continue as button.")
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.FACEBOOK_AUTHENTICATION_CONTINUE_AS_BTN,
                                                  "Facebook authentication - Continue as button", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Facebook authentication - Continue as button")
                return False
            else:
                webdrvr.find_element_by_xpath(DOM.FACEBOOK_AUTHENTICATION_CONTINUE_AS_BTN).click()
            time.sleep(2)

            logi.appendMsg("INFO - Going to verify Facebook authentication result.")
            rc = self.KmcBasicFuncs.verifyElement(webdrvr, logi, DOM.FACEBOOK_AUTHENTICATION_RESULT,
                                                  "Facebook authentication result ", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Facebook authentication result.")
                return False
            else:
                logi.appendMsg("PASS - verifyElement Facebook authentication result.")

            # Get Access token generated successfully
            resultAuthenticaion = str(webdrvr.find_element_by_xpath(DOM.FACEBOOK_AUTHENTICATION_RESULT).text)
            ExpectedResult = "Access token generated successfully"
            if resultAuthenticaion != ExpectedResult:
                logi.appendMsg(
                    "FAIL - Facebook authentication result.resultAuthenticaion = " + resultAuthenticaion + " , ExpectedResult = " + ExpectedResult)
                return False
            else:
                logi.appendMsg("PASS - Facebook authentication result - Access token generated successfully")

        except Exception as e:
            print(e)
            logi.appendMsg("FAIL - verify verifyFacebookAuthentication.")
            return False

        return True
