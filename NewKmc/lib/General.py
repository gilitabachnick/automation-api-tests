import datetime
import unicodedata

from selenium.common.exceptions import NoSuchElementException

import DOM
import KmcBasicFuncs
import autoitWebDriver


class general:

    def __init__(self, Wd, logi, Wdobj):
        self.Wd = Wd
        self.logi = logi
        self.Wdobj = Wdobj
        self.basicFuncs = KmcBasicFuncs.basicFuncs()

        if self.Wdobj.RUN_REMOTE:
            self.autoitWebDriver = autoitWebDriver.autoitWebDrive()
            self.AWD = self.autoitWebDriver.retautoWebDriver()

    #########################################
    # Takes unicode text and returns string
    #########################################
    def convertUnicodeToStr(self, unicodeElement):
        if unicodeElement == "":
            convertedString = ""
        else:
            convertedString = unicodedata.normalize('NFKD', unicodeElement).encode('ascii', 'ignore')

        return convertedString

    # Takes text and returns boolean
    def convertStrToBool(self, text):
        try:
            if text.lower() == 'true':
                return True
            elif text.lower() == 'false':
                return False
        except:
            self.logi.appendMsg("String is not true or false")
            return None

    def convertTextToNumber(self, textToConvert):
        try:
            textToConvert = textToConvert.replace(',', '')
            return int(textToConvert)
        except ValueError:
            return float(textToConvert)

    def get_element(self, locator):
        try:
            el = self.Wd.find_element_by_xpath(locator)
            return el
        except NoSuchElementException:
            return False

    def get_child_element(self, childLocator, parentLocator):
        try:
            el = self.Wd.find_element_by_xpath(parentLocator)
            childEl = el.find_element_by_xpath(childLocator)
            return childEl
        except NoSuchElementException:
            return False
        
    def get_element_from_container(self, rContainer, childLocator):
        try:
            childEl = rContainer.find_element_by_xpath(childLocator)
            return childEl
        except NoSuchElementException:
            return False
        
    def click(self,locator):
        try:
            el = self.get_element(locator)
            if el == False:
                self.logi.appendMsg("FAIL - failed to find element")
                return False
            else:
                el.click()
        except:
            self.logi.appendMsg("FAIL - failed to click element")
            return False

    def waitForSpinnerToFinish(self, timeout = 60):
        self.Wd.implicitly_wait(0)
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() <= wait_until:
            if isinstance(self.get_element(DOM.SPINNER), bool):
                self.basicFuncs.setImplicitlyWaitToDefault(self.Wd)
                break

    def waitForLoadingToDisappear(self, timeout = 30):
        self.Wd.implicitly_wait(0)
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() <= wait_until:
            if isinstance(self.get_element(DOM.ANALYTICS_LOADING), bool):
                self.basicFuncs.setImplicitlyWaitToDefault(self.Wd)
                break
    
    
    def stripNumber(self, strNum):
        newStr = ""
        try:
            newStr = ''.join((ch if ch in '0123456789.,-' else '') for ch in strNum)
        except:
            self.logi.appendMsg("FAIL - Cannot obtain number from string")
            newStr = ""
        return newStr
    
    def stripNoNumber(self, strNum):
        newStr = ""
        try:
            newStr = ''.join((ch if ch not in '0123456789.,-' else '') for ch in strNum)
            newStr = newStr.strip()
        except:
            self.logi.appendMsg("FAIL - Cannot obtain non-numeric characters from string")
            newStr = ""
        return newStr
    
    ####################################################################################################################
    # Function convertFileSize Convert file size to its value in B, KB, MB, GB and TB.
    # Params: 
    #        size: number representing the size of a file on a unit specified on sizeIn parameter - numeric
    #        sizeIn: original unit (B, KB, MB, GB and TB) - string
    #        sizeOut: final unit (B, KB, MB, GB and TB) - string
    #        precision: decimal points- default = 2 - numeric
    # Return: Converted size float with the proper precision to the sizeOut unit - in case cannot calculate returns same size - on error returns 0.0
    ####################################################################################################################
    def convertFileSize(self, size, sizeIn, sizeOut, precision=2):
        retValue = 0.0
        try:
            if sizeIn == "B":
                if sizeOut == "KB":
                    retValue = round((size/1024.0), precision)
                elif sizeOut == "MB":
                    retValue = round((size/1024.0**2), precision)
                elif sizeOut == "GB":
                    retValue = round((size/1024.0**3), precision)
                elif sizeOut == "TB":
                    retValue = round((size/1024.0**4), precision)
            elif sizeIn == "KB":
                if sizeOut == "B":
                    retValue = round((size*1024.0), precision)
                elif sizeOut == "MB":
                    retValue = round((size/1024.0), precision)
                elif sizeOut == "GB":
                    retValue = round((size/1024.0**2), precision)
                elif sizeOut == "TB":
                    retValue = round((size/1024.0**3), precision)
            elif sizeIn == "MB":
                if sizeOut == "B":
                    retValue = round((size*1024.0**2), precision)
                elif sizeOut == "KB":
                    retValue = round((size*1024.0), precision)
                elif sizeOut == "GB":
                    retValue = round((size/1024.0), precision)
                elif sizeOut == "TB":
                    retValue = round((size/1024.0**2), precision)
            elif sizeIn == "GB":
                if sizeOut == "B":
                    retValue = round((size*1024.0**3), precision)
                elif sizeOut == "KB":
                    retValue = round((size*1024.0**2), precision)
                elif sizeOut == "MB":
                    retValue = round((size*1024.0), precision)
                elif sizeOut == "TB":
                    retValue = round((size/1024.0), precision)
            elif sizeIn == "TB":
                if sizeOut == "B":
                    retValue = round((size*1024.0**4), precision)
                elif sizeOut == "KB":
                    retValue = round((size*1024.0**3), precision)
                elif sizeOut == "MB":
                    retValue = round((size*1024.0**2), precision)
                elif sizeOut == "GB":
                    retValue = round((size*1024.0), precision)
            else:
                retValue = round(size, precision)
        except:
            return 0.0
        
        return retValue


