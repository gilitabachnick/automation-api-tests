'''
Created on Jan 29, 2018

@author: Adi.Miller
'''

import time

from selenium.webdriver.common.keys import Keys

import DOM
import KmcBasicFuncs


class entrypagefuncs:

    def __init__(self, Wd, logi=None):
        self.Wd = Wd
        self.KmcBasicFuncs = KmcBasicFuncs.basicFuncs()
        self.logi = logi

        self.BasicFuncs = KmcBasicFuncs.basicFuncs()

    # select entries in entries table, send the range of rows to select as string separate with "," in - tblRowstoSelectRange,
    #     example : selectEntries("1,9")
    #    for one row send only the number of the row example : selectEntries("0")
    def selectEntries(self, tblRowstoSelectRange):
        try:
            uncheckedEntries = self.Wd.find_elements_by_tag_name('tr')

            if tblRowstoSelectRange.find(",") > 0:
                tblRowstoSelectRangeArr = tblRowstoSelectRange.split(",")
                for i in range(int(tblRowstoSelectRangeArr[0]), int(tblRowstoSelectRangeArr[1])):
                    chk = uncheckedEntries[i].find_element_by_xpath(DOM.ENTRY_CHECKBOX)
                    chk.click()
            else:
                chk = uncheckedEntries[int(tblRowstoSelectRange)].find_element_by_xpath(DOM.ENTRY_CHECKBOX)
                chk.click()
        except Exception as e:
            print(e)
            return False

    # select all entries in the table        
    def selectAll(self):
        chkAll = self.Wd.find_elements_by_xpath(DOM.ENTRY_CHECKBOX)
        chkAll[0].click()
        time.sleep(3)

    def cancel_selected(self):
        try:
            self.Wd.find_element_by_xpath(DOM.ENTRY_CANCEL_SELECTED).click()
        except Exception as e:
            print(e)

    def bulk_delete_selected(self, confirm_delete=True):
        try:
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_BULK_DELETE).click()
            if confirm_delete:
                self.Wd.find_element_by_xpath(DOM.ADD_EXISTING_ALERT_YES).click()
            else:
                self.Wd.find_element_by_xpath(DOM.ADD_EXISTING_ALERT_NO).click()
        except Exception as e:
            print(e)

    # return entry categories    
    def retEntryCategories(self, entryIdName):

        rc = self.KmcBasicFuncs.selectEntryfromtbl(self.Wd, entryIdName)
        retCategories = ""
        if rc:
            categoriesField = self.Wd.find_element_by_xpath(DOM.ENTRY_CATEGORIES)
            categories = categoriesField.find_elements_by_xpath(DOM.ENTRY_CATEGORIES_LABELS)
            for i in (categories):
                retCategories = retCategories + i.text + ";"

            return retCategories[:-1]
        else:
            return False

    # this def select the number of rows in table entries that would shown
    # numofRows - the the wanted number of rows to select
    def selectNumOfRowsToShowInTbl(self, numofRows):

        self.Wd.find_element_by_xpath(DOM.ENTRIES_DROPDOWN_NUM_OF_ROWS).click()
        lst = self.Wd.find_element_by_xpath(DOM.ENTRIES_DROPDOWN_LIST)
        lstItems = lst.find_elements_by_xpath(DOM.ENTRIES_DROPDOWN_ITEMS)
        for i in lstItems:
            if i.text == str(numofRows):
                i.click()
                break

    def dropFolderWaitForUploadAndEntry(self, entryId_Name):

        testStatus = True

        self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
        self.Wd.find_element_by_xpath(DOM.ENTRIES_DROPFOLDER_TAB).click()
        time.sleep(2)
        timeOut = 600
        startTime = time.perf_counter()
        foundindrpfoldertag = False
        # wait 5 minutes to drop folder line finish processing
        while (time.perf_counter() <= startTime + timeOut):
            self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
            try:
                uploadStatus = self.Wd.find_element_by_xpath(DOM.TBL_STATUS_CELL).text
            except:
                if foundindrpfoldertag:
                    try:
                        self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_NO_RESULT)
                        timeOut = 0
                        self.logi.appendMsg(
                            "PASS - the drop folder upload line was removed from drop folder tab as expected")
                        shouldBeEntry = True
                    except:
                        continue
                else:
                    time.sleep(3)
                    startTime = time.perf_counter()
                    continue
            if uploadStatus == 'Uploading' or uploadStatus == 'Downloading' or uploadStatus == 'Processing':
                foundindrpfoldertag = True
                time.sleep(3)
            else:
                timeOut = 0
                if uploadStatus == 'Done':
                    self.logi.appendMsg("PASS - the drop folder upload line got the status \"Done\" as expected")
                    shouldBeEntry = True
                else:
                    self.logi.appendMsg(
                        "FAIL - the drop folder upload line did not get the status \"Done\" as expected, the status was - " + uploadStatus)
                    testStatus = False
                    shouldBeEntry = False
            # case that the row in drop folder disappear after finish uploading 

        time.sleep(10)

        if foundindrpfoldertag:
            self.logi.appendMsg(
                "PASS - the file was found in drop folder tab and its status when exit waiting for it was: " + uploadStatus)
        else:
            self.logi.appendMsg("FAIL - the file was NOT found in drop folder tab after uploading it by ftp or sftp")

        # verify the entry is in status Ready
        if shouldBeEntry:

            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(5)
            startTime = time.perf_counter()
            timeOut = 300
            while (time.perf_counter() <= startTime + timeOut):
                self.BasicFuncs.searchEntrySimpleSearch(self.Wd, entryId_Name)
                if self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd) > 0:
                    timeOut = 0
                else:
                    continue

            if timeOut == 0:
                self.logi.appendMsg("INFO - going to verify that the entry is in status \"Ready\"")
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                entryStatus, lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd, entryId_Name)
                if lineText == "NoEntry":
                    self.logi.appendMsg("FAIL - the entry " + entryId_Name + " was not found in entry table")
                    testStatus = False
                if entryStatus:
                    self.logi.appendMsg(
                        "PASS - the entry " + entryId_Name + " was uploaded succefully and got the status Ready as expected")
                else:
                    self.logi.appendMsg(
                        "FAIL - the entry is not \"Ready\", this is the text of the entry row in the table: " + lineText)
            else:
                self.logi.appendMsg(
                    "FAIL - could not find the entry " + entryId_Name + " in entry table 2 minutes after it done uploading")

        return testStatus

    # this function updates basic meta data of an entry
    # EntryNewTags, EntryNewCategories - if need to send few send them with ; between each other for example: EntryNewTags="ff;dd;sw"
    def EntrySetBasicMetadata(self, EntryNewName=None, EntryNewDescription=None, EntryNewTags=None,
                              EntryNewCategories=None, EntryNewReferenceID=None, saveByButton=True):

        try:
            if EntryNewTags != None:
                tagsarr = EntryNewTags.split(";")
            else:
                tagsarr = None

            if EntryNewCategories != None:
                Categorysarr = EntryNewCategories.split(";")
            else:
                Categorysarr = None
        except Exception as e:
            print(e)
            pass

        try:
            if EntryNewName != None:
                nameField = self.Wd.find_element_by_xpath(DOM.ENTRY_NAME)
                nameField.clear()
                nameField.send_keys(EntryNewName)

            if EntryNewDescription != None:
                descField = self.Wd.find_element_by_xpath(DOM.ENTRY_DESC)
                descField.clear()
                descField.send_keys(EntryNewDescription)

            if EntryNewTags != None:
                tagsField = self.Wd.find_element_by_xpath(DOM.TAGS_ADD_TAGS_NAME)
                try:
                    existTags = tagsField.find_elements_by_xpath(DOM.CATEGORY_CLOSE_TAG)
                    for tag in existTags:
                        tag.click()
                        time.sleep(1)
                except:
                    print("No tags")
                for i in tagsarr:
                    tagsField.send_keys(i + Keys.RETURN)

            if EntryNewCategories != None:
                findCategory = self.Wd.find_element_by_xpath(DOM.ENTRY_CATEGORIES_FIND)
                for i in Categorysarr:
                    findCategory.find_element_by_xpath(DOM.ENTRY_CATEGORY_FIND_TEXTBOX).send_keys(i)
                    time.sleep(2)
                    try:
                        self.Wd.find_element_by_xpath(DOM.ENTRY_CATEGORY_SELECTION.replace("TEXTTOREPLACE", i)).click()

                    except:
                        print('No such Category name: ' + i)
                        return False

            if EntryNewReferenceID != None:
                RefField = self.Wd.find_element_by_xpath(DOM.ENTRY_REFERENCEID)
                RefField.clear()
                RefField.send_keys(EntryNewReferenceID)

            time.sleep(3)

            if saveByButton:
                self.Wd.find_element_by_xpath(DOM.CATEGORY_SAVE).click()
            else:  # press the back button and discard changes
                self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
                time.sleep(3)
                try:
                    dialogWin = self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_EDIT)
                    dialogWin.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
                except:
                    print("could not press the yes button in the dialog window")
                    return False
                time.sleep(3)

            return True

        except:
            return False

    def setAccessControlToEntry(self, entryname_id, accessCtrlName):

        self.logi.appendMsg("INFO- going to set access control- " + accessCtrlName + " to entry- " + entryname_id)

        # go to entries tab
        self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
        time.sleep(3)

        rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, entryname_id, True)
        if not rc:
            self.logi.appendMsg("FAIL - could not find the entry- " + entryname_id + " in entries table")

        # go to entry access control
        self.Wd.find_element_by_xpath(DOM.ENTRY_ACCESS_CONTROL).click()
        time.sleep(3)
        self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_DD_MTYPE).click()
        self.Wd.find_element_by_xpath(DOM.ENTRY_ACCESS_CONTROL_ITEM.replace('TEXTTOREPLACE', accessCtrlName)).click()
        time.sleep(1)
        self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()
        time.sleep(3)

        # go to entries tab
        self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
        time.sleep(3)


    # The function receives Webdriver object and entry name and return twodimensional aray of flavor names and statuses
    def retAllFlavorsStatus(self, webdrvr, entryIdName):
        from bs4 import BeautifulSoup
        flavorMatrix = []
        try:
            rc = self.KmcBasicFuncs.selectEntryfromtbl(self.Wd, entryIdName)
            if rc:
                self.Wd.find_element_by_xpath(DOM.ENTRY_FLAVORS_TAB).click()  # Enter flavors tab
                time.sleep(3)
                soup = BeautifulSoup(webdrvr.page_source, 'html.parser')
                allTable = soup.findAll('table')
                table = allTable[1]  # Flavors table
                rows = table.findAll('tr')
                for tr in rows:
                    cols = tr.findAll('td')
                    if cols[7].text != '':  # Flavor status not empty
                        flavorMatrix.append([cols[0].text, cols[7].text])  # Append flavor name and status to matrix
            else:
                return False
        except Exception as Exp:
            print (Exp)
            return False
        return flavorMatrix

    # This function gets Webdrive object, entry name, string of flavor names separated by specified character
    # and return true/false if flavors of entry match flavors of string, not matter flavors index/status
    def compareFlavors(self, webdrvr, entryName, transcodingFlavors, separatorChar=","):
        try:
            flavorList = transcodingFlavors.split(separatorChar)
            flavorsMatrix = self.retAllFlavorsStatus(webdrvr, entryName)
            flavorsOnly = [i[0] for i in flavorsMatrix]  # Taking only flavors names
            sameElements = list(set(flavorsOnly).intersection(flavorList))  # Check what flavors exist in both lists, not matter position
            if len(sameElements) == len(flavorsOnly):  # Check if all the elements are the same
                return True
            else:
                return False
        except Exception as Exp:
            print(Exp)
            return False
    ######################################################################################
    # Function retEntryFlavors : returns entry's converted flavors names (i.e.: "Source,Mobile (3GP)")
    # Params:
    #    entryIdName : entry name - string - mandatory
    #    separatorChar : character that will split the flavors - default =","
    ######################################################################################
    def retEntryFlavors(self, entryIdName, separatorChar=","):
        try:

            # search for entry name
            rc = self.KmcBasicFuncs.selectEntryfromtbl(self.Wd, entryIdName)
            retFlavors = ""

            if rc:

                # search for converted flavors and concatenate string
                self.Wd.find_element_by_xpath(DOM.ENTRY_FLAVORS_TAB).click()
                time.sleep(3)
                listFlavors = self.Wd.find_elements_by_xpath(DOM.ENTRY_CONVERTED_FLAVORS)
                time.sleep(2)
                for theFlavor in (listFlavors):
                    retFlavors = retFlavors + theFlavor.text + separatorChar

                return retFlavors[:-1]
            else:
                return False
        except:
            return False

    ######################################################################################

    ######################################################################################
    # Function compareEntryFlavors verifies if flavors on list were transcoded on entry
    # Param:
    #        entryName: entry name - string - mandatory
    #        transcodingFlavors: flavors list - string with comma-separated (or other character, see below) flavor names  (i.e. "Source,Mobile (3GP)")
    #        separatorChar : character that will split the flavors - default =","
    # Return: True= All the flavors were transcoded - False= not all the flavors were transcoded
    ######################################################################################
    def compareEntryFlavors(self, entryName, transcodingFlavors, separatorChar=","):
        comparedFlavors = True
        try:

            # Go to Entry section
            self.logi.appendMsg("INFO - Going to Entry table and searching entry = " + entryName)
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)

            # Select entry
            if self.KmcBasicFuncs.searchEntrySimpleSearch(self.Wd, entryName):

                # Get converted flavors
                time.sleep(1)
                self.logi.appendMsg("INFO - Going to get entry flavors.")
                flavorStr = self.retEntryFlavors(entryName)
                if flavorStr:

                    # Compare entry's flavors with expected flavors
                    self.logi.appendMsg("INFO - Going to compare entry flavors.")
                    flavorList = transcodingFlavors.split(separatorChar)
                    for flavorValue in flavorList:
                        time.sleep(10)
                        self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
                        time.sleep(5)
                        self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH).click()
                        if flavorStr.find(flavorValue) == -1:
                            comparedFlavors = False
                            self.logi.appendMsg("FAIL - Flavor " + flavorValue + " not converted on entry.")
                        else:
                            self.logi.appendMsg("PASS - Flavor " + flavorValue + " converted on entry.")

                else:
                    comparedFlavors = False
                    self.logi.appendMsg("FAIL - No flavors found")
            else:
                comparedFlavors = False
                self.logi.appendMsg("FAIL - Entry not found")
        except:
            comparedFlavors = False
            self.logi.appendMsg("FAIL - Cannot get flavors")

        return comparedFlavors

    #######################################################################################################
    # Function PreviewAndEmbed verifies if the entry plays ok by detecting the QR code that the video plays
    # Param:
    #        env: Testing env is set by isProd - string - mandatory
    #        PreviewEmbedHTTPSSelection: True/False/No param - optional
    #        PreviewEmbedTYPESelectionText:  Dynamic Embed/IFrame Embed/Auto Embed/Thumbnail Embed/No param - optional
    ########################################################################################################

    def PreviewAndEmbed(self, env, PreviewEmbedHTTPSSelection=None, PreviewEmbedTYPESelectionText=None, PlayerVersion=3,
                        PlayerName=None, webdrvr=None, JustPlayOnBrowser=False, TestPlay=True):

        if webdrvr == None:
            webdrvr = self.Wd

        try:
            primTab = webdrvr.window_handles[0]

        except Exception as e:
            print(e)
            pass
        if JustPlayOnBrowser == False:
            try:
                webdrvr.find_element_by_xpath(DOM.SHAREEMBED).click()
                time.sleep(3)
            except:
                self.logi.appendMsg("FAIL - could not find the Share & Embed option")

        if JustPlayOnBrowser == True:
            playerIframe = webdrvr.find_element_by_id('kaltura_player_ifp')
        # webdrvr.switch_to.default_content()

        ################ Set Protocol/Embed Type #################
        # Set player Name
        if PlayerName != None:
            self.logi.appendMsg("INFO - Going to select player. PlayerName = " + PlayerName)

            webdrvr.find_element_by_xpath(DOM.PREVIEWANDEMBED_SELECTPLAYER_FATHER).click()
            time.sleep(2)
            DrpDwnFather = webdrvr.find_element_by_xpath(DOM.PREVIEWANDEMBED_SELECTPLAYER_FATHER)
            DrpDwnFather.find_element_by_xpath(
                DOM.PREVIEWANDEMBED_SELECT_PLAYER.replace("TEXTTOREPLACE", PlayerName)).click()
            time.sleep(2)

        # Set Embed Type
        if PreviewEmbedTYPESelectionText != None:
            self.logi.appendMsg("INFO - Going to press on the Advanced setting link.")
            webdrvr.find_element_by_xpath(DOM.ADVANCED_SETTINGS_LINK).click()
            time.sleep(2)
            self.logi.appendMsg("INFO - Going to select embed type: " + PreviewEmbedTYPESelectionText)

            time.sleep(5)
            # textToFind = "Embed"
            # DrpFatherBTN = self.KmcBasicFuncs.selectOneOfInvisibleSameObjects(webdrvr,DOM.FIELD_TYPE_DROPDOWN,textToFind)
            # DrpFatherBTN.click()
            # time.sleep(2)
            webdrvr.find_element_by_xpath(DOM.PREVIEWANDEMBED_SELECT_EMBERD_TYPE).click()
            DrpDwnFather = webdrvr.find_element_by_xpath(DOM.DROPDOWN_NARROW_FATHER)

            DrpDwnFather.find_element_by_xpath(
                DOM.PREVIEWANDEMBED_EMBEDTYPE.replace("TEXTTOREPLACE", PreviewEmbedTYPESelectionText)).click()
            time.sleep(2)
        # Set HTTPS
        if PreviewEmbedHTTPSSelection != None:
            self.logi.appendMsg("INFO - Going to set PreviewEmbed HTTPS Selection: " + str(PreviewEmbedHTTPSSelection))
            HTTPS_Status_ariachecked_Father = webdrvr.find_element_by_xpath(DOM.PREVIEWANDEMBED_HTTPS)
            HTTPS_Status_ariachecked = HTTPS_Status_ariachecked_Father.find_element_by_xpath(
                DOM.PREVIEWANDEMBED_HTTPS_STATUS).get_attribute("aria-checked")
            if (PreviewEmbedHTTPSSelection == True and HTTPS_Status_ariachecked == "false") or (
                    PreviewEmbedHTTPSSelection == False and HTTPS_Status_ariachecked == "true"):
                webdrvr.find_element_by_xpath(DOM.PREVIEWANDEMBED_HTTPS).click()

        ###########################################################################
        if JustPlayOnBrowser == False:
            time.sleep(2)
            webdrvr.find_element_by_xpath(DOM.PREVIEWEMBEDLINK).click()
            time.sleep(3)

            ShareEmbedTab = webdrvr.window_handles[1]
            webdrvr.switch_to.window(ShareEmbedTab)
            time.sleep(1)

        # iframe in prod env exist only when it is on embed type= iframe embad
        # the iframe  id in testing env is kaltura_player except when it was set to dynamic and the player is V2 
        if PreviewEmbedTYPESelectionText != None:
            if (env == 'testing' and PreviewEmbedTYPESelectionText.lower().find(
                    "dynamic") >= 0 and PlayerVersion == 2) or (
                    PreviewEmbedTYPESelectionText.lower().find("auto") >= 0 and PlayerVersion == 2) or (
                    env == 'prod' and PreviewEmbedTYPESelectionText.lower().find(
                    "dynamic") >= 0 and PlayerVersion == 2):
                playerIframe = webdrvr.find_element_by_id('kaltura_player_ifp')
            elif (env == 'testing' and PreviewEmbedTYPESelectionText.lower().find(
                    "dynamic") < 0 and PreviewEmbedTYPESelectionText.lower().find("iframe") >= 0) or (
                    env == 'prod' and PreviewEmbedTYPESelectionText.lower().find("iframe") >= 0):
                playerIframe = webdrvr.find_element_by_id('kaltura_player')

        ################### Verify protocol ###########################
        UrlOfEmbedPage = webdrvr.current_url
        if PreviewEmbedHTTPSSelection == True:
            self.logi.appendMsg(
                "INFO - Going to verify if the page is playing in the right protocol. PreviewEmbedHTTPSSelection = " + str(
                    PreviewEmbedHTTPSSelection))
            if UrlOfEmbedPage.find("https") == -1:
                self.logi.appendMsg("FAIL - The embed page plays http, instead of https.")
            else:
                self.logi.appendMsg("PASS - The embed page plays https")
        elif PreviewEmbedHTTPSSelection == False:
            self.logi.appendMsg(
                "INFO - Going to verify if the page is playing in the right protocol. PreviewEmbedHTTPSSelection = " + str(
                    PreviewEmbedHTTPSSelection))
            if UrlOfEmbedPage.find("http:") == -1:
                self.logi.appendMsg("FAIL - The embed page plays https, instead of http.")
            else:
                self.logi.appendMsg("PASS - The embed page plays http.")

        ################### Verify Embed code ###########################

        if PreviewEmbedTYPESelectionText == "Auto Embed":
            self.logi.appendMsg(
                "INFO - Going to verify if the page is playing in the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
            if UrlOfEmbedPage.find("auto") == -1:
                self.logi.appendMsg(
                    "FAIL - The entry doesn't play in the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
            else:
                self.logi.appendMsg(
                    "PASS - The entry is played with the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
        elif PreviewEmbedTYPESelectionText == "IFrame Embed":
            self.logi.appendMsg(
                "INFO - Going to verify if the page is playing in the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
            if UrlOfEmbedPage.find("iframe") == -1:
                self.logi.appendMsg(
                    "FAIL - The entry doesn't play in the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
            else:
                self.logi.appendMsg(
                    "PASS - The entry is played with the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
        elif PreviewEmbedTYPESelectionText == "Dynamic Embed":
            self.logi.appendMsg(
                "INFO - Going to verify if the page is playing in the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
            if UrlOfEmbedPage.find("dynamic") == -1:
                self.logi.appendMsg(
                    "FAIL - The entry doesn't play in the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)
            else:
                self.logi.appendMsg(
                    "PASS - The entry is played with the right embed code. PreviewEmbedTYPESelectionText = " + PreviewEmbedTYPESelectionText)

                ###################################################################

        time.sleep(5)

        if (PlayerVersion == 2):
            # if PreviewEmbedTYPESelectionText.lower().find("iframe")>=0:#auto-noswitch
            webdrvr.switch_to.frame(playerIframe)
            if TestPlay:
                try:
                    big_play_button = webdrvr.find_element_by_xpath(DOM.PLAYBTN)
                    if big_play_button.is_displayed():
                        big_play_button.click()
                        return True
                except Exception as e:
                    print(e)
                    return False

        elif (PlayerVersion == 3):
            if PreviewEmbedTYPESelectionText != None:
                if PreviewEmbedTYPESelectionText.lower().find("iframe") >= 0:
                    webdrvr.switch_to.frame(playerIframe)
            if TestPlay:
                try:
                    if env == "prod":
                        play_button = webdrvr.find_element_by_xpath(DOM.PLAYBTNV3_PROD)
                    elif env == "testing":
                        play_button = webdrvr.find_element_by_xpath(DOM.PLAYBTNV3_TESTING)

                    play_button.click()
                    return True
                except Exception as e:
                    print(e)
                    return False
        return True
    # verify the entry preview details elements
    # medialess (Boolean) - default = False - if sent true checks that medialess elements do not display
    def verify_entry_preview_details(self, medialess=False):
        basic_elements = [DOM.ENTRY_ID, DOM.CREATION_DATE, DOM.OWNER, DOM.DURATION, DOM.MODERATION, DOM.PLAYS]
        medialess_non_showing_elements = [DOM.PLAYS, DOM.DURATION]
        entry_type_elements = [DOM.VIDEO_TYPE, DOM.AUDIO_TYPE, DOM.IMAGE_TYPE]

        # Check if the icon of any of the types bellow displays
        for type_xpath in entry_type_elements:
            try:
                rc = self.Wd.find_element_by_xpath(type_xpath)
            except:
                if type_xpath == DOM.IMAGE_TYPE:
                    self.logi.appendMsg("FAIL - medialess element is displaying")
                    return False
                continue

            if rc.is_displayed() == True:
                # Remove duration from basic element list if image type
                if 'kIconimage-small' in type_xpath:
                    basic_elements.remove(DOM.DURATION)

                self.logi.appendMsg("PASS - entry type icon is displaying")
                break

        # Need to check plays and duration elements dose not appear with media less entries
        if medialess:
            # remove both elements from basic list
            basic_elements.remove(DOM.PLAYS)
            basic_elements.remove(DOM.DURATION)
            for non_showing_element_xpath in medialess_non_showing_elements:
                try:
                    rc = self.Wd.find_element_by_xpath(non_showing_element_xpath)

                    if rc.is_displayed() == True:
                        self.logi.appendMsg("FAIL - medialess element is displaying NOT as expected")
                        return False
                except:
                    self.logi.appendMsg("PASS - medialess element is not displaying as expected")
                    continue

        # Verify basic elements appear
        for element_xpath in basic_elements:
            rc = self.Wd.find_element_by_xpath(element_xpath)
            if rc.is_displayed() == True:
                self.logi.appendMsg("PASS - basic element is displaying")
                continue
            else:
                self.logi.appendMsg("FAIL - basic element is not displaying")
                return False

        return True

    # Function to navigate between entries in preview mode
    # navigate_direction (string) - next or previous 
    def navigate_entries(self, navigate_direction):
        try:
            if navigate_direction == 'next':
                self.Wd.find_element_by_xpath(DOM.NEXT_ENTRY_BUTTON).click()
                return True
            elif navigate_direction == 'previous':
                self.Wd.find_element_by_xpath(DOM.PREVIOUS_ENTRY_BUTTON).click()
                return True
        except:
            self.logi.appendMsg("FAIL - entry navigation did not succeed")
            return False

    # verify the entry preview details elements
    # medialess (Boolean) - default = False - if sent true checks that medialess elements do not display
    def verify_entry_side_preview_menu(self, environment):
        basic_elements, remove_side_menu_elements = self.get_side_menu_elements(environment)
        entry_type_elements = [DOM.VIDEO_TYPE, DOM.AUDIO_TYPE, DOM.IMAGE_TYPE]

        # Check if the icon of any of the entry types displays
        for type_xpath in entry_type_elements:
            try:
                rc = self.Wd.find_element_by_xpath(type_xpath)
            except:
                if type_xpath == DOM.IMAGE_TYPE:
                    self.logi.appendMsg("FAIL - medialess element is displaying")
                    return False
                continue

            if rc.is_displayed() == True:
                self.logi.appendMsg("PASS - entry type icon is displaying")

                # Remove duration from basic element list if image type
                if 'kIconimage-small' in type_xpath:
                    for remove_ele in remove_side_menu_elements:
                        basic_elements.remove(remove_ele)

                if 'kIconsound-small' in type_xpath:
                    if environment == 'prod':
                        basic_elements.remove(DOM.DISTRIBUTION)

                break

        # Verify basic elements appear
        for element_xpath in basic_elements:
            rc = self.Wd.find_element_by_xpath(element_xpath)
            if rc.is_displayed() == True:
                self.logi.appendMsg("PASS - basic element is displaying")
                continue
            else:
                self.logi.appendMsg("FAIL - basic element is not displaying")
                return False

        return True

    # function to cycle through the entry preview side menu
    # verify that the title changes according to the selected menu
    # environment (string) - testing or prod - send as self.env from test file
    def cycle_through_side_menu(self, environment):
        # list of basic elements
        basic_elements, remove_side_menu_elements = self.get_side_menu_elements(environment)
        entry_type_elements = [DOM.VIDEO_TYPE, DOM.AUDIO_TYPE, DOM.IMAGE_TYPE]

        # list is set up according to the environment, no DISTRIBUTION_TITLE in prod
        if environment == 'testing':
            text_menu = [DOM.METADATA_TITLE, DOM.THUMBNAILS_TITLE, DOM.ACCESS_CONTROL_TITLE, DOM.SCHEDULING_TITLE,
                         DOM.FLAVORS_TITLE,
                         DOM.CAPTIONS_TITLE, DOM.RELATED_FILES_TITLE, DOM.CLIPS_TITLE, DOM.USERS_TITLE,
                         DOM.ADVERTISEMENTS_TITLE]
            remove_text_menu = [DOM.THUMBNAILS_TITLE, DOM.FLAVORS_TITLE, DOM.CAPTIONS_TITLE, DOM.CLIPS_TITLE,
                                DOM.ADVERTISEMENTS_TITLE]
        elif environment == 'prod':
            text_menu = [DOM.METADATA_TITLE, DOM.THUMBNAILS_TITLE, DOM.ACCESS_CONTROL_TITLE, DOM.SCHEDULING_TITLE,
                         DOM.FLAVORS_TITLE,
                         DOM.DISTRIBUTION_TITLE, DOM.CAPTIONS_TITLE, DOM.RELATED_FILES_TITLE, DOM.CLIPS_TITLE,
                         DOM.USERS_TITLE,
                         DOM.ADVERTISEMENTS_TITLE]
            remove_text_menu = [DOM.THUMBNAILS_TITLE, DOM.FLAVORS_TITLE, DOM.DISTRIBUTION_TITLE, DOM.CAPTIONS_TITLE,
                                DOM.CLIPS_TITLE,
                                DOM.ADVERTISEMENTS_TITLE]

        # Check if the icon of any of the types bellow displays
        for type_xpath in entry_type_elements:
            try:
                rc = self.Wd.find_element_by_xpath(type_xpath)
            except:
                if type_xpath == DOM.IMAGE_TYPE:
                    self.logi.appendMsg("FAIL - medialess element is displaying")
                    return False
                continue

            if rc.is_displayed() == True:
                self.logi.appendMsg("PASS - entry type icon is displaying")

                # Remove duration from basic element list if image type
                if 'kIconimage-small' in type_xpath:
                    for remove_ele in remove_side_menu_elements:
                        basic_elements.remove(remove_ele)

                    for remove_ele in remove_text_menu:
                        text_menu.remove(remove_ele)

                if 'kIconsound-small' in type_xpath:
                    if environment == 'prod':
                        basic_elements.remove(DOM.DISTRIBUTION)
                        text_menu.remove(DOM.DISTRIBUTION_TITLE)

                break

        time.sleep(1)

        # Verify text element appear when menu item is selected
        for element_xpath, title in zip(basic_elements, text_menu):
            rc = self.Wd.find_element_by_xpath(element_xpath)
            if rc.is_displayed() == True:
                rc.click()
                time.sleep(1)
                preview_title = self.Wd.find_element_by_xpath(title)
                if preview_title.is_displayed() == True:
                    continue
            else:
                self.logi.appendMsg("FAIL - basic element is not displaying")
                return False

        return True

    # Gets the environment type (testing OR prod) and returns the list of side elements and elements to be removed
    def get_side_menu_elements(self, environment):
        try:
            if environment == 'testing':
                basic_elements = [DOM.METADATA, DOM.THUMBNAILS, DOM.ACCESS_CONTROL, DOM.SCHEDULING, DOM.FLAVORS,
                                  DOM.CAPTIONS, DOM.RELATED_FILES, DOM.CLIPS, DOM.USERS, DOM.ADVERTISEMENTS]
                remove_side_menu_elements = [DOM.THUMBNAILS, DOM.FLAVORS, DOM.CAPTIONS, DOM.CLIPS, DOM.ADVERTISEMENTS]
            elif environment == 'prod':
                basic_elements = [DOM.METADATA, DOM.THUMBNAILS, DOM.ACCESS_CONTROL, DOM.SCHEDULING, DOM.FLAVORS,
                                  DOM.DISTRIBUTION, DOM.CAPTIONS, DOM.RELATED_FILES, DOM.CLIPS, DOM.USERS,
                                  DOM.ADVERTISEMENTS]
                remove_side_menu_elements = [DOM.THUMBNAILS, DOM.FLAVORS, DOM.DISTRIBUTION, DOM.CAPTIONS, DOM.CLIPS,
                                             DOM.ADVERTISEMENTS]

            return basic_elements, remove_side_menu_elements

        except:
            self.logi.appendMsg("FAIL - basic element is not displaying")
            return False

    ######################################################################################
    # Function SortEntryThumbnailsTable : sorting the entry's thumbnails table by 'byColName' (currently by Dimensions
    # Params:
    #    byColName : currently Dimensions 
    #    sortOrder : asc- smallest on top, desc-largest on top
    ######################################################################################
    def SortEntryThumbnailsTable(self, byColName="Dimensions", sortOrder="asc"):
        try:
            self.logi.appendMsg("INFO - Going to sort thumbnails' table by " + str(byColName))
            # get 'sortable column icon' element (sort arrow)
            upDown = self.Wd.find_element_by_xpath(DOM.THUMBNAIL_DIMENSIONS_UP_DOWN)
            # get the (sort type) element's state - up or down
            currentState = upDown.get_attribute('class').split('sort-')[1]

            if (currentState != 'amount-up') and (currentState != 'amount-down'):
                self.logi.appendMsg("FAILED to get the element's state - up or down")

            # Clicking on the Dimensions col title for sort (up or down) according to the sort type- 'asc' or 'desc'
            if sortOrder == "asc":
                if (currentState == 'down'):
                    upDown.click()
            else:  # 'desc' order
                if (currentState == 'up'):
                    upDown.click()

            time.sleep(1)

            # Get all dimensions strings for all the thumbnails' rows
            dimensionsList = self.Wd.find_elements_by_xpath(DOM.THUMBNAIL_DIMENSIONS)

            if len(dimensionsList) < 3:  # checking thumbnails' number (2 is the minimum number for sorting)
                self.logi.appendMsg("FAIL - Sort is not relevant for less than 2 thumbnails")
                return False

            for i in range(len(dimensionsList)):
                if i != len(dimensionsList) - 1:
                    # get current width from dimensions string
                    currentDimensions = int(dimensionsList[i].text.split("x")[0])
                    # get next width from dimensions string
                    nextDimensions = int(dimensionsList[i + 1].text.split("x")[0])
                    if sortOrder == "asc":
                        # failure - from largest width to smallest
                        if currentDimensions < nextDimensions:
                            self.logi.appendMsg("FAIL - Thumbnails' table was NOT sorted successfully")
                            return False
                    elif sortOrder == "desc":
                        if currentDimensions > nextDimensions:
                            self.logi.appendMsg("FAIL - Thumbnails' table was NOT sorted successfully")
                            return False

            self.logi.appendMsg("PASS - Thumbnails' table was sorted successfully")
            return True

        except Exception as Exp:
            print(Exp)
            return False
