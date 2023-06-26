'''
Created on 27 May 2019

@author: moran.cohen
'''

import datetime
import time
from time import strptime

import DOM
import KmcBasicFuncs
import MySelenium


####ADDED to compare XML to EXCEL
# init excel
# init xml

class SchedulingFuncs(object):
    
    
    def __init__(self, webdrvr, logi):
        
        self.Wd = webdrvr
        self.logi = logi
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        
        
        
    def SetSchedulingDate(self,FlagEndDate,Day,Month,Year):
             
        try:        
            # Set startDate.Year                
            self.Wd.find_element_by_xpath(DOM.SCHEDULING_STARTDATE_YEAR.replace("TEXTTOREPLACE",Year)).click()
            # Set startDate.Month
            self.Wd.find_element_by_xpath(DOM.SCHEDULING_STARTDATE_MONTH.replace("TEXTTOREPLACE",Month)).click()
            # Set startDate.Day
            FindDayResult=False
            for i in range(1,7):
                if FindDayResult == True:
                    break
                for x in range(1,8):
                    SchedulingDay = DOM.SCHEDULING_STARTDATE_DAY.replace("row",str(i))
                    SchedulingDay = SchedulingDay.replace("col",str(x))
                    if self.Wd.find_element_by_xpath(SchedulingDay).text == Day:
                        self.Wd.find_element_by_xpath(SchedulingDay).click()
                        FindDayResult=True
                        break
                    else:
                        FindDayResult=False
                    
            if FindDayResult == False:
                self.logi.appendMsg("FAIL - Day is not found. Day = " + Day)
                return False                            
                        
            # Verify that scheduling startDate is save in the textbox UI    
            self.logi.appendMsg("INFO - Going to check Scheduling date from UI" )
            if FlagEndDate == False:
                Scheduling_DateText = self.Wd.find_element_by_xpath(DOM.SCHEDULING_STARTDATE_TEXT).get_attribute("value")
            else:
                Scheduling_DateText = self.Wd.find_element_by_xpath(DOM.SCHEDULING_ENDDATE_TEXT).get_attribute("value")
                                      
            if Scheduling_DateText == "":
                self.logi.appendMsg("FAIL - Set of Scheduling startDate. Expected_Date= " +  Day + "/" + Month + "/" + Year + " ,  Actual_Date= EMPTY")
            else: # Compare between actual UI result to expected date 
                # Actual date UI result  
                date_time_obj = datetime.datetime.strptime(Scheduling_DateText,'%m/%d/%Y %H:%M')
                Actual_day = int(date_time_obj.day)
                Actual_month =  int(date_time_obj.month)
                Actual_year =  int(date_time_obj.year)
                
                # Change string Month to int
                word = Month
                new = word[0].upper() + word[1:3].lower()
                Expected_NumStartMonth = int(strptime(new,'%b').tm_mon)
                Expected_NumStartDay = int(Day)
                Expected_NumStartYear = int(Year)
                            
                # Compare actual to expected date
                CompareStatus = True
                if Actual_day != Expected_NumStartDay:
                    self.logi.appendMsg("FAIL - Comparison between Actual_day to Expected_NumStartDay. Actual_day= " +  Actual_day + " ,  Expected_Day= " + Expected_NumStartDay)
                    self.logi.appendMsg("FAIL - Comparison between Expected to Actual date. Expected_Date= " +  Day + "/" + Month + "/" + Year + " ,  Actual_sDate= " + str(date_time_obj.date()))
                    CompareStatus = False
                if Actual_month != Expected_NumStartMonth:
                    self.logi.appendMsg("FAIL - Comparison between Actual_month to Expected_NumMonth. Actual_month= " +  Actual_month + " ,  Expected_Month= " + Expected_NumStartMonth)
                    self.logi.appendMsg("FAIL - Comparison between Expected to Actual date. Expected_Date= " +  Day + "/" + Month + "/" + Year + " ,  Actual_Date= " + str(date_time_obj.date()))
                    CompareStatus = False
                if Actual_year != Expected_NumStartYear:
                    self.logi.appendMsg("FAIL - Comparison between Actual_year to Expected_NumYear. Actual_year= " +  Actual_year + " ,  Expected_NumYear= " + Expected_NumStartYear)
                    self.logi.appendMsg("FAIL - Comparison between Expected to Actual date. Expected_Date= " +  Day + "/" + Month + "/" + Year + " ,  Actual_Date= " + str(date_time_obj.date()))
                    CompareStatus = False
                                
                if CompareStatus == True:
                    self.logi.appendMsg("PASS - Scheduling startDate.  Expected_Date= " +  Day + "/" + Month + "/" + Year + " ,  Actual_Date= " + str(date_time_obj.date()))
                else:
                    self.logi.appendMsg("FAIL - Scheduling startDate.  Expected_Date= " +  Day + "/" + Month + "/" + Year + " ,  Actual_Date= " + str(date_time_obj.date()))
                    return False
                
                return True
                                  
        except Exception as e:
            print(e)
            return False
                        
        
        
    def setSchedulingToEntry(self,entryname_id,SchedulingEnable,StartDay,StartMonth,StartYear,EndDay,EndMonth,EndYear):  
        
        try:
            enableEndDate=False
            if StartDay==None or StartMonth==None or StartYear == None:
                StartDay=""
                StartMonth=""
                StartYear=""
            if StartDay==EndDay or EndMonth==None or EndYear == None:
                EndDay=""
                EndMonth=""
                EndYear=""
            else:
                enableEndDate = True
                    
            self.logi.appendMsg("INFO- Going to set scheduling- StartDate=" + str(StartDay) + "/" + str(StartMonth) + "/" + str(StartYear) + ", EndDate= " + str(EndDay) + "/" + str(EndMonth) + "/" + str(EndYear) + " to entry- " + str(entryname_id))
            
            # Go to entries tab
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click() 
            time.sleep(3)
            self.logi.appendMsg("INFO - Going to select entry. ENTRY = " + entryname_id )
            rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, entryname_id, True)
            if not rc:
                self.logi.appendMsg("FAIL - could not find the entry- " + entryname_id + " in entries table")
                return False
            
            self.logi.appendMsg("INFO - Going to scheduling tab")      
            # Go to entry scheduling
            self.Wd.find_element_by_xpath(DOM.ENTRY_SCHEDULING).click()
            if SchedulingEnable==False:
                self.logi.appendMsg("INFO - Going to set Anytime") 
                self.Wd.find_element_by_xpath(DOM.SCHEDULING_ANYTIME_RB).click() 
            else:
                #******* Set Scheduling dates ************************
                self.logi.appendMsg("************* INFO - Going to set Scheduling StartDate. Expected_startDate= " +  StartDay + "/" + StartMonth + "/" + StartYear )
            
                time.sleep(3)
                self.Wd.find_element_by_xpath(DOM.SCHEDULING_SCHEDULED_RB).click()
                time.sleep(1)
                # Update startDate
                self.Wd.find_element_by_xpath(DOM.SCHEDULING_STARTDATE_BTN).click()
                time.sleep(2)
                rc = self.SetSchedulingDate(False,StartDay,StartMonth,StartYear)                
                if not rc:
                    self.logi.appendMsg("FAIL - SetSchedulingDate StartDate. Expected_startDate= " +  StartDay + "/" + StartMonth + "/" + StartYear )
                    return False
                else:
                    self.logi.appendMsg("PASS - SetSchedulingDate StartDate. Expected_startDate= " +  StartDay + "/" + StartMonth + "/" + StartYear )
            
                time.sleep(3)
                #******* Set EndDate Scheduling ************************
                if enableEndDate == True:
                    # Verify what is the checkbox status
                    checkboxEndDate = self.Wd.find_element_by_xpath(DOM.SCHEDULING_ENDDATE_CB).get_attribute("class").find("active")
                    if checkboxEndDate == -1: 
                        # Click on the enddate button
                        self.Wd.find_element_by_xpath(DOM.SCHEDULING_ENDDATE_CB).click()
                    else:
                        # Close the start date window
                        self.Wd.find_element_by_xpath(DOM.SCHEDULING_SCHEDULED_RB).click()
                    time.sleep(1)
                    # Open end date window
                    self.Wd.find_element_by_xpath(DOM.SCHEDULING_ENDDATE_BTN).click()
                    time.sleep(2)         
                    self.logi.appendMsg("************** INFO - Going to set EndDate Scheduling. Expected_EndDate= " +  EndDay + "/" + EndMonth + "/" + EndYear )
                    
                    rc = self.SetSchedulingDate(True,EndDay,EndMonth,EndYear)
                    if not rc:
                        self.logi.appendMsg("FAIL - SetSchedulingDate EndDate. Expected_EndDate= " +  EndDay + "/" + EndMonth + "/" + EndYear )
                        return False
                    else:
                        self.logi.appendMsg("PASS - SetSchedulingDate EndDate. Expected_EndDate= " +  EndDay + "/" + EndMonth + "/" + EndYear )
                        
                                   
                # Save entry
                self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()
                time.sleep(3)
            
            # Go to entries tab
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click() 
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(e)
            return False