'''
Created on Jan 31, 2018

@author: Adi.Miller
'''

import datetime
import os
import time
#import subprocess

import pyautogui
import pywinauto
from selenium.webdriver.common.keys import Keys

import DOM
import KmcBasicFuncs
import autoitWebDriver

class uploadfuncs:
    
    def __init__(self, Wd, logi, Wdobj):
        self.Wd = Wd
        self.logi = logi
        self.Wdobj = Wdobj
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()

        if self.Wdobj.RUN_REMOTE:
            self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
            self.AWD =  self.autoitwebdriver.retautoWebDriver()
    
    # for upload from desktop send in howToUpload="desktop" or use the defaule, for url send howToUpload="url"  
    # if need to upload few entries send them in one string in "filePth" parameter limited with ";" 
    #      from example: uploadFromDesktop("c:\temp\adi.jpg;c:\temp\adi.mpeg",...)

    def windows_upload_dialog(self, path):
        app = pywinauto.application.Application()  # Open application handler
        app = app.connect(title=u'Open', class_name='#32770')  # Focus on window with title "Open"
        app[' open ']['Edit1'].set_edit_text(path)  # Send file path
        time.sleep(1)
        app[' open ']['Button1'].click_input()  # Click "Open" button
        print(' Upload finished ')

    def uploadFromDesktop(self, filePth, howToUpload="desktop", theUrl="none", transcodingProfile="default", Fname=None):
        
        fromdesktop = False
        fromurl = False
        filesToUpload = filePth.split(";")
        
        self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
        try:
            if howToUpload=="desktop":
                fromdesktop = True
                uploadFromDesktop =  self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_DESKTOP)
            elif howToUpload=="url":
                fromurl = True
                uploadFromDesktop =  self.Wd.find_element_by_xpath(DOM.UPLOAD_FROM_URL)
        except:
            self.logi.appendMsg("FAIL - could not find the object Upload From " + howToUpload + ", exit the test")
            self.logi.reportTest('fail',self.sendto)
            assert False
              
        uploadFromDesktop.click()
        time.sleep(5)
        
        uploadSettingsWin = self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_WIN)
        
        # upload few entries
        i=0
        for entryfile in (filesToUpload):
            
            if fromdesktop:
                
                if self.Wdobj.RUN_REMOTE:
                    print("-------REMOTE----------")
                    pthstr = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData')) + entryfile
                    #pth = r'C:\selenium\automation-api-tests\NewKmc\UploadData'
                    #self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe', pth)
                else:
                    print("-----LOCAL---------")
                    pth1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                    pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                    print(" going to set file path: " + str(os.path.abspath(os.path.join(pth1, entryfile))))
                    # subprocess.call([os.path.abspath(os.path.join(pth2, "openFile.exe")), os.path.abspath(os.path.join(pth1, entryfile))])

                    pthstr = str(os.path.abspath(os.path.join(pth1, entryfile)))
                    # print(pthstr)
                    # pyautogui.FAILSAFE = False
                    # pyautogui.typewrite(pthstr)
                    # #time.sleep(2)
                    # pyautogui.press('enter')

                    # if self.Wdobj.RUN_REMOTE:
                    #     self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe', pthstr)
                    # else:
                    #     pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                    #     pth2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Tests'))
                    #     #subprocess.call([pth2 + "\\openFile.exe", pthstr])
                self.windows_upload_dialog(pthstr)

            elif fromurl:
                urlbox = uploadSettingsWin.find_element_by_xpath(DOM.UPLLOAD_FILE_URL)
                urlbox.send_keys(theUrl)
                
            time.sleep(1)
            
            if Fname!=None:
                self.Wd.find_element_by_xpath(DOM.UPLOAD_FILE_NAME).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.UPLOAD_SETTINGS_EDIT).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.UPLOAD_EDIT_FILE_NAME).send_keys(Keys.CONTROL, 'a')
                self.Wd.find_element_by_xpath(DOM.UPLOAD_EDIT_FILE_NAME).send_keys(Fname + Keys.RETURN)
                time.sleep(2)
                
        
        # Set Transcoding Profile if relevant
            if transcodingProfile != "default":
                
                # Select Transcoding Profile
                self.logi.appendMsg("INFO - Going to select Transcoding Profile " + transcodingProfile)
                time.sleep(2)
                try:
                    self.Wd.find_element_by_xpath(DOM.UPLOAD_TRANSCODING_DROPDOWN).click()
                    time.sleep(1)
                    dynamicDOM = DOM.UPLOAD_TRANSCODING_ITEM.replace('TEXTTOREPLACE',transcodingProfile)
                    self.Wd.find_element_by_xpath(dynamicDOM).click()
                    
                    # Check Transcoding Profile was selected
                    time.sleep(1)
                    dynamicDOM = DOM.UPLOAD_TRANSCODING_SELECTED_ITEM.replace('TEXTTOREPLACE',transcodingProfile)
                    self.Wd.find_element_by_xpath(dynamicDOM)
                    
                except:
                    self.logi.appendMsg("FAIL - Cannot select Transcoding Profile drop down")
                    assert False
                    
            # case there are more than one entry to upload
            if len(filesToUpload)>1 and i+1<len(filesToUpload):
                i+=1
                self.Wd.find_element_by_xpath(DOM.UPLOAD_ADD_FILE).click()
                time.sleep(3)

        #=======================================================================
        # uploadSettingsRow = uploadSettingsWin.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_ROW)
        #=======================================================================
          
        self.logi.appendMsg("INFO- Going to upload the files")
        time.sleep(3)
        self.Wd.find_element_by_xpath(DOM.UPLOAD_UPLOAD).click()
        time.sleep(3)
        
    # this function creates bulk upload 
    # uploadType - what to upload (entry, category...) 
    # uploadFile - send only the file name, the file should be part of the project and located in "UploadData" folder   
    def bulkUpload(self,uploadType, uploadFile):
        
        self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()
        try:
            bulkUpload =  self.Wd.find_element_by_xpath(DOM.BULK_UPLOAD)
        except:
            self.logi.appendMsg("FAIL - could not find the object Upload From Desktop, exit the test")
            self.logi.reportTest('fail',self.sendto)
            return False
            
        bulkUpload.click()
        theTime = str(datetime.datetime.time(datetime.datetime.now()))[:5]
        time.sleep(3)
        
        if uploadType == "entry":
            self.Wd.find_element_by_xpath(DOM.BULK_UPLOAD_ENTRIES).click() 
            
        time.sleep(3)   
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData')) 
        if self.Wdobj.RUN_REMOTE:
            print("from RUN REMOTE")
            pthstr = 'C:\\selenium\\automation-api-tests\\NewKmc\\UploadData\\' + uploadFile
            #self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe', pth)
        else:
            pth1 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            pth2 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Tests'))
            print(" going to set file path: " + str(os.path.abspath(os.path.join(pth1, uploadFile))))
            #subprocess.call([os.path.abspath(os.path.join(pth2, "openFile.exe")), os.path.abspath(os.path.join(pth1, uploadFile))])

            #if platform.system() == 'Windows':
            pyautogui.FAILSAFE = False
            pthstr = str(os.path.abspath(os.path.join(pth1, uploadFile)))
            print(pthstr)
            #pyautogui.typewrite(pthstr)

            #pyautogui.press('enter')

            # else:  # Linux/Mac
            #     if localSettings.LOCAL_RUNNING_BROWSER == clsTestService.PC_BROWSER_FIREFOX:
            #         buttonFileName = 'open_button_ff.png'
            #     elif localSettings.LOCAL_RUNNING_BROWSER == clsTestService.PC_BROWSER_CHROME:
            #         buttonFileName = 'open_button_ch.png'
            #     pyautogui.typewrite(filePath)
            #     sleep(3)
            #     xy = pyautogui.locateCenterOnScreen(os.path.abspath(
            #         os.path.join(localSettings.LOCAL_SETTINGS_MEDIA_PATH, 'images',
            #                      buttonFileName)))  # returns center x and y
            #     sleep(1)
            #     pyautogui.click(xy)
        self.windows_upload_dialog(pthstr)
        time.sleep(5)
        
        return theTime

    # Prepare an entry from the create button
    # entry_type (string) - video or audio only
    # entry_name (string) - default is empty str and the name will be 'Draft Entry'
    #                       or the name if sent as parameter
    def prepare_entry(self, entry_type, entry_name=''):
        self.Wd.find_element_by_xpath(DOM.UPLOAD_BTN).click()

        time.sleep(1)

        try:
            if entry_type == 'video':
                self.Wd.find_element_by_xpath(DOM.PREPARE_VIDEO_ENTRY).click()
            elif entry_type == 'audio':
                self.Wd.find_element_by_xpath(DOM.PREPARE_AUDIO_ENTRY).click()
        except:
            self.logi.appendMsg("FAIL - prepare entry failed")
            return False

        time.sleep(5)

        if entry_name != '':
            self.Wd.find_element_by_xpath(DOM.ENTRY_NAME).clear()
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.ENTRY_NAME).send_keys(entry_name)
            self.logi.appendMsg("PASS - prepared entry successfully")

        time.sleep(1)

        self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()
        time.sleep(2)
        self.Wd.find_element_by_xpath(DOM.CATEGORY_BACK).click()
    
    # this function closes the bulk upload message after verifying the message is correct
    # it goes to bulk upload status page and wait for the correct status sended in expStatus 
    def bulkMessageAndStatus(self, expStatus, theTime, itimeout=300):
        
        rc = True
        theMin = str(int(theTime[3:])+1)
        if len(theMin)==1:
            theMin = "0" + theMin
        timeRange = theTime[:3] + theMin

        time.sleep(5)
        
        try:
            msgwin = self.Wd.find_elements_by_xpath(DOM.BULK_SUCCESS_MESSAGE_WIN)
            if msgwin[1].text.lower().find("Your request has been submitted. Track the progress of your bulk job in the Bulk Upload Log page".lower())>=0:
                self.logi.appendMsg("PASS - bulk Upload Submitted OK")
            else:
                self.logi.appendMsg("FAIL - the message \"Your request has been submitted. Track the progress...\" did not appear in the bulk message window")
                rc = False
                
            try: 
                
                self.logi.appendMsg("INFO - Going to press the link to bulk upload status window and wait for the " + expStatus + " status, the upload time was- " + str(timeRange) + " and one minute before range")
                self.Wd.find_element_by_xpath(DOM.BULK_MSG_LINK_TO_LOAD_PAGE).click()
                time.sleep(3)
                bulkTable = self.Wd.find_element_by_xpath(DOM.ENTRIES_TABLE)
                refresh = self.Wd.find_element_by_xpath(DOM.ENTRY_TBL_REFRESH)
                refresh.click()
                time.sleep(3)
                
                finit = False
                TimNotOver = False
                starttime = time.time()
                while not finit and not TimNotOver :  # wait 5 minutes or untill the status changes to Finished successfully
                    tblRows = self.Wd.find_elements_by_xpath(DOM.ENTRY_ROW)
                    if  tblRows[0].text.lower().find(expStatus.lower())>=0:  #(tblRows[1].text.find(theTime)>=0 or tblRows[1].text.find(timeRange)>=0) and
                        finit = True
                        self.logi.appendMsg("PASS - The bulk upload status has changed to " + expStatus + " as expected")
                    else:
                        if time.time()-starttime > itimeout:
                            self.logi.appendMsg("FAIL - the bulk upload status was not done after " + str(
                                itimeout) + " seconds. Status is: " + tblRows[1].text)
                            TimNotOver = True
                            rc = False
                    
                    refresh.click()
                    time.sleep(5)    
            except Exception as exp:
                print(exp)
                self.logi.appendMsg("FAIL - the bulk upload status window did not appear")
                rc = False
                
        except Exception as exp:
            print(exp)
            self.logi.appendMsg("FAIL - the bulk upload message window did not pop")
            rc = False
            
        
        return rc
    
    #############################################################################################################
    # this function do bulk upload + verify the bulk status + verify the entries uploaded (if it should succeed)
    # logi - is the log file
    # fileToUpload - the file that is going to be uploaded in the bulk upload process
    # expstatus - of the bulk upload
    # entryList - send as list if entries should be uploaded
    #
    # exaple: bulkUploadAndEntriesVerify(self.logi, fname, expstatus, [entry1,entry2,entry3])
    #############################################################################################################
     
    def bulkUploadAndEntriesVerify(self, fileToUpload, expstatus, entryList=None):
        
        tmpStatus = True
        theTime = str(datetime.datetime.time(datetime.datetime.now()))[:5]
        
        self.bulkUpload("entry", fileToUpload)
        time.sleep(1)
        self.logi.appendMsg("INFO - Going to verify the bulk upload message window appear with the correct text in it")
        rc = self.bulkMessageAndStatus(expstatus, theTime, 900)
        if not rc:
            tmpStatus = False

        self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
        time.sleep(3)
        
        if entryList != None:
            
            for i in entryList:
                self.logi.appendMsg("INFO- Going to verify that the entries uploaded and in status Ready")
                entryStatus,lineText = self.BasicFuncs.waitForEntryStatusReady(self.Wd,i)
                if not entryStatus:
                    self.logi.appendMsg("FAIL - the entry \"" + i + "\"  was not uploaded and should have been!!")
                    tmpStatus = False
                else:
                    self.logi.appendMsg("PASS - the entry \"" + i + "\" was Uploaded successfully as expected")
                     
            
            self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
            time.sleep(3)  
            
        return tmpStatus
    
    
    #############################################################################################################
    # Function uploadTPCheck checks if transcoding profile is present on Upload screen dropdown
    # Params:
    #        transcodingProfile : transcoding profile name - string - mandatory
    # Return: True: the TP exist - False: the TP does not exist
    #############################################################################################################
    def uploadTPCheck(self,transcodingProfile):
        existTP = False
        try:
            
            # Search Transcoding Profile on dropdown
            self.logi.appendMsg("INFO - Going to evaluate Transcoding Profile " + transcodingProfile + " on Upload screen.")
            self.Wd.find_element_by_xpath(DOM.UPLOAD_TRANSCODING_DROPDOWN).click()
            time.sleep(0.5)
            try:
                dynamicDOM = DOM.UPLOAD_TRANSCODING_ITEM.replace('TEXTTOREPLACE',transcodingProfile)
                self.Wd.find_element_by_xpath(dynamicDOM)
                self.logi.appendMsg("INFO - Transcoding Profile exist.")
                existTP = True
            except:
                self.logi.appendMsg("INFO - Transcoding Profile not exist.")
                existTP = False
                pass
            
        except:
            self.logi.appendMsg("FAIL - Cannot evaluate Transcoding Profiles on Upload screen.")
            
        return existTP
    
    
    #######################################################################################################
    # Function Upload Thumbnail upload a thumbnail for an entry 
    # Param:
    #      thumbnailFileName -  must be located in 'Upload Data' folder in this project. for example 'smalljpg.jpg'  
    #       
    ########################################################################################################
    
    
    def UploadThumbnail(self,thumbnailFileName):
        
        
        rowsNumBefore = len(self.Wd.find_elements_by_xpath(DOM.GLOBAL_TABLE_HEADLINE))
        self.logi.appendMsg("INFO - RowsNumBefore: " +str(rowsNumBefore))
        
        #Click on the Upload (thumbnail) button
        try:  
            self.logi.appendMsg("INFO - Going to click on the 'upload' (thumbnail) button")
            time.sleep(2)
            rc = self.Wd.find_element_by_xpath(DOM.UPLOAD_THUMBNAIL_BUTTON)
            if not rc:
                self.logi.appendMsg("FAIL - could not find the 'Upload' button")
                return False
            rc.click()              
            time.sleep(2)      
            if self.Wdobj.RUN_REMOTE:
                pthstr = r'C:\selenium\automation-api-tests\NewKmc\UploadData' + thumbnailFileName
                #self.AWD.execute_script(r'C:\selenium\automation-api-tests\NewKmc\autoit\openFileChrome.exe', pth)
            else:

                pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
                # subprocess.call(['openFile.exe' ,pth + thumbnailFileName])
                pyautogui.FAILSAFE = False
                pthstr = str(os.path.abspath(os.path.join(pth, thumbnailFileName)))
                print(pthstr)
                print(" going to set file path: " + str(os.path.abspath(os.path.join(pthstr, thumbnailFileName))))

                # pyautogui.typewrite(pthstr)
                # time.sleep(5)
                # pyautogui.press('enter')
            self.windows_upload_dialog(pthstr)
            time.sleep(10)
            
            ''''**** Verification -rowsNum includes the table title row, e.g - for 2 thumbnails the number of rows would be 3 ****''' 
            rowsNum = len(self.Wd.find_elements_by_xpath(DOM.GLOBAL_TABLE_HEADLINE))            
            if rowsNum != rowsNumBefore+1:
                self.logi.appendMsg("FAIL - The thumbnails' number should have been " + str(rowsNumBefore) + " and actually it is: " + str(rowsNum-1) + " - Not as expected")
                return False
            else:
                self.logi.appendMsg("PASS - The thumbnails' number before was " + str(rowsNumBefore-1) + " and after adding a new thumbnail it is: " + str(rowsNum-1) + " - Thumbnail was uploaded successfully")
                return True
                
        except Exception as Exp:
            print(Exp)
            return False

    def delete_thumbnail(self):
        try:
            self.Wd.find_element_by_xpath(DOM.TBL_MORE_ACTIONS).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.USERS_ROW_ACTION_DELETE).click()
            time.sleep(1)
            self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_YES).click()

        except Exception as e:
            print(e)
            return False