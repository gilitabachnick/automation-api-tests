'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1890_SIP.py
 
 @desc : this test check the SIP basic flow - The test created new SIP meeting  by ZOOM site and then login to KMC and play the live entry on preview&embed 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import ClienSession
import Config
import Practitest
import Entry
import Transcoding
import uiconf
import live
import tearDownclass
import MySelenium
import ZoomFuncs
import KmcBasicFuncs
import Entrypage
import reporter2

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
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
            self.ServerURL = inifile.RetIniVal(section, 'SIP_ServerURL')
            self.RoomSuffix = "@vc.kaltura.com"
            self.user   = inifile.RetIniVal(section, 'KMCuserDistribution')
            self.pwd    = inifile.RetIniVal(section, 'KMCpwdDistribution')
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
            self.ServerURL = inifile.RetIniVal(section, 'ServerURL')
            self.RoomSuffix = "@vc-stg.kaltura.com"
            self.user   = inifile.RetIniVal(section, 'partnerId4770_USER')
            self.pwd    = inifile.RetIniVal(section, 'partnerId4770_PWD')
            
        #ZOOM site
        self.ZoomUrl    = "https://zoom.us/signin"
        self.ZoomUser   = inifile.RetIniVal('Zoom', 'ZoomUser')
        self.ZoomPwd    = inifile.RetIniVal('Zoom', 'ZoomPwd')
        #KMC account
        self.PublisherID = inifile.RetIniVal(section, 'SIP_PublisherID')
        self.UserSecret =  inifile.RetIniVal(section, 'SIP_AdminSecret')      
        self.url    = inifile.RetIniVal(section, 'Url')
        self.sendto = inifile.RetIniVal(section, 'sendto')
        
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('4586')
        self.Wdobj = MySelenium.seleniumWebDrive()                            
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_1890_SIP')
        self.ZoomFuncs  = ZoomFuncs.ZoomFuncs(self.Wd,self.logi)
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()
        self.entryPage = Entrypage.entrypagefuncs(self.Wd,self.logi) 
        self.logi.initMsg('test_1890_SIP')
                 
        # create client session
        self.logi.appendMsg('start create session for partner: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
        
        ''' RETRIEVE TRANSCODING ID AND CREATE SOURCE ONLY IF NOT EXIST'''
        Transobj = Transcoding.Transcoding(self.client,'SourceOnly')
        self.cloudId =  Transobj.getTranscodingProfileIDByName('Cloud transcode')
        self.passtrhroughId = Transobj.getTranscodingProfileIDByName('Passthrough')
        self.sourceonlyId =  Transobj.getTranscodingProfileIDByName('SourceOnly')
        
        if self.cloudId==None or self.passtrhroughId==None:
            self.logi.appendMsg('One of the followings: Cloude Transcode or Passthrough transcoding profiles of live not exist for the publisher, can not continue the test')
            self.logi.reportTest('fail')
            assert False
        
        if self.sourceonlyId==None:
            if isProd: 
                self.sourceonlyId = Transobj.addTranscodingProfile(1,'0') 
                if isinstance(self.sourceonlyId,bool):
                    self.logi.reportTest('fail')
                    self.testTeardownclass.exeTear()
                    assert False
            else:
                self.sourceonlyId = Transobj.addTranscodingProfile(1,'32')
                if isinstance(self.sourceonlyId,bool):
                    self.logi.reportTest('fail')
                    self.testTeardownclass.exeTear()
                    assert False
         
        # Create player of latest version 
        self.logi.appendMsg('Going to add the latest version player')      
        myplayer = uiconf.uiconf(self.client, 'livePlayer')  
        if isProd:
            self.player = myplayer.addPlayer(None,'prod',False, False)
        else:
            self.player = myplayer.addPlayer(isDrm=False)
        self.logi.appendMsg('new player was add, conf ID=' + str(self.player.id))
        if isinstance(self.player,bool):
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
        
        self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')
        #Create live Entry
        self.logi.appendMsg('Going to add live entry')
        self.live = live.Livecls(self.client, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.player.id)
        myentry = Entry.Entry(self.client,"autoLive_" + str(datetime.datetime.now()), "SIP Automation test", "SIP tag", "Admintag", "SIP category", 1)  # file(filePth,'rb')
        self.entry = myentry.AddEntryLiveStream(None, None)

    def test_1890_SIP(self):
        
        global testStatus
        global KMC_Zoom_Deletion  
        global MeetingId
        
        PreviewEmbedTYPESelectionText = "Dynamic Embed"
        PreviewEmbedHTTPSSelection = False
        meetingDuration = 2 #seconds
        PlayerVersion = 3      
        
        self.logi.initMsg('test_1890_SIP.py')
        
        # Create SIP URL
        self.logi.appendMsg('Going to generate Sip Url.')
        resultSipUrl = self.client.sip.pexip.generateSipUrl(self.entry.id)
        if self.env == 'prod':
            CheckSipUrl = resultSipUrl.find(self.RoomSuffix)
            if CheckSipUrl == -1:
                 self.logi.appendMsg("FAIL - SIP URL is not valid =  " + resultSipUrl )
                 testStatus = False
                 return
            else:
                self.logi.appendMsg("PASS - Production Create SIP URL  =  " + resultSipUrl )
        else:
            #self.logi.appendMsg("FAIL - SIP URL is not supported on testing.qa - No license" )
            CheckSipUrl = resultSipUrl.find(self.RoomSuffix)
            if CheckSipUrl == -1:
                 self.logi.appendMsg("FAIL - SIP URL is not valid =  " + resultSipUrl )
                 testStatus = False
                 return
            else:
                self.logi.appendMsg("PASS - Testing.qa Create SIP URL  =  " + resultSipUrl )
        
        # ZOOM SITE
        try:
             # Login to ZOOM web site
             self.logi.initMsg('Going to login to Zoom site')
             rc = self.ZoomFuncs.invokeZOOMLogin(self.Wd, self.Wdobj, self.ZoomUrl, self.ZoomUser, self.ZoomPwd)
             if rc == False:
                 self.logi.appendMsg("FAIL - Invoke ZOOM Login to web site" )
                 testStatus = False
                 return
                
             self.Wd.maximize_window()
                
            # Create meeting from Zoom site with SIP config -->sending parameter sip=True
             self.logi.initMsg('Going to create meeting to Zoom site')
             rc,MeetingId = self.ZoomFuncs.CreateMeetingFromZoomSite(self.Wd, self.Wdobj, self.ZoomUrl, self.ZoomUser, self.ZoomPwd,2,resultSipUrl)
             if rc == False:
                 self.logi.appendMsg("FAIL - Create Meeting From Zoom Site" )
                 testStatus = False
                 return    
            
             # KMC verification for the ZOOM entry
             self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
             rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
             self.Wd.maximize_window()
             # Save KMC window
             primContentTab = self.Wd.window_handles[0]
             
            # Select Entry
             self.logi.appendMsg("INFO - Going to select the entry. entryId = " + self.entry.id)          
             rc = self.BasicFuncs.selectEntryfromtbl(self.Wd, self.entry.id, True)
             if not rc:
                self.logi.appendMsg("FAIL - could not find the entry with EntryId:" + self.entry.id + " in entries table")
                     
             self.logi.appendMsg("********** INFO - Going to use player - VERSION = " + str(PlayerVersion) )
                
             self.Wd.maximize_window()
             # Save window 
             primTab = self.Wd.window_handles[0]
         
             # Play the entry by PreviewAndEmbed
             self.logi.appendMsg("INFO - Going to play the entry on PreviewAndEmbed player. entryId = " + self.entry.id)    
             rc = self.entryPage.PreviewAndEmbed(self.env,PreviewEmbedHTTPSSelection,PreviewEmbedTYPESelectionText,PlayerVersion,"Automation player_version" + str(PlayerVersion),self.Wd)
             if not rc:
                 testStatus = False
                 self.logi.appendMsg("FAIL - PreviewAndEmbed : PlayerVersion = " + str(PlayerVersion) + ", PlayerName = Automation player_version" + str(PlayerVersion))
             else:
                 self.logi.appendMsg("PASS - PreviewAndEmbed : PlayerVersion = " + str(PlayerVersion) + ", PlayerName = Automation player_version" + str(PlayerVersion))
             # meetingDuration    
             time.sleep(meetingDuration)
              
             # Close embed player tab                   
             self.Wd.close()
             time.sleep(2)
                
             # Return to previous window  
             self.Wd.switch_to.window(primTab)
             time.sleep(2)
             # Close preview&embed window   
             self.Wd.find_element_by_xpath(DOM.PREVIEWANDEMBED_CLOSE_BTN).click()
             time.sleep(2)
                
             # Close KMC            
             self.Wd.close()          
             time.sleep(6)
        
             # Leave/End meeting on Zoom site
             self.logi.initMsg('Going to Leave/End meeting on Zoom site')
             rc = self.ZoomFuncs.LeaveMeetingSIPZOOMMeeting(self.Wd, self.Wdobj,MeetingId ,self.ZoomUser, self.ZoomPwd)
             if rc == False:
                 self.logi.appendMsg("FAIL - LeaveMeetingSIPZOOMMeeting From Zoom Site" )
                 testStatus = False
                 return
             else:
                 self.logi.appendMsg("PASS - LeaveMeetingSIPZOOMMeeting From Zoom Site" )    
             
          
        except Exception as e:
            print(e)
            testStatus = False
            pass
             
        
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
       
    def teardown_class(self):
        
        print('#############')
        print(' Tear down')
        print('#############')
        
        try:
            self.testTeardownclass.exeTear()
            # Delete the live entry
            self.logi.appendMsg("INFO - Going to delete the live entry. entryId = " + self.entry.id)
            time.sleep(20)
            result = self.client.baseEntry.delete(self.entry.id)
            print("Info - " + result) 
        except Exception as exep:
                print(str(exep))

        try:
            self.Wd.quit()
        except:
            pass
          
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '1890','1') 
           self.logi.reportTest('fail',self.sendto) 
           
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '1890','0')
           self.logi.reportTest('pass',self.sendto) 
           assert True        

    #pytest.main(args=['test_1890_SIP.py','-s'])    
        
        
        