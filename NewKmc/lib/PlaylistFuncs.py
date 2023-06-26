'''
Created on Oct 10, 2018

@author: lihi.shapira
'''

import collections
import time

from selenium.webdriver.common.keys import Keys

import DOM
import KmcBasicFuncs


class playlistfuncs:
    

    def __init__(self, webdrvr, logi):
        
        self.Wd = webdrvr
        self.logi = logi
        self.basicFuncs = KmcBasicFuncs.basicFuncs()
        
    # this function create a playlist with entries
    # sent the entries as a list object with entry name
    # manual send true if the playlist should be manual or don't send (its default) and send false if it should be rule based 
        
    def CreatPlayList(self, playlistName, entryList ,playlistDesc="playlist desc", manual=True):        
               
        # Navigate to Playlists tab and click to add playlist
        self.logi.appendMsg("INFO - Navigating to Playlists section")
        self.Wd.find_element_by_xpath(DOM.PLAYLISTS_TAB).click()
        time.sleep(2)
        self.logi.appendMsg("INFO - Going to click 'Add Playlist'")
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_ADDPLAYLIST_BTN).click()
        time.sleep(2)
        
        # select manual or rule based
        if manual:
            self.Wd.find_element_by_xpath(DOM.PLAYLIST_MANUAL_RDBTN).click()
        else:
            self.Wd.find_element_by_xpath(DOM.PLAYLIST_RULEBASED_RDBTN).click()
        
        # Adding playlist's data in form
        self.logi.appendMsg("INFO - Going to enter text in Playlist's Name and description fields name= " + playlistName + " description= " + playlistDesc)
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_ADD_NEW_PLYLST_NAME).send_keys(playlistName)
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_ADD_NEW_DESCRIPTION).send_keys(playlistDesc)
                
        self.logi.appendMsg("INFO - going to save the playlist, screen should be on playlist content page")
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_CREATE_NEXT_BTN).click()
        time.sleep(2)
        
        try:
            self.Wd.find_element_by_xpath(DOM.PLAYLIST_PAGE_NAME.replace("NAMETOREPLACE",playlistName))
        except:
            self.logi.appendMsg("FAIL - the screen did not moved to playlist content page, or the playlist name was incorrect in the page")
            return False
        
        # call add entries function
        if (self.addEntriesToPlaylist(entryList)):
            self.logi.appendMsg("PASS - found all entries to add to the playlist")
        else: 
            self.logi.appendMsg("FAIL - did not find all entries to add to the playlist")                
        
        # call playlist verify
        if self.VerifyAddEntriesToPlaylist(entryList):
            return True
        else:
            return False

    # this function delete playlists from playlist table, if you need to delete more than one playlist send the entries (name or id) with entriesSeparator=";" as delimiter by default (can be change the sign)
    # example: delete_playlist(wd,"a;b")
    def delete_playlist(self, webdrvr, playlists, playlist_separator=";"):

        tmpstatus = True

        playlist_Arr = playlists.split(playlist_separator)
        for playlist in (playlist_Arr):
            webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(Keys.CONTROL, 'a')
            webdrvr.find_element_by_xpath(DOM.SEARCH_ENTRIES).send_keys(playlist + Keys.RETURN)
            time.sleep(3)
            # if no results for the entry search continue to next entry
            try:
                webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                continue
            except:
                rc = self.basicFuncs.CheckUncheckRowInTable(webdrvr, 0)
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_DELETE).click()
                time.sleep(1)
                webdrvr.find_element_by_xpath(DOM.ADD_EXISTING_ALERT_YES).click()
                time.sleep(3)
                entriesTbl = webdrvr.find_element_by_xpath(DOM.ENTRIES_TABLE)
                try:
                    webdrvr.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                    tmpstatus = True
                except:
                    tmpstatus = False

        return tmpstatus
    
    #this function adds entries to a playlist (existing or new). 
    #this function starts from position where the system is on a certain playlist>'content' page  
         
    def addEntriesToPlaylist(self, entryList, boolSave=True):
        #Clicking on 'Add Entry' button
        self.logi.appendMsg("INFO - Going to click on 'Add Entry' button")
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_ADD_ENTRY_BTN).click()
        time.sleep(3) 
        
        for i in entryList:
            if (self.basicFuncs.searchEntrySimpleSearch(self.Wd,i, True)):
                time.sleep(3)
                entryRowsArr = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                self.logi.appendMsg("INFO - Going to add entry: " + i)
                time.sleep(3)
                entryRowsArr[0].find_element_by_xpath(DOM.PLAYLIST_PLUS_BTN).click()
                
                
            else :
                self.logi.appendMsg("FAIL - Could not find entry: " + i) 
                if entryList.len == 1:
                    return False  
        
        #Clicking on ADD button
        time.sleep(2)
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_ADD_BTN).click()
        time.sleep(1)
        
        if boolSave:
            #Save the entries addition
            self.Wd.find_element_by_xpath(DOM.PLAYLIST_SAVE_BTN ).click()
            while not self.Wd.find_element_by_xpath(DOM.PLAYLIST_SAVE_BTN ).get_attribute("disabled"):  # wait till the save button become disable
                time.sleep(1)
                
        return True
        
        
    def VerifyAddEntriesToPlaylist(self, entryList):
        
        #go to Content tab  
        self.Wd.find_element_by_xpath(DOM.PLAYLIST_CONTENT_SECTION).click()  
        time.sleep(7) 
              
        #Inserting all playlist's rows into an array  
        entriesNameArr = [] 
        entryRowsArr = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
        for i in range(0,len(entryRowsArr)):
            entryName = self.basicFuncs.retTblRowName(self.Wd, i)
            entriesNameArr.append(entryName)     
        #time.sleep(2) 
        
        #Creating strings from the two lists to display in the log file
        names_str = (", ").join(entriesNameArr)
        entryList_str = (", ").join(entryList)
        
        #verify the playlist's entries are the correct entries from 'entryList'- comparing lists
        if set(entryList)!= set(entriesNameArr):
            temp1 = [x for x in entryList if x not in entriesNameArr]         
            temp1_str = (", ").join([temp1])        
            temp2 = [x for x in entriesNameArr if x not in entryList]    
            temp2_str = (", ").join(temp2)                                                      
            self.logi.appendMsg("FAIL - The expected entries were: " + entryList_str + " and the actual entries are: " + names_str + ", The differences are - " + temp1_str + temp2_str ) 
            return False  
        else:
            self.logi.appendMsg("PASS - The expected entries were successfully added to the playlist")
            return True
        
    # Function that checks the position of an entry and moves it up or down the list
    # If the entry is 1st or last and move up or down is sent it will not preform the action
    # move_diraction (String) = the direction to move the entry - 'Move Up', 'Move to Top', 'Move Down', 'Move to Bottom'
    # NEED TO NAVIGATE TO SPECIFIC PLAYLIST CONTENT (entries list) BEFORE USING THIS FUNCTION
    def verify_entry_position_and_move(self, move_diraction, entry_name):
        try:
            # save list before moving
            playlist_before = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW_NAME)
            count = 0
            for entry_index in playlist_before:
                if playlist_before[count].text == entry_name:
                    index = count
                    break
                else:
                    count += 1
                    continue

            time.sleep(3)

            try:
                if move_diraction == 'Move Up' or move_diraction == 'Move to Top':
                    if index == 0:
                        self.logi.appendMsg("FAIL - The entry did not move up as it is the first item")
                        return False
                    if move_diraction == 'Move Up':
                        move_xpath = DOM.MOVE_UP
                    else:
                        move_xpath = DOM.MOVE_TO_TOP
                    time.sleep(1)
                    self.move_entry_position(move_xpath, entry_name)
                elif move_diraction == 'Move Down' or move_diraction == 'Move to Bottom':
                    if index == len(playlist_before):
                        self.logi.appendMsg("FAIL - The entry did not move up as it is the first item")
                        return False
                    if move_diraction == 'Move Down':
                        move_xpath = DOM.MOVE_DOWN
                    else:
                        move_xpath = DOM.MOVE_TO_BOTTOM
                    time.sleep(1)
                    self.move_entry_position(move_xpath, entry_name)

            except Exception as e:
                print(e)
                self.logi.appendMsg("FAIL - the entry did not move")
                return False

            playlist_after = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW_NAME)

            if playlist_before == playlist_after:
                self.logi.appendMsg("FAIL - playlist did not update after entry move")
                return False

            self.logi.appendMsg("PASS - playlist changed after entry move")
            return True

        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - entry position and move action failed")
            return False

    # helper function to verify_entry_position_and_move
    # after position is verified and move action can be preformed the given entry by name is moved
    # diraction_xpath (String) - value sent from verify_entry_position_and_move
    # entry_name (String) - value sent from verify_entry_position_and_move
    def move_entry_position(self, diraction_xpath, entry_name):
        playlist = self.Wd.find_elements_by_xpath(DOM.PLAYLIST_ROW_ACTIONS)
        entry_name_table = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW_NAME)
        time.sleep(1)
        for webElement in range(len(entry_name_table)):
            webElementText = entry_name_table[webElement].text
            # check if the given profile name exists in the user profiles list
            if entry_name in webElementText:
                playlist[webElement].click()
                self.Wd.find_element_by_xpath(diraction_xpath).click()
                time.sleep(1)
                break
        
   #The function removes spesific entry from a playlist(in a playlist page -> Content tab) 
   #entry_name - the name of the entry we want to remove from the playlist
    def remove_entry_from_playlist(self, entry_name):
        
        boolEntryFound = False
        numOfRowsInPlayList = self.basicFuncs.retNumOfRowsInEntryTbl(self.Wd)
        for i in range(1,numOfRowsInPlayList+1):
            if self.basicFuncs.retTblRowName(self.Wd, i, "entry")== entry_name:
                boolEntryFound = True
                break
        
        if boolEntryFound:
            #Click on the '...' Actions button for the entry in the first row:        
            self.logi.appendMsg("INFO - Going to select 'actions>Remove from Playlist' for the wanted entry: " + entry_name)
            time.sleep(1)
            #Select 'Remove from Playlist' option
            if self.basicFuncs.tblSelectAction(self.Wd,i-1,"Remove from Playlist")!=True:
                self.logi.appendMsg("FAIL - could not select \"Remove from Playlist\" option")
                return False
            
            numOfRowsInPlayListAfter = self.basicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            
            if (numOfRowsInPlayListAfter+1) == numOfRowsInPlayList:
                self.logi.appendMsg("PASS - the number of entries before the remove action was: " + str(numOfRowsInPlayList) + " and the number after was: " + str(numOfRowsInPlayListAfter) + " as expected")
                return True
            else:
                self.logi.appendMsg("FAIL - the number of entries before the remove action was: " + str(numOfRowsInPlayList) + " and the number after was: " + str(numOfRowsInPlayListAfter) + " NOT as expected")
                return False       
        else:
            self.logi.appendMsg("FAIL - cannot find the entry: " + entry_name + " in the current playlist")
            return False

    #The function duplicates an entry in playlist (in a playlist page -> Content tab) 
    #entry_name - the name of the entry we want to duplicate
    def duplicate_entry_in_playlist(self, entry_name):
        
        boolEntryFound = False
        numOfRowsInPlayList = self.basicFuncs.retNumOfRowsInEntryTbl(self.Wd)
        for i in range(1,numOfRowsInPlayList):
            if self.basicFuncs.retTblRowName(self.Wd, i, "entry") == entry_name:
                boolEntryFound = True
                break
        
        if boolEntryFound:
            #Click on the '...' Actions button for the entry in the first row:        
            self.logi.appendMsg("INFO - Going to select 'actions>Remove from Playlist' for the wanted entry: " + entry_name)
            #Select 'Remove from Playlist' option
            if self.basicFuncs.tblSelectAction(self.Wd,i-1,"Duplicate")!=True:
                self.logi.appendMsg("FAIL - could not select \"Duplicate\" option")
                return False
            
           #counting rows' num in the playlist after the duplicate action
            numOfRows = self.basicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            arr = []
            #entering the entries' names into an array
            for i in range (1,numOfRows+1):
                arr.append(self.basicFuncs.retTblRowName(self.Wd, i-1, "entry"))
                
            dupEntry =  [item for item, count in list(collections.Counter(arr).items()) if count > 1] 
            if dupEntry[0] == entry_name:
                self.logi.appendMsg("PASS - the entry- " + entry_name + " was duplicated as expected")
                return True 
            else:
                self.logi.appendMsg("FAIL - the entry- " + entry_name + " was NOT duplicated")
                return False                       
        else:
            self.logi.appendMsg("FAIL - cannot find the entry: " + entry_name + " in the current playlist")
            return False     
        
    ######################################################################################
    # Function SortPlaylistContentTable : sorting the entries in the playlist's table by 'byColName' (currently by ;Name')
    # Params:
    #    byColName : currently Name -alphabetical 
    #    sortOrder : asc- alphabetical a->z, desc-alphabetical z->a
    ######################################################################################
    def SortPlaylistContentTable(self, sortOrder = "asc", byColName="Name"):
        try:                                  
            self.logi.appendMsg("INFO - Going to sort playlist's table by " + str(byColName))                           
            #Get all entries' names elements (=titles) for all the entries' rows before sorting them
            namesListElementsBefore = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW_NAME)
            
            #Create new list for all entries' names (strings (=text)) for all the entries' rows before sorting them
            namesListBefore = []
            for nameElement in namesListElementsBefore:
                namesListBefore.append(nameElement.text)
                        
            #Click on the 'Name'column's title to see the sort's icon (arrow)
            nameTitleElement = self.Wd.find_element_by_xpath(DOM.PLAYLIST_NAME_COL_TITLE)
            time.sleep(1)
            nameTitleElement.click()
            
            #get 'sortable column icon' element (sort arrow)
            upDown = self.Wd.find_element_by_xpath(DOM.PLAYLIST_NAME_COL_UP_DOWN)
            #get the (sort type) element's state - up or down
            currentState = upDown.get_attribute('class').split('sort-')[1]
            
            #When no state was found (not 'up' and not 'down')
            if (currentState != 'up') and (currentState != 'down'):
                self.logi.appendMsg("FAILED to get the element's state - up or down")
                #Exit function?
             
            if len(namesListBefore) < 3: #checking entries' number (2 is the minimum number for sorting)
                self.logi.appendMsg("FAIL - Sort is not relevant for less than 2 entries in playlist")
                return False   
                
            #Sort the names' list by function
            if sortOrder == "asc":
                sortedList = sorted(namesListBefore, key=str.lower)
            else:
                sortedList = sorted(namesListBefore, key=str.lower, reverse=True)
                       
            #Actual sort in KMC - Clicking on the Names' col title for sort (up or down) according to the sort type- 'asc' or 'desc'
            if sortOrder == "asc":
                if (currentState == 'down'):
                    upDown.click()
            else: #'desc' order
                if (currentState == 'up'):
                    upDown.click()
                    
            time.sleep(1) 
            
            #Get all entries' names strings (=titles) for all the entries' rows after sorting them
            namesListElementsAfter = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW_NAME)
            
            #Create new list for all entries' names (strings (=text)) for all the entries' rows before sorting them
            namesListAfter = []
            for nameElement in namesListElementsAfter:
                namesListAfter.append(nameElement.text)
            
            #Verification - comparing sort function result with the actual sot's resuly via KMC                 
            if collections.Counter(sortedList) == collections.Counter(namesListAfter): 
                    self.logi.appendMsg("PASS - Playlist's table was sorted successfully")                                                                    
                    return True 
            else: 
                    self.logi.appendMsg("FAIL - Playlist's table was NOT sorted successfully") 
                    return False 

        
        except Exception as Exp:
            print(Exp)
            return False    
        
    def FindPlaylistRowInPlaylistsTable(self, playlistId):
        playlistRowsElements = self.Wd.find_elements_by_xpath(DOM.PLAYLIST_TABLE_ROW)
        for playlistRowElement in (playlistRowsElements):
            if playlistRowElement.text.find(playlistId) >= 0:
                self.logi.appendMsg("PASS - the playlist- " + playlistId  + " was found OK")
                return playlistRowElement
        
            self.logi.appendMsg("FAIL - the playlist- " + playlistId + " was NOT found")
            return False
       




         
               
             
        