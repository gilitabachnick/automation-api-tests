'''
Created on Jun 9, 2019

@author: Renan.Bresler
'''

import datetime
import time
from datetime import datetime
from datetime import timedelta
from math import ceil

from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import DOM
import Enums
import General
import KmcBasicFuncs
import autoitWebDriver


class analyticsFuncs:
    
    def __init__(self, Wd, logi, Wdobj):
        self.Wd = Wd
        self.logi = logi
        self.Wdobj = Wdobj
        self.basicFuncs = KmcBasicFuncs.basicFuncs()
        self.general = General.general(self.Wd, self.logi, self.Wdobj)
        
        if self.Wdobj.RUN_REMOTE:
            self.autoitWebDriver = autoitWebDriver.autoitWebDrive() 
            self.AWD =  self.autoitWebDriver.retautoWebDriver()
    
    ####################################################################################################################
    # Function goAnalytics: Go to Analytics section menu/submenu and checks if it is OK
    # Params:
    #        menuItem = Text of the Analytics menu option - string - default = '' (empty means no click on menu)
    #        submenuItem = Text of the Analytics submenu option- string - default = '' (empty means no click on submenu)  
    ####################################################################################################################
    def goAnalytics(self, menuItem = '', submenuItem = '', navigateToTab = True):
        self.logi.appendMsg("INFO - Going to Analytics Section...")
        
        try:
            if navigateToTab == True:
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_TAB).click()
                time.sleep(5)
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_BACK_BUTTON)
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_LOGO)

            if menuItem != "":
                self.logi.appendMsg("INFO - Going to menu item " + menuItem)
                try:
                    dynamicDOM = DOM.ANALYTICS_MENU_ITEM.replace('TEXTTOREPLACE', menuItem)
                    self.Wd.find_element_by_xpath(dynamicDOM).click()
                    self.general.waitForLoadingToDisappear()
                    self.general.waitForSpinnerToFinish()
                    time.sleep(5)
                    if submenuItem != "":
                        self.logi.appendMsg("INFO - Going to submenu item " + submenuItem)
                        try:
                            dynamicDOM = DOM.ANALYTICS_SUBMENU_ITEM.replace('TEXTTOREPLACE', submenuItem)
                            self.Wd.find_element_by_xpath(dynamicDOM).click()
                            self.general.waitForLoadingToDisappear()
                            self.general.waitForSpinnerToFinish()
                            time.sleep(5)
                    
                        except:
                            self.logi.appendMsg("FAIL - Going to submenu item " + submenuItem)
                            return False
                    
                except:
                    self.logi.appendMsg("FAIL - Going to menu item " + menuItem)
                    return False
                
        except:
            self.logi.appendMsg("FAIL - Going to Analytics section")
            return False
        
        return True
    
        
    ####################################################################################################################
    # Function setDatePreset: sets date on analytics page through preset options
    # Params:
    #        presetType: The desired preset - number - Mandatory
    #                                                        1- LAST 7 Days
    #                                                        2- LAST 30 Days
    #                                                        3- LAST 3 Months
    #                                                        4- LAST 12 Months
    #                                                        5- CURRENT Week
    #                                                        6- CURRENT Month
    #                                                        7- CURRENT Quarter
    #                                                        8- CURRENT Year
    #        compareMode: Compare mode switch- True/False - default=False
    #        comparePeriod: set the compare period, only usable if compareMode=True - 1=Same period last year / 2=Same period starting at - default=1
    #        compareStart: date of start of compare mode in case comparePeriod=2 - string date format "%Y-%m-%d" - default=[today date]
    # Return: True - Success / False - Fail (True only means the operation passed - not date correctness please see isDate() function to validate)
    ####################################################################################################################
    def setDatePreset(self, presetType, compareMode=False, comparePeriod = 1, compareStart = datetime.today().strftime("%Y-%m-%d")):
        try:
            self.logi.appendMsg("INFO - Going to set Date Preset")
            
            # Verifies is in compare mode and exit compare if relevant
            if self.isCompare() and not compareMode:
                self.logi.appendMsg("INFO - Exiting Compare Mode...")
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_EXIT_COMPARE).click()
                self.general.waitForSpinnerToFinish()
                time.sleep(1)
               
            # Establish date preset text
            if presetType >= 1 and presetType <= 4:
                
                if presetType == 1:
                    
                    # LAST 7 days
                    datePreset = "7 Days"
                
                elif presetType == 2:
                
                    # LAST 30 days
                    datePreset = "30 Days"
                
                elif presetType == 3:
                
                    # LAST 3 months
                    datePreset = "3 Months"
                
                elif presetType == 4:
                    
                    # LAST 12 months
                    datePreset = "12 Months"
                
                self.logi.appendMsg("INFO - Setting LAST " + datePreset)
                
            elif presetType >= 5 and presetType <= 8:
                
                if presetType == 5:
                    
                    # CURRENT week
                    datePreset = "Week"
                
                elif presetType == 6:
                    
                    # CURRENT month
                    datePreset = "Month"
                
                elif presetType == 7:
                    
                    # CURRENT quarter
                    datePreset = "Quarter"
                    
                elif presetType == 8:
                    
                    # CURRENT year
                    datePreset = "Year"
                    
                self.logi.appendMsg("INFO - Setting CURRENT " + datePreset)
                
            else:
                
                self.logi.appendMsg("FAIL - Error on preset type definition")
                return False
            
            # Open date preset on dropdown
            self.Wd.find_element_by_xpath(DOM.ANALYTICS_DATE_DROPDOWN).click()
            time.sleep(0.5)
            
            # Select Preset option
            dynamicDOM = DOM.ANALYTICS_DATE_VIEW_OPTION.replace('TEXTTOREPLACE','Preset')
            self.Wd.find_element_by_xpath(dynamicDOM).click()
            time.sleep(0.5)
            
            # Select relevant date option
            dynamicDOM = DOM.ANALYTICS_DATE_PRESET_OPTION.replace('TEXTTOREPLACE',datePreset)
            self.Wd.find_element_by_xpath(dynamicDOM).click()
            time.sleep(0.5)
            
            # Verifying and setting Compare Mode
            if compareMode:
                if not self.setCompare(comparePeriod, compareStart):
                    return False
            
            # Press Apply button
            self.Wd.find_element_by_xpath(DOM.ANALYTICS_DATE_APPLY).click()
            
        except:
            
            self.logi.appendMsg("FAIL - Cannot setup Date Preset")
            return False
    
        return True
    
    
    ####################################################################################################################
    # Function setDateCustom: sets date on analytics report page through specific date range
    # Params:
    #        dateFrom: Start date on report - string date format "%Y-%m-%d" - default=[today date]
    #        dateEnd: End date on report - string date format "%Y-%m-%d" - default=[today date]
    #        compareMode: Compare mode switch- True/False - default=False
    #        comparePeriod: set the compare period, only usable if compareMode=True - 1=Same period last year / 2=Same period starting at - default=1
    #        compareStart: date of start of compare mode in case comparePeriod=2 - string date format "%Y-%m-%d" - default=[today date]
    # Return: True - Success / False - Fail  (True only means the operation passed - not date correctness please see isDate() function to validate) 
    ####################################################################################################################
    def setDateCustom(self, dateFrom = datetime.today().strftime("%Y-%m-%d"), dateTo = datetime.today().strftime("%Y-%m-%d"), compareMode = False, comparePeriod = 1, compareStart = datetime.today().strftime("%Y-%m-%d")):
        try:
            
            self.logi.appendMsg("INFO - Going to set Specific Date Range")
            
            # Verifies is in compare mode and exit compare if relevant
            if self.isCompare() and not compareMode:
                self.logi.appendMsg("INFO - Exiting Compare Mode...")
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_EXIT_COMPARE).click()
                self.general.waitForSpinnerToFinish()
                time.sleep(1)
            
            # Open date dropdown
            self.Wd.find_element_by_xpath(DOM.ANALYTICS_DATE_DROPDOWN).click()
            time.sleep(0.5)
            
            # Select Preset option
            dynamicDOM = DOM.ANALYTICS_DATE_VIEW_OPTION.replace('TEXTTOREPLACE','Specific Date Range')
            self.Wd.find_element_by_xpath(dynamicDOM).click()
            time.sleep(0.5)
            
            # Wait for range calendar object
            containerWE = self.Wd.find_element_by_xpath(DOM.ANALYTICS_RANGE_CALENDAR)
            time.sleep(0.5)
            
            # Set date picker
            if self.setDatePicker(containerWE, dateFrom, dateTo):
                time.sleep(0.5)
            else:
                return False
            
            # Verifying and setting Compare Mode
            if compareMode:
                if not self.setCompare(comparePeriod, compareStart):
                    return False
            
            # Press Apply button
            self.Wd.find_element_by_xpath(DOM.ANALYTICS_DATE_APPLY).click()
            
        except:
            
            self.logi.appendMsg("FAIL - Cannot setup Specific Date Range")
            return False
        
        return True
    
    ####################################################################################################################
    # Function setCompare: set Compare Mode (the function assumes the date widget is open)
    # Params:
    #        comparePeriod = set the compare period, only usable if compareMode=True - 1=Same period last year / 2=Same period starting at - default=1
    #        compareStart = date of start of compare mode in case comparePeriod=2 - string date format "%Y-%m-%d" - default=[today date] 
    # Return: True: Success - False: Fail
    #################################################################################################################### 
    def setCompare(self, comparePeriod = 1, compareStart = datetime.today().strftime("%Y-%m-%d")):
        try:
            
            self.logi.appendMsg("INFO - Going to set Compare Mode")
                
            # Verifies is not in compare mode and check compare checkbox
            if not self.isCompare():
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_DATE_COMPARE_CHECKBOX).click()
                time.sleep(0.5)
            
            if comparePeriod == 2:
                textCompare = "Same period starting at:" + compareStart
                optionValue = "specific"
            else:
                textCompare = "Same period last year"
                optionValue = "lastYear"
                
            # Set compare option
            self.logi.appendMsg("INFO - Setting Compare Mode - " + textCompare)
            dynamicDOM = DOM.ANALYTICS_DATE_COMPARE_OPTION_RADIOBUTTON.replace('TEXTTOREPLACE', optionValue)
            self.Wd.find_element_by_xpath(dynamicDOM).click()
            time.sleep(0.5)
            
            # Set start date for compare period if relevant
            if comparePeriod == 2:
                if not self.setCompareStart(compareStart):
                    return False
        
        except:
            
            self.logi.appendMsg("FAIL - Cannot set Compare Mode")
            return False
        
        return True

    ####################################################################################################################
    # Function setCompareStart: set Compare Mode custom start date (the function assumes the date widget is open)
    # Params:
    #        dateFrom: date to set - string date format "%Y-%m-%d" - default=[today date]
    # Return: True: Success - False: Fail
    ####################################################################################################################
    def setCompareStart(self, dateFrom = datetime.today().strftime("%Y-%m-%d")):
        try:
            self.logi.appendMsg("INFO - Going to open Compare Start Date date-picker")
            
            # Wait & click on calendar object to open date picker
            containerWE = self.Wd.find_element_by_xpath(DOM.ANALYTICS_COMPARE_ICON_INPUT_CALENDAR)
            containerWE.find_element_by_xpath(DOM.ANALYTICS_ICON_CALENDAR_BUTTON).click()
            time.sleep(0.5)
            
            # Set date picker
            if self.setDatePicker(containerWE, dateFrom):
                time.sleep(0.5)
            else:
                return False
        except:
        
            self.logi.appendMsg("FAIL - Cannot open date-picker")
            return False
        
        return True
    
    ####################################################################################################################
    # Function setDatePicker: set date picker object date/s
    # Params:
    #        dateFrom: date to set - string date format "%Y-%m-%d" - default=[today date]
    #        dateTo: end date to set in case of range - string date format "%Y-%m-%d" - default="" means is not a range date-picker
    #        containerWE: containser web element of the date=picker if relevant - selenium web element object - mandatory
    # Return: True: Success - False: Fail
    ####################################################################################################################
    def setDatePicker(self, containerWE, dateFrom = datetime.today().strftime("%Y-%m-%d"), dateTo = "" ):
        try:
            
            self.logi.appendMsg("INFO - Setting date-picker date/s: " + dateFrom + " " + dateTo)
            
            dateRange = [dateFrom,dateTo]
            
            for dt in dateRange:
                if dt != "":
                    
                    # Separate year month and day
                    dateSplit = dt.split("-")
                    
                    # Open dropdown and select month
                    containerWE.find_element_by_xpath(DOM.ANALYTICS_DATE_PICKER_MONTH_DROPDOWN).click()
                    time.sleep(0.5)
                    
                    # Calculate dropdown value and select properly (value different than month number)
                    dateSplit[1] = str(int(dateSplit[1])-1)
                    dynamicDOM = DOM.ANALYTICS_DATE_PICKER_DROPDOWN_OPTION.replace('TEXTTOREPLACE', dateSplit[1])
                    containerWE.find_element_by_xpath(dynamicDOM).click()
                    time.sleep(0.5)
                    
                    # Open dropdown and select year
                    containerWE.find_element_by_xpath(DOM.ANALYTICS_DATE_PICKER_YEAR_DROPDOWN).click()
                    time.sleep(0.5)
                    dynamicDOM = DOM.ANALYTICS_DATE_PICKER_DROPDOWN_OPTION.replace('TEXTTOREPLACE', dateSplit[0])
                    containerWE.find_element_by_xpath(dynamicDOM).click()
                    time.sleep(0.5)
                    
                    # CLick on day
                    dynamicDOM = DOM.ANALYTICS_DATE_PICKER_DAY.replace('TEXTTOREPLACE', dateSplit[2].lstrip("0"))
                    containerWE.find_element_by_xpath(dynamicDOM).click()
                    time.sleep(0.5)
            
        except:
            self.logi.appendMsg("FAIL - Cannot set date picker dates")
            return False
        
        return True
    
    
    ####################################################################################################################
    # Function isCompareMode: verifies the date widget is in Compare Mode and set properly
    # Params:
    #        comparePeriod: compare period - 1=Same period last year / 2=Same period starting at - default=1
    #        compareStart:  date of start of compare mode in case comparePeriod=2 - string date format "%Y-%m-%d" - default=[today date]
    #        kmcDateFormat: date format set on KMC user settings - default =  MM/DD/YYYY
    # Return: True: Compare Mode set properly- False: Compare Mode not set properly 
    ####################################################################################################################
    def isCompareMode(self, comparePeriod = 1 , compareStart = "", kmcDateFormat = "MM/DD/YYYY"):
        try:
            # Verifying compare mode
            if self.isCompare():
                
                # Open date dropdown
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_DATE_DROPDOWN).click()
                time.sleep(0.5)
                
                # Define option to verify
                if comparePeriod == 1:
                    
                    textCompare = "Same period last year"
                    optionValue = "lastYear"
                    
                else:
                    
                    # Verify start date paramater is valid
                    if compareStart != "":
                        textCompare = "Same period starting at:" + compareStart
                        optionValue = "specific"
                    else:
                        self.logi.appendMsg("FAIL - Compare Mode start date to evaluate not defined.")
                        return False
                
                # Verify compare option radio-button
                self.logi.appendMsg("INFO - Verifying Compare Mode option - " + textCompare )
                dynamicDOM = DOM.ANALYTICS_DATE_COMPARE_OPTION.replace('TEXTTOREPLACE', optionValue)
                compareOption = self.Wd.find_element_by_xpath(dynamicDOM)
                
                try:
                    
                    #verify radiobutton is ON on the option
                    compareOption.find_element_by_xpath(DOM.ANALYTICS_DATE_COMPARE_RADIOBUTTON_ON)
                    
                    if comparePeriod == 1:
                        
                        # Option "Same period last year" OK
                        self.logi.appendMsg("PASS - Compare Mode set properly")
                    
                    else:
                        
                        # Verify Compare start date
                        self.logi.appendMsg("INFO - Verifying Compare Mode start date.")
                        inputContainer = self.Wd.find_element_by_xpath(DOM.ANALYTICS_COMPARE_ICON_INPUT_CALENDAR)
                        
                        # Extract date and convert to kmc date format
                        self.logi.appendMsg("INFO - Extracting start date...")
                        inputValue = inputContainer.find_element_by_xpath(DOM.ANALYTICS_DATE_INPUT).get_attribute("value")
                        dateValues = inputValue.split("/")
                        if kmcDateFormat == "DD/MM/YYYY":
                            
                            # DD/MM/YYYY
                            startDate = dateValues[2] + "-" + dateValues[1] + "-" + dateValues[0]
                            
                        else:
                            
                            # MM/DD/YYYY
                            startDate = dateValues[2] + "-" + dateValues[0] + "-" + dateValues[1]
                        
                        # Compare dates
                        if compareStart == startDate:
                            
                            self.logi.appendMsg("PASS - Compare Mode start date is set properly")
                            
                        else:
                            
                            self.logi.appendMsg("FAIL - Compare Mode start date not set properly - actual date: " + startDate)
                            return False
                    
                except:
                    
                    # Option verification failed
                    self.logi.appendMsg("FAIL - Compare Mode option not set properly")
                    return False
                
                # Close date drop-down
                self.Wd.find_element_by_xpath(DOM.ANALYTICS_POPUP_WIDGET_OVERLAY).click()
                            
            else:
                
                self.logi.appendMsg("FAIL - Compare Mode not set properly.")
                return False
            
        except:
            self.logi.appendMsg("FAIL - Compare Mode cannot be verified.")
            return False
        
        return True
    
    
    ####################################################################################################################
    # Function isCompare: verifies the date widget is in Compare Mode or Normal mode
    # Return: True: Compare Mode - False:Normal Mode 
    ####################################################################################################################
    def isCompare(self):
        try:
            
            # Checks if compare icon exist on date widget
            self.logi.appendMsg("INFO - Verifying Compare/Normal Mode") 
            res = self.Wdobj.Sync(self.Wd,DOM.ANALYTICS_COMPARE_ICON)           
            
            if isinstance(res,bool):
                
                self.logi.appendMsg("INFO - Date widget on Normal Mode")
                return False
            
            else:
                
                self.logi.appendMsg("INFO - Date widget on Compare Mode")
                return True
            
        except:
            
            self.logi.appendMsg("FAIL - Cannot verify Compare/Normal Mode")
            return False
        
        return False
    
    
    ####################################################################################################################
    # Function isDate: verifies the date of the analytics page is set in the desired way
    # Params: 
    #        presetType: preset types desired - number 1-9 -
    #                                                        1- LAST 7 Days
    #                                                        2- LAST 30 Days
    #                                                        3- LAST 3 Months
    #                                                        4- LAST 12 Months
    #                                                        5- CURRENT Week
    #                                                        6- CURRENT Month
    #                                                        7- CURRENT Quarter
    #                                                        8- CURRENT Year
    #                                                        9- Custom (uses dateFrom and dateTo custom params)
    #        dateFrom: date-from in the case presetType = 9 - date string format "%Y-%m-%d" - default = today date
    #        dateTo: date-to in the case presetType = 9 - date string format "%Y-%m-%d" - default = [today date]
    ####################################################################################################################
    def isDate(self, presetType, dateFrom = datetime.today().strftime("%Y-%m-%d"), dateTo = datetime.today().strftime("%Y-%m-%d")):
        try:
            self.logi.appendMsg("INFO - Verifying preset or custom date on drop-down control date range")
            
            # initialize calculated expected dates
            startDate = datetime.today()
            endDate = datetime.today()
            
            # extract date widget values
            retDate = []
            retDate = self.getDateRange()
            
            if len(retDate) > 0:
                
                compFrom = retDate[0]
                compTo = retDate[1]
                
                if presetType == 9:
                
                    # custom dates maintains dates From/To as is
                    self.logi.appendMsg("INFO - Verifying custom date range matches")
                
                elif presetType >= 1 and presetType <= 4:
                    
                    # calculates date-to in LAST presets (yesterday date)
                    endDate= datetime.today() - timedelta(days=1)
                    
                    if presetType == 1:
                        
                        # Calculates start date for LAST 7 days
                        self.logi.appendMsg("INFO - Verifying LAST 7 days")
                        startDate = endDate - timedelta(days=6)
                    
                    elif presetType == 2:
                    
                        # Calculates start date for LAST 30 days
                        self.logi.appendMsg("INFO - Verifying LAST 30 days")
                        startDate = endDate - timedelta(days=29)
                    
                    elif presetType == 3:
                    
                        # Calculates start date for LAST 3 months
                        self.logi.appendMsg("INFO - Verifying LAST 3 months")
                        startDate = self.monthDelta(endDate, -3)
                    
                    elif presetType == 4:
                        
                        # Calculates start date for LAST 12 months
                        self.logi.appendMsg("INFO - Verifying LAST 12 months")
                        startDate = self.monthDelta(endDate, -12)
                    
                elif presetType >= 5 and presetType <= 8:
                    
                    if presetType == 5:
                        
                        # Calculates start date for CURRENT week
                        self.logi.appendMsg("INFO - Verifying CURRENT week")
                        startDate = self.getWeekStart(endDate)
                    
                    elif presetType == 6:
                        
                        # Calculates start date for CURRENT month
                        self.logi.appendMsg("INFO - Verifying CURRENT month")
                        startDate = endDate.replace(day=1)
                    
                    elif presetType == 7:
                        
                        # Calculates start date for CURRENT quarter
                        self.logi.appendMsg("INFO - Verifying CURRENT quarter")
                        startDate = self.getQuarterStart(endDate)
                        
                    elif presetType == 8:
                        
                        # Calculates start date for CURRENT year
                        self.logi.appendMsg("INFO - Verifying CURRENT year")
                        startDate = endDate.replace(day=1, month=1)
                
                else:
                    
                    self.logi.appendMsg("FAIL - Error on preset type definition")
                    return False
                
                # convert dates to string in case of preset dates
                if presetType != 9:
                    dateFrom = startDate.strftime("%Y-%m-%d")
                    dateTo = endDate.strftime("%Y-%m-%d")
                
                verifyDate = True
                
                # verifies date-from 
                if compFrom == dateFrom:
                    self.logi.appendMsg("PASS - Expected date From: " + dateFrom + " - Actual widget date From: " + compFrom)
                else:
                    self.logi.appendMsg("FAIL - Expected date From: " + dateFrom + " - Actual widget date From: " + compFrom)
                    verifyDate = False
                
                # verifies date-to
                if compTo == dateTo:
                    self.logi.appendMsg("PASS - Expected date To: " + dateTo + " - Actual widget date To: " + compTo)
                else:
                    self.logi.appendMsg("FAIL - Expected date To: " + dateTo + " - Actual widget date To: " + compTo)
                    verifyDate = False
                
                if not verifyDate:
                    return False
                
            else:
                return False
            
        except:
            
            self.logi.appendMsg("FAIL - Cannot verify date from drop-down control.")
            return False
        
        return True
    
    ####################################################################################################################
    # Function getDateRange: gets date range from date dropdown
    # Return: 
    #        dateFT: date from/to array[2]- string - format "%Y-%m-%d"
    ####################################################################################################################
    def getDateRange(self):
        dateFT = []
        
        try:
        
            self.logi.appendMsg("INFO - Extracting date from drop-down control.")
            
            # Verifies date widget exist
            dateControl = self.Wdobj.Sync(self.Wd,DOM.ANALYTICS_DATE_DROPDOWN)
            if isinstance(dateControl, bool):
                
                self.logi.appendMsg("FAIL - Date drop-down control missing.")
                
            else:    
                
                # Extract & convert dates From-To
                dateStr = dateControl.text
                dateGroup = dateStr.split(" - ")
                for dateChar in dateGroup:
                    strToDate= datetime.strptime(dateChar,"%b %d, %Y").date()
                    dateFT.append(strToDate.strftime("%Y-%m-%d"))
                self.logi.appendMsg("PASS - Date from: " + dateFT[0])
                self.logi.appendMsg("PASS - Date to  : " + dateFT[1])
        
        except:
            
            self.logi.appendMsg("FAIL - Cannot extract date from drop-down control.")
            dateFT = []
        
        return dateFT
    
    ####################################################################################################################
    # Function getKMCDateFormat: gets KMC date format
    # Return: KMC date format string
    ####################################################################################################################
    def getKMCDateFormat(self):
        kmcFormat = ""
        try:
            
            self.logi.appendMsg("INFO - Extracting KMC date format.")
            
            # Open user settings menu
            self.Wd.find_element_by_xpath(DOM.ANALYTICS_KMC_USER_MENU).click()
            
            # Check user setting menu is open
            parentDOM = self.Wdobj.Sync(self.Wd,DOM.ANALYTICS_KMC_USER_SETTINGS)
            if isinstance(parentDOM, bool):
                
                kmcFormat = ""
                self.logi.appendMsg("FAIL - Cannot open KMC user settings.")
                
            else:
                
                # Get date format value
                kmcFormat = parentDOM.find_elements_by_xpath(DOM.ANALYTICS_KMC_USER_SETTINGS_DROPDOWN)[1].text
                self.logi.appendMsg("INFO - KMC date format: " + kmcFormat)
                
        except:
            
            kmcFormat = ""
            self.logi.appendMsg("FAIL - Cannot extract KMC date format.")
            pass
        
        # Close popup menu
        self.Wd.find_element_by_xpath(DOM.ANALYTICS_POPUP_WIDGET_OVERLAY).click()
        
        return kmcFormat
    
    
    ####################################################################################################################
    # Function isPageTitle: checks the analytics page title
    # Params:
    #        pageTitle = String title to check
    # Return: True if Title is OK, False if not
    ####################################################################################################################
    def isPageTitle(self, pageTitle):
        try:
            self.logi.appendMsg("INFO - Going to verify page title = " + pageTitle)
            dynamicDOM = DOM.ANALYTICS_PAGE_TITLE.replace('TEXTTOREPLACE', pageTitle)
            self.Wd.find_element_by_xpath(dynamicDOM)
            self.logi.appendMsg("PASS - Title OK")
        except:
            self.logi.appendMsg("FAIL - Checking page title = " + pageTitle)
            return False
        
        return True
    
    ####################################################################################################################
    # Function isGraphPeriod: verifies specific graph period button selected value (in general Monthly/Daily, but could be other)
    # Params:
    #        periodName = String selected period to verify
    #        selectorOrder = Number of button group on the page if there is more than one - Number (1 to x) - Default = 1
    #        verbose = print messages to log - boolean - default=True
    #        rContainer = webelement where to search the button group - default = "" (search on self.Wd)
    # Return: True if period is OK, False if not
    ####################################################################################################################
    def isGraphPeriod(self, periodName, selectorOrder = 1, verbose = True, rContainer = ""):
        periodOK = True
        try:
            
            if verbose:
                self.logi.appendMsg("INFO - Going to verify selected period = " + periodName)
            
            if rContainer == "":
                periodBtn = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_SELECTED_PERIOD)[selectorOrder - 1]
            else:
                periodBtn = rContainer.find_elements_by_xpath("."+DOM.ANALYTICS_SELECTED_PERIOD)[selectorOrder - 1]
            
            if periodBtn.text == periodName:
                if verbose:
                    self.logi.appendMsg("PASS - Selected period OK")
            else:
                if verbose:
                    self.logi.appendMsg("FAIL - Selected period not match")
                periodOK = False
                
        except:
            
            self.logi.appendMsg("FAIL - Checking selected period")
            return False
        
        return periodOK
    
    ####################################################################################################################
    # Function setGraphPeriod: set graph period button to value (in general Monthly/Daily, but could be other)
    # Params:
    #        periodName = String selected period to verify
    #        selectorOrder = Number of button group on the page if there is more than one - Number (1 to x) - Default = 1
    #        rContainer = webelement where to search the button group - default = "" (search on self.Wd)
    # Return: True if period setting is OK, False if not
    ####################################################################################################################
    def setGraphPeriod(self, periodName, selectorOrder = 1, rContainer=""):
        try:
            self.logi.appendMsg("INFO - Going to set graph period to " + periodName)
            dynamicDOM = DOM.ANALYTICS_GRAPH_PERIOD_BUTTON.replace('TEXTTOREPLACE', periodName)
            if rContainer == "":
                periodBtn = self.Wd.find_elements_by_xpath(dynamicDOM)[selectorOrder - 1]
            else:
                periodBtn = rContainer.find_elements_by_xpath("."+dynamicDOM)[selectorOrder - 1]
            
            periodBtn.click()
            time.sleep(1)
            self.general.waitForSpinnerToFinish()
            time.sleep(2)
            
            if not self.isGraphPeriod(periodName, selectorOrder, True, rContainer):
                return False
        
        except Exception:
            self.logi.appendMsg("FAIL - Setting graph period to " + periodName)
            return False
        
        return True
    
    ####################################################################################################################
    # Function iframeInit: switch the webdriver to iframe
    # Return: True or False on success
    ####################################################################################################################
    def iframeInit(self):
        try:
            self.logi.appendMsg("INFO - Switching Webdriver to iframe")
            self.Wd.switch_to.frame(self.Wd.find_element_by_tag_name("iframe"))
        except:
            self.logi.appendMsg("FAIL - Switching Webdriver to iframe")
            return False
        return True
    
    ####################################################################################################################
    # Function iframeInit: switch the webdriver from iframe back to default
    # Return: True or False on success
    ####################################################################################################################
    def iframeEnd(self):
        try:
            self.logi.appendMsg("INFO - Switching Webdriver from iframe to default")
            self.Wd.switch_to.default_content()
        except:
            self.logi.appendMsg("FAIL - Switching Webdriver from iframe to default")
            return False
        return True
    
    
    ####################################################################################################################
    # Function getQuarterStart: returns the quarter start date based on the dates passed
    # Params: 
    #        dt: date into the quarter - datetime format - default = [today date]
    ####################################################################################################################
    def getQuarterStart(self, dt = datetime.today()):
        return datetime(dt.year, (dt.month - 1) // 3 * 3 + 1, 1)
    
    ####################################################################################################################
    # Function getWeekStart: returns the week start date based on the date passed
    # Params: 
    #        dt: date into the week - datetime format - default = [today date]
    ####################################################################################################################
    def getWeekStart(self, dt = datetime.today()):
        return dt - timedelta(days=dt.isoweekday() % 7)
        
    ####################################################################################################################
    # Function monthDelta: Return date +/- delta months
    # Params: 
    #        date: start date - datetime format - mandatory
    #        delta: the number of month to add (positive) or substract (negative) - number - mandatory
    # Return: Calculated date - datetime format
    ####################################################################################################################
    def monthDelta(self, date, delta):
        m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        if not m: m = 12
        d = min(date.day, [31,
            29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date.replace(day=d,month=m, year=y)

    ####################################################################################################################
    # Function monthsBetween: Return the total number of months covered between 2 dates
    # Params: 
    #        dateFom: start date - date string format "%Y-%m-%d" - mandatory
    #        dateTo: End date - date string format "%Y-%m-%d" - mandatory
    # Return: number of months included between 2 dates - integer
    ####################################################################################################################
    def monthsBetween(self, dateFrom, dateTo):
        
        monthsCount = 0
        startD= dateFrom[:4] + dateFrom[5:7]
        endD = dateTo[:4] + dateTo[5:7]
        
        if len(startD) == 6 and len(endD) == 6:
            
            start, end = int(startD), int(endD)
            
            while start <= end:
                year, month = divmod(start, 100)
                
                if month == 13:
                    start += 88
                    continue
                
                monthsCount += 1
                start += 1
                
        return monthsCount
    
    ####################################################################################################################
    # Function daysBetween: Return the total number of days covered between 2 dates
    # Params: 
    #        dateFom: start date - date string format "%Y-%m-%d" - mandatory
    #        dateTo: end date - date string format "%Y-%m-%d" - mandatory
    # Return: number of days included between 2 dates - integer
    ####################################################################################################################
    def daysBetween(self, dateFrom, dateTo):
        
        daysCount = int((datetime.strptime(dateTo,"%Y-%m-%d").date() - datetime.strptime(dateFrom,"%Y-%m-%d").date()).days) + 1
        
        return daysCount
    
    ####################################################################################################################
    # Function isReportTitle verifies Title on the report section
    # Params:
    #        rContainers: report container webelement object - mandatory
    #        sectionTitle: Expected title of the section- string - mandatory
    ####################################################################################################################
    def isReportTitle(self, rContainer, sectionTitle):
        
        try:
            
            self.logi.appendMsg("INFO - Going to verify section title")
            actualTitle = self.getReportTitle(rContainer)
            
            if actualTitle.strip() == sectionTitle.strip():
                self.logi.appendMsg("PASS - Section title: " + sectionTitle + " as expected.")
                return True
            else:
                self.logi.appendMsg("FAIL - Expected section title: " + sectionTitle + "Actual section title: " + actualTitle)
                return False
            
        except:
            
            self.logi.appendMsg("FAIL - Verifying section title")
            return False
    
    ####################################################################################################################
    # Function getReportTitle get Title of the report section
    # Params:
    #         rContainer: report container webelement object - mandatory
    ####################################################################################################################
    def getReportTitle(self,rContainer):
        rTitle = ""
        try:
            rTitle = rContainer.find_element_by_xpath(DOM.ANALYTICS_REPORT_SECTION_TITLE).text
        
        except:
            self.logi.appendMsg("FAIL - Obtaining section title.")
            rTitle = ""
        
        return rTitle
    
    
    ####################################################################################################################
    # Function isReportTabSet verifies Tab names set on the report section
    # Params:
    #        rContainer: report container webelement object - mandatory
    #        sectionTabs: Expected tabs name comma-separated - string in the form "tab1,tab2,tabN"- mandatory
    #        separatorChar: flavors param  seperator character - default = ","
    ####################################################################################################################
    def isReportTabSet(self, rContainer, sectionTabs, separatorChar = ","):
        try:
            self.logi.appendMsg("INFO - Going to verify section tabs")
            expectedValues = sectionTabs.split(separatorChar)
            actualValues = self.getReportTabNames(rContainer)
            return self.evalExpectedArray(expectedValues, actualValues, True)
        
        except:
            
            self.logi.appendMsg("FAIL - Error verifying section tabs.")
            return False
    
    ####################################################################################################################
    # Function getReportTabs get Tabs array names on the report section
    # Params:
    #         rContainer: report container webelement object - mandatory
    # Return: array of tab names
    ####################################################################################################################
    def getReportTabNames(self,rContainer):
        rTabs = []
        try:
            
            tabObjs= rContainer.find_elements_by_xpath(DOM.ANALYTICS_REPORT_TAB_NAME)
            for xTabs in tabObjs:
                rTabs.append(xTabs.text) 
                
        except:
            
            self.logi.appendMsg("FAIL - Obtaining section tabs.")
            rTabs = []
            
        return rTabs

    ####################################################################################################################
    # Function getGraphTooltips get Tooltips array values from graph canvas
    # Params:
    #         rContainer: report container webelement object - mandatory
    #         xStart: Starting point of the graph scan - integer - pixel X coordinate
    #         xEnd: Ending point of the graph scan - integer - pixel X coordinate
    #         xOffset: x Jump on every iteration- integer - pixels
    #         yStart: Starting point of the graph scan - integer - pixel Y coordinate
    #         invertCoordinates: True:scan the graph in vertical (Y) direction converting all X values to Y and all Y values to X - False (default)
    #         isCompareMode: splits all the elements of the tool tip on an array and not plain text
    # Return: array of all graph tooltips content (if CompareMode=True each element is an array if not plain text)
    ####################################################################################################################
    def getGraphTooltips(self, rContainer, xStart = 0, xEnd = 0, xOffset = 0, yStart = 30, invertCoordinates = False, isCompareMode = False):
        
        rTooltips = []
        try:
            
            self.logi.appendMsg("INFO - Getting graph tool tips...")
            
            canvas = rContainer.find_element_by_xpath(DOM.ANALYTICS_GRAPH_CANVAS)
            
            if xEnd == 0:
                repoChart = rContainer.find_element_by_xpath("."+DOM.ANALYTICS_REPORT_CHART)
                chartWith = self.general.stripNumber(repoChart.value_of_css_property("width").strip())
                xEnd = int(chartWith)
            
            self.logi.appendMsg("INFO - Graph width: " + str(xEnd) + "px")
            
            #if offset is 0 then calculate
            if xOffset == 0:
                self.logi.appendMsg("INFO - Auto-configuring graph parsing parameters... ")
                
                dateWidget = self.getDateRange()
                
                if self.isGraphPeriod("Monthly", verbose = False, rContainer = rContainer):
                    graphPeriod = "Monthly"
                else:
                    graphPeriod = "Daily"
                
                xOffset = self.calcGraphOffset(xEnd, dateWidget[0], dateWidget[1], graphPeriod)
                
                
            self.logi.appendMsg("INFO - Parsing offset: " + str(xOffset) + "px")
                
            yOffset = 0
            xPos = xStart
            yPos = yStart
            posOffset = xOffset
            
            if invertCoordinates:
                
                self.logi.appendMsg("INFO - Converting coordinates for vertical graph parsing")
                
                yOffset = xOffset
                xOffset = 0
                xPos = yStart
                yPos = xStart
                
            self.logi.appendMsg("INFO - Parsing graph...")
            
            mouse = ActionChains(self.Wd)
            mouse.move_to_element_with_offset(canvas, xPos, yPos).perform()
            time.sleep(3)
            
            self.Wd.implicitly_wait(2)
            
            for offsetVal in range(xStart,xEnd,posOffset):
                
                try:
                    if isCompareMode:
                        
                        compareToolTipList = []
                        toolText = rContainer.find_element_by_xpath(DOM.ANALYTICS_GRAPH_TOOLTIP).text.split("\n")
                        
                        for text in toolText:
                            toolTip = self.cleanStr(text)
                            toolTip = self.general.convertUnicodeToStr(toolTip)
                            toolTip = toolTip.strip()
                            compareToolTipList.append(toolTip)

                        if compareToolTipList not in rTooltips and compareToolTipList != [""]:
                            rTooltips.append(compareToolTipList)
                            
                    else:
                        
                        toolText = rContainer.find_element_by_xpath(DOM.ANALYTICS_GRAPH_TOOLTIP).text

                        toolText = self.cleanStr(toolText)
                        toolText = self.general.convertUnicodeToStr(toolText)
                        toolText = toolText.strip()
                        
                        if (toolText not in rTooltips) and toolText!="":
                            rTooltips.append(toolText)
                            
                except:
                    
                    pass
                
                if invertCoordinates:
                    yPosVal = offsetVal
                    xPosVal = xPos
                else:
                    xPosVal = offsetVal
                    yPosVal = yPos
                
                mouse = ActionChains(self.Wd)
                mouse.move_to_element_with_offset(canvas, xPosVal, yPosVal).perform()
        
        except MoveTargetOutOfBoundsException:
            pass
        
        except:
            
            self.logi.appendMsg("FAIL - Obtaining section graph tooltips.")
            rTooltips = []
        
        self.basicFuncs.setImplicitlyWaitToDefault(self.Wd)
        
        return rTooltips
    
    ####################################################################################################################
    # Function calcGraphOffset calculates the offset in pixels necessary to parse graphic canvas based on dates
    # Params:
    #        canvasWidth: width of graph canvas object - integer
    #        dateFrom: start date - string date format "%Y-%m-%d"
    #        dateTo: end date - string date format "%Y-%m-%d"
    #        graphPeriod: Daily/Monhtly - string
    # Return: Offset for parsing graph in pixels - integer
    ####################################################################################################################
    def calcGraphOffset(self, canvasWidth, dateFrom , dateTo, graphPeriod):
        graphOffset = 0
        canvasWidth = canvasWidth - 60  # extract margin for Y-axis labels (average)
        numPoints = 0
        
        try:
            
            if graphPeriod == "Monthly":
                numPoints = self.monthsBetween(dateFrom, dateTo)
            elif graphPeriod == "Daily":
                numPoints= self.daysBetween(dateFrom, dateTo)
            else:
                self.logi.appendMsg("FAIL - Obtaining graph offset - period not valid, setting to 1 pixel.")
            
            if numPoints > 0:
                graphOffset = int(int(canvasWidth/numPoints)/2)
            else:
                graphOffset = 1
                
            if graphOffset <= 0:
                graphOffset = 1
                
        except:
            
            self.logi.appendMsg("FAIL - Cannot calculate graph offset, setting to 1 pixel.")
            graphOffset = 1
        
        return graphOffset
    
    ####################################################################################################################
    # Function evalExpectedArray checks the values on an expected array matches the actual values array and print results
    # Params:
    #         expectedValues: Array with expected values - string array - mandatory
    #         ActualValues: Array with actual values - string array - mandatory
    #         sortValues: indicate if the values should appear sorted as expected array - boolean - default = False
    #         verbose: indicate if print messages to log - boolean
    # Return: True - Passed , False - Fail
    ####################################################################################################################
    def evalExpectedArray(self, expectedValues, actualValues, sortedValues = False, verbose = True):
        retEval = True
        try:
            
            
            # Remove leading and ending spaces on string elements
            for indInlist in range(0,len(expectedValues)):
                expectedValues[indInlist].strip()
            
            for indInlist in range(0,len(actualValues)):
                actualValues[indInlist].strip()
                
            # Check the expected values are present in actual array
            if verbose:
                self.logi.appendMsg("INFO - Comparing expected items with actual result...")
            foundInActAndNotInExp = [xValue for xValue in actualValues if not xValue in expectedValues]
            foundInActAndInExp = [xValue for xValue in actualValues if xValue in expectedValues]
            foundInExpAndNotInAct = [xValue for xValue in expectedValues if not xValue in actualValues]
            
            for j in (foundInActAndInExp):
                if verbose:
                    self.logi.appendMsg("PASS - The expected item " + j + " found on actual result")
            for j in (foundInActAndNotInExp):
                if verbose:
                    self.logi.appendMsg("FAIL - The item " + j + " found in the actual result and is not expected")
                retEval = False
            for j in (foundInExpAndNotInAct):
                if verbose:
                    self.logi.appendMsg("FAIL - The expected item " + j + " was not found in the actual result")
                retEval = False
            
            # Check the sorting of the expected values matches actual array, if relevant
            if sortedValues and retEval:
                
                if verbose:
                    self.logi.appendMsg("INFO - Comparing sorting on expected items with actual result...")
                for indInExp in range(0,len(expectedValues)):
                    
                    for indInlist in range(0,len(actualValues)):
                        
                        if actualValues[indInlist] == expectedValues[indInExp]:
                            break
                    
                    if indInExp == indInlist:
                        if verbose:
                            self.logi.appendMsg("PASS - The item " + expectedValues[indInExp] + " is in index position " + str(indInExp) + " as expected")
                    else:
                        if verbose:
                            self.logi.appendMsg("FAIL - The item " + expectedValues[indInExp] + " was expected in index position " + str(indInExp) + " and actually is in index position " + str(indInlist))
                        retEval = False
                    
        except:
            
            if verbose:
                self.logi.appendMsg("FAIL - Error comparing expected with actual arrays.")
            retEval = False
        
        return retEval

    #Returns a start date for compare mode with custom period
    #Start date will be 15 days backwards according to preset (e.g if preset is 3 months so start date is 3 months + 15 days backwards)
    #Preset == '' is for specific date range start date
    #Pass preset 9 to create a specific date delta
    def createCustomCompareDate(self, preset='', customDelta=''):
        today = datetime.today()

        if preset == '':
            startDate = today - timedelta(days=15)
        if preset == 1 or preset == 5:
            startDate = today - timedelta(days=21)
        if preset == 2 or preset == 6:
            startDate = today - timedelta(days=44)
        if preset == 3 or preset == 7:
            today = self.monthDelta(today, -3)
            startDate = today - timedelta(days=15)
        if preset == 4 or preset == 8:
            today = self.monthDelta(today, -12)
            startDate = today - timedelta(days=15)
        if preset == 9:
            startDate = today - timedelta(days=customDelta)

        return startDate.strftime("%Y-%m-%d")

    # Returns dictionary at the following format:
    # {'Metric name' : Value}
    def getHighlightsValuesNormalMode(self):
        sectionDict = {}
        try:
            metricsList = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_HIGHLIGHTS_METRIC)
            for row in metricsList:
                key = self.general.convertUnicodeToStr(
                    row.find_element_by_xpath(DOM.ANALYTICS_HIGHLIGHTS_METRIC_TITLE).text)
                value = self.general.convertUnicodeToStr(
                    row.find_element_by_xpath(DOM.ANALYTICS_HIGHLIGHTS_METRIC_VALUE).text)
                sectionDict[key] = value
        except:
            self.logi.appendMsg("FAIL - Couldn't get highlights values")
            return False

        return sectionDict

    def getTopVideosHighlightsData(self, iscompare=False):
        videosDict = {}
        i=0
        try:
            datesList = []
            if iscompare:
                topVideosContainer = self.Wd.find_element_by_xpath(
                    DOM.ANALYTICS_SUMMARY_SECTION.replace('TITLE', 'Top Videos'))
                topVideosCompareDates = topVideosContainer.find_elements_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_DATES)
                for date in topVideosCompareDates:
                    datesList.append(self.general.convertUnicodeToStr(date.text))

            topVideos = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_HIGHLIGHTS_ROW)
            for row in topVideos:
                key = self.general.convertUnicodeToStr(
                    row.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_INDEX).text)
                valuesList =[]
                title = self.general.convertUnicodeToStr(
                    row.find_element_by_xpath(DOM.ANALYTICS_REPORT_SECTION_TITLE).text)
                valuesList.append(title)
                score = self.general.convertUnicodeToStr(
                    row.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_SCORE).text)
                valuesList.append(score)

                if iscompare:
                    valuesList.insert(0,key)
                    videosDict[datesList[i]] = valuesList
                    i+=1
                else:
                    videosDict[key] = valuesList

        except:
            self.logi.appendMsg("FAIL - Couldn't get highlights values")
            return False

        return videosDict

    #expectedOrder - list of titles that should be in highlights section
    #helpTooltips - can be text or a list of texts if there are several tooltips
    def verifyHighlightsGui(self,isCompareMode):
        expectedOrder = ['Player Impressions', 'Plays', 'Unique Viewers', 'Minutes Viewed']
        toolTipText = "Snapshot of important metrics for the selected timeframe"
        try:
            #check all highlights metrics titles appear
            currentOrder = self.getHighlights(isCompareMode)
            if len(currentOrder) != len(expectedOrder):
                self.logi.appendMsg("FAIL - Number of metrics appear in highlights are "+ str(len(currentOrder)) +", and should be "+str(len(expectedOrder)))
                return False
            for i in range(len(expectedOrder)):
                key = expectedOrder[i]
                if not key in currentOrder:
                    self.logi.appendMsg("FAIL - "+key+" doesn't appear in highlights metrics")
                    return False

            #Check help tooltips
            if self.verifyTooltipText('Highlights',toolTipText) == False:
               self.logi.appendMsg("FAIL - tooltip is not correct")
               return False

        except:
            self.logi.appendMsg("FAIL - Couldn't check highlights gui")
            return False

        return True

    def verifyTopVideosGui(self,title, toolTipText):
        videosList = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_HIGHLIGHTS_ROW)

        if len(videosList) !=3:
            self.logi.appendMsg("FAIL - Should be displayed 3 and actual "+len(videosList)+" are displayed")
            return False

        # toolTipText = 'Top videos based on the Kaltura engagement formula'
        if self.verifyTooltipText(title,toolTipText) == False:
            self.logi.appendMsg("FAIL - tooltip is not correct")
            return False


        return True

    def verifyReportTitle(self, title):

        reportHeader  = self.general.get_element(DOM.ANALYTICS_REPORT_HEADER)
        reportTitle = (reportHeader.find_element_by_xpath(DOM.ANALYTICS_REPORT_SECTION_TITLE)).text

        if self.general.convertUnicodeToStr(reportTitle) != title:
            self.logi.appendMsg("FAIL - Report title is incorrect")
            return False

        self.logi.appendMsg("PASS - Report title was verified")
        return True

    def verifyTooltipText(self, title, toolTipText, isTabTitle = False):
        try:
            if isTabTitle:
                toolTipIcon = self.general.get_element(DOM.ANALYTICS_SUB_TITLE_HELP_TOOLTIP_ICON.replace("TITLE", title))
            else:
                toolTipIcon = self.general.get_element(DOM.ANALYTICS_TITLE_HELP_TOOLTIP_ICON.replace("TITLE", title))

            mouse = ActionChains(self.Wd)
            mouse.move_to_element(toolTipIcon).perform()
            helpTooltips = self.general.get_element(DOM.ANALYTICS_HELP_TOOLTIP_CONTENT)

            if helpTooltips.text != toolTipText:
                self.logi.appendMsg("FAIL - tooltip text is incorrect")
                return False
        except:
            self.logi.appendMsg("FAIL - Couldn't verify toolTip")
            return False

        self.logi.appendMsg("SUCCESS - tooltip was verified")
        return True


    # Returns dictionary with all highlights metrics at the following format:
    # {Metric name e.g Plays/share : [trend calculation value(%), previous period dates, previous period sum , current period dates, current period sum]}
    def getHighlightsValuesCompareMode(self):
        trendDict={}

        # Get all highliights metrics
        metricsList = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_HIGHLIGHTS_METRIC)
        try:
            for row in metricsList:
                trendList = []
                trendnum = row.find_element_by_xpath(DOM.ANALYTICS_HIGHLIGHTS_METRIC_VALUE_COMPARE_MODE)
                key = self.general.convertUnicodeToStr(row.find_element_by_xpath(DOM.ANALYTICS_HIGHLIGHTS_METRIC_TITLE).text)
                trendValue = self.general.convertUnicodeToStr(trendnum.text)
                if trendValue != "":
                    trendValue = self.general.convertTextToNumber(trendValue.replace("%", ""))
                if trendValue == "":
                    try:
                        iconList = trendnum.find_elements_by_tag_name('i')
                        trendIcon = iconList[1].get_attribute('class')
                    except:
                        self.logi.appendMsg("FAIL - Couldn't get trend direction")
                        return False
                else:
                    trendIcon = self.general.convertUnicodeToStr(trendnum.find_element_by_tag_name('i').get_attribute('class'))
                trendList.append(trendValue)
                trendList.append(trendIcon)

                # Get tooltip values for each metric
                ActionChains(self.Wd).move_to_element(trendnum).perform()
                time.sleep(0.5)
                tooltipList = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_COMPARE_TOOLTIP)
                for date in tooltipList:
                    time.sleep(0.5)
                    periodDate = self.general.convertUnicodeToStr(date.find_element_by_xpath(DOM.ANALYTICS_COMPARE_TOOLTIP_DATE).text)
                    periodDate = periodDate.replace("\n", "")
                    trendList.append(periodDate)
                    periodValue = self.general.convertUnicodeToStr(date.find_element_by_xpath(DOM.ANALYTICS_COMPARE_TOOLTIP_VALUE).text)
                    periodValue = periodValue.replace("\n", "")
                    periodValue = periodValue.replace("min", "")
                    trendList.append(periodValue)

                trendDict[key] = trendList
        except:
            self.logi.appendMsg("FAIL - Couldn't get trend values")
            return False

        return trendDict

    def getHighlights(self, isCompareMode=False):
        if isCompareMode:
            return self.getHighlightsValuesCompareMode()
        else:
            return self.getHighlightsValuesNormalMode()

    def verifyHighlights(self, isCompareMode=False, preset ='',comparePeriod=''):
        if isCompareMode:
            return self.verifyHighlightsCompareMode(comparePeriod, preset)
        else:
            return self.verifyHighlightsNormalMode()

    def verifyTopVideos(self, isCompareMode=False, preset ='',comparePeriod=''):
        if isCompareMode:
            return self.verifyTopVideosCompareMode()
        else:
            return self.verifyTopVideosNormalMode()

    def verifyTooltipCustomDatesRange(self,periodDates, preset,currentDatesDelta):
        periodDates = periodDates.split("  ")
        startDate =  datetime.strptime(periodDates[0].strip(), '%b %d, %Y')
        endDate = datetime.strptime(periodDates[1].strip(), '%b %d, %Y')

        dateRange = (endDate - startDate).days
        if preset == 1:
            if dateRange != 6:
                self.logi.appendMsg("Fail - date range is not correct")
                return False
        if preset == 2:
            if dateRange != 29:
                self.logi.appendMsg("Fail - date range is not correct")
                return False
        if preset == 3:
            if not 90 <= dateRange <= 92:
                self.logi.appendMsg("Fail - date range is not correct")
                return False
        if preset == 4:
            if not 365 <= dateRange <= 366:
                self.logi.appendMsg("Fail - date range is not correct")
                return False
        if preset == 5 or preset == 6 or preset == 7 or preset == 8:
            if currentDatesDelta != dateRange:
                self.logi.appendMsg("Fail - date range is not correct")
                return False

        return True

    #Compare period - 1 = last year, 2 = custom
    def verifyHighlightsTooltipDatesCompareMode(self,previousPeriodDates, currentPeriodDates,comparePeriod, preset):
        tmp = self.general.get_element(DOM.ANALYTICS_DATE_DROPDOWN)
        pageDateRange = self.general.convertUnicodeToStr(tmp.text)

        #Calculate correct dates for tooltip
        pageDateRange = pageDateRange.split("-")
        pageDateRangeStart = datetime.strptime(pageDateRange[0].strip(), '%b %d, %Y')
        pageDateRangeEnd = datetime.strptime(pageDateRange[1].strip(), '%b %d, %Y')


        # Compare correct dates with current period
        currentPeriodDatesList = currentPeriodDates.split("  ")
        currentStartDate = datetime.strptime(currentPeriodDatesList[0].strip(), '%b %d, %Y')
        if currentStartDate != pageDateRangeStart:
            self.logi.appendMsg("FAIL - tooltip current year start date is not correct")
            return False
        currentEndDate = datetime.strptime(currentPeriodDatesList[1].strip(), '%b %d, %Y')
        if currentEndDate != pageDateRangeEnd:
            self.logi.appendMsg("FAIL - tooltip current year end date is not correct")
            return False

        #If compare period is last year
        if comparePeriod == 1:
            LastYearDateStart = self.monthDelta(pageDateRangeStart, -12)
            lastYearDateEnd = self.monthDelta(pageDateRangeEnd, -12)

            #Compare previous period delta is 1 year
            previousPeriodDatesList = previousPeriodDates.split("  ")
            if datetime.strptime(previousPeriodDatesList[0].strip(), '%b %d, %Y') != LastYearDateStart:
                self.logi.appendMsg("FAIL - tooltip last year start date is not correct")
                return False
            if datetime.strptime(previousPeriodDatesList[1].strip(), '%b %d, %Y') != lastYearDateEnd:
                self.logi.appendMsg("FAIL - tooltip last year end date is not correct")
                return False

        # If compare period is custom
        elif comparePeriod == 2:
            #Verify custom dates delta
            currentDatesDelta = (currentEndDate - currentStartDate).days
            if self.verifyTooltipCustomDatesRange(previousPeriodDates, preset, currentDatesDelta) ==False:
                return False

        self.logi.appendMsg("PASS - Period dates in highlights tooltips were verified")
        return True

    def verifyHighlightsTrend(self, previousTotal, currentTotal, actualResult, trendDirection):
        if actualResult != "":
            expectedResult = self.calcTrend(previousTotal,currentTotal)
        elif actualResult == "":
            expectedResult = 0

        if expectedResult == 0 and actualResult == "":
            if "icon-minus" not in trendDirection:
                return False
        if expectedResult == 0 and actualResult != "":
            if expectedResult != actualResult:
                self.logi.appendMsg("FAIL - Trend value in highlights is not correct")
                return False
        if expectedResult < 0:
            if trendDirection != "icon-regression":
                self.logi.appendMsg("FAIL - Trend arrow icon is incorrect")
                return False
            if not abs(expectedResult+1) <= actualResult <= abs(expectedResult-1):
                self.logi.appendMsg("FAIL - Trend value in highlights is not correct")
                return False
        if expectedResult > 0:
            if trendDirection != "icon-progress":
                self.logi.appendMsg("FAIL - Trend arrow icon is incorrect")
                return False
            if not abs(expectedResult-1) <= actualResult <= abs(expectedResult+1):
                self.logi.appendMsg("FAIL - Trend value in highlights is not correct")
                return False

        self.logi.appendMsg("Pass - Trend calculation value and indication were verified")
        return True

    def verifyTopVideosNormalMode(self):
        self.logi.appendMsg("INFO - Going to verify top vidoes highlights in normal mode")

        #Verify top videos gui
        # if self.verifyTopVideosGui() == False:
        #     self.logi.appendMsg("FAILED to verify highlights gui")
        #     return False

        #Verify videos titles and scores are the same as in top videos table
        topVideos = self.getTopVideosHighlightsData()
        tableFirstPageRows = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE_ROW)
        videosDict={}
        for row in tableFirstPageRows:
            key = self.general.convertUnicodeToStr(
                row.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_INDEX).text)
            valuesList=[]
            title = self.general.convertUnicodeToStr(
                row.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE_ENTRY_NAME).text)
            valuesList.append(title)
            score = self.general.convertUnicodeToStr(
                row.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE_SCORE).text)
            valuesList.append(score)
            videosDict[key] = valuesList

        for entry in topVideos:
            if topVideos[entry][0] != videosDict[entry][0]:
                self.logi.appendMsg("FAIL - Video #"+str(entry)+" title is not the same in highlights and table")
                return False
            if topVideos[entry][1] != videosDict[entry][1]:
                self.logi.appendMsg("FAIL - Video #"+str(entry)+" score is not the same in highlights and table")
                return False

        self.logi.appendMsg("PASS - Top vidoes highlights were verified")
        return True

    def verifyHighlightsNormalMode(self):
        self.logi.appendMsg("INFO - Going to verify highlights metrics in normal mode")

        #Verify all metrics that should be appear and tooltip
        # if self.analyticsFuncs.verifyHighlightsGui(False) == False:
        #     self.logi.appendMsg("FAILED to verify highlights gui")
        #     return False

        # Get highlights values
        metricDict = self.getHighlights(False)
        if metricDict == False:
            return False

        graph = self.general.get_element(DOM.ANALYTICS_HIGHLIGHTS_REPORT)
        canvas = self.general.get_child_element(DOM.ANALYTICS_GRAPH_CANVAS, DOM.ANALYTICS_HIGHLIGHTS_REPORT)
        if canvas == False:
            return False
        canvasWidth = int(canvas.get_attribute("width"))

        # For each metric in highlights
        for metric in metricDict:
            if metric == "Captions Selected":
                continue

            highlightValue = self.general.convertTextToNumber(metricDict[metric])
            # Move to current metric tab in graph report
            if self.general.click(DOM.ANALYTICS_REPORT_TAB.replace('TAB_NAME', metric)) == False:
                return False

            # Get graph tooltips values
            graphData = self.getGraphTooltips(graph, 50, canvasWidth, 50)
            graphValue = 0

            # Sum graph values
            for data in graphData:
                value = data.partition(":")[2]
                graphValue += self.general.convertTextToNumber(value)

            # Verify graph values sum is as value in highlights
            if "Unique Viewers" in metric or "Contributors" in metric:
                if not highlightValue <= graphValue:
                    self.logi.appendMsg("FAIL - sum of unique viewers is smaller than presented sum in highlights")
                    return False
            # Metrics with 'minutes' values can be rounded
            elif "Minutes" in metric:
                if not highlightValue - 1 <= graphValue <= highlightValue + 1:
                    self.logi.appendMsg("FAIL - sum of " + metric + " is not in the expected range")
                    return False
            else:
                if not highlightValue == graphValue:
                    self.logi.appendMsg("FAIL - sum of " + metric + " is not the same in highlights and graph report")
                    return False

        self.logi.appendMsg("PASS - All highlights metrics were verified")
        return True

    def verifyTopVideosCompareMode(self):
        self.logi.appendMsg("INFO - Going to verify top videos highlights in compare mode")

        topVideos = self.getTopVideosHighlightsData(True)
        if topVideos == False:
            self.logi.appendMsg("FAIL - Couldn't get top videos highlights stats")
            return False
        try:
            table = self.Wd.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE)
            compareTables = table.find_elements_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_COMPARE_TABLES)
            for period in compareTables:
                periodDate = self.general.convertUnicodeToStr((period.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_DATES)).text)
                periodVideoInIndex = period.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE_ROW_BY_INDEX.replace('INDEX',topVideos[periodDate][0]))
                tableVideoTitle = self.general.convertUnicodeToStr((periodVideoInIndex.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE_ENTRY_NAME)).text)
                tableVideoScore = self.general.convertUnicodeToStr((periodVideoInIndex.find_element_by_xpath(DOM.ANALYTICS_TOP_VIDEOS_TABLE_SCORE)).text)
                if topVideos[periodDate][1] != tableVideoTitle:
                    self.logi.appendMsg("FAIL - Video title is not the same in highlights and table")
                    return False
                if topVideos[periodDate][2] != tableVideoScore:
                    self.logi.appendMsg("FAIL - Video score is not the same in highlights and table")
                    return False
        except:
            self.logi.appendMsg("FAIL - Couldn't get top videos highlights stats")
            return False

        self.logi.appendMsg("PASS - top videos highlights stats were verified")
        return True

    def verifyHighlightsCompareMode(self,comparePeriod, preset):
        self.logi.appendMsg("INFO - Going to verify highlights metrics in compare mode")

        # Get highlights values
        metricDict = self.getHighlights(True)
        if metricDict == False:
            return False

        #Get graph element
        graph = self.general.get_element(DOM.ANALYTICS_HIGHLIGHTS_REPORT)
        canvas = self.general.get_child_element(DOM.ANALYTICS_GRAPH_CANVAS, DOM.ANALYTICS_HIGHLIGHTS_REPORT)
        if canvas == False:
            return False
        canvasWidth = int(canvas.get_attribute("width"))

        # For each metric in highlights
        for metric in metricDict:

            #Verify highlights tooltip dates are correct
            if self.verifyHighlightsTooltipDatesCompareMode(metricDict[metric][2], metricDict[metric][4], comparePeriod, preset) == False:
                self.logi.appendMsg("FAIL - highlights tooltip dates are incorrect")
                return False

            #Extract highlights values
            metricToolTipLastPeriod = self.general.convertTextToNumber(metricDict[metric][3])
            metricToolTipCurrentPeriod = self.general.convertTextToNumber(metricDict[metric][5])
            trendValue = metricDict[metric][0]
            trendDirection = metricDict[metric][1]

            #Captions doesn't have a graph presentation
            if metric == "Captions Selected":
                continue

            # Move to current metric tab in graph report
            if self.general.click(DOM.ANALYTICS_REPORT_TAB.replace('TAB_NAME', metric)) == False:
                return False

            # Get graph tooltips values
            if comparePeriod == 2:
                if preset == 4 or preset == 8:
                    graphData = self.getGraphTooltips(graph, 0, canvasWidth, 1, isCompareMode=True)
                else:
                    graphData = self.getGraphTooltips(graph, 0, canvasWidth, 10, isCompareMode=True)
            else:
                graphData = self.getGraphTooltips(graph, 50, canvasWidth, 50, isCompareMode =True)
            lastPeriodGraphValue = 0
            currentPeriodGraphValue = 0

            # Sum graph values
            for data in graphData:
                lastPeriodValue = self.general.convertTextToNumber(data[1].partition(":")[2])
                currentPeriodValue = self.general.convertTextToNumber(data[3].partition(":")[2])
                lastPeriodGraphValue += lastPeriodValue
                currentPeriodGraphValue += currentPeriodValue

            # Verify graph values sum is as value in highlights
            if metric == '':
                if metricToolTipLastPeriod != 0 or metricToolTipCurrentPeriod !=0:
                    self.logi.appendMsg("FAIL - there is no trend value and should be")
                    return False
                if lastPeriodGraphValue != 0 or currentPeriodGraphValue !=0:
                    self.logi.appendMsg("FAIL - sum of graph values should be 0 for both periods")
                    return False
            if "Unique Viewers" in metric or "Contributors" in metric:
                if not metricToolTipLastPeriod <= lastPeriodGraphValue and not metricToolTipCurrentPeriod <= currentPeriodGraphValue:
                    self.logi.appendMsg("FAIL - sum of " + metric + " is smaller than presented sum in highlights")
                    return False
            # Metrics with 'minutes' values can be rounded
            elif "Minutes" in metric:
                if not metricToolTipLastPeriod - 1 <= lastPeriodGraphValue <= metricToolTipLastPeriod + 1:
                    self.logi.appendMsg("FAIL - sum of " + metric + " is not in the expected range")
                    return False
            else:
                if not metricToolTipCurrentPeriod == currentPeriodGraphValue and metricToolTipLastPeriod == lastPeriodGraphValue:
                    self.logi.appendMsg("FAIL - sum of " + metric + " is not the same in highlights and graph report")
                    return False

            if self.verifyHighlightsTrend(metricToolTipLastPeriod,metricToolTipCurrentPeriod,trendValue,trendDirection) == False:
                self.logi.appendMsg("FAIL - trend calculation and arrow icon is incorrect")
                return False

        self.logi.appendMsg("PASS - All highlights metrics were verified")
        return True
    
    
    ####################################################################################################################
    # Function getDataTable returns array with the common data table on specific container 
    # Params:
    #         rContainer: Container webelement where the table is
    #         isCompare: Takes the data as trend percentage value and signs it as per trend icon (decrease with -) and adds tooltip values as an array
    # Return: array of data table values including titles on row 0
    ####################################################################################################################
    def getDataTable(self,rContainer, isCompare = False):
        tData = []
        rowData = []
        
        try:
            self.logi.appendMsg("INFO - Going to get data table values...")
            
            dataHeaders = rContainer.find_elements_by_xpath(DOM.ANALYTICS_TABLE_HEADERS)
            for headerX in dataHeaders:
                rowData.append(self.general.convertUnicodeToStr(headerX.text))
            tData.append(rowData)
            
            pagesTotal = self.pagerNav(rContainer, Enums.PagerNav.LAST)
            self.pagerNav(rContainer, Enums.PagerNav.FIRST)
            for pageCount in range(pagesTotal):
            
                if pageCount > 0:
                    self.pagerNav(rContainer, Enums.PagerNav.NEXT)
                    time.sleep(2)
                
                dataRows = rContainer.find_elements_by_xpath(DOM.ANALYTICS_TABLE_ROWS)
                for rowY in dataRows:
                    rowColumns = rowY.find_elements_by_xpath(DOM.ANALYTICS_TABLE_ROW_COLUMNS)
                    rowData = []
                    
                    for rowX in rowColumns:
                        rowText = rowX.text
                        rowText = self.cleanStr(rowText)
                        rowText = self.general.convertUnicodeToStr(rowText)
                                                
                        if isCompare and len(rowData)>0:
                            
                            if rowText!="":
                                iconClass = rowX.find_element_by_xpath(".//i").get_attribute("class")
                                if iconClass == "icon-regression":
                                    rowText = "-" + rowText
                            
                            rowValues = []
                            rowValues.append(rowText)
                            
                            trendCont = self.general.get_element_from_container(rowX, DOM.ANALYTICS_TREND_LABEL)
                            if str(trendCont) != "False":
                                tooltipData = self.getTrendTooltip(trendCont)
                                rowValues.append(tooltipData)
                            
                            rowData.append(rowValues)

                        else:
                            rowData.append(rowText)
                    
                    tData.append(rowData)  
        except:
            self.logi.appendMsg("FAIL - Cannot get data table values")
            tData = []
            
        return tData
    
    ####################################################################################################################
    # Function pagerNav navigates pager control through command buttons and page number
    # Params:
    #         rContainer: Container webelement where the object is
    #         pagerCommand: enum Enums.PagerNav values: NEXT,PREV,LAST,FIRST,PAGE
    #         pageNo: pager number direct access to pager control visible page only in case PAGE command used
    # Return: active page number 
    ####################################################################################################################
    def pagerNav(self, rContainer, pagerCommand, pageNo = 1):
        try:
            
            if pagerCommand == Enums.PagerNav.NEXT:
                doPager= rContainer.find_element_by_xpath(DOM.ANALYTICS_PAGER_NEXT)
            elif pagerCommand == Enums.PagerNav.PREV:
                doPager= rContainer.find_element_by_xpath(DOM.ANALYTICS_PAGER_PREV)
            elif pagerCommand == Enums.PagerNav.LAST:
                doPager= rContainer.find_element_by_xpath(DOM.ANALYTICS_PAGER_LAST)
            elif pagerCommand == Enums.PagerNav.FIRST:
                doPager= rContainer.find_element_by_xpath(DOM.ANALYTICS_PAGER_FIRST)
            else:
                doPager= rContainer.find_element_by_xpath(DOM.ANALYTICS_PAGER_PAGE_NO.replace('TEXTTOREPLACE', str(pageNo)))
            
            doPager.click()
            self.general.waitForSpinnerToFinish()
            time.sleep(1)
            
            currentPage = rContainer.find_element_by_xpath(DOM.ANALYTICS_PAGER_ACTIVE_PAGE)
            activePage = int(currentPage.text)
                                    
        except:
            self.logi.appendMsg("FAIL - Cannot navigate pager")
            activePage = 0
        
        return activePage
    
    ####################################################################################################################
    # Function cleanStr cleans string obtained from table or tooltip webelement (unicode)
    # Params:
    #         dirtyStr: Dirty string (unicode)
    # Returns: String with no special characters (unicode)
    ####################################################################################################################
    def cleanStr(self,dirtyStr):
        dirtyStr = dirtyStr.replace("\n\u2022","")
        cleanStr = " ".join(dirtyStr.split())
        cleanStr = cleanStr.strip()
        return cleanStr
    
    ####################################################################################################################
    # Function calcTrend calculates trend for compare mode (rounded no decimal points)
    # Params:
    #         previousValue = previous period value - numeric -mandatory
    #         currentValue = current period value - numeric - mandatory
    # Returns: trend integer value (if not possible to calculate returns False)
    ####################################################################################################################
    def calcTrend(self, previousValue, currentValue):
        try:
            trendResult = int(ceil((currentValue-previousValue)/float(previousValue)*100))
        except:
            self.logi.appendMsg("FAIL - Cannot calculate trend")
            return False
        return trendResult
    
    ####################################################################################################################
    # Function getTrendTooltip get tooltip data from trend hover on compare mode
    # Params:
    #         trendElement = webelement to hover trend value to obtain tooltip
    # Returns: array with tooltip data
    ####################################################################################################################
    def getTrendTooltip(self, trendElement):
        trendList = []
        try:
            
            ActionChains(self.Wd).move_to_element(trendElement).perform()
            time.sleep(0.5)
            tooltipList = self.Wd.find_elements_by_xpath(DOM.ANALYTICS_COMPARE_TOOLTIP)
            
            for toolVal in tooltipList:
                time.sleep(0.5)
                periodDate = self.general.convertUnicodeToStr(toolVal.find_element_by_xpath(DOM.ANALYTICS_COMPARE_TOOLTIP_DATE).text)
                periodDate = periodDate.replace("\n", "")
                trendList.append(periodDate)
                periodValue = self.general.convertUnicodeToStr(toolVal.find_element_by_xpath(DOM.ANALYTICS_COMPARE_TOOLTIP_VALUE).text)
                periodValue = periodValue.replace("\n", "")
                trendList.append(periodValue)
        
        except:
            
            self.logi.appendMsg("FAIL - Cannot obtain trend tooltip data")
            trendList = []
        
        return trendList
    
    ####################################################################################################################
    # Function evalTrendTooltip evaluates the trend calculation from tool tip and trend obtained strings. The function normalize values for different units like MB/GB/TB.
    # Params:
    #        trendStr = Trend string as obtained from data table/highligh/graph
    #        prevStr = Tool tip previous value string as obtained from data table/highligh/graph (including measurement unit)
    #        curStr = Tool tip current value string as obtained from data table/highligh/graph (including measurement unit)
    #        threshold: permitted variation on calculation result in percentage - default = 5 (5% less or 5% more from expected result)
    # Return: True:Trend is OK - False: trend not match formula calculation
    ####################################################################################################################
    def evalTrendTooltip(self, trendStr, prevStr, curStr, threshold = 5 ):
        verifTrend = True
         
        try:
            
            trendStr = self.general.stripNumber(trendStr)
            
            if trendStr != "":
                
                trendValue = self.general.convertTextToNumber(trendStr)
                
                # normalize values to effective comparison
                previousValue = self.normalizeMetric(prevStr)
                currentValue = self.normalizeMetric(curStr)
                
                calcTrend = self.calcTrend(previousValue, currentValue)
                
                if str(calcTrend)!="False":
                    expectedTrend = str(calcTrend)
                    thresholdValue = abs(calcTrend * threshold/100)
                    
                    if not (calcTrend-thresholdValue <= trendValue <= calcTrend+thresholdValue):
                        verifTrend = False
                else:
                    
                    expectedTrend = "(cannot be calculated)"
                    verifTrend = False
            else:
                
                trendStr = "-"
                if prevStr == "" or self.normalizeMetric(prevStr) == 0 or prevStr == "0" or self.general.stripNumber(prevStr) == "0":
                    expectedTrend = "-"
                else:
                    expectedTrend = "(cannot be calculated)"
                    verifTrend = False
            
            if not(verifTrend):
                self.logi.appendMsg("FAIL - Trend expected : " + expectedTrend + " %  -  actual: " + str(trendValue) + " % - threshold: +/- " + str(threshold) + " % from the expected result")
                
        except:
            self.logi.appendMsg("FAIL - Cannot evaluate Trend %")
            return False
        
        return verifTrend
           
    ####################################################################################################################
    # Function verifyTrendTable calculates the trend percentages on the table got from getDataTable are OK
    # Params:
    #        trendTable: array of compare mode table obtained from getDataTable function
    #        threshold: permitted variation on calculation result in percentage - default = 5 (5% less or 5% more from expected result)
    #        minCorrect: minimum percentage of correct values to consider the table correct - default 90 (%)
    # Return: True, False
    ####################################################################################################################
    def verifyTrendTable(self, trendTable, threshold = 5, minCorrect = 90):
        try:
            verifTrend = True
            notCorrect = 0
            self.logi.appendMsg("INFO - Going to verify trend data table.")
            iRow = 0
            for rowTable in trendTable:
                
                iCol = 0
                if iRow>0:
                    for colTable in rowTable:
                        if iCol>0:
                            
                            verifCol = self.evalTrendTooltip(colTable[0], colTable[1][1], colTable[1][3])
                            
                            if not verifCol:
                                
                                self.logi.appendMsg("FAIL - Trend % calculation for " + trendTable[0][iCol] + " on " + trendTable[iRow][0])
                                notCorrect = notCorrect + 1

                        iCol += 1
                
                iRow += 1
    
            if ceil((1-(notCorrect/((iCol-1)*(iRow-1))))*100) >= minCorrect:
                self.logi.appendMsg("PASS - More than " + str(minCorrect)+ " % of the table values are correct.")
                verifTrend = True
            else:
                self.logi.appendMsg("FAIL - Less than " + str(minCorrect)+ " % of the table values are correct.")
                verifTrend = False
                    
        except:
            self.logi.appendMsg("FAIL - Cannot verify trend data table")
            return False
        
        return verifTrend
    
    ####################################################################################################################
    # Function compareGraphDateTable verifies dates table values and line graphs values for metrics are the same on each tab
    # Params:
    #         rContainer: Container webelement where the table is
    #         sectionTabs: Expected tabs name comma-separated - string in the form "tab1,tab2,tabN"- mandatory
    #         columnOrder: comma separated values in the form tab:column on the table, tab starting from 1 - example: "1:1,2:3,3:2,4:4"  - default ="" (all tabs in same column order)
    #         compareMode: indicates the graph and table are on normal or compare mode - boolean - default=False (normal mode)
    #         threshold: permitted variation on calculation result in percentage - default = 1 (1% less or 1% more from expected result)
    #         separatorChar: separator char for sets on sectionTabs and columnOrder parameter - default=","
    #         dateTable: optional parameter allowing evaluate an external date table array - default="" (the function will parse the date table)
    #         kmcDateFormat: current KMC date format setting - default="MM/DD/YYYY"
    # Return: True - Passed  , False - Failed
    ####################################################################################################################
    def compareGraphDateTable(self, rContainer, sectionTabs, columnOrder = "", compareMode = False, threshold = 1, separatorChar = ",", dateTable = "", kmcDateFormat = "MM/DD/YYYY"):
        
        dataOK = True
        
        try:
            
            # obtain data table (if not passed as parameter)
            if dateTable == "":
                dateTable = self.getDataTable(rContainer, compareMode)
            
            # verify first/last table period match date widget
            self.logi.appendMsg("INFO - Going to verify table period match date widget...")
            
            self.Wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(2)
            
            dateWidget = self.getDateRange()
            
            firstDate = dateTable[1][0].strip()
            lastDate = dateTable[(len(dateTable)-1)][0].strip()
            
            isDaily = self.isGraphPeriod("Daily", verbose = False, rContainer = rContainer)
            
            if isDaily:
                
                firstDate = self.normalizeDate(firstDate, kmcDateFormat)
                lastDate = self.normalizeDate(lastDate, kmcDateFormat)
                    
            else:
                
                for dateX in range(len(dateWidget)):
                    strToDate= datetime.strptime(dateWidget[dateX],"%Y-%m-%d").date()
                    dateWidget[dateX] = strToDate.strftime("%B %Y")
                
            if firstDate == dateWidget[0]:
                self.logi.appendMsg("PASS - First table date: " + firstDate)
            else:
                self.logi.appendMsg("FAIL - First table date: " + firstDate + "does not match date widget start date: " + dateWidget[0])
                dataOK = False
                
            if lastDate == dateWidget[1]:
                self.logi.appendMsg("PASS - Last table date: " + lastDate)
            else:
                self.logi.appendMsg("FAIL - Last table date: " + lastDate + "does not match date widget end date: " + dateWidget[1])
                dataOK = False
            
            # Verify the trend percentage calculation on data table for compare mode
            if compareMode:
               dataOK = self.verifyTrendTable(trendTable = dateTable)
                
            # if all OK check graphs in tabs
            if dataOK:
            
                metricOrder = columnOrder.split(separatorChar)
                tabsCompare = sectionTabs.split(separatorChar)
                tabCount = 0
                for tabs in tabsCompare:
                    
                    tabOK = True
                    
                    # calculates proper table column to compare with current tab graph
                    tabCount += 1
                    if columnOrder == "":
                        currentColumn = tabCount
                    else:
                        try:
                            
                            currentColumn = -1
                            for xOrder in range(len(metricOrder)): 
                                orderElem = metricOrder[xOrder].split(":")
                                if tabCount == int(orderElem[0]):
                                    currentColumn = int(orderElem[1])
                                    break
                                
                        except:
                            currentColumn = -1
                    
                    # obtain graph point values
                    self.logi.appendMsg("INFO - Going to get " + tabs + " graph values...")
                    
                    rContainer.find_element_by_xpath("." + DOM.ANALYTICS_REPORT_TAB.replace("TAB_NAME", tabs)).click()
                    time.sleep(2)
                    
                    grContainer = rContainer.find_element_by_xpath("." + DOM.ANALYTICS_REPORT_CHART)
                    canvasWidth =  int(grContainer.find_element_by_xpath(DOM.ANALYTICS_GRAPH_CANVAS).get_attribute("width"))
                    graphTooltips = self.getGraphTooltips(rContainer, isCompareMode = compareMode)
                    
                    self.logi.appendMsg("INFO - " +str(len(graphTooltips))+ " tool tips found")
                    
                    if currentColumn >= 0 and len(graphTooltips) > 0:
                        
                        self.logi.appendMsg("INFO - Going to verify " + tabs + " table and graph values...")
                        
                        for xTooltip in range(len(graphTooltips)):
                        
                            if not compareMode:
                                
                                # calculate graph and column date and metric values
                                colElem = dateTable[xTooltip+1][currentColumn]
                                colDate = dateTable[xTooltip+1][0].strip()
                                
                                graphElem = graphTooltips[xTooltip]
                                graphData = graphElem.split()
                                graphDate = graphData[0].strip()
                                
                                extractFrom = 1
                                if not isDaily:  # if period is set to Monthly adjust date and metric value content
                                    graphDate += " " + graphData[1].strip()
                                    extractFrom = 2
                                graphMetric = ""
                                for xVal in range(extractFrom, len(graphData)):
                                    graphMetric += graphData[xVal]
                                                                
                                # strip from metric text label (if exist)
                                labeledMetric = graphMetric.split(":")
                                graphMetric= labeledMetric[len(labeledMetric)-1]
                                
                                # normalize values to effective comparison
                                graphValue = self.normalizeMetric(graphMetric)
                                colValue = self.normalizeMetric(colElem)
                                        
                                # compare graph and column dates, if OK then compare metrics
                                if colDate!=graphDate:
                                    self.logi.appendMsg("FAIL - Table date for " + dateTable[0][currentColumn] + " : " + colDate + " different than graph date on tool tip: " + graphDate)
                                    tabOK = False
                                else:
                                    # compare metric values with threshold
                                    thresholdValue = abs(colValue * threshold/100)
                                    if not (colValue-thresholdValue <= graphValue <= colValue+thresholdValue):
                                        self.logi.appendMsg("FAIL - Table value for " + dateTable[0][currentColumn] + " column on " + colDate + " : " + colElem + " different than graph tool tip : " + graphElem + " (normalized values compared if relevant)")
                                        tabOK = False
                                   
                            else:
                                
                                tabOK = False
                                
                                
                    else:
                        self.logi.appendMsg("FAIL - Cannot verify table column or tool tips for " + tabs + " graph")
                        tabOK = False
                    
                    if tabOK:
                        self.logi.appendMsg("PASS - Dates data table metrics values match graphs on tab " + tabs)
                    else:
                        self.logi.appendMsg("FAIL - Some data table values not match date widget or graphs on tab " + tabs)
                        dataOK = False
            
        except:
            self.logi.appendMsg("FAIL - Cannot verify data table and graph values")
            return False
        
        if dataOK:
            self.logi.appendMsg("PASS - Dates data table metrics values match graphs")
        else:
            self.logi.appendMsg("FAIL - Some data table values not match date widget or graphs")
        
        return dataOK
    
    ####################################################################################################################
    # Function setTableMenu sets dimension menu on data table of graph
    # Params:
    #         rContainer: Container webelement - mandatory
    #         strOption: Menu option- string - mandatory
    ####################################################################################################################
    def setTableMenu(self, rContainer, menuOption):
        res = True
        try:
            
            self.logi.appendMsg("INFO - Going to select dimensions menu option " + menuOption)
            dMenu= rContainer.find_element_by_xpath(DOM.ANALYTICS_TABLE_DIMENSION_MENU)
            dMenu.click()
            #general.waitForSpinnerToFinish()
            time.sleep(1)
            
            dynamicDOM = DOM.ANALYTICS_TABLE_SELECT_MENU_OPTION.replace('TEXTTOREPLACE', menuOption)
            dOption = dMenu.find_element_by_xpath(dynamicDOM)
            dOption.click()
            #general.waitForSpinnerToFinish()
            time.sleep(1)
            
        except:
            
            self.logi.appendMsg("FAIL - Selecting dimension menu option")
            res = False
        
        return res
    
    ####################################################################################################################
    # Function compareAccumulativeDateTable verifies dates table values and accumulative values for metrics are the same
    # Params:
    #         rContainer: Container webelement where the table is
    #         sectionTabs: Expected accumulative metrics name comma-separated - string in the form "metric1,metric2,metricN"- mandatory
    #         columnOrder: comma separated values in the form metric:column on the table, metric starting from 1 - example: "1:1,2:3,3:2,4:4"  - default ="" (all metrics in same column order)
    #         compareMode: indicates the graph and table are on normal or compare mode - boolean - default=False (normal mode)
    #         threshold: permitted variation on calculation result in percentage - default = 1 (1% less or 1% more from expected result)
    #         separatorChar: separator char for sets on sectionTabs and columnOrder parameter - default=","
    #         dateTable: optional parameter allowing evaluate an external date table array - default="" (the function will parse the date table)
    # Return: True - Passed  , False - Failed
    ####################################################################################################################
    def compareAccumulativeDateTable(self, rContainer, sectionMetrics ,columnOrder = "", compareMode = False, threshold = 1, separatorChar = ",", dateTable = ""):
        dataOK = True
        try:
            isDaily = self.isGraphPeriod("Daily", verbose = False, rContainer = rContainer)
            
            self.logi.appendMsg("INFO - Getting metrics accumulative values...")
            accElem = self.getAccumulativeItems(rContainer, compareMode)
            
            if accElem != []:
                
                # if Daily mode is set obtain table on Monthly mode since calculation is based on monthly values always
                if isDaily:
                    self.logi.appendMsg("INFO - Getting table values in Monthly period mode (needed for calculations)...")
                    self.setGraphPeriod("Monthly", 1, rContainer)
                    dateTable = self.getDataTable(rContainer, compareMode)
                    self.setGraphPeriod("Daily", 1, rContainer)
                else:
                    # obtain data table (if not passed as parameter)
                    if dateTable == "":
                        dateTable = self.getDataTable(rContainer, compareMode)
                
                metricOrder = columnOrder.split(separatorChar)
                metricsCompare = sectionMetrics.split(separatorChar)
                metricCount = 0
                for metricsName in metricsCompare:
                    
                    metricStr = ""
                    for accMetric in accElem:
                        if accMetric[0] == metricsName:
                            metricStr = accMetric[1]
                    
                    if metricStr != "":
                        # calculates proper table column to compare with current accumulative metric
                        metricCount += 1
                        if columnOrder == "":
                            currentColumn = metricCount
                        else:
                            
                            try:
                                currentColumn = -1
                                for xOrder in metricOrder: 
                                    orderElem = xOrder.split(":")
                                    if metricCount == int(orderElem[0]):
                                        currentColumn = int(orderElem[1])
                                        break
                            except:
                                currentColumn = -1
                        
                        if currentColumn >= 0:
                            
                            if not compareMode:
                                # compare metric values with table
                                self.logi.appendMsg("INFO - Going to verify " + metricsName + " accumulative value...")
                                accValue = self.normalizeMetric(metricStr)
                                
                                totalMetric = 0
                                for xTable in range(1,len(dateTable)):
                                    totalMetric += self.normalizeMetric(dateTable[xTable][currentColumn])
                                
                                thresholdValue = abs(accValue * threshold/100)
                                if not (accValue-thresholdValue <= totalMetric <= accValue+thresholdValue):
                                    self.logi.appendMsg("FAIL - Table value of " + metricsName + ": " + metricStr + " (normalized: " + str(accValue) + ") different than total from table: " + str(totalMetric) + " (normalized values compared if relevant)")
                                    dataOK = False
                        
                        else:
                            
                            self.logi.appendMsg("FAIL - Cannot get column metric value.")
                            dataOK = False
                            
                    else:
                         self.logi.appendMsg("FAIL - Cannot get accumulative metric value.")
                         dataOK = False
                                
            else:
                self.logi.appendMsg("FAIL - No Accumulative metrics to compare.")
                dataOK = False
                
        except:
            self.logi.appendMsg("FAIL - Cannot compare Accumulative totals")
            dataOK = False
        
        if dataOK:
            self.logi.appendMsg("PASS - Accumulative totals match table columns")
        else:
            self.logi.appendMsg("FAIL - Some Accumulative totals not match table columns or cannot be calculated")
        
        return dataOK
    
    ####################################################################################################################
    # Function getAccumulativeItems get array of label and value of each item of the accumulative object
    # Params:
    #         rContainer: Container webelement where the accumulative object is
    #         compareMode: indicates the accumulative report is on normal or compare mode - boolean - default=False (normal mode)
    # Return: array with all the items of the Accumulative object
    ####################################################################################################################
    def getAccumulativeItems(self, rContainer, compareMode = False):
        accItems = []
        try:
            
            accTitles = rContainer.find_elements_by_xpath(DOM.ANALYTICS_ACCUMULATIVE_ITEM_TITLE)
            accValues = rContainer.find_elements_by_xpath(DOM.ANALYTICS_ACCUMULATIVE_ITEM_VALUE)
            
            for xValue in range(len(accTitles)):
                
                completeItem = [accTitles[xValue].text,accValues[xValue].text]
                for xText in range(len(completeItem)):
                    completeItem[xText] = self.general.convertUnicodeToStr(self.cleanStr(completeItem[xText])).strip()
                
                accItems.append(completeItem)
                
        except:
            
            self.logi.appendMsg("FAIL - Cannot get items from Accumulative object")
            accItems = []
        
        return accItems
    
    ####################################################################################################################
    # Function normalizeMetric return normalized float value from metric string obtained from too ltip or data table element
    #          Normalizations: - if the string contains MB/TB/GB units it will return the value converted to MB
    #                          - all other units the value is stripped from unit returned as is (float)
    # Params:
    #        metricStr: metric value string obtained from tool tip or data table element including units (e.g. "10.2 TB")
    #        precision: decimal points- default = 6
    #        stripLabel: strips metric label separated by ":" if exist - default = True
    # Return: float value of the metric
    ####################################################################################################################
    def normalizeMetric(self, metricStr, precision = 6, stripLabel = True):
        fileUnits = ["GB","TB"]
        
        try:
            
            if stripLabel:
                labeledMetric = metricStr.split(":")
                metricStr = labeledMetric[len(labeledMetric)-1]
            
            mUnit = self.general.stripNoNumber(metricStr)
            mStr = self.general.stripNumber(metricStr)
            normalMetric = self.general.convertTextToNumber(mStr)
            
            if mUnit in fileUnits:
                normalMetric = self.general.convertFileSize(normalMetric, mUnit, "MB", precision)
        
        except:
            
            self.logi.appendMsg("FAIL - Cannot normalize metric.")
            return False
        
        return normalMetric
    
    ####################################################################################################################
    # Function normalizeDate return normalized date string in the format "YYYY-MM-DD" from date obtained from tooltips/tables/graphs
    #          
    # Params:
    #        dateStr: date string on current KMC date format - string
    #        kmcDateFormat: current KMC date format - string
    # Return: date string in format "YYYY-MM-DD"
    ####################################################################################################################
    def normalizeDate(self,dateStr, kmcDateFormat = "MM/DD/YYYY"):
        try:
            
            dateValues = dateStr.split("/")
            if kmcDateFormat == "DD/MM/YYYY":
                
                # DD/MM/YYYY
                normalDate = dateValues[2] + "-" + dateValues[1] + "-" + dateValues[0]
                
            else:
                
                # MM/DD/YYYY
                normalDate = dateValues[2] + "-" + dateValues[0] + "-" + dateValues[1]
                
        except:
            
            self.logi.appendMsg("FAIL - Cannot normalize date.")
            normalDate = ""
        
        return normalDate