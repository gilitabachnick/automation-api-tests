################################################################
#
# This function library contain all Atomic reusable
#
# functions related to the New Kmc
#
# date created: 7.5.17
#
# author: Adi Miller
#
################################################################


import datetime
import os
import re
import subprocess
import time
import sys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import DOM
import Entrypage
import autoitWebDriver
import uploadFuncs

class basicFuncs:
    
    def invokeLogin(self, webdrvr, Wdobj, url, user, pwd): 
        webdrvr.get(url)
        webdrvr.implicitly_wait(10)
        rc = self.wait_element(webdrvr, DOM.LOGIN_USER)
        if rc == False:
            if Wdobj.Sync(webdrvr,DOM.ENTRIES_TAB):
                # Login to KMS is done already
                return True
            else:
                # Failed login
                return False
        Wdobj.valToTextbox(webdrvr, DOM.LOGIN_USER, user)
        time.sleep(1)
        Wdobj.valToTextbox(webdrvr, DOM.LOGIN_PASS, pwd)
        webdrvr.find_element_by_xpath(DOM.LOGIN_SUBMIT).click()
        
        #time.sleep(10)
        popup = Wdobj.Sync(webdrvr, DOM.POPUP_MSG)
        if popup!=False:
            rc = self.selectOneOfInvisibleSameObjects(webdrvr, DOM.MSG_CLOSE)
            rc.click()
            time.sleep(5)
        # close the welcome message window
        try: 
            webdrvr.find_element_by_xpath(DOM.CATEGORY_PREFERENCES_POP)
            rc = self.selectOneOfInvisibleSameObjects(webdrvr,DOM.MSG_CLOSE)
            rc.click()
        except:
            pass
        
        if Wdobj.Sync(webdrvr,DOM.ENTRIES_TAB):
            return True
        else:
            return False
        
    # this function check or uncheck a row in table entries, rowNumber start in 0
    # if need to select more than one rows send it in format "1-7" 
    def CheckUncheckRowInTable(self, webdrvr, rowNumber=1):  
        if str(rowNumber).find("-")>=0:
            rowsArr = rowNumber.split("-")
            startRow = int(rowsArr[0])
            endRow = int(rowsArr[1])+1
            
        elif rowNumber!=0:
            startRow = rowNumber-1
            endRow = rowNumber
        
        if rowNumber==0:
            Entries = webdrvr.find_elements_by_xpath(DOM.GLOBAL_TABLE_HEADLINE)
            startRow = rowNumber
            endRow = rowNumber +1
        else:
            Entries = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)
            
        for i in range(startRow,endRow):
                
            chk = Entries[i].find_elements_by_xpath(DOM.ENTRY_CHECKBOX)
            try:
                chk[0].click()
                tmpstatus= True
            except:
                tmpstatus=  False
                
        return tmpstatus
        
    def isBulkActionsExsit(self, webdrvr):
        try:
            blkobj = webdrvr.find_element_by_xpath(DOM.ENTRIES_BULK_DIV)
            if blkobj.get_attribute('class').find('kHidden')==-1:
                return True
            else:
                return False
        except:
            return False
            
    
    def retNumberOfSelectedEntries(self, webdrvr):
        try:
            selectedEntriesNum = webdrvr.find_elements_by_xpath(DOM.SELECTED_ENTRIES)
            numOfSelected = len(selectedEntriesNum)
        
        except:
            numOfSelected = 0
            
        return  numOfSelected
    ###############################################################################
    # this function selects a refine filter by its path 
    # pthToselection - send the path to the selection 
    #            example: "Media Types;Audio"   
    # if you need multiple filters send , between topics and ; between sun node
    #             example: "Media Types;Audio,Durations;Long"
    ###############################################################################
    def selectRefineFilter(self,webdrvr,pthToselection,leaveOpen=False): 
        try:
            webdrvr.find_element_by_xpath(DOM.REFINE_BUTTON).click()
        except:
            return False
        
        filtArr = pthToselection.split(',')
        
        refineWin = webdrvr.find_element_by_xpath(DOM.REFIN_POP)
        refineRows = refineWin.find_elements_by_xpath(DOM.REFINE_SUBJECT_ROW)
        for filterNum in range(0,len(filtArr)):
            sonArr = filtArr[filterNum].split(';')
            for i in range(0,len(refineRows)):
                if refineRows[i].text.find(sonArr[0])!= -1:
                    if len(sonArr)==1:
                        refineRows[i].click()
                    else:
                        try:
                            refineRows[i].find_element_by_xpath(DOM.REFINE_EXPAND).click()
                        except:
                            pass
                        refineLeafes = refineRows[i].find_elements_by_xpath(DOM.REFINE_LEAF_SUBJECT_ROW)
                        for sonsNum in range(1,len(sonArr)):
                            for j in range(0,len(refineLeafes)):
                                if refineLeafes[j].text.find(sonArr[sonsNum])!= -1:
                                    refineLeafes[j].click()
                                    break
        if not leaveOpen:            
            try:        
                refineWin.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
            except:
                return False

    # function to verify selected active tag list
    # Needs webdriver logi and list of tags to check
    # tags_list (list of strings) - the tags to compare from the active filter, must be in the same order as the active filter list
    def verify_entrires_active_filter_selected(self, webdrvr, logi, tags_list):
        try:
            activeFilters = webdrvr.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
        except:
            if len(tags_list)==0:
                return True
            else:
                return False

        FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)

        for tag, tag2 in zip(tags_list, FilterTags):
            if tag == tag2.text:
                continue
            else:
                logi.appendMsg("FAIL - active filter dose not appear")
                return False

        return True

    # this function closes spesific filter tag, actually click on the close icon of the tag     
    def closeFilterTag(self, webdrvr, tagText):
        activeFilters = webdrvr.find_element_by_xpath(DOM.ENTRY_ACTIVE_FILTERS)
        FilterTags = activeFilters.find_elements_by_xpath(DOM.ENTRY_FILTERS_TAG)
        time.sleep(2)
        for i in FilterTags:
            if i.text == tagText:
                i.find_element_by_xpath(DOM.ENTRY_FILTER_TAG_CLOSE).click()
                break
        time.sleep(2)
        
    # this function create category filter 
    def selectCategoryFilter(self, webdrvr, filtertxt, closeFiltWind=True):
        FilterCat = webdrvr.find_element_by_xpath(DOM.CATEGORY_FILTER)
        FilterCat.click()
        time.sleep(2)
        webdrvr.find_element_by_xpath(DOM.CATEGORY_FIND).send_keys(filtertxt)
        time.sleep(2)
        try:
            webdrvr.find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_LIST).click()
        except Exception as e:
            print(e)
            print('No such Category name: ' + filtertxt) 
            return False
            
        time.sleep(1)
        
        if closeFiltWind:
            filterCategoryWin = webdrvr.find_element_by_xpath(DOM.CATEGORY_POP)
            try:
                filterCategoryWin.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
                
            except Exception as exp:
                print(exp)   
                return False  
        
        return True
    
    # this function set filter preference to category only or category and sub categories
    # send true in boolCatOnly if preferences needed to be set is "category only" otherwise send false
    def setFilrePreferences(self, webdrvr, boolCatOnly):
        # open filter category window
        try:
            webdrvr.find_element_by_xpath(DOM.CATEGORY_FILTER).click()
        except:
            return False
        
        # open preferences pop up
        try: 
            webdrvr.find_element_by_xpath(DOM.CATEGORY_FILTER_PREFERENCES).click()
        except:
            return False
        
        #popupWin = webdrvr.find_element_by_xpath(DOM.CATEGORY_PREFERENCES_POP)
        bttns = webdrvr.find_element_by_xpath (DOM.CATEGORY_FILTER_PREFRENCES_BTTNS)
        rdBtn = bttns.find_elements_by_xpath(DOM.CATEGORY_FILTER_PREFRENCES_RBTN)
        #rdBtn = popupWin.find_elements_by_xpath(DOM.CATEGORY_FILTER_PREFRENCES_RBTN)
        for i in rdBtn:
            if i.text .find("category only")!= -1 and boolCatOnly:
                i.click()
            if i.text .find("category only")== -1 and not boolCatOnly:
                i.click()
                
        
        webdrvr.find_elements_by_xpath(DOM.CATEGORY_PREFERENCES_CLOSE)[-1].click()  # If there was popup, use last
        time.sleep(1)
        webdrvr.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
        
    # this function returns category filter tree node line as an object by its text
    def retTreeNodeFilterlineObj(self, webdrvr, lineText):
        founded = False
        try:
            filtWindow = webdrvr.find_element_by_xpath(DOM.CATEGORY_FILTER_WIN)
            lines =  filtWindow.find_elements_by_xpath(DOM.CATEGORY_TREE_NODE_LINE)
            for i in (lines):
                if i.text.find(lineText)!=-1:
                    return i
                else:
                    continue
            
            if not founded:
                return None
        except:
            return None 
        
    
    # this function counts rows in entries table
    def retNumOfRowsInEntryTbl(self,webdrvr):    
        return len(webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW))
    
    # Function that uploads a file and waits for ready status
    # no_media - a media that is in ready state but has no flavours
    def upload_entry_and_wait_for_status_ready(self, webdriver, entryIdName, sendto, basicFuncs, logi, Wdobj, no_media=False):
        logi.appendMsg("INFO - Going to upload vod entry and verify upload")
        try:
            logi.appendMsg("INFO - going to upload file")
            webdriver.find_element_by_xpath(DOM.UPLOAD_BTN).click()
            try:
                uploadFromDesktop = webdriver.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            except:
                logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
                logi.reportTest('fail', sendto)
                return False

            uploadFromDesktop.click()
            time.sleep(5)

            if Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive()
                AWD = self.autoitwebdriver.retautoWebDriver()
                pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                # AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe',
                #                         pth + "\\" + entryIdName)
            else:
                pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                pth1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                #subprocess.call([pth1 + r'\openFile.exe', pth + "\\" + entryIdName])
            pthstr = str(os.path.abspath(os.path.join(pth, entryIdName)))
            uploadFuncs.uploadfuncs.windows_upload_dialog(self, pthstr)
            time.sleep(3)
            webdriver.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
            time.sleep(3)
            webdriver.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)
            webdriver.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)

            logi.appendMsg("INFO- going to wait until the entry will be in status ready or no media")
            entryStatus, lineText = basicFuncs.waitForEntryStatusReady(webdriver, os.path.splitext(entryIdName)[0], no_media=no_media)
            if not entryStatus:
                logi.appendMsg(
                    "FAIL - the entry " + entryIdName + " status was not changed to Ready after 5 minutes , this is what the entry line showed: " + lineText)
                return False
            else:
                logi.appendMsg("PASS - the entry " + entryIdName + " uploaded successfully")
                return True

        except Exception as Exp:
            print(Exp)
            logi.appendMsg("FAIL - step 2: FAILED to upload vod entry and verify upload")
            return False

        return True

    
    
    # this function wait until entry is in status ready
    def waitForEntryStatusReady(self,webdrvr, entryIdName , itimeout=300, no_media=False):
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(entryIdName + Keys.RETURN)
        
        time.sleep(3)
        
        entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
        bStatusReady = False
        #itimeout = 300
        startTime = time.time()
        while not bStatusReady:
            webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)
            try:
                lineText = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)[0].text
                if lineText.find("Ready") > 0:
                    bStatusReady = True
                elif no_media == True:
                    if lineText.find("No Media") > 0:
                        bStatusReady = True
                elif lineText.find("Deleted") > 0:
                    return self.fail_entry_status_exception()
                else:
                    time.sleep(1)
            except:
                return self.fail_entry_status_exception()
                
            if startTime + itimeout < time.time():
                return False,lineText
        
        return True,lineText

    # function for raised exception from waitForEntryStatusReady function
    def fail_entry_status_exception(self):
        return False, "NoEntry"

    # function to get the entry id by a give row - default is 0
    def get_entry_id(self, webdrvr, row_num=0):
        pattern = r"\d_........"
        return re.search(pattern, webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)[row_num].text).group(0)
    # By default, the function gets entry by name and return its duration.
    # Optionally, It can get value for desired duration to compare with actual one.
    # In case it's trim entry compared, it will wait for duration to be updated for specified timeout
    def retEntryDuration(self, webdrvr, entryIdName, compareDuration = False, isTrim = False, itimeout=600):
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(entryIdName + Keys.RETURN)
        trimDurationRight = True
        time.sleep(3)

        entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
        startTime = time.time()

        webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
        time.sleep(3)
        try:
            lineText = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)[0].text
            if lineText.find("Ready") > 0:
                if not isinstance(compareDuration, bool):
                    while lineText.find(compareDuration) < 0 and lineText.find(compareDuration[1:]) < 0:  # The second condition removes leading 0 in hours
                        if isTrim:  # Wait for duration in trim entry to be updated
                            time.sleep(5)
                            if startTime + itimeout < time.time():
                                trimDurationRight = False
                                break
                        else:
                            trimDurationRight = False
                            break
                values = lineText.split(' ')
                length = len(values)
                duration = values[length-3]
                if trimDurationRight:
                    return True, duration
                else:
                    return False, duration
            else:
                return False, 'Entry not ready'

        except Exception as Exp:
            print(Exp)
            return False, Exp

    #this function delete entry\s from entry table, if you need to delete more than one entry send the entries (name or id) with entriesSeparator=";" as delimiter by default (can be change the sign)
    # example: deleteEntries(wd,"a.jpg;b.wav")
    def deleteEntries(self,webdrvr,entries,entriesSeparator=";"):
        tmpstatus = True
        entriesArr =  entries.split(entriesSeparator)
        for entry in(entriesArr):
            webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
            webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(entry + Keys.RETURN)
            time.sleep(3)
            # if no results for the entry search continue to next entry
            try:
                webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                continue
            except:
                rc = self.CheckUncheckRowInTable(webdrvr, 0)
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_DELETE).click()
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.POPUP_MESSAGE_YES).click()
                time.sleep(3)
                entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
                try:
                    webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                    tmpstatus = True
                except:
                    tmpstatus = False
                
        return tmpstatus
    
    # this def returns the media type of an entry in a certain row in the table (lines start from 0)
    def retEntryMediaType(self, webdrvr, lineNum=1):
        Entries = webdrvr.find_elements_by_tag_name('tr')
        try:
            Entries[lineNum].find_element_by_xpath(DOM.ENTRY_TABLE_VIDEO_ICON)
            return "video"
        except:
            pass
        try:
            Entries[lineNum].find_element_by_xpath(DOM.ENTRY_TABLE_AUDIO_ICON)
            return "audio"
        except:
            pass
        try:
            Entries[lineNum].find_element_by_xpath(DOM.ENTRY_TABLE_IMAGE_ICON)
            return "image"
        except:
            return False
    
    
    # this entry only create simple searches for entry in entry table
    #  send entry name or id in entryNameId 
    def searchEntrySimpleSearch(self,webdrvr, entryNameId, exact_search=False):
        try:
            searchField = webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES)
            searchField.send_keys(Keys.CONTROL, 'a')
            if exact_search:
                searchField.send_keys('"' + entryNameId + '"' + Keys.RETURN)
            else:
                searchField.send_keys(entryNameId + Keys.RETURN)
            time.sleep(3)
            return True
        except:
            return False

    # after searching for an entry with searchEntrySimpleSearch verify the result
    # Function is meant to find only 1 entry
    # search_info (string) - what was expected to search
    def verify_entry_search_result(self, wd, logi, search_info):
        # verify the entry appears when searching by its category
        logi.appendMsg("INFO - goning to search in the entry filter and verify it appears")
        numOfEntriesFound = self.retNumOfRowsInEntryTbl(wd)
        if numOfEntriesFound == 1:
            logi.appendMsg("PASS - the entry returned for the search: " + search_info)
            return True
        else:
            logi.appendMsg("FAIL - looked for 1 returned entry for searching: " + search_info + " and actually retreived: " + str(numOfEntriesFound))
            return False
        
    # this function search for entry and then press the first result retreived , send entry name or id in entryNameId  
    # if it is for category send isEntry=False
    def selectEntryfromtbl(self, webdrvr, entryNameId, isEntry=True): 
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(entryNameId + Keys.RETURN)
        time.sleep(4)
        
        entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
        try:
            entryline = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)
            if isEntry:
                entryline[0].find_element_by_xpath(DOM.ENTRY_ROW_NAME).click()
            else:
                entryline[0].find_element_by_xpath(DOM.CATEGORY_ROW_NAME).click()
            time.sleep(3)
            return True
        except:
            return False
    
    
    def deleteCategories(self, webdrvr, categories, categoriesSeparator=";"):   
        tmpstatus = True
        webdrvr.find_element_by_xpath(DOM.CATEGORIES_TAB).click()
        time.sleep(3)
        
        categoriesArr =  categories.split(categoriesSeparator)
        for entry in(categoriesArr):
            webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
            webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(entry + Keys.RETURN)
            time.sleep(3)
            # if no results for the entry search continue to next entry
            try:
                webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                continue
            except:
                rc = self.CheckUncheckRowInTable(webdrvr, 0)
                time.sleep(2)
                webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_DELETE).click()
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.POPUP_MESSAGE_YES).click()
                time.sleep(3)
                entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
                try:
                    webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                    tmpstatus = True
                except:
                    tmpstatus = False
                
        return tmpstatus     
    
