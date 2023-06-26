'''
Created on 12 Mar 2019

@author: moran.cohen
'''

import time
####ADDED to compare XML to EXCEL
import urllib.error  # For getting feed string from XML feed
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# init excel
import xlrd

import DOM
import MySelenium


# init xml


class SyndicationFuncs(object):
    
    
    def __init__(self, webdrvr, logi):
        
        self.Wd = webdrvr
        self.logi = logi
        self.Wdobj = MySelenium.seleniumWebDrive()
        
        
        
    def CreatSyndicationGoogle(self,SyndicationName,PlaylistName,LandingPage,AllContent=False,ContentFlavor=None,AddToDefaultTranscodingProfile=None,Playback=None,Player=None,AdultContent=None):        
        
        DestinationName = "Google"
        try:       
            # Navigate to Syndication tab and click to add Feed
            self.logi.appendMsg("INFO - Navigating to Syndication section")
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_TAB).click()
            time.sleep(10)
            self.logi.appendMsg("INFO - Going to click 'Add Feed'")
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_ADDFEED_BTN).click()
            time.sleep(3)
                        
            # Select ALL Content(true) or Playlist based
            if AllContent:
                self.Wd.find_element_by_xpath(DOM.SYNDICATION_ALLCONTENT_RDB).click()    
                
            else:
                # Select Playlist based feed
                self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYLISTCONTENT_RDB).click()
                # Adding Syndication's playlist in form
                self.logi.appendMsg("INFO - Going to select playlist in Syndication's feed")             
                try:                     
                    #self.Wd.find_element_by_xpath(SYNDICATION_PLAYLIST_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",PlaylistName)).click()                 
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYLIST_SEARCHDROPDOWN).click()
                    PlaylistSelectorMain=self.Wd.find_elements_by_xpath(DOM.SYNDICATION_PLAYLIST_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",PlaylistName))
                    time.sleep(1)
                    PlaylistSelectorMain[0].find_element_by_xpath(DOM.SYNDICATION_PLAYLIST_SELECTION_INSERT).click()
                    #self.Wd.find_element_by_xpath(SYNDICATION_PLAYLIST_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",PlaylistName)).click()
                except Exception as e:
                    print(e)
                    self.logi.appendMsg("FAIL - The playlist wasn't found in the list. PlaylistName = " + PlaylistName)
                    # Press on Cancel button 
                    syndicationBTN=self.Wd.find_element_by_xpath(DOM.SYNDICATION_MAIN_BTN)
                    syndicationBTN.find_element_by_xpath(DOM.SYNDICATION_CANCEL_BTN).click()
                    return False
            
            time.sleep(1)
                           
            # Adding Syndication's name in form
            self.logi.appendMsg("INFO - Going to enter Syndication's Name = " + SyndicationName)
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_NAME).send_keys(SyndicationName)
                      
            # Adding Syndication's Destination in form
            self.logi.appendMsg("INFO - Going to select Destination in Syndication's feed, destination= " + DestinationName)             
            try:            
                self.Wd.find_element_by_xpath(DOM.SYNDICATION_DESTINATION_MAIN).click()
                time.sleep(1)
                self.Wd.find_element_by_xpath(DOM.SYNDICATION_DESTINATION_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",DestinationName)).click()
            except Exception as e:
                print(e)
                self.logi.appendMsg("FAIL - The Destination wasn't found in the list")
                return False
        
            # Adding Syndication's LandingPage in form
            self.logi.appendMsg("INFO - Going to enter Syndication's LandingPage= " + LandingPage)
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_LANDINGPAGE).send_keys(LandingPage)   
        
            # ************************* Update optional fields ***************************
            try:          
                if ContentFlavor != None:
                    self.logi.appendMsg("INFO - Going to update Syndication's ContentFlavor = " + str(ContentFlavor))
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_CONTENTFLAVOR_MAIN).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_CONTENTFLAVOR_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",ContentFlavor)).click()
                if AddToDefaultTranscodingProfile != None:
                    self.logi.appendMsg("INFO - Going to set Syndication's AddToDefaultTranscodingProfile ON")
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_ADD_DEFAULT_TRANSCODINGPROFILE).click()
                                                                              
                if Playback != None:
                    self.logi.appendMsg("INFO - Going to update Syndication's Playback = " + Playback)
                    if Playback == "From Google":
                        self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYBACK_FROMGOOGLE).click()                         
                    elif Playback == "Linkback to my site":
                        self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYBACK_LINKBACKTOMYSITE).click()
                    else:
                        self.logi.appendMsg("FAIL - The Playback wasn't found in the list. Playback = " + Playback)
                        return False
                                                                      
                if Player != None and Playback != "Linkback to my site":
                    self.logi.appendMsg("INFO - Going to update Syndication's Player = " + Player)
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYER_MAIN_SELECTION).click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYER_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",Player)).click()
                
                if AdultContent != None:
                    self.logi.appendMsg("INFO - Going to set Syndication's AdultContent ON")
                    self.Wd.find_element_by_xpath(DOM.SYNDICATION_ADULTCONTENT).click()    
                                   
            
            except Exception as e:
                    print(e)
                    self.logi.appendMsg("FAIL - Syndication Update optional fields")
                    return False
        
        
            # Press on save button
            self.logi.appendMsg("INFO - Going to save the Syndication feed")
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_SAVE_BTN).click()
            time.sleep(2)
        
            return True
        
        except Exception as e:
            print(e)
            return False
    
       
    
    
    
    def VerifySyndicationGoogle(self,SyndicationName,PlaylistName,LandingPage,AllContent=False,ContentFlavor=None,AddToDefaultTranscodingProfile=None,Playback=None,Player=None,AdultContent=None):
        
        DestinationName = "Google"
        try:
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_NAME_TABLE.replace("TEXTTOREPLACE",SyndicationName)).click()
            time.sleep(2)
            
            # Verify Syndication's name in form
            self.logi.appendMsg("INFO - Going to verify Syndication Name")           
            rc=self.Wd.find_element_by_xpath(DOM.SYNDICATION_NAME).get_attribute("value")
            if rc == SyndicationName:
                self.logi.appendMsg("PASS - Syndication's Name")
            else:
                self.logi.appendMsg("FAIL - Syndication's Name. SyndicationName = " + SyndicationName)
            
            
            
            self.logi.appendMsg("INFO - Going to check AllContent/playlistBased")    
            self.logi.appendMsg("INFO - Going to verify Playlist name= " + PlaylistName)                     
            # Verify that there is not playlist when selecting AllContent option 
            if AllContent:
                res = self.Wdobj.Sync(self.Wd,DOM.SYNDICATION_PLAYLIST_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",PlaylistName))
                if not isinstance(res,bool):
                    self.logi.appendMsg("FAIL - AllContent selection, but there is PlaylistName. PlaylistName = " + PlaylistName)
                else:       
                    self.logi.appendMsg("PASS - AllContent.")
                
            else:
                # Verify that there is playlist when selecting playlist based option
                res = self.Wdobj.Sync(self.Wd,DOM.SYNDICATION_PLAYLIST_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",PlaylistName))
                if isinstance(res,bool):
                    self.logi.appendMsg("FAIL - PlaylistName. PlaylistName = " + PlaylistName)
                else:       
                    self.logi.appendMsg("PASS - PlaylistName.")
               
            
            time.sleep(1)
                           
                                 
            # Verify Syndication's Destination in form
            self.logi.appendMsg("INFO - Going to check Destination in Syndication's feed")             
            res = self.Wdobj.Sync(self.Wd,DOM.SYNDICATION_DESTINATION_EDIT.replace("TEXTTOREPLACE",DestinationName))
            if isinstance(res,bool):
                self.logi.appendMsg("FAIL - DestinationName. DestinationName = " + DestinationName)
            else:       
                self.logi.appendMsg("PASS - DestinationName. DestinationName")
            
            
            # Verify Syndication's LandingPage in form
            self.logi.appendMsg("INFO - Going to check text in Syndication's LandingPage")            
            rc=self.Wd.find_element_by_xpath(DOM.SYNDICATION_LANDINGPAGE).get_attribute("value")
            if rc == LandingPage:
                self.logi.appendMsg("PASS - Syndication's LandingPage")
            else:
                self.logi.appendMsg("FAIL - Syndication's LandingPage. LandingPage= " + LandingPage)
                
                           
             
            # Check that actual ContentFlavor is equal to expected - OK      
            if ContentFlavor != None:
                 
                self.logi.appendMsg("INFO - Going to check Syndication's ContentFlavor")
                rc=self.Wd.find_element_by_xpath(DOM.SYNDICATION_CONTENTFLAVOR_MAIN.replace("Source",ContentFlavor)).text
                if rc == ContentFlavor:
                    self.logi.appendMsg("PASS - Syndication's ContentFlavor")
                else:
                    self.logi.appendMsg("FAIL - Syndication's ContentFlavor. Expected_ContentFlavor= " + ContentFlavor + ", Actual_AdultContent = " + rc )
            
            # Check that actual AddToDefaultTranscodingProfile checkbox is equal to expected           
            if AddToDefaultTranscodingProfile != None:
                
                self.logi.appendMsg("INFO - Going to check Syndication's AddToDefaultTranscodingProfile")
                AddToDefaultTranscodingProfileMain = self.Wd.find_element_by_xpath(DOM.SYNDICATION_ADD_DEFAULT_TRANSCODINGPROFILE)     
                isCheckedAddToDefaultTranscodingProfile = AddToDefaultTranscodingProfileMain.find_element_by_xpath(DOM.SYNDICATION_ADD_DEFAULT_TRANSCODINGPROFILE_CHECKBOX).get_attribute("class").find("check")                  
                   
                if (isCheckedAddToDefaultTranscodingProfile == -1 and not  AddToDefaultTranscodingProfile) or (isCheckedAddToDefaultTranscodingProfile != -1 and   AddToDefaultTranscodingProfile) :
                    self.logi.appendMsg("PASS - Syndication's AddToDefaultTranscodingProfile")
                else:
                    self.logi.appendMsg("FAIL - Syndication's AddToDefaultTranscodingProfile. Expected_AddToDefaultTranscodingProfile has different value then Actual_AddToDefaultTranscodingProfile" )
                
                 
            # Check that actual Playback checkbox is equal to expected                                                              
            if Playback != None:
                self.logi.appendMsg("INFO - Going to check Syndication's Playback")
                if Playback == "From Google":
                    #self.Wd.find_element_by_xpath(SYNDICATION_PLAYBACK_FROMGOOGLE).click()
                    rc=self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYBACK_FROMGOOGLE).get_attribute("class")
                    if rc.find("active") == -1:
                        self.logi.appendMsg("FAIL - Syndication's Playback. Expected_Playback= Active - " + Playback + ", Actual_Playback = Not active " + rc )
                    else:
                        self.logi.appendMsg("PASS - Syndication's Playback")                     
                elif Playback == "Linkback to my site":
                    #self.Wd.find_element_by_xpath(SYNDICATION_PLAYBACK_LINKBACKTOMYSITE).click()
                    rc=self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYBACK_LINKBACKTOMYSITE).get_attribute("class")
                    if rc.find("active") == -1:
                        self.logi.appendMsg("FAIL - Syndication's Playback. Expected_Playback= Active - " + Playback + ", Actual_Playback = Not active" )
                    else:
                        self.logi.appendMsg("PASS - Syndication's Playback")
                else:
                    self.logi.appendMsg("FAIL - The Playback wasn't found in the list. Playback = " + Playback)
                    return False
      
            
            # Check that actual Player is equal to expected - OK                                                 
            if Player != None and Playback != "Linkback to my site":
                self.logi.appendMsg("INFO - Going to check Syndication's Player")
                rc=self.Wd.find_element_by_xpath(DOM.SYNDICATION_PLAYER_CHECKBOX_SELECTION.replace("TEXTTOREPLACE",Player)).text
                 
                if rc == Player:
                    self.logi.appendMsg("PASS - Syndication's Player")
                else:
                    self.logi.appendMsg("FAIL - Syndication's Player. Player= " + Player)
            
                 
            # Check that actual AdultContent check is equal to expected 
            if AdultContent != None:
                self.logi.appendMsg("INFO - Going to update Syndication's AdultContent")
                AdultContentMain = self.Wd.find_element_by_xpath(DOM.SYNDICATION_ADULTCONTENT)     
                isCheckedAdultContent = AdultContentMain.find_element_by_xpath(DOM.SYNDICATION_ADULTCONTENT_CHECKBOX).get_attribute("class")                      
                if isCheckedAdultContent.find("check") == -1:
                    ActualResultAdultContent = False
                else:
                    ActualResultAdultContent = True
                    
                if  str(ActualResultAdultContent) == str(AdultContent):          
                    self.logi.appendMsg("PASS - Syndication's AdultContent")  
                else:
                    self.logi.appendMsg("FAIL - Syndication's AdultContent. Expected_AdultContent= " + str(AdultContent) + ", Actual_AdultContent = " + str(ActualResultAdultContent) )
                             
                                   
            
            # Press on Cancel button
            self.logi.appendMsg("INFO - Going to Cancel the Syndication feed") 
            syndicationBTN=self.Wd.find_element_by_xpath(DOM.SYNDICATION_MAIN_BTN)
            syndicationBTN.find_element_by_xpath(DOM.SYNDICATION_CANCEL_BTN).click()
            time.sleep(2)
               
            
            return True
            
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - got the following exception - " + e)
            return False
        
        
    def DeleteSyndication(self,SyndicationName):
               
        try:
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_NAME_TABLE.replace("TEXTTOREPLACE",SyndicationName)).click()
            time.sleep(2)  
            
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_DELETE_BTN).click()
            time.sleep(2)  
            self.Wd.find_element_by_xpath(DOM.SYNDICATION_DLT_CONFIRM_DELETE_YES).click()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(e)
            return False
        
    def GetFeedSyndicationContent(self):
               
        try:            
            rcURL=self.Wd.find_element_by_xpath(DOM.SYNDICATION_URL).get_attribute("value")
            time.sleep(2)  
            
            file = urllib.request.urlopen(rcURL)
            data = file.read()
            file.close()
            
            return True,data
            
            
        except Exception as e:
            print(e)
            return False
    
    def GetSyndicationFeedID(self):
               
        try:            
            rID = self.Wd.find_element_by_xpath(DOM.SYNDICATION_ID).text
            
            return True,rID
            
            
        except Exception as e:
            print(e)
            return False
    
    
    def CompareSyndicationFeedXMLTOEXCEL(self,Environment,XMLContentStr,EXCELfile,SyndicationFeedID):
               
        try:
            #Environment = 2 #Production
            #Environment = 3 #Testing
            #Environment = 4 #PA-Reports
            #Environment = 5 #OnPrem
            
            CompareTestResult = True
                        
            # Give the location of the file 
            loc = (EXCELfile)
              
            # To open Workbook 
            wb = xlrd.open_workbook(loc) 
            
            sheet = wb.sheet_by_name("SyndicationXmlVerify")
            
            
            mydoc = ET.ElementTree(ET.fromstring(XMLContentStr))
            
            root  = mydoc.getroot()
                       
            ns = {'default': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                  'video': 'http://www.google.com/schemas/sitemap-video/1.1'}
            
            for i in range(1, sheet.nrows): 
                xpath = sheet.cell_value(i, 0) 
                BranchIndex = sheet.cell_value(i, 1)
                ValueToCheckFromExcel = sheet.cell_value(i, Environment) #2 --> production ; 3 --> Testing
                #Add SyndicationFeedID to video:content_loc
                if xpath == ".default:url/video:video/video:content_loc":
                    ValueToCheckFromExcel = ValueToCheckFromExcel + SyndicationFeedID
                
                if (BranchIndex == ""):
                    continue
               
                #make urlset/url/loc from branch index 1 become ./url[1]/loc etc.
                xpath =  xpath.replace(".default:url/", ".default:url[" + str(BranchIndex).split('.')[0] + "]/")
                self.logi.appendMsg(xpath)
                xmlNode = mydoc.find(xpath, ns)
                
                if (xmlNode is None):
                    print("Xpath not found")
                    CompareTestResult = False
                else:
                    print("Xml:  " + xmlNode.text)
                    print("Excel:" + ValueToCheckFromExcel)
                    if (xmlNode.text == ValueToCheckFromExcel):
                        print("Equal")
                    else: 
                        print("Not equal")
                        CompareTestResult = False
            
                    print("")
            
                        
            return CompareTestResult          
                        
        except Exception as e:
            print(e)
            return False