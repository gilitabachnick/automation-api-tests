import _thread
import datetime
import os
import sys
import time

from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#import BrowserProxy
import ClienSession
import reporter
import Config
import tearDownclass
import Practitest
import Entry
import Transcoding
import clsPlayerV2
import uiconf
import strclass
import QrcodeReader
import live


isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')


isProd = True  
 
#===========================================================================
# Description :   Live test  
#
# test scenario:  upload live entry
#                 stream the entry
#                 sniff ts and manifest packets,
#                 verify ts downloaded correct,
#                 
#                 
# verifications:  video play (QRcode)
#                 manifest and license packets retrieve OK reply
#===========================================================================

''' ----- CONSTANTS ------- '''
FFMPEGPATH =  '/home/ubuntu/ffmpeg'   

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
        else:
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
            
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret =  inifile.RetIniVal('Environment', 'UserSecret')  
        #self.primaryBroadcastingUrl = inifile.RetIniVal('Live', 'primaryBroadcastingUrl') 
        
        self.testTeardownclass = tearDownclass.teardownclass()
        self.practitest = Practitest.practitest()
        self.logi = reporter.Reporter('Live')
        self.logi.initMsg('Live setup')
                 
        # create client session
        self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
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
        self.logi.appendMsg('going to add the latest version player')
        
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
        self.live = live.Livecls(self.client, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.player.id)
        
    def StreamFromFfmpeg(self, primaryBroadcastingUrl, kentry=None):
        #primaryBroadcastingUrl = primaryBroadcastingUrl.replace('il-wowza-centos-01','il-wowza-centos-rec-01')
        if kentry==None:
            kentry =self.entry
        else:
            primaryBroadcastingUrl = kentry.primaryBroadcastingUrl
            self.startTime = time.time()
            
        filePth = '/home/ubuntu/MediaUpload/LiveQr30min.mp4'
        comand = FFMPEGPATH +' -re -i ' + filePth + ' -c:v copy -c:a copy -f flv  -rtmp_live 1 "' + primaryBroadcastingUrl + '/' + kentry.id + '_1" > /dev/null 2>&1 &'
        print(comand)
        _thread.start_new_thread(os.system,(comand,))
        self.testTeardownclass.addTearCommand(os,'system(\'killall ffmpeg\')')
    
    def Entryandstrem(self, conversionProfileId, recordStatus=0, dvrStatus=0, Kentry=None):
        #conversionProfileId=self.sourceonlyId
        
        ''' UPLOAD NEW LIVE ENTRYT '''
        if Kentry == None:
            # Upload entry with the above transcoding profile
            self.logi.appendMsg('going to upload new live entry ')
            self.myentry = Entry.Entry(self.client,"autoLive_" + str(datetime.datetime.now()), "Live Automation test", "Live tag", "Admintag", "adi category", 1,None,conversionProfileId)  # file(filePth,'rb')
            self.entry = self.myentry.AddEntryLiveStream(None, None, recordStatus, dvrStatus)
            if isinstance(self.entry,bool):
                self.logi.appendMsg('Entry was not uploaded after 5 minutes')
                self.logi.reportTest('fail')
                return False
            
            elif isinstance(self.entry, str):
                self.logi.appendMsg('Entry got error when trying to upload it')
                self.logi.reportTest('fail')
                return False
            else:
                self.logi.appendMsg('Finished upload new live entry, id = ' + str(self.entry.id))
                self.testTeardownclass.addTearCommand(self.myentry,'DeleteEntry(\'' + str(self.entry.id) + '\')')
        else:
            self.entry = Kentry
            
                
        self.primaryBroadcastingUrl = self.entry.primaryBroadcastingUrl
        
                
        ''' START STREAMING FROM FFMPEG '''  #self.primaryBroadcastingUrl = self.primaryBroadcastingUrl.replace("centos-01","centos-03")
        self.StreamFromFfmpeg(self.primaryBroadcastingUrl)
        self.startTime = time.time()        
        # build URL for player page
        self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>'
        if isProd:
            self.baseUrl = self.baseUrl + '&env=production'   
               
        strcls = strclass.strclass(self.baseUrl)
        newParams = str(self.PublisherID) + ',' + str(self.player.id) + ',' + self.entry.id 
        self.baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,', newParams)
        self.logi.appendMsg('player page url is:' + self.baseUrl)
        
        '''PLAY THE STREAMED VIDEO '''
        selDriver = 2
        time.sleep(90)
             
        if selDriver==0:
            selDriver = "firefox" 
        elif selDriver==1:
            selDriver = "internet explorer"
        elif selDriver==2:
            selDriver = "chrome"
            
        self.kaltplayer = clsPlayerV2.playerV2("kaltura_player_1418811966") 
        self.driver = self.kaltplayer.testWebDriverLocalOrRemote (selDriver)
        
        try:
            self.driver.get(self.baseUrl)
        except:
            self.logi.appendMsg('could not get to the player base url- might be connection problem')
            self.logi.reportTest('fail')
            return False
       
        if selDriver==0 or selDriver==1: 
            self.driver.maximize_window()
        time.sleep(5)
        
        # allow the pop up streaming
        if selDriver==0:
            Webelement = self.driver.find_element_by_xpath('//body')
            Webelement.send_keys(Keys.ALT+'a')
            time.sleep(1)
            Webelement.send_keys(Keys.ALT+'r')
            time.sleep(2)
        
        
        timeisfinish = False
        timer = 0
        self.kaltplayer.switchToPlayerIframe(self.driver)
        
        while not timeisfinish:        
            try:
                time.sleep(1)
                timer = timer + 1
                if timer == 300:  # THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE
                    timeisfinish = True
                    self.logi.appendMsg('FAIL - THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE')
                    self.logi.reportTest('fail')
                    assert False
                    
                self.kaltplayer.clickPlay(self.driver)
                self.logi.appendMsg(' play clicked ok')
                timeisfinish = True
            
            except Exception as exp:
                print(exp)
                return False
            
        # wait till live is actually played after press the play button
        self.logi.appendMsg('video with QR code is playing')
        time.sleep(20)
        return True
    
    def entryStatusChanges(self,nameAddition=None):

        entries =  self.myentry.getEntryListByName(self.entry.name) #
        if isinstance(entries,bool):
            self.logi.appendMsg('FAIL - could not find entry with the name: ' + str(self.entry.name))
            self.logi.reportTest('fail')
            return False
    
        self.logi.appendMsg("INFO - going to check that a new entry was created and it has the status NO MEDIA while streaming")
        if nameAddition!=None:
            newEntryName = self.entry.name + nameAddition
        else:
            newEntryName = self.entry.name
            
        entries =  self.myentry.getEntryListByName(newEntryName,'no content')           
        if entries.objects.__len__() < 1:
            self.logi.appendMsg('FAIL - new entry should have been created with status NO MEDIA and it was not created')
            self.status = False
            return False
            
        else: #retrieve the new entry id
            self.logi.appendMsg("PASS - new entry with the same name- " + newEntryName + " and id= " + entries.objects[0].id + "  was created with status NO MEDIA OK")
            newEntryId = entries.objects[0].id
            self.logi.appendMsg("INFO - going to stop the streaming and check that the entry status changed to Ready")
            os.system('killall ffmpeg')   
            time.sleep(30) 
            startTime = time.time()   
            newEntry = self.myentry.getEntry(newEntryId)
            if int(newEntry.status.value) == 2:
                self.logi.appendMsg("PASS - the entry status is READY as excpected")
            else:
                self.logi.appendMsg("FAIL - the entry status should have been with the value 2 - READY and it is actually value is: " + str(newEntry.status.value))
                self.status = False
                
            return newEntryId   

    def PlayRecordedEntry(self,entryId):
    
        self.logi.appendMsg("INFO - going to play the recorded entry - " + entryId + " and check it starts at 00:00 time of the stream") 
        timeisfinish = False
        timer = 0
        
        newbaseUrl = self.baseUrl.replace('entryID=' + self.entry.id, 'entryID=' + entryId)
        print(('the URL IS:' +newbaseUrl))
        time.sleep(5)
        
        playkaltplayer = clsPlayerV2.playerV2("kaltura_player_1418811966") 
        self.playdriver = playkaltplayer.testWebDriverLocalOrRemote ('chrome')
        
        try:
            self.playdriver.get(newbaseUrl)
        except:
            self.logi.appendMsg('could not get to the player base url- might be connection problem')
            self.logi.reportTest('fail')
            return False
        
        playkaltplayer.switchToPlayerIframe(self.playdriver)
        
        while not timeisfinish:        
            try:
                time.sleep(1)
                timer = timer + 1
                if timer == 300:  # THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE
                    timeisfinish = True
                    self.logi.appendMsg('THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE')
                    self.logi.reportTest('fail')
                    assert False
                    
                playkaltplayer.clickPlay(self.playdriver)
                print(' play clicked ok')
                timeisfinish = True
            
            except Exception as exp:
                print('no play')
                return False
        
        
        timeisfinish = False
        
        self.QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.playdriver, logobj=self.logi)
        self.QrCode.initVals()
        while not timeisfinish:
            firstQr = self.QrCode.saveScreenShot()
            firstQr = self.QrCode.retQrVal(firstQr)
            if isinstance(firstQr, bool):
                time.sleep(0.5)
                timer = timer+1
                if timer == 120:
                    timeisfinish=True
                    self.logi.appendMsg("FAIL - the video did not play 2 minute after pressing the play button")
                    self.status = False
            else: # retrieve only the hour of the QR code value
                hrval = str(firstQr.split(' ')[1].split('.')[0])
                if hrval=='00:00:27' or hrval=='00:00:28' or hrval=='00:00:29':
                    self.logi.appendMsg("PASS - the entry started play from 00:00 time of the stream")
                    self.status = True
                else:
                    self.logi.appendMsg("FAIL - the video did not played from the 00:00 second of the stream but from: " + hrval)
                    self.status = False  
                    
                timeisfinish=True
                
        return self.status
    #################################################            
    '''
    @PLAY_SOURCEONLY_test
    '''       
    ################################################    
    def test_playSourceOnly(self):
           
        # id=kaltura_player_1403192124
        self.status = True
        self.logi.initMsg('SOURCE ONLY AND PLAY LIVE test')
           
        self.status = self.Entryandstrem(self.sourceonlyId)
           
        ''' read QR code for 5 minutes of play'''
        self.logi.appendMsg("going to read QR code for 5 minutes of play")
        if self.status:
            QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
            timeisfinish = False
              
            #while not time is up (5 minutes) continue to check the Qr codes on the stream
            while not timeisfinish:
                rc = QrCode.placeCurrPrevScr()
                if rc:
                    rc = QrCode.checkProgress(1)
                    if not rc:
                        self.status = False 
                if time.time()-self.startTime > 390:
                    timeisfinish = True
                      
            self.driver.quit()
               
            if self.status == False :
                self.logi.reportTest('fail')
                assert False
               
            else:
                self.logi.reportTest('pass')
                assert True
      
    #################################################            
    '''
    @CLOUD_TRANSCODE__DVR_AND_PLAY_LIVE_test
    '''       
    ################################################
    def test_cloudTranscode_DVR(self):
            
         self.logi.initMsg('CLOUD TRANSCODE + DVR AND PLAY LIVE test')
                    
         self.status = self.Entryandstrem(self.cloudId,0,1) 
             
         ''' read QR code for 2 minutes of play'''
         self.logi.appendMsg("going to read QR code for 2 minutes of play")
         if self.status:
             ''' ----- first play 2 minutes -------'''
             QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             timeisfinish = False
             tmpStatus = True
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
             while not timeisfinish:
                 rc = QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = QrCode.checkProgress(1)
                     if not rc:
                         tmpStatus = False
                         self.status = False 
                 if time.time()-self.startTime > 120:
                     timeisfinish = True
                       
             if tmpStatus == True:
                 self.logi.appendMsg("PASS - first 2 minutes played video OK")
             else:
                 self.logi.appendMsg("FAIL - first 2 minutes did NOT play the video ok")
                        
             self.logi.appendMsg("going to scroll to start point - REWIND")
             self.kaltplayer.clickOnSlider(self.driver, 0)
               
             #===================================================================
             # reTimer = self.kaltplayer.getCurrentTimeLabel(self.driver)
             # if isinstance(reTimer, bool):
             #     self.logi.appendMsg("FAIL- could not find timer element to check it is in -02:00")
             #     self.status = False
             # elif reTimer=='-02:00':
             #     print 'It is -02:00'
             # else:
             #     self.logi.appendMsg("FAIL- timer should have been with value -02:00 after scrolling rewind and it is- " + str(reTimer))
             #     self.status = False
             #===================================================================
               
             ''' ----- second play 1 minutes -------'''
             QrCode.initVals()
             #QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             timeisfinish = False
             timer = 0
             tmpStatus = True
             self.logi.appendMsg("going to read QR code for 1 minute of play - after Rewind")
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
               
             while not timeisfinish:
                  
                 rc = QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = QrCode.checkProgress(1)
                     if not rc:
                         tmpStatus = False
                         self.status = False 
                 timer = timer + 1
                 #if timer == 300:
                 if timer == 60:
                     timeisfinish = True  
                        
             if tmpStatus == True:
                 self.logi.appendMsg("PASS - 1 minute of played video after Rewind, played OK")
             else:
                 self.logi.appendMsg("FAIL - 1 minute of played video after Rewind, did NOT play the video ok") 
                        
             self.logi.appendMsg("going to scroll to middle point - Forward")
             self.kaltplayer.clickOnSlider(self.driver, 50)
                
             #===================================================================
             # reTimer = self.kaltplayer.getCurrentTimeLabel(self.driver)
             # if isinstance(reTimer, bool):
             #     self.logi.appendMsg("FAIL- could not find timer element to check it is in -02:00")
             #     self.status = False
             # elif reTimer[:1]=='-':
             #     print 'It is -'
             # else:
             #     self.logi.appendMsg("FAIL- timer should have been with value \"-\" after scrolling forward to the middle, and it is- " + str(reTimer[:1]))
             #     self.status = False
             #===================================================================
                
             ''' ----- third play 1 minutes -------'''
             QrCode.initVals()
             #QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             timeisfinish = False
             timer = 0
             tmpStatus = True
             self.logi.appendMsg("going to read QR code for 1 minute of play - after Forward to middle point")
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
             while not timeisfinish:
                 rc = QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = QrCode.checkProgress(1)
                     if not rc:
                         tmpStatus = False
                         self.status = False 
                 timer = timer + 1
                 #if timer == 300:
                 if timer == 60:
                     timeisfinish = True 
                        
             if tmpStatus == True:
                 self.logi.appendMsg("PASS - 1 minute of played video after Forward to middle point, played OK")  
             else:
                 self.logi.appendMsg("FAIL - 1 minute of played video after Forward to middle point did NOT play the video ok")    
                
             self.logi.appendMsg("going to Press the back to live button")
             self.kaltplayer.clickLiveIconBackToLive(self.driver)
             reTimer = self.kaltplayer.getCurrentTimeLabel(self.driver)
                
             ''' check scroll is at the end of it'''
                            
             ''' ----- forth play 1 minutes -------'''
             QrCode.initVals()
             #QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             timeisfinish = False
             timer = 0
             tmpStatus = True
             self.logi.appendMsg("going to read QR code for 1 minute of play - afetr Back to live")
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
             while not timeisfinish:
                 rc = QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = QrCode.checkProgress(1)
                     if not rc:
                         tmpStatus = False
                         self.status = False 
                 timer = timer + 1
                 #if timer == 300:
                 if timer == 60:
                     timeisfinish = True  
                       
             self.driver.quit()
                        
             if tmpStatus == True:
                 self.logi.appendMsg("PASS - Last 1 minute of played video after back to live, played OK") 
             else:
                 self.logi.appendMsg("FAIL - Last 1 minute of played video after back to live, did NOT play the video ok")
                    
             if self.status == False:
                 self.logi.reportTest('fail')
                 assert False
             else:
                 self.logi.reportTest('pass')
                 assert True
                  
    
    #################################################            
    '''
    @PASS_THROUGH__ENABLE_RECORDING_APPEND_RECORD_test
    '''       
    ################################################
    def test_PassThrough_RecordingAppend(self):
            
         self.status = True
         self.logi.initMsg('PASS THROUGH + ENABLE RECORDING- APPEND RECORD test')
            
            
         self.status = self.Entryandstrem(self.passtrhroughId,1,0)  
         ''' read QR code for 5 minutes of play''' 
         self.logi.appendMsg("going to read QR code for 5 minutes of play")
         if self.status:
             self.QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             self.QrCode.initVals()
             timeisfinish = False
              
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
             while not timeisfinish:
                 rc = self.QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = self.QrCode.checkProgress(1)
                     if not rc:
                         self.status = False 
                 if time.time()-self.startTime > 390:
                     timeisfinish = True
                 
             if self.status == True :
                 self.logi.appendMsg("PASS - Video played ok with no stops all the last 5 minutes")
                    
         newEntryId = self.entryStatusChanges()
         self.driver.quit()
         time.sleep(60)
         if not isinstance(newEntryId, bool):
             time.sleep(15)
             self.PlayRecordedEntry(newEntryId)
             self.playdriver.quit()
             startTime = time.time()                         
             timeisfinish = False
             itimer = 0
             interStatus = False
             while not timeisfinish:
                 time.sleep(1)
                 # check that the flavors in status OK wait 15 minutes for that
                 EntryFlavors = self.myentry.flavorList(newEntryId)
                 for i in range(0,EntryFlavors.totalCount):
                     if EntryFlavors.objects[i].status.value != 2:
                         interStatus = False
                         continue
                     else:
                         interStatus = True
                    
                 if interStatus:
                     self.logi.appendMsg("PASS - the Entry flavors got the status OK after - " + str(time.time()-startTime) + " Seconds as excpected")
                     timeisfinish = True
                 else:
                     if time.time()-startTime > 900:
                         timeisfinish = True
                         self.logi.appendMsg("FAIL - the Entry flavors did not get the status OK 15 minutes after the entry was in status Ready") 
                         self.status = False
                        
            
         if self.status == False:
             self.logi.reportTest('fail')
             assert False
              
         else:
             self.logi.reportTest('pass')
             assert True
              
    #################################################            
    '''
    @PASS_THROUGH__ENABLE_RECORDING_CREATE_STOPSTREAM_4MIN_test
    '''       
    ################################################ 
    def test_PassThrough_RecordingCretae_stopStream_4Min(self):
             
         self.status = True
         self.logi.initMsg('PASS THROUGH + ENABLE RECORDING- APPEND RECORD STOP STREAM 4 MINUTES test')
             
             
         self.status = self.Entryandstrem(self.passtrhroughId,2,0)  
         ''' read QR code for 5 minutes of play''' 
         self.logi.appendMsg("going to read QR code for 5 minutes of play")
         if self.status:
             self.QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             self.QrCode.initVals()
             timeisfinish = False
                
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
             while not timeisfinish:
                 rc = self.QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = self.QrCode.checkProgress(1)
                     if not rc:
                         self.status = False 
                 if time.time()-self.startTime > 390: 
                     timeisfinish = True
                  
             if self.status == True :
                 self.logi.appendMsg("PASS - Video played ok with no stops all the last 5 minutes")
             else:
                 self.logi.appendMsg("FAIL - Video did Not play ok all the last 5 minutes")
                 
             newEntryId1 = self.entryStatusChanges(' 1')
                 
             '''
             @WAIT_4_MINUTES and then stream again for 2 minutes
             '''
             time.sleep(240)
             self.logi.appendMsg("INFO - streaming again for 2 minutes, new entry with the same name + 2 should be created")
                
             self.StreamFromFfmpeg(None,self.entry)
             while time.time()-self.startTime <119:
                 time.sleep(1)
                            
             newEntryId2 = self.entryStatusChanges(' 2')
             self.logi.appendMsg("INFO - stop streaming after 2 minutes")
                
             time.sleep(60)
                
             # play the both recorded entries
             if not isinstance(newEntryId1, bool):
                 self.status = self.PlayRecordedEntry(newEntryId1)
                 self.playdriver.quit()
                
             if not isinstance(newEntryId2, bool):
                 self.status = self.PlayRecordedEntry(newEntryId2)
                    
             self.logi.appendMsg("INFO - going to check that the second entry duration is 2 minutes")            
             dur = self.kaltplayer.getDuration(self.playdriver)
               
               
             acctdur = datetime.datetime(1900,1,1,0,int(dur.split(':')[0]),int(dur.split(':')[1]))
             expdur = datetime.datetime(1900,1,1,0,2,0)
             if (expdur-acctdur).total_seconds() < 13:
                 self.logi.appendMsg("PASS - the entry duration is less then 12 seconds less than the 2 minutes of stream as Expected")
             else:
                 self.logi.appendMsg("FAIL - the entry duration time is More than 13 seconds less then the stream of 2 minutes, the actual duration is: " + str(dur))
                 self.status = False
               
             self.playdriver.quit()
                
         if self.status == False:
             self.logi.reportTest('fail')
             assert False
              
         else:
             self.logi.reportTest('pass')
             assert True
      
    
    #################################################            
    '''
    @PASS_THROUGH__ENABLE_RECORDING_CREATE_STOPSTREAM_2MIN_test
    '''       
    ################################################
    def test_PassThrough_RecordingCretae_stopStream_2Min(self):
           
         self.status = True
         self.logi.initMsg('PASS THROUGH + ENABLE RECORDING- APPEND RECORD STOP STREAM 2 MINUTES test')
           
           
         self.status = self.Entryandstrem(self.passtrhroughId,2,0)  
         ''' read QR code for 5 minutes of play''' 
         self.logi.appendMsg("going to read QR code for 5 minutes of play")
         if self.status:
             self.QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
             self.QrCode.initVals()
             timeisfinish = False
              
             #while not time is up (5 minutes) continue to check the Qr codes on the stream
             while not timeisfinish:
                 rc = self.QrCode.placeCurrPrevScr()
                 time.sleep(1)
                 if rc:
                     rc = self.QrCode.checkProgress(1)
                     if not rc:
                         self.status = False 
                 if time.time()-self.startTime > 390: 
                     timeisfinish = True
                
             if self.status == True :
                 self.logi.appendMsg("PASS - Video played ok with no stops all the last 5 minutes")
             else:
                 self.logi.appendMsg("FAIL - Video did Not play ok all the last 5 minutes")
               
             newEntryId1 = self.entryStatusChanges(' 1')
               
             '''
             @WAIT_2_MINUTES and then stream again for 2 minutes
             '''
             time.sleep(120)
     
             self.logi.appendMsg("INFO - streaming again for 2 minutes, 2 more minutes of duration should be add to the entry id-" + newEntryId1)
              
             self.StreamFromFfmpeg(None,self.entry)
             while time.time()-self.startTime <119:
                 time.sleep(1)
                          
             os.system('killall ffmpeg')
             self.logi.appendMsg("INFO - stop streaming after 2 minutes")
              
             time.sleep(60)
             
             if not isinstance(newEntryId1, bool):
                  self.status = self.PlayRecordedEntry(newEntryId1)
               
             self.logi.appendMsg("INFO - going to check that the entry duration is 6.5 + 2 minutes")            
             dur = self.kaltplayer.getDuration(self.playdriver)
             
             acctdur = datetime.datetime(1900,1,1,0,int(dur.split(':')[0]),int(dur.split(':')[1]))
             expdur = datetime.datetime(1900,1,1,0,8,30)
             if (expdur-acctdur).total_seconds() < 24:
                 self.logi.appendMsg("PASS - the entry duration is less then 24 seconds less from the 8.5 total stream time, as Expected")
             else:
                 self.logi.appendMsg("FAIL - the entry duration time is More than 24 seconds less then the stream of 2 minutes, the actual duration is: " + str(dur))
                 self.status = False
             
             self.playdriver.quit()
              
         if self.status == False:
             self.logi.reportTest('fail')
             assert False
         else:
             self.logi.reportTest('pass')
             assert True
    
    
    
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    
    
    def teardown_class(self):
        print('tear down')
        self.testTeardownclass.exeTear()   
    
#pytest.main('test_Live.py -s')    
        
        
        