#     # this def return the name of a specific row in table, from entry table - entry name from categories table category name , etc.
#     # first row in table is 1 and not 0
#     # tableItem (was "entryOrCategory") - entry is default and used for entries/moderation/playlists.  For Administration users table - send "user". For categories table - send "category".
# !!!! Need to replace entryOrCategory var (also in test 1082) to tableItem
#
    def retTblRowName(self, webdrvr, rowNum, tableItem="entry"):
        try: 
            if tableItem=="entry":
                elem = DOM.ENTRY_ROW_NAME
            elif tableItem=="user":
                elem = DOM.ADMIN_USERS_ROW_NAME
                tblRows = webdrvr.find_elements_by_xpath(DOM.ADMIN_USERS_TBL_ROW)
                wantedRow = tblRows[rowNum]
            elif tableItem=='accessctrl': 
                elem = DOM.ACCESS_CONTROL_PROFILE_NAME_TBL
            else:
                elem = DOM.CATEGORY_ROW_NAME
            
            if tableItem !="user":   
                tblRows = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)
                wantedRow = tblRows[rowNum-1]
                
            return wantedRow.find_element_by_xpath(elem).text
        except:
            return False

    # this function press on the 3 dots button and select the wanted action
    # rowNum - is the row in the table to select the action for, start from 0
    # theAction - send the action you want to select not case sensitive 
    def tblSelectAction(self, webdrvr, rowNum, theAction, theTbl="entry"):
        try: 
            if theTbl == "user":
                tblRows = webdrvr.find_elements_by_xpath(DOM.ADMIN_USERS_TBL_ROW)
                wantedRow = tblRows[rowNum]
            else:
                tblRows = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)
                wantedRow = tblRows[rowNum]
            
            time.sleep(2)
            wantedRow.find_element_by_xpath(DOM.TBL_MORE_ACTIONS).click()
            time.sleep(2)
            menuItems = webdrvr.find_elements_by_xpath(DOM.TBL_ACTION_MENUE)
            for i in menuItems:
                try:
                    if i.text.lower() == theAction.lower():
                        i.click()
                        return True
                except:
                    continue
        except:
            return False
        
        return False
    
    # this function press on the bulk actions button and select the wanted action
    # theAction - send the action you want to select not case sensitive if there is sub item then send it with > between them
    # for example "add/ remove tags>add tags"   
    def bulkSelectAction(self, webdrvr, theAction):
        actionsArr = theAction.split(">")
        if len(actionsArr)>1:
            hover = True
        else:
            hover = False
        
        try:
            webdrvr.find_element_by_xpath(DOM.BULK_ACTIONS).click()
            menuItems = webdrvr.find_elements_by_xpath(DOM.TBL_ACTION_MENUE)
            for i in menuItems:
                try:
                    if i.text.lower()==actionsArr[0].lower():
                        if hover:  # this case is when need to select sub menu item
                            ActionChains(webdrvr).move_to_element(i).perform()
                            newMenuItems = webdrvr.find_elements_by_xpath(DOM.TBL_ACTION_MENUE)
                            for j in newMenuItems:
                                try:
                                    if j.text.lower() == actionsArr[1].lower():
                                        j.click()
                                        return True
                                except:
                                    continue
                        else:
                            i.click()
                            return True
                except:
                    continue
        except:
            return False
        return False
            
    # this function return the correct object in case you have few objects with the same locator (same attribute) and only one of them is visible on screen
    # objLocatr = send the object DOM definition      
    def selectOneOfInvisibleSameObjects(self, webdrvr, objLocatr,objText=None):
        elements = webdrvr.find_elements_by_xpath(objLocatr)
        for el in elements:
            if el.size['width']!=0 and el.size['height']!=0 :
                if objText!=None:
                    if el.text.find(objText)>=0:
                        return el
                else:
                    return el
        return False
         
    def generateAdminConsoleKs (self, host, user, passwd, sessionUser, environment):
        try:
            import KalturaClient
            import Config

            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))

            if environment == 'prod':
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                print(' from Prod')
                print('PRODUCTION ENVIRONMENT')
            else:
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                print('from Testing')
                print('TESTING ENVIRONMENT')

            #adminUser = inifile.RetIniVal('admin_console_access', 'session_user')
            adminUser = sessionUser
            adminSecret = inifile.RetIniVal('admin_console_access', 'secret')

            KS = KalturaClient.KalturaClient.generateSession(adminSecret, adminUser, 2, -2, 86400,
                                                                        'disableentitlement').decode("utf-8")
            return KS
        except Exception as err:
            return err

    # This function login to AdminConsole or MAConsole - by default, in old fashion (user/pass) or in new fashion (OKTA) if KS provided
    def invokeConsoleLogin(self,webdrvr,wdobj,logi,url,user,pwd,ks=False):
        self.Wd = webdrvr
        self.logi = logi
        self.Wdobj = wdobj
        #If admin cosole KS provided, login with it overriding OKTA
        if ks:
            temp_url = url.split('partner')
            temp_url[1] = "user/login?ks="+ks
            url = ''.join(temp_url)
            # Open browser with link
            self.Wd.get(url)
            time.sleep(10)
        else:
            self.Wd.get(url)
            time.sleep(10)
            # Set LOGIN details
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_LOGIN_USER).send_keys(user)
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_LOGIN_PASS).send_keys(pwd)
            # Click on the SUBMIT button
            self.Wd.find_element_by_xpath(DOM.MACONSOLE_LOGIN_LOGIN).click()
        # Searching MACONSOLE_ENTRIES_TAB
        res = self.Wdobj.Sync(self.Wd,DOM.MACONSOLE_ENTRIES_TAB)            
        if isinstance(res,bool):
            return False
        else:       
            return True
        
    #this function set implicitly_wait to default
    def setImplicitlyWaitToDefault(self,webdrvr):
        webdrvr.implicitly_wait(30)
        
    #this function for different media types on filter
    def differetnMediaTypesFilter(self,webdrvr,MediaTypes,numberROW):
        self.selectRefineFilter(webdrvr,MediaTypes)
        entryRows = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)
        tempentrypage = Entrypage.entrypagefuncs(webdrvr)
        tempentrypage.selectNumOfRowsToShowInTbl(numberROW)
    
        self.wait_element(webdrvr,DOM.ENTRY_TYPE_ICON_AUDIO, timeout=3, multipleElements=False)  
        return entryRows

    # This function gets Wd as object, starts on KEA screen and return timeline as object
    def getTimeline(self, webdrvr):
        try:
            #time.sleep(7)
            iframe = webdrvr.find_elements_by_xpath('//iframe')
            webdrvr.switch_to.frame(iframe[1])
            clipline = webdrvr.find_element_by_xpath(DOM.CLIP_TIMELINE)
        except Exception as Exp:
            print(Exp)
            return False
        return clipline

    # This function starts on KEA screen and return duration, both as datetime object and string
    def checkClipDuration(self, webdrvr):
        try:
            duration = webdrvr.find_element_by_xpath(DOM.CLIP_DURATION).text.split('Total: ')
            durationKMC = duration[1]
            if len(durationKMC) < 9:  # Minutes only
                durationTime = datetime.datetime.strptime(durationKMC, '%M:%S.%f')
                if durationTime.microsecond >= 500_000:  # Rounding to the nearest second
                    durationTime += datetime.timedelta(seconds=1)
                stringDuration = durationTime.strftime('%M:%S')
            else:  # Hours too
                durationTime = datetime.datetime.strptime(durationKMC, '%H:%M:%S.%f')
                if durationTime.microsecond >= 500_000:  # Rounding to the nearest second
                    durationTime += datetime.timedelta(seconds=1)
                stringDuration = durationTime.strftime('%H:%M:%S')
            zeroTime = datetime.datetime.strptime("00:00:00", '%H:%M:%S')
            clipDuration = int((durationTime - zeroTime).total_seconds())  # Clip duration in total seconds, rounded
        except Exception as Exp:
            print(Exp)
            return False
        return clipDuration, stringDuration

    # This function will get timeline as object and return its dimensions
    def checkClipDimensions(self, webdrvr, timeline):
        try:
            timelineWidth = timeline.rect['width']
            timelineHeight = timeline.rect['height']
        except Exception as Exp:
            print(Exp)
            return False, Exp
        return True, timelineWidth, timelineHeight

    # This function will get timeline as object and mark part of it from and to specified time positions
    def setTimelineDuration(self, webdrvr, timeLine, fromSecond, toSecond):
        try:
            result, width, height = self.checkClipDimensions(webdrvr, timeLine)
            if result:
                seconds, secondsString = self.checkClipDuration(webdrvr)
                clipOffsetY = height / 2  # Always click in the middle of timeline by height
                pixelPerSecond = width / seconds
                clipOffsetStartX = pixelPerSecond * fromSecond
                clipOffsetEndX = pixelPerSecond * toSecond - clipOffsetStartX
                actions = ActionChains(webdrvr)
                actions.move_to_element_with_offset(timeLine, clipOffsetStartX, clipOffsetY).click().perform()
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.CLIP_START).click()
                time.sleep(1)
                actions.move_to_element_with_offset(timeLine, clipOffsetEndX, clipOffsetY).click().perform()
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.CLIP_END).click()
                time.sleep(1)
                setDuration, setStringDuration = self.checkClipDuration(webdrvr)
            else:
                return False
        except Exception as Exp:
            print(Exp)
            return False
        return True, setDuration, setStringDuration

    # This is function will get clip timeline as object and create clip or/and trim of specified duration
    #
    def createClipTrim(self, webdrvr, timeline, fromSecondClip, toSecondClip, fromSecondTrim, toSecondTrim, isClip = True, isTrim = True):
        try:
            if isClip:  # Starting entry clipping
                clip, clipDuration, clipStringDuration = self.setTimelineDuration(webdrvr, timeline, fromSecondClip, toSecondClip)  # Mark for clip
                if clip:
                    self.wait_element(webdrvr,DOM.EDITOR_SAVE_A_COPY, timeout=5, multipleElements=False).click()
                    time.sleep(2)
                    self.wait_element(webdrvr,DOM.CREATE_A_CLIP_COPY, timeout=5, multipleElements=False).click()
                    if isinstance(self.wait_element(webdrvr,DOM.SUCCESS_EDITOR_POPUP, timeout=10, multipleElements=False), bool):
                        return False
                    else:
                        webdrvr.find_element_by_xpath(DOM.CLIP_OK).click()
                        time.sleep(2)
                        if isTrim:  # Reset timeline for trim
                            webdrvr.find_element_by_xpath(DOM.CLIP_RESET).click()
                            time.sleep(1)
                            webdrvr.find_element_by_xpath(DOM.CLIP_RESET_CONTINUE).click()
                            timeline = webdrvr.find_element_by_xpath(DOM.CLIP_TIMELINE)  # Getting new timeline object after reset
                else:
                    return False
            if not isTrim:
                trimStringDuration = '0'
            if isTrim:  # Starting entry trimming
                trim, trimDuration, trimStringDuration = self.setTimelineDuration(webdrvr, timeline, fromSecondTrim, toSecondTrim)  # Mark for trim
                if trim:
                    self.wait_element(webdrvr,DOM.TRIM_SAVE, timeout=5, multipleElements=False).click()
                    time.sleep(2)
                    self.wait_element(webdrvr,DOM.TRIM_SAVE_CONFIRM, timeout=5, multipleElements=False).click()
                    if isinstance(self.wait_element(webdrvr,DOM.TRIM_POPUP, timeout=10, multipleElements=False), bool):
                        return False
                else:
                    return False
            time.sleep(2)
            webdrvr.switch_to_default_content()  # Return to entries page
            self.wait_element(webdrvr, DOM.PREVIEWANDEMBED_CLOSE_BTN, timeout=5, multipleElements=False).click()
            self.wait_element(webdrvr, DOM.ENTRIES_ACTIVE, timeout=5, multipleElements=False).click()
        except Exception as Exp:
            print(Exp)
            return False
        if not isClip:
            clipStringDuration = '0'
        return True, clipStringDuration, trimStringDuration
    
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
                        if el.size['width']!=0 or el.size['height']!=0:
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
            
            
    # Moran.cohen
    # This function verify element was found
    # caption: generate message on fail/pass
    # Return Element if found else return False
    def verifyElement(self, webdrvr, logi,locator, caption, timeout=10, multipleElements=False):
        try:  
            element = self.wait_element(webdrvr, locator, timeout, multipleElements)
            
            if element == False:
                logi.appendMsg("INFO: Element " + caption + " was NOT found; Locator by: " + locator )
                return False
            else:
                logi.appendMsg("PASS: Element " + caption + " was found")
                return element
        except Exception as exp:
            print(exp)
            logi.appendMsg("INFO: Element " + caption + " was NOT found; Locator by: " + locator )
            return False
            
    
    # Moran.cohen
    # This function wait until entry is exist
    def waitForEntryCreation(self,webdrvr, entryIdName , itimeout=300):
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
        webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(entryIdName + Keys.RETURN)
        
        time.sleep(3)
        
        entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
        bStatusReady = False
        #itimeout = 300
        startTime = time.time()
        while not bStatusReady:
            webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            time.sleep(3)
            try:
                lineText = webdrvr.find_elements_by_xpath(DOM.ENTRY_ROW)[0].text
                if lineText.find("Ready") > 0:
                    bStatusReady = True
                elif lineText.find("Deleted") > 0:
                    return self.fail_entry_status_exception()
                else:
                    time.sleep(1)
            except:
                rc,lineText= self.fail_entry_status_exception()
                if lineText == "NoEntry" and startTime + itimeout > time.time():
                    pass
                else:
                    return False,lineText
                
            if startTime + itimeout < time.time():
                return False,lineText
        
        return True,lineText


    # Moran.cohen
    # This function Change KMC Account if it is not equel to ExpectedKMCAccount
    def ChangeKMCAccount(self, webdrvr, Wdobj, logi, ExpectedKMCAccount):
        try:
            logi.appendMsg("INFO - Going to click on User Name of the account")
            webdrvr.find_element_by_xpath(DOM.KMC_USER_NAME).click()
            rc = self.verifyElement(webdrvr, logi,DOM.KMC_CHANGE_ACCOUNT_BTN, "Change account button", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Change account button")
                return False
            logi.appendMsg("INFO - Going to click on Change Account button")
            time.sleep(2)
            webdrvr.find_element_by_xpath(DOM.KMC_CHANGE_ACCOUNT_BTN).click()
            time.sleep(2)
            dynamicDOM_KMC_ACCOUNT_NAME = "//label[contains(text(),'" + ExpectedKMCAccount + "')]" #DOM.KMC_ACCOUNT_NAME.replace('TEXTTOREPLACE',ExpectedKMCAccount)
            rc = self.verifyElement(webdrvr, logi, dynamicDOM_KMC_ACCOUNT_NAME, "Account Name", 10)
            if rc == False:
                logi.appendMsg("FAIL - verifyElement Account Name")
                return False
            ActualKMCAccount = webdrvr.find_element_by_xpath(dynamicDOM_KMC_ACCOUNT_NAME).get_attribute("class").find("active")
            # Press click - If the account is not already selected 
            if ActualKMCAccount == -1:
                logi.appendMsg("INFO - Going to click on Change Account option = " + ExpectedKMCAccount)
                webdrvr.find_element_by_xpath(dynamicDOM_KMC_ACCOUNT_NAME).click()
                time.sleep(2)
                logi.appendMsg("INFO - Going to click on continue button")
                webdrvr.find_element_by_xpath(DOM.KMC_ACCOUNT_CONTINUE_BTN).click()
            else:    
                logi.appendMsg("INFO - Going to click on Account close button")    
                webdrvr.maximize_window()
                
                # Close the ChangeAccount window
                popup = Wdobj.Sync(webdrvr, DOM.POPUP_MSG)
                if popup!=False:
                    rc = self.selectOneOfInvisibleSameObjects(webdrvr, DOM.MSG_CLOSE)
                    rc.click()
                
                # Close the ChangeAccount window
                try: 
                    webdrvr.find_element_by_xpath(DOM.CATEGORY_PREFERENCES_POP)
                    rc = self.selectOneOfInvisibleSameObjects(webdrvr,DOM.MSG_CLOSE)
                    rc.click()
                except:
                    pass
            
            # Check for welcome message window       
            popup = Wdobj.Sync(webdrvr, DOM.POPUP_MSG)
            if popup!=False:
                rc = self.selectOneOfInvisibleSameObjects(webdrvr, DOM.MSG_CLOSE)
                rc.click()
    
            # Close the welcome message window
            try: 
                webdrvr.find_element_by_xpath(DOM.CATEGORY_PREFERENCES_POP)
                rc = self.selectOneOfInvisibleSameObjects(webdrvr,DOM.MSG_CLOSE)
                rc.click()
            except:
                pass
            return True
        
        except Exception as exp:
            print(exp)
            logi.appendMsg("FAIL: KMC Account Name doesn't exist on KMS. ExpectedKMCAccount = " + ExpectedKMCAccount )
            return False
    
    # Moran.cohen
    # element visible
    def is_visible(self,webdrvr, locator, multipleElements=False):
        try:
            if multipleElements == True:
                elements = webdrvr.find_elements_by_xpath(locator)
                for el in elements:
                    if el.size['width']!=0 or el.size['height']!=0:
                        if el.is_displayed() == True:
                            return True            
            else:
                if webdrvr.find_element_by_xpath(locator).is_displayed() == True:
                    return True
                else:
                    return False
        except NoSuchElementException:
            return False
     
    # Moran.cohen
    # This function waits for the element to appear (self.is_visible)
    def wait_visible(self, webdrvr, locator, timeout=10, multipleElements=False):
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        webdrvr.implicitly_wait(0)
        while True:
            try:
                if self.is_visible(webdrvr, locator, multipleElements) == True:
                    self.setImplicitlyWaitToDefault(webdrvr)
                    if multipleElements == True:
                        elements = webdrvr.find_elements_by_xpath(locator)
                        for el in elements:
                            if el.size['width']!=0 or el.size['height']!=0:
                                self.setImplicitlyWaitToDefault(webdrvr)
                                return el
                        return False
                    else:
                        el = webdrvr.find_element_by_xpath(locator)
                        self.setImplicitlyWaitToDefault(webdrvr)
                        return el                        
                if wait_until < datetime.datetime.now():
                    self.setImplicitlyWaitToDefault(webdrvr)
                    return False                
            except:
                if wait_until < datetime.datetime.now():
                    self.setImplicitlyWaitToDefault(webdrvr)
                    return False                 
                pass

    """
    Moran.cohen
    Returns element based on provided locator.
    Locator include the method and locator value in a tuple.
    :param locator,
    Use Example: 
    locator = ('xpath', DOM.ELEMENT)
    rc = get_element(self, locator)
    :return: Element
    """
    def get_element(self,webdrvr, locator):
        method = locator[0]
        values = locator[1]
        
        if type(values) is str:
            try:
                return self.get_element_by_type(webdrvr,method, values)
            except NoSuchElementException:
                raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)
        elif type(values) is list:
            for value in values:
                try:
                    return self.get_element_by_type(webdrvr,method, value)
                except NoSuchElementException:
                    pass
            self.logi.appendMsg("INFO - Element not found by: " + method + " = " + values)
            raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)
        
    
    """
    Moran.cohen
    Returns element based on provided locator.
    Locator include the method and locator value in a tuple.
    :param locator:
    :return:
    """
    def get_child_element(self,parent, locator, multipleElements=False):
        method = locator[0]
        values = locator[1]
        
        if type(values) is str:
            try:
                if multipleElements == True:
                    elements = self.get_child_elements_by_type(parent, method, values)
                    for el in elements:
                        if el.size['width']!=0 or el.size['height']!=0:
                            return el                    
                else:
                    return self.get_child_element_by_type(parent, method, values)
            except NoSuchElementException:
                raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)
        elif type(values) is list:
            for value in values:
                try:
                    return self.get_child_element_by_type(parent, method, value)
                except NoSuchElementException:
                    pass
            self.logi.appendMsg("INFO - Element not found by: " + method + " = " + values)
            raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)        
   
   
    """
    Moran.cohen
    Return elements based on provided locator.
    Locator include the method and locator value in a tuple.
    :param locator:
    :return:
    """
    def get_child_elements(self,parent, locator):
        method = locator[0]
        values = locator[1]
        
        if type(values) is str:
            try:
                return self.get_child_elements_by_type(parent, method, values)
            except NoSuchElementException:
                raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)
        elif type(values) is list:
            for value in values:
                try:
                    return self.get_child_elements_by_type(parent, method, value)
                except NoSuchElementException:
                    pass
            self.logi.appendMsg("INFO - Element not found by: " + method + " = " + values)
            raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)                
        
    # Moran.cohen
    #This function return the element according to method
    # method parameter - xpath/accessibility_id/android/ios/class_name/id/xpath/name/tag_name/css
    def get_element_by_type(self,webdrvr, method, value):
        if method == 'accessibility_id':
            return webdrvr.find_element_by_accessibility_id(value)
        elif method == 'android':
            return webdrvr.find_element_by_android_uiautomator('new UiSelector().%s' % value)
        elif method == 'ios':
            return webdrvr.find_element_by_ios_uiautomation(value)
        elif method == 'class_name':
            return webdrvr.find_element_by_class_name(value)
        elif method == 'id':
            return webdrvr.find_element_by_id(value)
        elif method == 'xpath':
            return webdrvr.find_element_by_xpath(value)
        elif method == 'name':
            return webdrvr.find_element_by_name(value)
        elif method == 'tag_name':
            return webdrvr.find_element_by_tag_name(value)
        elif method == 'css':
            return webdrvr.find_element_by_css_selector(value)           
        else:
            self.logi.appendMsg("INFO - Element not found by: " + method + " = " + value)
            raise Exception('Invalid locator method.')
        
    
    # Moran.cohen
    # This function return the elements by type 
    # method parameter - xpath/accessibility_id/android/ios/class_name/id/xpath/name/tag_name/css    
    def get_child_element_by_type(self,parent, method, value):
        if method == 'accessibility_id':
            return parent.find_element_by_accessibility_id(value)
        elif method == 'android':
            return parent.find_element_by_android_uiautomator('new UiSelector().%s' % value)
        elif method == 'ios':
            return parent.find_element_by_ios_uiautomation(value)
        elif method == 'class_name':
            return parent.find_element_by_class_name(value)
        elif method == 'id':
            return parent.find_element_by_id(value)
        elif method == 'xpath':
            return parent.find_element_by_xpath(value)
        elif method == 'name':
            return parent.find_element_by_name(value)
        elif method == 'tag_name':
            return parent.find_element_by_tag_name(value) 
        elif method == 'css':
            return parent.find_element_by_css_selector(value)          
        else:
            self.logi.appendMsg("INFO - Invalid locator method: " + method + " = " + value)
            raise Exception('Invalid locator method.')
    
        
    # Moran.cohen
    # This function return the elements according to method and parent object
    # method parameter - xpath/accessibility_id/android/ios/class_name/id/xpath/name/tag_name/css    
    def get_child_elements_by_type(self,parent, method, value):
        if method == 'accessibility_id':
            return parent.find_elements_by_accessibility_id(value)
        elif method == 'android':
            return parent.find_elements_by_android_uiautomator('new UiSelector().%s' % value)
        elif method == 'ios':
            return parent.find_elements_by_ios_uiautomation(value)
        elif method == 'class_name':
            return parent.find_elements_by_class_name(value)
        elif method == 'id':
            return parent.find_elements_by_id(value)
        elif method == 'xpath':
            return parent.find_elements_by_xpath(value)
        elif method == 'name':
            return parent.find_elements_by_name(value)
        elif method == 'tag_name':
            return parent.find_elements_by_tag_name(value)   
        elif method == 'css':
            return parent.find_elements_by_css_selector(value)      
        else:
            self.logi.appendMsg("INFO - Invalid locator method: " + method + " = " + value)
            raise Exception('Invalid locator method.')             

    
    """
    Moran.cohen
    Returns element based on provided locator.
    Locator include the method and locator value in a tuple.
    :param locator:
    :return: List.
    Call Example,
    locator = ('xpath', DOM.X)    
    Elementlist1 = self.BasicFuncs.get_elements(self.Wd,locator)
    """
    def get_elements(self,webdrvr,locator):
        method = locator[0]
        values = locator[1]

        if type(values) is str:
            return self.get_elements_by_type(webdrvr,method, values)
        elif type(values) is list:
            for value in values:
                try:
                    return self.get_elements_by_type(webdrvr,method, value)
                except NoSuchElementException:
                    pass
            raise NoSuchElementException("FAILED to get element locator value: " + values + "; method: " + method)

      
    # Moran.cohen
    # This function return the elements by type
    # method parameter - xpath/accessibility_id/android/ios/class_name/id/xpath/name/tag_name/css  
    def get_elements_by_type(self,webdrvr, method, value):
        if method == 'accessibility_id':
            return webdrvr.find_elements_by_accessibility_id(value)
        elif method == 'android':
            return webdrvr.find_elements_by_android_uiautomator(value)
        elif method == 'ios':
            return webdrvr.find_elements_by_ios_uiautomation(value)
        elif method == 'class_name':
            return webdrvr.find_elements_by_class_name(value)
        elif method == 'id':
            return webdrvr.find_elements_by_id(value)
        elif method == 'xpath':
            return webdrvr.find_elements_by_xpath(value)
        elif method == 'name':
            return webdrvr.find_elements_by_name(value)
        elif method == 'tag_name':
            return webdrvr.find_elements_by_tag_name(value) 
        elif method == 'css':
            return webdrvr.find_elements_by_css_selector(value)          
        else:
            self.logi.appendMsg("INFO - Element not found by: " + method + " = " + value)
            raise Exception('Invalid locator method.')

    # Ilia Vitlin
    # This function gets default admin console page, entryId and batch job name as arguments,
    # enters Batch Process Control tab, finds specific type of batch jobs history for entryId in
    # Entry Investigation and returns matrix of found batch jobs together with their IDs and statuses
    def getBatchJobStatus(self, webdrvr, entryId, jobName):
        from bs4 import BeautifulSoup
        jobMatrix = []
        try:
            #Search for entryId
            webdrvr.find_element_by_xpath(DOM.BATCH_PROCESS_CONTROL).click()
            webdrvr.find_element_by_xpath(DOM.BATCH_SEARCH_ENTRY_INPUT).send_keys(entryId)
            webdrvr.find_element_by_xpath(DOM.BATCH_SEARCH_ENTRY_BUTTON).click()
            #Parse table with BS4
            soup = BeautifulSoup(webdrvr.page_source, 'html.parser')
            allTable = soup.findAll('table')
            for table in allTable:
                rows = table.findAll('tr')
                for tr in rows:
                    cols = tr.findAll('td')
                    for td in cols:
                        if td.find(text = jobName):
                            jobMatrix.append([td.text, table.contents[1].text, table.contents[2].text])
                    break
        except Exception as exp:
            print(exp)
            return False
        return jobMatrix

    def resetPassword(self, webdrvr, Wdobj, logi, url, email):
        webdrvr.get(url)
        time.sleep(5)
        rc = self.wait_element(webdrvr, DOM.LOGIN_USER)
        if rc == False:
            logi.appendMsg('Login page not loaded!')
            return False
        else:
            webdrvr.find_element_by_xpath(DOM.FORGOT_PASSWORD).click()
            Wdobj.valToTextbox(webdrvr, DOM.RESET_EMAIL, email)
            time.sleep(1)
            webdrvr.find_element_by_xpath(DOM.RESET_BUTTON).click()
            time.sleep(1)
            if not webdrvr.find_element_by_xpath(DOM.RESET_MESSAGE):
                logi.appendMsg('No reset password message found, failed !')
                return False
            return True

    def generateRandomPassword(self, length):
        import secrets
        try:
            password = secrets.token_urlsafe(length) + '1!'
        except Exception as EXP:
            print(EXP)
            return False
        return password

    def setNewPassword(self, webdrvr, Wdobj, logi, url, password):
        try:
            webdrvr.get(url)
            time.sleep(5)

            Wdobj.valToTextbox(webdrvr, DOM.NEW_PASSWORD, password)
            Wdobj.valToTextbox(webdrvr, DOM.CONFIRM_PASSWORD, password)
            webdrvr.find_element_by_xpath(DOM.SEND_PASSWORD).click()
            if not webdrvr.find_element_by_xpath(DOM.SUCCESS_MESSAGE):
                logi.appendMsg('No password set message found, failed!')
                return False
        except Exception as EXP:
            print(EXP)
            return False
        return True
