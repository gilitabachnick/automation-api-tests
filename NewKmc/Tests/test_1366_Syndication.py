import os
import sys
import time
####ADDED to compare XML to EXCEL
#init excel
#init xml


pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import reporter2

import Config
import Practitest
import autoitWebDriver
import distributionFuncs
import Entrypage
import uploadFuncs
import KmcBasicFuncs
import PlaylistFuncs
import SyndicationFuncs


### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

class TestClass:

    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'KMCQaAutomation')
            self.pwd    = inifile.RetIniVal(section, 'KMCPWDQaAutomation') 
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.logi = reporter2.Reporter2('test_1366_Syndication')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.distribusionsFuncs = distributionFuncs.distributefuncs(self.Wd,self.logi)
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            # Syndication setup
            self.SyndicationFuncs = SyndicationFuncs.SyndicationFuncs(self.Wd,self.logi)
            self.SyndicationName= "Syndication Auto1"
            self.SyndicationLandingPage = "https://www.google.com/"
            self.SyndicationAllContent= False
            self.SyndicationPlayback=None
            self.SyndicationPlayer="Existing Player V2"
            self.SyndicationContentFlavor=None
            self.SyndicationAddToDefaultTranscodingProfile=None
            self.SyndicationAdultContent=None
            # Playlist setup
            self.PlaylistName = "playlist for syndication test"                        
            self.playlistFuncs = PlaylistFuncs.playlistfuncs(self.Wd, self.logi)
                                    
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
                            
                
        except:
            pass
    
    
    
            
    def test_Syndication(self):
             
        global testStatus
        
        self.logi.initMsg('test_1366_Syndication')
        
        try:            
            
            # Invoke and login
            self.logi.appendMsg("INFO - Going to login to KMC")
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            if not rc:
                self.logi.appendMsg("FAIL - Login to KMC") 
                testStatus = False
                return               
            self.Wd.maximize_window()            
            
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            
            # Add entries to playlist
            self.logi.appendMsg("INFO - Going to create playlist") 
            rc = self.playlistFuncs.CreatPlayList(self.PlaylistName, ["Video Learning - Student Perspective","Video Insights - Integration","Video Insights - EMEA Culture"])
            if not rc:
               self.logi.appendMsg("FAIL - Could NOT create playlist with entries - PlaylistName = " + self.PlaylistName )
               testStatus = False
               return
          
            # Create Syndication type Google
            self.logi.appendMsg("INFO - Going to create Syndication type Google")            
            rc = self.SyndicationFuncs.CreatSyndicationGoogle(self.SyndicationName, self.PlaylistName, self.SyndicationLandingPage, self.SyndicationAllContent, self.SyndicationContentFlavor, self.SyndicationAddToDefaultTranscodingProfile, self.SyndicationPlayback, self.SyndicationPlayer, self.SyndicationAdultContent)           
            if not rc:
                self.logi.appendMsg("FAIL - CreatSyndication") 
                testStatus = False
                return     
            
            # Press on Edit syndication by syndication name
            self.logi.appendMsg("******** INFO - Going to check values on the Syndication feed in Eit Syndication window*************")
            rc=self.SyndicationFuncs.VerifySyndicationGoogle(self.SyndicationName, self.PlaylistName, self.SyndicationLandingPage, self.SyndicationAllContent, self.SyndicationContentFlavor, self.SyndicationAddToDefaultTranscodingProfile, self.SyndicationPlayback, self.SyndicationPlayer, self.SyndicationAdultContent)
            if not rc:
                self.logi.appendMsg("FAIL - VerifySyndicationGoogle") 
                testStatus = False
                return         
            
            # Get FeedSyndication Content XML
            self.logi.appendMsg("INFO - Going to Get the Syndication feed URL")
            rc,FeedXMLContentStr=self.SyndicationFuncs.GetFeedSyndicationContent()
            if not rc:
                self.logi.appendMsg("FAIL - GetFeedSyndicationContent") 
                testStatus = False
                return         
            
            # Get Syndication FeedID
            self.logi.appendMsg("INFO - Going to Get the Syndication FeedID")       
            rc,SyndicationFeedID=self.SyndicationFuncs.GetSyndicationFeedID()
            if not rc:
                self.logi.appendMsg("FAIL - GetFeedSyndicationID") 
                testStatus = False
                return
            
            self.logi.appendMsg("*********** INFO - Going to Compare SyndicationFeedXML TO EXCEL *************")
            # Set Environment for excel: 
            #Environment = 2 #Production
            #Environment = 3 #Testing
            #Environment = 4 #PA-Reports
            #Environment = 5 #OnPrem
            if isProd == True:
               Environment = 2 
            elif isProd == False:
                Environment = 3
            else:
                Environment = 4
                Environment = 5
                    
            #===================================================================
            # EXCELfile="C:\\Users\\moran.cohen\\Downloads\\script_syndication\\Syndication.xlsx"
            #===================================================================
            if "nv" not in self.url:  # Use other XLS for NVD console user/pass login
                EXCELfile = os.path.join(os.path.dirname( __file__ ), '..', 'UploadData','Syndication.xls')
            else:
                EXCELfile = os.path.join(os.path.dirname( __file__ ), '..', 'UploadData','Syndication NVQ.xls')

            rc = self.SyndicationFuncs.CompareSyndicationFeedXMLTOEXCEL(Environment, FeedXMLContentStr, EXCELfile,SyndicationFeedID)
            if not rc:
                self.logi.appendMsg("FAIL - CompareSyndicationFeedXMLTOEXCEL") 
                testStatus = False
                return        
            else:
                self.logi.appendMsg("PASS - CompareSyndicationFeedXMLTOEXCEL")
            
        except Exception as e:
            print(e)
            testStatus = False
            self.logi.appendMsg("FAIL - on one of the following: KMC login | UPLOAD | WaitForReady | DrillDown | Distribution tab Failed")
              
        
          
        
    def teardown(self):   
        
        global teststatus
        
        # Delete syndication feed
        try:
            self.logi.appendMsg("INFO - Going to delete the Syndication feed")
            self.SyndicationFuncs.DeleteSyndication(self.SyndicationName)
        except Exception as e:
            print(e)
            pass
        # Delete playlist
        try:
            self.Wd.find_element_by_xpath(DOM.PLAYLISTS_TAB).click()
            time.sleep(3) 
            self.logi.appendMsg("INFO - Going to delete the playlist")
            self.BasicFuncs.deleteEntries(self.Wd,self.PlaylistName)
        except:
            pass
        
        # Close browser                
        self.Wd.quit()
            
        if testStatus == False:
            self.logi.reportTest('fail',"moran.cohen@kaltura.com")
            self.practitest.post(Practi_TestSet_ID, '1366','1')
            assert False
        else:
            self.logi.reportTest('pass',"moran.cohen@kaltura.com")
            self.practitest.post(Practi_TestSet_ID, '1366','0')
            assert True         
            
    #===========================================================================
    # pytest.main(args=['test_1366_Syndication.py','-s'])
    #===========================================================================