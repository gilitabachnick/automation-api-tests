'''
upload
set access Control
create player
Play '''

import os
import sys
import time

import pytest
from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
import ClienSession
import Config
import Entry
import reporter
import uiconf

import strclass
import QrcodeReader
import tearDownclass
#import myPyShark
import clsPlayerV2

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')

    #===========================================================================
    # Description :   UDrm test for play ready 
    #
    # test scenario:  create CENC UDRM profile,
    #                 Create player with uDRM plugin,
    #                 Create transcoding profile name Drmautotest,
    #                 get play ready access control default,
    #                 upload new entry with the transcoding profile just created,
    #                 get user KS,
    #                 play the DRM from a player page,
    #                 sniff player packates.
    #                 
    # verifications:  video play (QRcode)
    #                 manifest and license packets retrieve OK reply
    #===========================================================================
    
''' ****************** MUST ADD CHECK FOR DELIVERY PROFILE 891 EXISTENCE IF IT IS DELETE IT ****************'''


class TestClass:
    
    
    status = True
    
    
    # this function play the video sniff the ethernet and check for QR code displayed
    # selDriver - send 2 for chrom selenium web driver, 0 for firefox, 1 for IE
    def playandsniff(self, selDriver, loaclDriver=False):
        
         #play video 
        self.logi.appendMsg('play the video')
        
        #=======================================================================
        # self.logi.appendMsg('start sniffing with pyshark')
        # if selDriver==0:
        #     pcfileName = 'test.pcapng'
        # elif selDriver==1:
        #     pcfileName = 'test1.pcapng'
        # elif selDriver==2:
        #     pcfileName = 'test2.pcapng'
        #     
        # self.mpsh = myPyShark.mypyshark()
        # pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'QRtemp'))
        # pcapngFile = os.path.join(pth,pcfileName)
        # thread.start_new_thread(self.mpsh.listen,(60,pcapngFile))
        # 
        # #play video 
        # self.logi.appendMsg('play the video')
        # player = clsPlayerV2.playerV2("kaltura_player_1418811966")
        # driverdict = {0:'webdriver.Firefox()',
        #               1:'webdriver.Ie(r\'C:\Python27\webdrivers\IEDriverServer.exe\')'}
        # if selDriver==2:
        #     options = webdriver.ChromeOptions()
        #     options.add_experimental_option('excludeSwitches', ['disable-component-update'])
        #     options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
        #     self.driver = webdriver.Chrome(r'C:\Python27\webdrivers\chromedriver.exe',chrome_options=options)
        # else:
        #     self.driver = eval(driverdict[selDriver])
        # 
        # try:
        #     self.driver.get(self.baseUrl)
        # except:
        #     print 'url set to browser'
        #     
        # self.driver.maximize_window()
        # time.sleep(5)
        # # allow the pop up streaming
        # if selDriver==0:
        #     Webelement = self.driver.find_element_by_xpath('//body')
        #     Webelement.send_keys(Keys.ALT+'a')
        #     time.sleep(1)
        #     Webelement.send_keys(Keys.ALT+'r')
        #     time.sleep(2)
        # self.logi.appendMsg('playing video with QR code runs')
        # 
        # try:
        #     player.switchToPlayerIframe(self.driver)
        #     player.clickPlay(self.driver)
        #     
        # except Exception as exp:
        #     self.logi.appendMsg('got the following exception when trying to play the video-' +str(exp))
        #     self.logi.reportTest('fail')
        #     self.status = False
        #     
        # time.sleep(55)
        # 
        # ''' read QR code'''
        # if self.status:
        #     QrCode = QrcodeReader.QrCodeReader()
        #     firstQr = QrCode.saveScreenShot()
        #     time.sleep(1)
        #     firstQr = str(QrCode.retQrVal(firstQr))[28:32].replace(':','')
        #     if isinstance(firstQr, bool):
        #         self.status = False
        #         self.logi.appendMsg('Video is not played correctly - first QR code displayed')
        #     time.sleep(3)
        #     
        #     secQr = QrCode.saveScreenShot()
        #     time.sleep(1)
        #     secQr = str(QrCode.retQrVal(secQr))[28:32].replace(':','')
        #     if isinstance(secQr, bool):
        #         self.status = False
        #         self.logi.appendMsg('Video is not played correctly - second QR code was not displayed')
        #     
        #     try:
        #         if int(secQr) < int(firstQr):
        #             self.status = False
        #             self.logi.appendMsg('Video is not played correctly - took 2 QR code images one after the other from the video played, the first value is:' + firstQr + 'the second value should have been larger than the first and its value is:' +secQr)
        #         else:
        #             self.logi.appendMsg('Video played correctly')
        #     except:
        #         self.status = False
        #         self.logi.appendMsg('Video is not played correctly - at least one of the QR code images trying to take on vodeo play was not displayed')
        #        
        # return pcapngFile
        #=======================================================================
        
         #play video 
        self.logi.appendMsg('play the video')
        if selDriver==0:
            selDriver = "firefox" 
        elif selDriver==1:
            selDriver = "internet explorer"
        elif selDriver==2:
            selDriver = "chrome"
            
        #=======================================================================
        # self.capture = BrowserProxy.clsBrowserMobCapture(selDriver.strip()) 
        # self.myProxy = self.capture.createProxyClient()
        #=======================================================================
       
        player = clsPlayerV2.playerV2("kaltura_player_1418811966")       
        self.driver = player.testWebDriverLocalOrRemote (selDriver, loaclDriver)
        
        try:
            self.driver.get(self.baseUrl)
        except:
            print('url set to browser')
        ########################################################################################
        
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
        self.logi.appendMsg('playing video with QR code runs')
        
        try:
            player.switchToPlayerIframe(self.driver)
            player.clickPlay(self.driver)
            time.sleep(60)
        except Exception as exp:
            self.logi.appendMsg('got the following exception when trying to play the video-' + str(exp))
            self.logi.reportTest('fail')
            self.status = False
            
        
        ''' read QR code'''
        if self.status:
            QrCode = QrcodeReader.QrCodeReader(wbDriver=self.driver)
            firstQr = QrCode.saveScreenShot()
            time.sleep(1)
            firstQr = QrcodeReader.retQrVal(firstQr)
            if isinstance(firstQr, bool):
                self.status = False
                self.logi.appendMsg('FAIL- Video is not played correctly - first QR code displayed')
            time.sleep(3)
            
            secQr = QrCode.saveScreenShot()
            time.sleep(1)
            secQr = QrcodeReader.retQrVal(secQr)
            if isinstance(secQr, bool):
                self.status = False
                self.logi.appendMsg('FAIL- Video is not played correctly - second QR code was not displayed')
                
            try:
                if int(secQr) < int(firstQr):
                    self.status = False
                    self.logi.appendMsg('FAIL- Video is not played correctly - took 2 QR code images one after the other from the video played, the first value is:' + firstQr + 'the second value should have been larger than the first and its value is:' +secQr)
                else:
                    self.logi.appendMsg('Video played correctly')
            except:
                self.status = False
                self.logi.appendMsg('FAIL- Video is not played correctly - at least one of the QR code images trying to take on vodeo play was not displayed')
        
            ########################################################################################
            #===================================================================
            # self.capture.saveHar(myProxy.har)
            # pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'QRtemp'))
            # actualEvents = capture.createHttpComscoreDict(myProxy.har)
            #===================================================================
            ########################################################################################
        
        return self.status
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        pth                 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        inifile             = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        pth                 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.PublisherID    = inifile.RetIniVal('UDRM', 'PublisherID')
        self.ServerURL      = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret     = inifile.RetIniVal('UDRM', 'UserSecret') 
        self.FileName       = inifile.RetIniVal('Entry', 'UDrmfile')
        acontrolId          = inifile.RetIniVal('UDRM', 'accessControlID')
        transProfileID      = inifile.RetIniVal('UDRM', 'TranscodingProfileID') 
        self.FileName = os.path.join(pth,self.FileName)
        self.testTeardownclass = tearDownclass.teardownclass()
    
        self.logi = reporter.Reporter('UDrm test')
        self.logi.initMsg('UDrm setup')
        
        self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
        
        # Upload entry with the above transcoding profile
        self.logi.appendMsg('going to upload new entry with the transcoding profile id: ' + str(transProfileID))
        myentry = Entry.Entry(self.client,"UDrmCENCauto", "UDrm CENC Automation test", "UDrm tag", "Admintag", "adi category", 0, open(self.FileName,'rb+'),transProfileID, acontrolId)
        entry = myentry.AddNewEntryWithFile(600)
        if isinstance(entry,bool):
            self.logi.appendMsg('Entry was not uploaded after 5 minutes')
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
        elif isinstance(entry, str):
            self.logi.appendMsg('Entry got error when trying to upload it')
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
        else:
            self.logi.appendMsg('Finished upload file to new entry id :' + str(entry.id))
        
        self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(entry.id) + '\')')
        
        # Create  player with uDRM plugin 
        self.logi.appendMsg('going to add new player with uDRM plugin ')
        myplayer = uiconf.uiconf(self.client)  
        player = myplayer.addPlayer('multiDrm','prod')
        self.logi.appendMsg('new player was add, conf ID=' + str(player.id))
        if isinstance(player,bool):
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
            
        self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(player.id) + ')')
        
        # get user KS
        self.logi.appendMsg('getting user Ks')
        startSess = ClienSession.clientSession(self.PublisherID,self.ServerURL,inifile.RetIniVal('UDRM', 'UseruserSecret'))
        self.userKS = startSess.GetKs(0,'scenario_default:*')[2]
        self.logi.appendMsg('User Ks is:' + self.userKS)
        
        # build URL for player page
        self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>&ks=<KS>&env=production'      
        strcls = strclass.strclass(self.baseUrl)
        newParams = str(self.PublisherID) + ',' + str(player.id) + ',' + entry.id + ',' + self.userKS
        self.baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,<KS>,', newParams)
        self.logi.appendMsg('player page url is:' + self.baseUrl)
          
     #==========================================================================
     # TEST CENC WIDEVINE    
     #==========================================================================
    
    
    def test_UdrmCENCwidevine(self):
          self.status = True
          print('FROM ######## UdrmCENCwidevine')
          self.logi.initMsg('UDrm CENC widevine test')
          self.status = True  
           
         # play with chrome
          pcapngFile = self.playandsniff(2)
               
          # verify manifest and license packets retrieve ok as response
          retManifest = self.mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\" and http contains \".mpd\"')
          self.logi.appendMsg('looking for packet of manifest')
          if retManifest ==0:
              self.status = False
              self.logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
          else:
              retmanifResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
              if int(retmanifResponse.http.response_code)!=200:
                  if int(retmanifResponse.http.response_code)== 302:
                      self.logi.appendMsg('the manifest request was redirect to cdn')
                  else:
                      print('did not find packet of manifest response')
                      self.logi.appendMsg('did not get \"OK\" response for the Manifest packet')
                      self.status = False
                      self.logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
              else:
                  self.logi.appendMsg('the response should have been 200 and so it is') 
    
            
    
        #=======================================================================
        # retLicense = self.mpsh.retFromCaptureFile(pcapngFile,'http contains "/cenc/widevine/license"')
        # self.logi.appendMsg('looking for packet of license')
        # if retLicense ==0:
        #     self.status = False
        #     self.logi.appendMsg('looking for packet of License, did not found after 60 seconds of listening to network')
        # else:
        #     retLicResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retLicense.tcp.stream) + ' and http and frame.number > ' + str(retLicense.number))
        #     if int(retLicResponse.http.response_code)<>200:
        #         self.logi.appendMsg('did not get \"OK\" response for the license packet')
        #         self.status = False
        #         self.logi.appendMsg('the response should have been 200 and it is: ' + retLicResponse.http.response_code + ' - ' + retLicResponse.http.response_phrase) 
        #     else:
        #         self.logi.appendMsg('the response should have been 200 and so it is')
        #         
        #=======================================================================
       
         
    
          self.driver.quit()
          
          if self.status == False:
            self.logi.reportTest('fail')
            self.practitest.post(Practi_TestSet_ID, '1874','1')
            assert False
          else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '1874','0')
            assert True
           
           
          time.sleep(10)   
         
        
   
    #===========================================================================
    # TEST CENC PLAY READY ON THE FLY    
    #===========================================================================
     
    
    
    def test_udrmPlayReadyOnFly(self):
        self.status = True  
        print('FROM ######## udrmPlayReadyOnFly')
        self.logi.initMsg('UDrm CENC widevine test')
            
        # play with FF
        pcapngFile = self.playandsniff(0)   
                
        # verify manifest and license packets retrieve ok as response
        retManifest = self.mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\" and http contains \".ism\"')
        self.logi.appendMsg('looking for packet of manifest')
        if retManifest ==0:
            self.status = False
            self.logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
        else:
            retmanifResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
            if int(retmanifResponse.http.response_code)!=200:
                if int(retmanifResponse.http.response_code)== 302:
                    self.logi.appendMsg('the manifest request was redirect to cdn')
                else:
                    print('did not find packet of manifest response')
                    self.logi.appendMsg('did not get \"OK\" response for the Manifest packet')
                    self.status = False
                    self.logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
            else:
                self.logi.appendMsg('the response should have been 200 and so it is') 
    
               
         #=======================================================================
         # retLicense = retLicense = self.mpsh.retFromCaptureFile(pcapngFile,'http contains "/playready/license"')
         # self.logi.appendMsg('looking for packet of license')
         # if retLicense ==0:
         #     self.status = False
         #     self.logi.appendMsg('looking for packet of License, did not found after 60 seconds of listening to network')
         # else:
         #     retLicResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retLicense.tcp.stream) + ' and http and frame.number > ' + str(retLicense.number))
         #     if int(retLicResponse.http.response_code)<>200:
         #         self.logi.appendMsg('did not get \"OK\" response for the license packet')
         #         self.status = False
         #         self.logi.appendMsg('the response should have been 200 and it is: ' + retLicResponse.http.response_code + ' - ' + retLicResponse.http.response_phrase) 
         #     else:
         #         self.logi.appendMsg('the response should have been 200 and so it is')
         #=======================================================================
                 
        
        self.driver.quit()
          
        if self.status == False:
            self.logi.reportTest('fail')
            self.practitest.post(Practi_TestSet_ID, '2356','1')
            assert False 
        else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '2356','0')
            assert True
        
      
    #===========================================================================
    
    
        #=======================================================================
        # time.sleep(10)
        #=======================================================================
        
     #===========================================================================
    # TEST CENC PLAY READY    
    #===========================================================================    
    
    def test_udrmCENCPlayReady(self):
         self.status = True   
         print('FROM ######## udrmCENCPlayReady')
         self.logi.initMsg('UDrm CENC widevine test')
            
         # play with FF
         pcapngFile = self.playandsniff(1)   
                
         # verify manifest and license packets retrieve ok as response
         retManifest = self.mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\" and http contains \".mpd\"')
         self.logi.appendMsg('looking for packet of manifest')
         if retManifest ==0:
             self.status = False
             self.logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
         else:
             retmanifResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
             if int(retmanifResponse.http.response_code)!=200:
                 if int(retmanifResponse.http.response_code)== 302:
                     self.logi.appendMsg('the manifest request was redirect to cdn')
                 else:
                     print('did not find packet of manifest response')
                     self.logi.appendMsg('did not get \"OK\" response for the Manifest packet')
                     self.status = False
                     self.logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
             else:
                 self.logi.appendMsg('the response should have been 200 and so it is') 
                
         #=======================================================================
         # retLicense = self.mpsh.retFromCaptureFile(pcapngFile,'http contains "/cenc/playready/license"')
         # self.logi.appendMsg('looking for packet of license')
         # if retLicense ==0:
         #     self.status = False
         #     self.logi.appendMsg('looking for packet of License, did not found after 60 seconds of listening to network')
         # else:
         #     retLicResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retLicense.tcp.stream) + ' and http and frame.number > ' + str(retLicense.number))
         #     if int(retLicResponse.http.response_code)<>200:
         #         self.logi.appendMsg('did not get \"OK\" response for the license packet')
         #         self.status = False
         #         self.logi.appendMsg('the response should have been 200 and it is: ' + retLicResponse.http.response_code + ' - ' + retLicResponse.http.response_phrase) 
         #     else:
         #         self.logi.appendMsg('the response should have been 200 and so it is')
         #         
         #=======================================================================
         self.driver.quit()
         
         if self.status == False:
            self.logi.reportTest('fail')
            self.practitest.post(Practi_TestSet_ID, '2357','1')
            assert False
         else:
            self.logi.reportTest('pass')
            self.practitest.post(Practi_TestSet_ID, '2357','0')
            assert True
         
         time.sleep(10)      
    #===========================================================================
    
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        if self.status == True:
            print('Tear Down')
            self.testTeardownclass.exeTear()
            
            
        
  
        
    
        

#pytest.main('test_UDRM_Prod.py -s')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    