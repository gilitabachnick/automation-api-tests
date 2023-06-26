'''
Created on Apr 25, 2018

@author: adi.miller
'''

import time

from selenium.webdriver.common.keys import Keys

import DOM
import KmcBasicFuncs


class categoryfuncs:
    

    def __init__(self, webdrvr, logi):
        
        self.Wd = webdrvr
        self.logi = logi
        self.basicFuncs = KmcBasicFuncs.basicFuncs()
    
    # this function adds category, send the new category name in categoryName
    # if no parent send categoryParent = "no" else send the parent name (not implemented)
    def addCategory(self, categoryName, categoryParent):    
        
        self.Wd.find_element_by_xpath(DOM.CATEGORY_ADD).click()
        time.sleep(1)
        try:
            self.Wd.find_element_by_xpath(DOM.CATEGORY_NAME).send_keys(categoryName)
            time.sleep(1)
            if categoryParent=="no":
                self.Wd.find_element_by_xpath(DOM.CATEGORY_NEW_NO_PARENT).click()
            else: # create the category under parent
                newCatWin = self.Wd.find_element_by_xpath(DOM.CATEGORY_ADD_POPUPWIN)
                time.sleep(1)
                newCatWin.find_element_by_xpath(DOM.NEW_CATEGORY_SEARCH).send_keys(categoryParent)
                time.sleep(2)
                autoCompLst = newCatWin.find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_LIST)
                
                try:
                    autoCompLst.click()
                    #find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_RES).click()
                except:
                    self.logi.appendMsg('FAIL - The parent Category name: ' + categoryParent + ' does not exist')
                    return False
        except:
            return False
        
        
        self.Wd.find_element_by_xpath(DOM.CATEGORY_NEW_APPLY).click()
        time.sleep(3)
        
        # verify the new category page is open with the new category just created
        try:
            catName = self.Wd.find_element_by_xpath(DOM.CATEGORY_NAME).get_attribute("value")
            if catName==categoryName:
                return True
            else:
                return False
        except:
            return False
        
    # this def edit a category for only new parameters that sent,
    # send value only for parameters you want to change,
    # tags should be separate with ";" between each other
    def updateCategory(self, newName=None, newDesc=None, newTags=None, newReference=None, saveByButton=True):
        
        try:
            tagsarr = newTags.split(";")
        except:
            tagsarr = None
            
        
        if newName!=None:
            nameField = self.Wd.find_element_by_xpath(DOM.CATEGORY_NAME)
            nameField.clear()
            nameField.send_keys(newName)
            
        if newDesc!=None:
            descField = self.Wd.find_element_by_xpath(DOM.CATEGORY_DESC)
            descField.clear()
            descField.send_keys(newDesc)
            
        if newTags!=None:
            tagsField = self.Wd.find_element_by_xpath(DOM.CATEGORY_TAGS)
            try:
                existTags= tagsField.find_elements_by_xpath(DOM.CATEGORY_CLOSE_TAG)
                for tag in existTags:
                    tag.click()
                time.sleep(1)
            except:
                print("no tags")
            for i in tagsarr:
                tagsField.send_keys(i)
                tagsField.send_keys(Keys.RETURN)
            
        if newReference!=None:
            RefField = self.Wd.find_element_by_xpath(DOM.CATEGORY_REFERENCE_ID)
            RefField.clear()
            RefField.send_keys(newReference)
        
        time.sleep(3)

        if saveByButton:
            self.Wd.find_element_by_xpath(DOM.CATEGORY_SAVE).click()
        else: # press the back button and discard changes
            self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
            time.sleep(3)
            dialogWin = self.Wd.find_element_by_xpath(DOM.CATEGORY_CANCEL_EDIT)
            try:
                dialogWin.find_element_by_xpath(DOM.CATEGORY_CANCEL_YES_BUTTON).click()
            except:
                print("should not press yes button")
            
        time.sleep(7)
    
    # this def delete category    
    def removeExistingCategory(self, catName):
        
        rc = self.basicFuncs.searchEntrySimpleSearch(self.Wd, catName)
        time.sleep(3)
        if rc:
            numOrCats = self.basicFuncs.retNumOfRowsInEntryTbl(self.Wd)
            if numOrCats > 0:
                self.basicFuncs.deleteCategories(self.Wd, catName)
        
        
    # this function verify category values in category page
    # send value only for parameters you want to change,
    # tags should be separate with ";" between each other
    # TagsSingle - send true if want to verify the only one tag exist and other might also, send False if need to check what you send in Tags are the only tags that should appear
    def verifyCategoryValues(self, Name=None, Desc=None, Tags=None, Reference=None, TagsSingle=None):
        
        tmpStatus = True
        
        try:
            tagsarr = Tags.split(";")
        except:
            tagsarr = None
            
        if Name!=None:
            nameCurr = self.Wd.find_element_by_xpath(DOM.CATEGORY_NAME).get_attribute("text")
            if Name != nameCurr:
                tmpStatus = False
            
        if Desc!=None:
            descCurr = self.Wd.find_element_by_xpath(DOM.CATEGORY_DESC).get_attribute("text")
            if descCurr!=Desc:
                tmpStatus = False
            
        if Tags!=None:
            exsistArrTags = []
            try:
                existTags= self.Wd.find_elements_by_xpath(DOM.TAGS_LABLE)
                for tag in existTags:
                    exsistArrTags.append(tag.text)
                
                if TagsSingle!=None:
                    if TagsSingle:
                        if not any(Tags in s for s in exsistArrTags):
                            tmpStatus = False
                else:    
                    if set(tagsarr)!=set(exsistArrTags):
                        tmpStatus = False
            except:
                print("no tags")
            
            
        if Reference!=None:
            RefField = self.Wd.find_element_by_xpath(DOM.CATEGORY_REFERENCE_ID)
            if Reference!=RefField:
                tmpStatus = False
                
        return tmpStatus 
        
        
        
        
    # this function deals with move category window after it is open, and it does the move category action 

    # if no parent send categoryParent = "no" else send the parent name     
        
    def moveCategory (self, categoryParent):
        
        try:
            if categoryParent=="no":
                self.Wd.find_element_by_xpath(DOM.CATEGORY_NEW_NO_PARENT).click()
            else: # create the category under parent
                moveCatWin = self.Wd.find_element_by_xpath(DOM.CATEGORY_ADD_POPUPWIN)
                time.sleep(1)
                moveCatWin.find_element_by_xpath(DOM.NEW_CATEGORY_SEARCH).send_keys(categoryParent)
                time.sleep(2)
                
                try:
                    self.Wd.find_element_by_xpath(DOM.CATEGORY_AUTO_COMPLETE_LIST).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.CATEGORY_NEW_APPLY).click()
                    self.Wd.find_element_by_xpath(DOM.GLOBAL_YES_BUTTON).click()
                    time.sleep(3)
                except:
                    self.logi.appendMsg('FAIL - The parent Category name: ' +  categoryParent + ' does not exist or the \"Apply\" button was disabled')
                    return False 
        except:
            return False 
        
        return True
        