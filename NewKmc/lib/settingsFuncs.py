'''
Created on Jan 07, 2019

@author: Adi.Miller
'''


import time
# TODO: check if builtins is in use


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import DOM
import KmcBasicFuncs



class settingsfuncs:
    
    def __init__(self, Wd, logi):
        self.Wd = Wd
        self.logi = logi
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        
       
    
    
    def AddCustomField(self, fieldType, fieldLabel, listValues=None, maxValues=None, shortDesc=None, description=None, searchable=False):
        
        numOfRowsBefore = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)                   
        #Click on 'Add Custom Field' button
        self.Wd.find_element_by_xpath(DOM.ADD_CUSTOM_FIELD_BUTTON).click()
        time.sleep(3) 
        
        #Add field label
        self.Wd.find_element_by_xpath(DOM.FIELD_LABEL).send_keys(fieldLabel)                           
        
        #Open 'Field Type' dropdown list                                                                     
        self.Wd.find_elements_by_xpath(DOM.FIELD_TYPE_DROPDOWN)[1].click()
        time.sleep(1)
        #Select the relevant fieldType from the list        
        fieldTypes = self.Wd.find_elements_by_xpath(DOM.FIELD_TYPE_SELECT_LIST)
        for fieldtype in fieldTypes:
            if fieldtype.text.find(fieldType)>=0:
                fieldtype.click()
                time.sleep(1)
                break
        
        #Check field type
        if (fieldType == "Text select list" ):
            values = listValues.split(",")
            newVal = ""
            for value in values:   
                newVal = newVal + value + Keys.RETURN
                
            self.Wd.find_element_by_xpath(DOM.LIST_VALUES_TEXTBOX).send_keys(newVal)
                
        #Click on Add button
        self.Wd.find_element_by_xpath(DOM.ADD_BUTTON_CUSTOM_FIELD).click()
        time.sleep(2)
        
        numOfRowsAfter = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)  
        
        if numOfRowsBefore+1 == numOfRowsAfter:
            self.logi.appendMsg("PASS - field " + fieldLabel + " of type: " + fieldType + " was added") 
            return True
        else:             
            self.logi.appendMsg("FAIL - field " + fieldLabel + " of type: " + fieldType + " was NOT added")
            return False
        
    
    # this def add sccess control profile
    # support authorized domain and authorized counteries sections,
    #  authorizedDomains and  authorizedCountries values can be 'all' (default), 'selected' or 'blocked'  
    def addAccessControlProfile(self, profileName, profileDesc, authorizedDomains='all', theDomains='none', authorizedCountries='all', theCountries='none'):
        
        try:
            self.logi.appendMsg("INFO - going to add new access control")
            self.logi.appendMsg("INFO - new access control parameterswould be: name= " + profileName + " description= " + profileDesc + " authorized Domains=" + authorizedDomains + " the authorized Domains= " + theDomains + " authorized Countries=" + authorizedCountries + " the authorized Countries=" + theCountries)
            self.navigate_to_access_control_menu()
            time.sleep(5)
            numofRowsBefore = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            self.Wd.find_element_by_xpath(DOM.ACCESS_CONTROL_ADD_PROFILE).click()
            time.sleep(1)
        except Exception as e:
            print(e)
        
        #set profile name and desc
        self.Wd.find_element_by_xpath(DOM.ACCESS_CONTROL_PROFILE_NMAE).send_keys(profileName)
        self.Wd.find_element_by_xpath(DOM.ACCESS_CONTROL_PROFILE_DESC).send_keys(profileDesc)
        
        # get the window and rows within it
        addProfileWin = self.Wd.find_element_by_xpath(DOM.POPUP_WIN)
        formRows = addProfileWin.find_elements_by_xpath(DOM.ACCESS_CONTROL_ADD_ROWS)
        
        if authorizedDomains!="all":
            if authorizedDomains == "selected":
                isSelected = True
                authorizedDomains = DOM.ACCESS_CONTROL_RBTN_GLOB.replace('TEXTTOREPLACE','Selected Domains Only')
                
            else:
                authorizedDomains = DOM.ACCESS_CONTROL_RBTN_GLOB.replace('TEXTTOREPLACE','Block Selected Domains')
            
            self.Wd.find_element_by_xpath(authorizedDomains).click()
            
            # insert the domain to the input text
            if isSelected:
                time.sleep(1)
                input_domain = self.Wd.find_elements_by_xpath(DOM.ACCESS_CONTROL_DOMAINS_INPUT)
                input_domain[0].send_keys(theDomains + Keys.RETURN)
            else:
                self.Wd.find_elements_by_xpath(DOM.ACCESS_CONTROL_DOMAINS_INPUT)[1].send_keys(theDomains + Keys.RETURN)
            
            
        if authorizedCountries!="all":
            self.Wd.execute_script("document.querySelector('body > kpopupwidget.opened > div > div > kaccesscontrolprofileseditprofile > div > form').scrollTo({top: 550, behavior: 'smooth'})")
            time.sleep(1)
            drpDownBtns= self.Wd.find_elements_by_xpath(DOM.COUNTRIES_LIST_DROP_DOWN_BTN)
            if authorizedCountries == "selected":
                authorizedCountries = DOM.ACCESS_CONTROL_RBTN_GLOB.replace('TEXTTOREPLACE','Selected Countries Only')
                isSelected = True
                drpDownBtn = drpDownBtns[0]
            else:
                authorizedCountries = DOM.ACCESS_CONTROL_RBTN_GLOB.replace('TEXTTOREPLACE','Block Selected Countries')
                drpDownBtn = drpDownBtns[1]
            
            self.Wd.find_element_by_xpath(authorizedCountries).click()
            drpDownBtn.click()
            self.Wd.find_element_by_xpath(DOM.COUNTRIES_LIST_FILTER_TXT).send_keys(theCountries)
            chk = self.BasicFuncs.selectOneOfInvisibleSameObjects(self.Wd,DOM.COUNTRIES_CHECKBOX)
            chk.click()
            drpDownBtn.click()
        
        
        self.Wd.find_element_by_xpath(DOM.SAVE_BTN).click()
        try:    
            self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE)
            self.Wd.find_element_by_xpath(DOM.GLOBAL_YES_BUTTON)
        except:
            print("No popup message after saving")

        # verify new access control was added
        time.sleep(3)
        numofRowsAfter = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
        if numofRowsBefore+1 == numofRowsAfter:
            self.logi.appendMsg("PASS- new access control created successfully")
            return True
        else:
            self.logi.appendMsg("FAIL- new access control was NOT created successfully")
            return False


    def navigate_to_access_control_menu(self):
        try:
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
            time.sleep(2)
            self.Wd.find_element_by_xpath(DOM.TAB_ACCESS_CONTROL).click()
        except:
            self.logi.appendMsg("FAIL - cannot navigate to access control menu")
       

    ##########################################################
    # Function addTranscodingProfile: adds a Transcoding Profile on Transcoding Settings
    # Params:
    #        profileName: Transcoding profile name - string - mandatory
    #        profileType: 1-Common/2-Live - numeric - default=1
    #        flavors: flavors to be added to the Transcoding Profile - string with comma-separated (or other character, see below)
    #                 flavor names  (i.e. "Source,Mobile (3GP)") - default="Source"
    #                 Send in flavor name - "No flavor" to not select any flavor
    #        profileDesc: Transcoding profile description - string - default=""
    #        defaultMetadata: Transcoding profile default metadata field - string - default=""
    #        separatorChar: flavors param  seperator character - default = ","
    ##########################################################
    def addTranscodingProfile(self, profileName, profileType = 1, flavors="Source", profileDesc = "", defaultMetadata = "", separatorChar = ","):
        
        # Go to Transcoding Settings section
        self.openTranscodingMenu()
        
        # Check number of rows on Trancoding Profile list
        self.logi.appendMsg("INFO - Checking number of existing Transcoding Profiles")
        rowsBefore = self.retNumOfRowsTranscProfiles(profileType)
                
        # Press Add Profile button as per profile type
        self.logi.appendMsg("INFO - Going to press Add Profile button")
        self.Wd.find_elements_by_xpath(DOM.TRANSCODING_ADD_PROFILE)[profileType-1].click()
        
        # Fill fields as per parameters
        time.sleep(1)
        self.logi.appendMsg("INFO - Going to fill fields")
        self.logi.appendMsg("INFO - Going to fill Name with " + profileName)
        self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_NAME).send_keys(profileName)
        time.sleep(1)
        self.logi.appendMsg("INFO - Going to fill Description with " + profileDesc)
        self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_DESCRIPTION).send_keys(profileDesc)
        time.sleep(1)
        self.logi.appendMsg("INFO - Going to fill Default Metadata Settings with " + defaultMetadata)
        self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_METADATA).send_keys(defaultMetadata)
        time.sleep(1)
        
        # Press Save button
        self.logi.appendMsg("INFO - Going press SAVE on pop-up")
        self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON).click()
        time.sleep(1)
        self.logi.appendMsg("INFO - Going verify Default Metadata Settings")
        try:
            # Checks if the Metadata Settings entry is displayed, if true will exit the creation of the profile
            rc = self.Wd.find_element_by_xpath(DOM.TRANSCODING_ERROR_MSG)
            if rc.is_displayed() == True:
                self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_OK).click()
                self.logi.appendMsg("INFO - wrong entry metadata settings error message displayed")
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.UPLOAD_CANCEL).click()
                return False
        except:
            pass
        self.logi.appendMsg("INFO - Checking for New Profile page...")
        time.sleep(3)
        
        # Check the flow goes to New Profile page (checks ID "new" , Title = profileName and trancoding icon)
        try:
            if profileType == 1:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_ICON)
            else:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_LIVEICON)
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_NEW_ID)
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_PROFILE_TITLE.replace('TEXTTOREPLACE',profileName))
            self.logi.appendMsg("INFO - New Profile page found")
        except:
            self.logi.appendMsg("FAIL - New Profile page not found")
        self.logi.appendMsg("INFO - Going to check flavors: " + flavors)
        time.sleep(1)
        
        # Check flavors checkboxes
        flavorList = flavors.split(separatorChar)
        for flavorValue in flavorList:
            if flavorValue == "No flavor":
                break
            self.logi.appendMsg("INFO - Checking " + flavorValue)
            dynamicDOM = DOM.TRANSCODING_FLAVOR_CHECKBOX.replace('TEXTTOREPLACE',flavorValue)
            self.Wd.find_element_by_xpath(dynamicDOM).click()
        time.sleep(2)
        self.logi.appendMsg("INFO - Going press SAVE on Transcoding Profile page")
        try:
            time.sleep(1)
            save_button = self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON)
            if save_button.is_displayed():
                save_button.click()
                time.sleep(1)
                try:
                    self.Wd.find_element_by_xpath(DOM.ADD_EXISTING_ALERT_YES).click()
                except:
                    pass
        except:
            self.logi.appendMsg("FAIL - SAVE failed")
        time.sleep(1)
        
        # Checking warning pop-up saving w/o flavors
        try:
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_ERR_POPUP)
            try:
                self.logi.appendMsg("INFO - No flavors were selected")
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_POPUP_YES_BUTTON).click()
                self.logi.appendMsg("INFO - SAVE performed but with no flavors")
            except:
                self.logi.appendMsg("FAIL - SAVE with no flavors failed")
        except:    
            self.logi.appendMsg("INFO - SAVE performed with flavors")
            pass

        time.sleep(2)
        
        # Return to Transcoding Profiles main page
        self.logi.appendMsg("INFO - Going back to Transcoding Profiles main page")
        try:
            time.sleep(1)
            backward_button = self.Wd.find_element_by_xpath(DOM.TRANSCODING_BACKWARD_BUTTON)
            if backward_button.is_displayed():
                backward_button.click()
        except:
            self.logi.appendMsg("FAIL - Backward button failure")
        time.sleep(5)
        
        # Check number of rows on Trancoding Profile list
        self.logi.appendMsg("INFO - Checking number of Transcoding Profiles")
        rowsAfter = self.retNumOfRowsTranscProfiles(profileType)
        if rowsBefore+1 == rowsAfter:
            self.logi.appendMsg("PASS - New Transcoding Profile created successfully")
            return True
        else:
            self.logi.appendMsg("FAIL - New Transcoding Profile was NOT created successfully")
            return False
    ##########################################################
    
    
    ##########################################################
    # Function retNumOfRowsTrasncProfiles returns the numbers of rows of Transcoding Profiles on Transcoding Settings
    # Params:
    #        profileType: 1-Common/2-Live - numeric - default=1
    ##########################################################
    def retNumOfRowsTranscProfiles(self, profileType = 1):
        try:
            profileList=self.Wd.find_elements_by_xpath(DOM.TRANSCODING_TABLE)[profileType-1]
        except:
            self.logi.appendMsg("FAIL - Cannot find table")
        numRows= len(profileList.find_elements_by_xpath(DOM.ENTRY_ROW))
        return numRows
    ##########################################################
    
    
    ##########################################################
    # Function deleteTranscodingProfiles: deletes  Transcoding Profile on Transcoding Settings matching the name & type provided
    # Params:
    #        profileName: Transcoding profile name - string - mandatory
    #        profileType: 1-Common/2-Live - numeric - default=1
    #        confirmDelete: default = true, send False to cancel delete
    ##########################################################

    def deleteTranscodingProfiles(self, profileName, profileType = 1, deleteFromActionMenu=False,confirmDelete=True):        
        # Go to Transcoding Settings section
        self.openTranscodingMenu()

        try:

            # Search for the transcoding profile on list
            self.logi.appendMsg("INFO - Checking Transcoding Profiles to delete with name = " + profileName)
            profileList = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_TABLE)[profileType-1]
            dynamicDOM = DOM.TRANSCODING_ROW_CHECKBOX.replace('TEXTTOREPLACE', profileName)
            trProfiles = profileList.find_elements_by_xpath(dynamicDOM)
            if trProfiles:

                # Check checboxes of rows found or delete by action menu
                for transProf in trProfiles:
                    if deleteFromActionMenu == True and profileName in dynamicDOM:
                        xpath_list = [DOM.TRANSCODING_DELETE_POPUP_NO, DOM.TRANSCODING_DELETE_POPUP_YES]
                        # lists of the action menu and names
                        tableAction = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_ROW_ACTIONS)
                        tabelNames = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_ROW_NAME)
                        for webElement in range(len(tabelNames)):
                            webElementText = tabelNames[webElement].text
                            # check if the given profile name exists in the transcoding profiles list (Vod and Live)
                            # first iteration cancel delete of transcoding profile
                            # second deletes the transcoding profile via action menu and exits the loop
                            if profileName in webElementText:
                                for i in xpath_list:
                                    tableAction[webElement].click()
                                    time.sleep(1)
                                    self.Wd.find_element_by_xpath(DOM.TRANSCODING_ROW_ACTION_DELETE).click()
                                    time.sleep(1)
                                    self.Wd.find_element_by_xpath(i).click()
                                    time.sleep(5)
                                    if "Yes" in i:
                                        return True
                    else:
                        transProf.click()

                if deleteFromActionMenu == False:
                    # Press Bulk Delete button on header
                    self.logi.appendMsg("INFO - Bulk delete of Transcoding Profiles")
                    time.sleep(0.5)
                    self.Wd.find_elements_by_xpath(DOM.TRANSCODING_BULK_DELETE)[profileType-1].click()
                    time.sleep(1)

                # Check Delete popup and confirm
                try:
                    self.Wd.find_element_by_xpath(DOM.TRANSCODING_DELETE_POPUP)
                    if confirmDelete:
                        self.Wd.find_element_by_xpath(DOM.TRANSCODING_DELETE_POPUP_YES).click()
                    else:
                        self.Wd.find_element_by_xpath(DOM.TRANSCODING_DELETE_POPUP_NO).click()
                        return True
                except:
                    self.logi.appendMsg("FAIL - Confirmation pop-up not found or Yes button error")
                    assert False
                time.sleep(1)

                # Check all the transcoding profiles selected where deleted
                self.logi.appendMsg("INFO - Checking if Transcoding Profiles  were deleted...")
                profileList = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_TABLE)[profileType-1]
                dynamicDOM = DOM.TRANSCODING_ROW_CHECKBOX.replace('TEXTTOREPLACE', profileName)
                trProfiles = profileList.find_elements_by_xpath(dynamicDOM)
                if trProfiles:
                    self.logi.appendMsg("INFO - Not all Transcoding Profiles were deleted")
                    if confirmDelete == False:
                        self.logi.appendMsg("PASS - Transcoding Profiles were not deleted after confirm cancellation")
                        return True
                else:
                    self.logi.appendMsg("PASS - Transcoding Profiles deleted")
            else:
                self.logi.appendMsg("INFO - No Transcoding Profiles to delete")
        except:
            self.logi.appendMsg("FAIL - Cannot delete Transcoding Profiles")
            assert False
    ##########################################################

    ##########################################################
    # Function updateTranscodingProfile: upadtes the last Transcoding Profile added on Transcoding Settings
    # Params:
    #        profileName: Original transcoding profile name - string - mandatory
    #        profileType: 1-Common/2-Live - numeric - default=1
    #        profileNameNew: New transcoding profile name - string - default="" -> (not update)
    #        flavors: flavors to be updated to the Transcoding Profile - string with comma-separated (or other character, see below) flavor names  (i.e. "Source,Mobile (3GP)") - default="" -> (not update)
    #        profileDesc: Transcoding profile description - string - default="" -> (not update)
    #        defaultMetadata: Transcoding profile default metadata field - string - default="" -> (not update)
    #        separatorChar: flavors param  seperator character - default = ","
    ##########################################################
    def updateTranscodingProfile(self, profileName, profileType = 1, profileNameNew = "",flavors="", profileDesc = "", defaultMetadata = "", separatorChar = ",", exitWithoutSaving=False):

        # Go to Transcoding Settings section
        self.openTranscodingMenu()
        transcodingId = 0

        self.openTranscodingProfile(profileName, profileType)

        # Check the flow goes to Profile page and replace metadata values
        try:

            # Check type of profile
            self.logi.appendMsg("INFO - Going to check Transcoding Profile update screen")
            if profileType == 1:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_ICON)
            else:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_LIVEICON)

            # Check Id and name are correct
            try:
                # self.Wd.find_element_by_xpath(DOM.TRANSCODING_UPDATE_ID.replace('TEXTTOREPLACE',str(transcodingId)))
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_PROFILE_TITLE.replace('TEXTTOREPLACE',profileName))
            except Exception as e:
                print(e)

            # Replace Metadata values
            self.logi.appendMsg("INFO - Going to fill fields")
            self.logi.appendMsg("INFO - Going to fill Name with " + profileNameNew)
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_NAME).send_keys(Keys.CONTROL, 'a')
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_NAME).send_keys(profileNameNew)
            time.sleep(1)
            self.logi.appendMsg("INFO - Going to fill Description with " + profileDesc)
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_UPDATE_DESCRIPTION).send_keys(Keys.CONTROL, 'a')
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_UPDATE_DESCRIPTION).send_keys(profileDesc)
            time.sleep(1)
            self.logi.appendMsg("INFO - Going to fill Default Metadata Settings with " + defaultMetadata)
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_METADATA).send_keys(Keys.CONTROL, 'a')
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_METADATA).send_keys(defaultMetadata)
            time.sleep(1)

            # Check flavors checkboxes
            self.logi.appendMsg("INFO - Going to Flavors section and update flavors checkboxes")
            self.Wd.find_element_by_xpath(DOM.ENTRY_FLAVORS_TAB).click()
            time.sleep(1)
            headerDOM = self.Wd.find_element_by_xpath(DOM.GLOBAL_TABLE_HEADLINE)
            headerDOM.find_element_by_xpath(DOM.ENTRY_CHECKBOX).click()
            time.sleep(0.5)
            headerDOM.find_element_by_xpath(DOM.ENTRY_CHECKBOX).click()
            time.sleep(0.5)
            flavorList = flavors.split(separatorChar)

            for flavorValue in flavorList:
                self.logi.appendMsg("INFO - Checking " + flavorValue)
                dynamicDOM = DOM.TRANSCODING_FLAVOR_CHECKBOX.replace('TEXTTOREPLACE',flavorValue)
                self.Wd.find_element_by_xpath(dynamicDOM).click()

            time.sleep(1)
            rc = self.exit_without_saving(exitWithoutSaving)

            if rc == True:
                self.logi.appendMsg("INFO - Exit without saving successful")
                return True
            else:
                self.logi.appendMsg("INFO - Exit without saving NOT successful")
                pass

            # Save changes
            self.logi.appendMsg("INFO - Going press SAVE on Transcoding Profile page")
            try:
                time.sleep(1)
                save_button = self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON)
                if save_button.is_displayed():
                    save_button.click()
            except:
                self.logi.appendMsg("FAIL - SAVE failed")
                return False
            time.sleep(1)

            # Checking warning pop-up saving w/o flavors
            try:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_ERR_POPUP)
                try:
                    self.logi.appendMsg("INFO - No flavors were selected")
                    self.Wd.find_element_by_xpath(DOM.TRANSCODING_POPUP_YES_BUTTON).click()
                    self.logi.appendMsg("INFO - SAVE performed but with no flavors")
                except:
                    self.logi.appendMsg("FAIL - SAVE with no flavors failed")
                    return False
            except:
                self.logi.appendMsg("INFO - SAVE performed with flavors")
                pass
            time.sleep(3)
            self.logi.appendMsg("INFO - Update Profile "+profileName+" page found and fields replaced")
            return True
        except:
            self.logi.appendMsg("FAIL - Update Profile "+profileName+" page not found or fields not replaced properly")
            return False


    ##########################################################

    def openTranscodingProfile(self, profileName, profileType):
        # Go to relevant Update transcoding profile screen
        try:
            transcodingId = 0

            # Search for the transcoding profile on list
            self.logi.appendMsg("INFO - Searching Transcoding Profile " + profileName + " to update...")
            profileList = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_TABLE)[profileType-1]
            dynamicDOM = DOM.TRANSCODING_ROW_ID.replace('TEXTTOREPLACE', profileName)
            trProfiles = profileList.find_elements_by_xpath(dynamicDOM)
            time.sleep(3)
            if trProfiles:

                # Check IDs of rows found and get last added row object
                numRows = len(trProfiles)
                for colTP in range(numRows):
                    valueDOM = int(trProfiles[colTP].text)
                    if valueDOM > transcodingId:
                        transcodingId = valueDOM

                # Go to update screen
                dynamicDOM = DOM.TRANSCODING_ROW_NAME_BY_ID.replace('TEXTTOREPLACE', str(transcodingId))
                profileList.find_element_by_xpath(dynamicDOM).click()
                time.sleep(3)
            else:
                self.logi.appendMsg("FAIL - No Transcoding Profile to update")
                return False
        except:
            self.logi.appendMsg("FAIL - Cannot find Transcoding Profile to update")
            return False


    ##########################################################
    # Function getTranscodingProfile retrieves the metadata and flavors from last TP with param name added
    # Params:
    #        profileName: Original transcoding profile name - string - mandatory
    #        profileType: 1-Common/2-Live - numeric - default=1
    # Return:
    #        dataOK: True/False - returns if get data is OK
    #        metadataTP: array in a way [NAME,DESCRIPTION,ENTRY_ID]
    #        flavorsTP: array of flavors configured on the TP
    ##########################################################
    def getTranscodingProfile(self, profileName, profileType = 1):
        metadataTP=[]
        flavorsTP=[]
        transcodingId = 0
        dataOK = True

        try:
            # Go to Transcoding Settings section
            self.openTranscodingMenu()

            # Search for the transcoding profile on list
            self.logi.appendMsg("INFO - Searching last Transcoding Profile " + profileName)
            profileList = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_TABLE)[profileType-1]
            dynamicDOM = DOM.TRANSCODING_ROW_ID.replace('TEXTTOREPLACE', profileName)
            trProfiles = profileList.find_elements_by_xpath(dynamicDOM)
            time.sleep(3)
            if trProfiles:

                # Check IDs of rows found and get last added row object
                numRows = len(trProfiles)
                for colTP in range(numRows):
                    valueDOM = int(trProfiles[colTP].text)
                    if valueDOM > transcodingId:
                        transcodingId = valueDOM

                # Go to screen
                dynamicDOM = DOM.TRANSCODING_ROW_NAME_BY_ID.replace('TEXTTOREPLACE', str(transcodingId))
                profileList.find_element_by_xpath(dynamicDOM).click()
                time.sleep(3)

                # Get metadata
                self.logi.appendMsg("INFO - Get Transcoding Profile Metadata")
                metadataTP.append(self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_NAME).get_attribute("value"))
                metadataTP.append(self.Wd.find_element_by_xpath(DOM.TRANSCODING_UPDATE_DESCRIPTION).get_attribute("value"))
                metadataTP.append(self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_METADATA).get_attribute("value"))

                # Get flavors
                self.logi.appendMsg("INFO - Get Transcoding Profile Flavors")
                self.Wd.find_element_by_xpath(DOM.ENTRY_FLAVORS_TAB).click()
                time.sleep(2)
                trFlavors = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_FLAVOR_NAME_SELECTED)
                for flavorRow in (trFlavors):
                    flavorsTP.append((flavorRow.text).strip())

        except:
            dataOK = False
            metadataTP = []
            flavorsTP = []
            self.logi.appendMsg("INFO - Error trying to get Transcoding Profile data")

        return dataOK,metadataTP,flavorsTP
    ##########################################################


    ######################################################################################
    # Function compareTranscodingProfile verifies if metadata & flavors set on a Transcoding Profile are correct
    # Param:
    #        profileName: Transcoding profile name - string - mandatory
    #        profileType: 1-Common/2-Live - numeric - mandatory
    #        profileDesc: Transcoding profile description - string - mandatory
    #        defaultMetadata: Transcoding profile default metadata field (Entry ID)  - string - mandatory
    #        transcodingFlavors: flavors  - string with comma-separated (or other character, see below) flavor names  (i.e. "Source,Mobile (3GP)") - mandatory
    #        separatorChar: flavors param  seperator character - default = ","
    # Return: True= All the data is OK - False= Some data is NOT OK
    ######################################################################################
    def compareTranscodingProfile(self, profileName, profileType, profileDesc, defaultMetadata ,transcodingFlavors, separatorChar = ","):
        comparedData = True
        metadataTP = []
        flavorsTP = []
        compMetadata = [profileName,profileDesc,defaultMetadata]
        try:

            # Get TP data
            comparedData,metadataTP,flavorsTP = self.getTranscodingProfile(profileName, profileType)

            if comparedData:

                # Compare Metadata
                if metadataTP:
                    self.logi.appendMsg("INFO - Going to compare Transcoding Profile Metadata.")
                    for xComp in range(3):
                        if metadataTP[xComp] == compMetadata[xComp]:
                            self.logi.appendMsg("PASS - Metadata " + compMetadata[xComp] + " on Transcoding Profile.")
                        else:
                            comparedData = False
                            self.logi.appendMsg("FAIL - Metadata " + compMetadata[xComp] + " is not present on Transcoding Profile.")
                else:
                    comparedData = False
                    self.logi.appendMsg("FAIL - No Metadata found")

                # Compare Flavors
                if flavorsTP:

                    # Compare TP's flavors with expected flavors
                    self.logi.appendMsg("INFO - Going to compare Transcoding Profile flavors.")
                    flavorList = transcodingFlavors.split(separatorChar)
                    if len(flavorList) == len(flavorsTP):
                        for flavorValue in flavorsTP:
                            if transcodingFlavors.find(flavorValue) == -1:
                                comparedData = False
                                self.logi.appendMsg("FAIL - Flavor " + flavorValue + " not present on Transcoding Profile.")
                            else:
                                self.logi.appendMsg("PASS - Flavor " + flavorValue + " on Transcoding Profile.")
                    else:
                        comparedData = False
                        self.logi.appendMsg("FAIL - Expected amount of flavors does not match.")

                else:
                    comparedData = False
                    self.logi.appendMsg("FAIL - No flavors found.")

            else:
                self.logi.appendMsg("FAIL - Error getting Transcoding Profile data.")

        except:
            comparedData = False
            self.logi.appendMsg("FAIL - Data Not Found.")

        return comparedData

    def setDefaultTranscodingProfile(self, profileName):
        try:
            # Go to Transcoding Settings section
            self.openTranscodingMenu()

            self.logi.appendMsg("INFO - Going to set Transcoding Profile to default")
            # lists of the action menu and names
            tableAction = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_ROW_ACTIONS)
            tabelNames = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_ROW_NAME)
            for webElement in range(len(tabelNames)):
                webElementText = tabelNames[webElement].text
                # check if the given profile name exists in the transcoding profiles list (Vod and Live)
                # first iteration cancel delete of transcoding profile
                # second deletes the transcoding profile via action menu and exits the loop
                if profileName in webElementText:
                    tableAction[webElement].click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.TRANSCODING_ROW_ACTION_SET_AS_DEFAULT).click()
                    time.sleep(1)
                    return True
        except:
            self.logi.appendMsg("FAIL - Cannot set Transcoding Profile to default")
            return False

    ######################################################################################
    # Function verifies if the requested transcoding profile is set to default
    # Param:
    #        profileName: Transcoding profile name - string - mandatory
    # Return: True= All the data is OK - False= Some data is NOT OK
    ######################################################################################
    def verifyDefaultTranscodingProfile(self, profileName):
        self.openTranscodingMenu()

        try:
            profileRowsList = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_ROW)

            self.logi.appendMsg("INFO - Going to verify default Transcoding Profile")
            # lists of the action menu and names
            for webElement in range(len(profileRowsList)):
                if profileName in profileRowsList[webElement].text and "Default" in profileRowsList[webElement].text:
                    return True
            else:
                self.logi.appendMsg("FAIL - Cannot verify default Transcoding Profile")
                return False

        except:
            self.logi.appendMsg("FAIL - Cannot verify default Transcoding Profile")
            return False

    # function that navigates to the transcoding profile menu
    def openTranscodingMenu(self):
        try:
            # Go to Transcoding Settings section
            self.logi.appendMsg("INFO - Going to Settings")
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
            time.sleep(5)
            self.logi.appendMsg("INFO - Going to Transcoding Settings")
            self.Wd.find_element_by_xpath(DOM.TAB_TRANSCODING_SETTINGS).click()
            time.sleep(5)
        except:
            self.logi.appendMsg("FAIL - Cannot open Transcoding menu")
            return False
    # function that navigates to a specified transcoding flavor menu
    # profileName (string) - the name of the profile to open
    # profileType (int 1 - VOD, 2 - live) - the type of profile to open
    def openTranscodingProfileFlavorMenu(self, profileName, profileType = 1):

        self.openTranscodingMenu()
        self.openTranscodingProfile(profileName, profileType)

        self.logi.appendMsg("INFO - Going to Flavors section and update flavors checkboxes")
        self.Wd.find_element_by_xpath(DOM.ENTRY_FLAVORS_TAB).click()

    # opens the flavor edit setting of a given flavor by name
    def openEditFlavorSettings(self, flavor_name):
        flavor_xpath = DOM.TRANSCODING_FLAVOR_NAME.replace('TEXTTOREPLACE', flavor_name)
        mouse = webdriver.ActionChains(self.Wd)
        flavor = self.Wd.find_element_by_xpath(flavor_xpath)
        mouse.move_to_element(flavor).perform()
        name_list = self.Wd.find_elements_by_xpath(DOM.TRANSCODING_FLAVOR_NAME_SELECTED)
        for i,name in enumerate(name_list):
            if name.text == flavor.text:
                self.Wd.find_elements_by_xpath(DOM.TRANSCODING_EDIT_FLAVOR_SETTINGS)[i].click()

    # edit a specific flavor, use openEditFlavorSettings before using this function
    # impactType (sting) - 'Required', 'Optional', 'No Impact'
    # Flavor Generation Policy (string) - 'Use Kaltura Optimization', 'Force Flavor generation'
    # intermediate_flavor_handling (string) - 'Keep', 'Delete Flavor'
    def editFlavorSettingsMenu(self, impactType="", flavor_generation_policy="", save_changes=False):
        if impactType != "":
            try:
                self.logi.appendMsg("INFO - going to change Impact on Entry Readiness")
                #Open 'Impact on Entry Readiness' dropdown list
                dropDown = self.Wd.find_element_by_xpath(DOM.IMPACT_ON_ENTRY_READINESS)
                dropDown.click()
                time.sleep(1)
                #Select the relevant fieldType from the list
                impactTypes = self.Wd.find_elements_by_xpath(DOM.IMPACT_ON_ENTRY_READINESS_LIST_ITEMS)
                for impact in impactTypes:
                    if impact.text == impactType:
                        impact.click()
                        time.sleep(1)
                        self.logi.appendMsg("INFO - Impact on Entry Readiness changed")
                        continue
            except Exception as e:
                print(e)
                self.logi.appendMsg("FAIL - Impact on Entry Readiness did not change")
                return False

        if flavor_generation_policy != "":
            try:
                self.logi.appendMsg("INFO - going to change Flavor Generation Policy")
                #Open 'Flavor Generation Policy' dropdown list
                self.Wd.find_element_by_xpath(DOM.FLAVOR_GENERATION_POLICY).click()
                time.sleep(1)
                #Select the relevant fieldType from the list
                generation_policys = self.Wd.find_elements_by_xpath(DOM.FLAVOR_GENERATION_POLICY_LIST_ITEMS)
                for policy in generation_policys:
                    if policy.text == flavor_generation_policy:
                        policy.click()
                        time.sleep(1)
                        self.logi.appendMsg("INFO - Flavor Generation Policy changed")
                        continue
            except Exception as e:
                print(e)
                self.logi.appendMsg("FAIL - Flavor Generation Policy did not change")
                return False

        # if intermediate_flavor_handling != "":
        #     try:
        #         self.logi.appendMsg("INFO - going to change Flavor Generation Policy")
        #         #Open 'intermediate_flavor_handling' dropdown list
        #         self.Wd.find_elements_by_xpath(DOM.FIELD_TYPE_DROPDOWN)[3].click()
        #         time.sleep(1)
        #         #Select the relevant fieldType from the list
        #         intermediate_flavor = self.Wd.find_elements_by_xpath(DOM.FIELD_TYPE_SELECT_LIST)
        #         for flavor in intermediate_flavor:
        #             if flavor.text == intermediate_flavor_handling:
        #                 flavor.click()
        #                 time.sleep(1)
        #                 self.logi.appendMsg("INFO - Flavor Generation Policy changed")
        #                 continue
        #     except Exception as e:
        #         print(e)
        #         self.logi.appendMsg("FAIL - Flavor Generation Policy did not change")
        #         return False

        if save_changes:
            try:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON).click()
                return True
            except:
                self.logi.appendMsg("FAIL - Edit flavor settings did not save")
                return False
        else:
            try:
                self.Wd.find_element_by_xpath(DOM.UPLOAD_CANCEL).click()
                return True
            except:
                self.logi.appendMsg("FAIL - Exit Edit flavor settings without saving")
                return False

    def open_my_user_settings_menu(self):
        try:
            # Go to Transcoding Settings section
            self.logi.appendMsg("INFO - Going to Settings")
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
            time.sleep(1)
            self.logi.appendMsg("INFO - Going to my user Settings")
            self.Wd.find_element_by_xpath(DOM.TAB_MY_USER_SETTINGS).click()
            time.sleep(5)
            return True
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - Cannot open user settings menu")
            return False

    # Function that edits the user name in my user settings
    # user_name (string) - the name to be used
    # save_changes (string) - default False, send True if changes should be saved
    def edit_my_user_name(self, user_name='', save_chagnes=False):
        try:
            self.logi.appendMsg("INFO - Open edit user model")
            self.Wd.find_element_by_xpath(DOM.MY_USER_NAME_SETTINGS).click()
            self.logi.appendMsg("INFO - Change first name")
            input_field = self.Wd.find_element_by_xpath(DOM.MY_USER_FIRST_LAST_NAME_INPUT)
            input_field.click()
            input_field.clear()
            input_field.send_keys(user_name)

            if save_chagnes:
                self.logi.appendMsg("INFO - Save before exit")
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON).click()
                return True
            else:
                self.logi.appendMsg("INFO - Exit without saving")
                self.Wd.find_element_by_xpath(DOM.UPLOAD_CANCEL).click()
                return True

        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - Cannot Open edit user model")
            return False

    # verify the user name in my user settings
    # check_name (string) - the name to be checked
    def verify_my_user_settings_name(self, check_name):
        try:
            current_name = self.Wd.find_element_by_xpath(DOM.CHECK_USER_NAME.replace("TEXTTOREPLACE", check_name))
            if check_name == current_name.text:
                self.logi.appendMsg("PASS - user name match")
                return True
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - could not verify name match")
            return False


    def deleteAccessControl(self, profileName):
        
        self.logi.appendMsg("INFO - going to delete access control: name= " + profileName )
        self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click() 
        time.sleep(2)
        self.Wd.find_element_by_xpath(DOM.TAB_ACCESS_CONTROL).click()
        time.sleep(5)
        numofRows = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
        tblRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
        
        # go through the rows, search for th eprofile name, once found it selet the check box of the row and delete it
        for i in range(numofRows):
            userNameInRow = self.BasicFuncs.retTblRowName(self.Wd, i+1, "accessctrl")
            if userNameInRow.find(profileName)>=0:
                self.BasicFuncs.CheckUncheckRowInTable(self.Wd,i+1)
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_DELETE).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.GLOBAL_YES_BUTTON).click()
                time.sleep(5)
                
        
        
        # verify new access control was added
        numofRowsAfter = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
        if numofRows-1 == numofRowsAfter:
            self.logi.appendMsg("PASS- The access control Deleted successfully")
            return True
        else:
            self.logi.appendMsg("FAIL- The access control was NOT deleted successfully")
            return False    
            
        # verify new access control was added
        numofRowsAfter = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
        if numofRows-1 == numofRowsAfter:
            self.logi.appendMsg("PASS- The access control Deleted successfully")
            return True
        else:
            self.logi.appendMsg("FAIL- The access control was NOT deleted successfully")
            return False    
            
            
        
    ##########################################################
    # Function 'checkCustomFieldsExist' checks if list of custom meta data fields and title exist or not in entry. 
    # returns true or false , if false - returns also which fields are missing.
    # Params:
    #        negCheck: for negative check send true, for possitive send false
    #        fieldsarr: list on the schema details- in index 0 - schema's title and from index 1 on - the fields' names.
    ##########################################################        
    def checkCustomFieldsExist(self,negCheck,fieldsarr):   
        
        fexist = False
        notFoundFields = ""
        ind = 0
        
        for i in fieldsarr:
            if ind==0:
                i = "//div[text()='" + i + "']"
            else:
                i = "//span[contains(text(),'" + i + "')]"
            try:
                self.Wd.find_element_by_xpath(i)
                fexist = True
            except:
                fexist = False
                notFoundFields = notFoundFields + ";" + i
                
            ind+=1
                
        if negCheck and fexist :
            return False,"none"
        if negCheck and not fexist :
            return True,"none"
        if not negCheck and fexist:
            return True,"none"
        if not negCheck and not fexist:
            return False,notFoundFields
                
    # Function to click on back arrow and approve or reject pop up
    # cancel_edit: default = True
    def click_on_back_button(self, cancel_edit=True):
        self.logi.appendMsg("INFO - Going back to Transcoding Profiles main page")
        try:
            time.sleep(1)
            backward_button = self.Wd.find_element_by_xpath(DOM.TRANSCODING_BACKWARD_BUTTON)
            if backward_button.is_displayed():
                backward_button.click()
        except:
            self.logi.appendMsg("FAIL - Backward button failure")
        time.sleep(5)

        if cancel_edit == False:
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_POPUP_NO_BUTTON).click()
        else:
            self.Wd.find_element_by_xpath(DOM.TRANSCODING_POPUP_YES_BUTTON).click()


    def open_edit_password(self):
        try:
            self.open_my_user_settings_menu()
            self.Wd.find_element_by_xpath(DOM.EDIT_PASSWORD).click()

            return True
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - Cannot open edit password")
            return False

    # Function to input user details in add user forum
    def input_my_user_settings_details(self, firstName="", lastName="", password="", save_changes=False):
        try:
            # Navigate to Administration > Users
            self.logi.appendMsg("INFO - Going to navigate to Administration > Users")
            self.open_my_user_settings_menu()

            time.sleep(1)

            self.logi.appendMsg("INFO - Open edit user model")
            self.Wd.find_element_by_xpath(DOM.MY_USER_NAME_SETTINGS).click()

            time.sleep(1)

            self.logi.appendMsg("INFO - going to verify user input fields")
            rows = self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_LABEL)
            rows_input = self.Wd.find_elements_by_xpath(DOM.MY_USER_SETTINGS_MODAL_INPUT)
            password_input = self.Wd.find_element_by_xpath(DOM.MY_USER_SETTINGS_PASSWORD_INPUT)

            for row in rows:
                if row.text == 'First Name':
                    try:
                        rows_input[0].clear()
                        rows_input[0].send_keys(firstName)
                    except:
                        raise NameError('FAIL - Insert input First Name failed')
                elif row.text == 'Last Name':
                    try:
                        rows_input[1].clear()
                        rows_input[1].send_keys(lastName)
                    except:
                        raise NameError('FAIL - Insert input Last Name failed')
                elif row.text == 'Password':
                    try:
                        password_input.clear()
                        password_input.send_keys(password)
                        rows_input[1].click()
                    except:
                        raise NameError('FAIL - Insert input Publisher User ID failed')
                else:
                    continue

            if save_changes:
                self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()

            return True

        except Exception as e:
            self.logi.appendMsg(str(e))
            self.logi.appendMsg("FAIL - Failed to input user's details")
            return False


    # Function to input user details in add user forum
    def input_my_user_password_details(self, current_password="", new_password="", re_type_new_password="", save_changes=False):
        try:
            # Navigate to Settings > My User Setting > edit password
            self.logi.appendMsg("INFO - Open edit user model")
            self.open_edit_password()

            self.logi.appendMsg("INFO - going to verify user input fields")
            rows = self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_LABEL)
            rows_input = self.Wd.find_elements_by_xpath(DOM.MY_USER_SETTINGS_MODAL_INPUT)

            for row in rows:
                if row.text == 'Current Password':
                    try:
                        rows_input[0].clear()
                        rows_input[0].send_keys(current_password)
                    except:
                        raise NameError('FAIL - Insert input First Name failed')
                elif row.text == 'New password':
                    try:
                        rows_input[1].clear()
                        rows_input[1].send_keys(new_password)
                    except:
                        raise NameError('FAIL - Insert input Last Name failed')
                elif row.text == 'Re-type the new password':
                    try:
                        rows_input[2].clear()
                        rows_input[2].send_keys(re_type_new_password)
                        rows_input[0].click()
                    except:
                        raise NameError('FAIL - Insert input Publisher User ID failed')
                else:
                    continue

            if save_changes:
                self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()

        except Exception as e:
            self.logi.appendMsg(str(e))
            self.logi.appendMsg("FAIL - Failed to input user's details")
            return False

    # Checks the number of input errors in the add user forum
    # num_of_errors = the number of expected errors to be checked
    def verify_valid_user_info_input(self, input_error_list, num_of_errors=0):
        error_num = 0

        # Loops over the errors in the user input, if xpath is not found moves to the next xpath
        # If found error counter is raised by 1
        for xpath_error in input_error_list:
            try:
                xpath = self.Wd.find_element_by_xpath(xpath_error)

                if xpath is not None:
                    error_num += 1
            except:
                continue

        try:
            if num_of_errors == error_num:
                self.logi.appendMsg("INFO - Number of input errors match")
                closeButton = self.BasicFuncs.selectOneOfInvisibleSameObjects(self.Wd, DOM.UPLOAD_SETTINGS_CLOSE)
                closeButton.click()
                return True
        except:
            self.logi.appendMsg("INFO - Number of errors dose not match")
            return False

    def open_reach_menu(self):
        try:
            self.Wd.find_element_by_xpath(DOM.SETTINGS_BUTTON).click()
            time.sleep(1)
            #self.Wd.find_element_by_xpath(DOM.REACH_TAB).click()
            self.Wd.execute_script(DOM.REACH_TAB_JS)
        except Exception as e:
            print(e)

    # function that opens the refine filter
    # only 2 options - expand (int)
    # 0 = Service
    # 1 = Turn Around Time
    # 2 = Choose Languages
    def open_refine_expand_menu(self, expand=0):
        expand_menus = self.Wd.find_elements_by_xpath(DOM.REFINE_EXPAND)

        try:
            if expand == 1:
                expand_menus[1].click()
            elif expand == 2:
                self.Wd.find_element_by_xpath(DOM.COUNTRIES_LIST_DROP_DOWN_BTN).click()
            else:
                expand_menus[0].click()
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - Was not able to open refine filter")
            return False

    # Opens the drop down menu inside the reach profile
    def select_refine_filter_option(self, select_option):
        try:
            self.Wd.find_element_by_xpath(DOM.REFINE_NAME.replace('TEXTTOREPLACE', select_option)).click()
        except Exception as e:
            print(e)
            return False

    # Selects the language from the drop down list
    def select_refine_filter_languages(self, select_lang, leave_open=False, deSelect=False):
        refineWin = self.Wd.find_element_by_xpath(DOM.REFIN_POP)

        try:
            if not deSelect:
                self.Wd.find_element_by_xpath(DOM.REACH_LANGUAGE.replace('TEXTTOREPLACE', select_lang)).click()
            else:
                self.Wd.find_element_by_xpath(DOM.REACH_LANGUAGE1.replace('TEXTTOREPLACE', select_lang)).click()
        except Exception as e:
            print(e)
            return False

        if not leave_open:
            try:
                refineWin.find_element_by_xpath(DOM.CATEGORY_CLOSE).click()
            except:
                return False

    # Opens the reach profile
    # profile_name (String) - the name of the profile to open
    def select_reach_profile(self, profile_name):
        try:
            self.Wd.find_element_by_xpath(DOM.REACH_PROFILE_NAME.replace('TEXTTOREPLACE', profile_name)).click()
        except Exception as e:
            print(e)
            return False

    # Opens the reach profile
    # profile_name (String) - the name of the profile to open
    def select_service_parameters(self):
        try:
            self.Wd.find_element_by_xpath(DOM.REACH_SERVICE_PARAMETERS).click()
        except Exception as e:
            print(e)
            return False

    # Edits the name of the Reach profile
    # profile_name (String) - The name that is meant to be changed
    # save_changes (Boolean) - If you want to save the name after the change
    def edit_reach_profile_name(self, profile_name, save_changes=False):
        try:
            input_field = self.Wd.find_element_by_xpath(DOM.REACH_PROFILE_NAME_INPUT)
            input_field.click()
            input_field.clear()
            input_field.send_keys(profile_name.strip())

            if save_changes:
                try:
                    self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON).click()
                except:
                    self.logi.appendMsg("FAIL - could not save reach name change")

        except Exception as e:
            print(e)
            return False

    # Used to clear the name to initiate an error
    # num_of_errors (Number) - The number of errors to verify
    def clear_reach_profile_name_for_validation(self, num_of_errors):
        try:
            input_field = self.Wd.find_element_by_xpath(DOM.REACH_PROFILE_NAME_INPUT)
            input_field.click()
            input_field.clear()
            input_field.send_keys(Keys.SPACE)
            input_field.send_keys(Keys.BACK_SPACE)

            time.sleep(2)

            self.verify_num_of_profile_menu_errors(num_of_errors)

        except Exception as e:
            print(e)
            return False

    def edit_max_characters_input(self, num_of_char, save_changes=False):
        try:
            self.Wd.find_element_by_xpath(DOM.REACH_SERVICE_PARAMETERS).click()

            input_field = self.Wd.find_element_by_xpath(DOM.REACH_PROFILE_NAME_INPUT)
            input_field.click()
            input_field.clear()
            input_field.send_keys(num_of_char)

            if save_changes:
                try:
                    self.Wd.find_element_by_xpath(DOM.TRANSCODING_ADD_SAVE_BUTTON).click()
                except:
                    self.logi.appendMsg("FAIL - could not save reach name change")

        except Exception as e:
            print(e)
            return False

    def clear_reach_max_characters_for_validation(self, num_of_errors):
        try:
            self.Wd.find_element_by_xpath(DOM.REACH_SERVICE_PARAMETERS).click()


            input_field = self.Wd.find_element_by_xpath(DOM.REACH_PROFILE_MAX_CHARACTERS_INPUT)
            input_field.click()
            time.sleep(1)
            input_field.clear()
            input_field.send_keys(Keys.SPACE)
            time.sleep(1)
            input_field.send_keys(Keys.BACK_SPACE)

            time.sleep(2)

            if self.verify_num_of_profile_menu_errors(num_of_errors) == False:
                return False

        except Exception as e:
            print(e)
            return False

    def verify_num_of_profile_menu_errors(self, num_of_errors=0):
        try:
            error_dot = self.Wd.find_elements_by_xpath(DOM.REACH_PROFILE_MENU_SETTINGS_ERROR)
            if len(error_dot) == num_of_errors:
                self.logi.appendMsg("INFO - Name error input displayed as expected")
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False

    def exit_without_saving(self, exitWithoutSaving):
        try:
            if exitWithoutSaving == True:
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_BACKWARD_BUTTON).click()
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_POPUP_NO_BUTTON).click()
                self.logi.appendMsg("Pass - cancel exit without saving successfully")
                time.sleep(2)
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_BACKWARD_BUTTON).click()
                self.Wd.find_element_by_xpath(DOM.TRANSCODING_POPUP_YES_BUTTON).click()
                self.logi.appendMsg("Pass - exit without saving successfully")
                return True
            else:
                return False
        except:
            self.logi.appendMsg("FAIL - exit without saving failed")
            return False
    # Changes the value of a slide buttons in a setting menu
    def edit_slide_value(self):
        slide_buttons = self.Wd.find_elements_by_xpath(DOM.REACH_PROFILE_SLIDER)

        for slide in slide_buttons:
            slide.click()
    # Change the value in the Reach profile metadata drop down
    # drop_down_item (Number) - The index of the drop down list to open
    # select_field_item (Number) - The index of the list item to select
    def edit_drop_down_metadata_item(self, drop_down_item, select_field_item):
        # Open 'Field Type' dropdown list
        self.Wd.find_elements_by_xpath(DOM.FIELD_TYPE_SELECT_LIST_ITEM)[drop_down_item].click()
        time.sleep(1)
        # Select the relevant fieldType from the list
        fieldTypes = self.Wd.find_elements_by_xpath(DOM.FIELD_TYPE_SELECT_LIST)
        fieldTypes[select_field_item].click()
