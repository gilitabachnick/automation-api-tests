import datetime

import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


class clsElement:
    
    #============================================================================================================
    #The class contains functions that relates to actions on elements.
    #============================================================================================================
       
    def verifyEelementLocation(self,driver,element,x,y,deviation=0):
        boolSuccess = True
        elX = element["x"]
        elY = element["y"]
        #If we set a deviation X should be: x - deviation < elX < x + deviation
        if (elX > (x + deviation)) or (elX < (x - deviation)):
            boolSuccess = False
        if (elY > (y + deviation)) or (elY < (y - deviation)):
            boolSuccess = False
        return boolSuccess

    def waitForElementByXpath(self, driver, xpathLocator, timeout):
        limitTimeout = datetime.datetime.now() + datetime.timedelta(0,timeout)
        while (datetime.datetime.now() <= limitTimeout):
            try:
                ui.WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, xpathLocator)))
                el = driver.find_element_by_xpath(xpathLocator)
                if el != None:
                    return el
            except (TimeoutException, NoSuchElementException):
                pass
        return None