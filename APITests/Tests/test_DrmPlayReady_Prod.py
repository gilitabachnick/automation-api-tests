#from pip._vendor.requests.packages.urllib3.util.connection import select
import _thread
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
import ClienSession
import Config
import Entry
import reporter
import uiconf
import strclass
#import myPyShark
import clsPlayerV2
import tearDownclass
import myPyShark
import QrcodeReader

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')

#py.test kaltest.py -m "ready"

class TestClass:
    
    #===========================================================================
    # Description :   Drm test for play ready 
    #
    # test scenario:  create DRM profile,
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
   
   
    def test_DrmPlayReady(self):
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        inifile             = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        PublisherID         = inifile.RetIniVal('DRM', 'PublisherID')
        ServerURL           = inifile.RetIniVal('Environment', 'ServerURL')
        UserSecret          = inifile.RetIniVal('DRM', 'UserSecret') 
        pth                 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        FileName            = inifile.RetIniVal('Entry', 'DrmPlayReadfile')
        transProfileID      = inifile.RetIniVal('DRM', 'PlayReadyTranscodingProfileID')
        acontrolId          = inifile.RetIniVal('DRM', 'PlayReadyaccessControlID')
        FileName            = os.path.join(pth, FileName)
        testTeardownclass   = tearDownclass.teardownclass()
        status = True
        
        logi = reporter.Reporter('Drm PlayReady test')
        logi.initMsg('DrmPlayReady test')
        logi.appendMsg('start create session for partenr: ' + PublisherID)
        
        mySess = ClienSession.clientSession(PublisherID,ServerURL,UserSecret)
        client = mySess.OpenSession()
        time.sleep(2)
        
        # Upload entry with the above transcoding profile
        logi.appendMsg('going to upload new entry with the transcoding profile id: ' + str(transProfileID))
        myentry = Entry.Entry( client,"DrmPlayReadyAuto", "Drm Play Ready Automatiion test", "Drm tag", "Admintag", "adi category", 0, open( FileName,'rb+'),transProfileID, acontrolId)
        entry = myentry.AddNewEntryWithFile(600)
        if isinstance(entry,bool):
            logi.appendMsg('Entry was not uploaded after 5 minutes')
            logi.reportTest('fail')
            assert False
        elif isinstance(entry, str):
            logi.appendMsg('Entry got error when trying to upload it')
            logi.reportTest('fail')
            assert False
        else:
            logi.appendMsg('Finished upload file to new entry id :' + str(entry.id))
        
        testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(entry.id) + '\')')
        
        # Create  player with uDRM plugin 
        logi.appendMsg('going to add new player with DRM plugin ')
        myplayer = uiconf.uiconf( client)  
        player = myplayer.addPlayer('multiDrm','prod')
        logi.appendMsg('new player was add, conf ID=' + str(player.id))
        if isinstance(player,bool):
            logi.reportTest('fail')
            testTeardownclass.exeTear()
            assert False
            
        testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(player.id) + ')')
        
        # get user KS
        logi.appendMsg('getting user Ks')
        startSess = ClienSession.clientSession( PublisherID, ServerURL,inifile.RetIniVal('DRM', 'UseruserSecret'))
        userKS = startSess.GetKs(0,'scenario_default:*')[2]
        logi.appendMsg('User Ks is:' + userKS)
        
        # build URL for player page
        baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>&ks=<KS>%3D%3D&drmServerURL=http%3A%2F%2Fplayreadylicense.kaltura.com%2Frightsmanager.asmx&env=production'      
        strcls = strclass.strclass(baseUrl)
        newParams = str(PublisherID) + ',' + str(player.id) + ',' + entry.id + ',' + userKS
        baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,<KS>,', newParams)
        logi.appendMsg('player page url is:' + baseUrl)
        
        # start pyshark on different thread
        logi.appendMsg('start sniffing with pyshark')
        mpsh = myPyShark.mypyshark()
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'QRtemp'))
        pcapngFile = os.path.join(pth,'test.pcapng')
        _thread.start_new_thread(mpsh.listen,(80,pcapngFile))
        
        #play video 
        logi.appendMsg('play the video')
        player = clsPlayerV2.playerV2("kaltura_player_1418811966")
        driver = webdriver.Firefox()
        driver.get(baseUrl)
        driver.maximize_window()
        time.sleep(5)
        
        # allow the pop up streaming
        Webelement = driver.find_element_by_xpath('//body')
        Webelement.send_keys(Keys.ALT+'a')
        time.sleep(1)
        Webelement.send_keys(Keys.ALT+'r')
        time.sleep(2)
        logi.appendMsg('playing video with QR code runs')
        testTeardownclass.addTearCommand(driver,'close()')
        try:
            player.switchToPlayerIframe(driver)
            player.clickPlay(driver)
            time.sleep(30)
        except Exception as exp:
            logi.appendMsg('got the following exception when trying to play the video-' + str(exp))
            logi.reportTest('fail')
            status = False
            assert False
        
        ''' read QR code'''
        QrCode = QrcodeReader.QrCodeReader()
        firstQr = QrCode.saveScreenShot()
        time.sleep(1)
        firstQr = QrCode.retQrVal(firstQr)
        if isinstance(firstQr, bool):
            status = False
            logi.appendMsg('Video is not played correctly - first QR code displayed')
        time.sleep(3)
        
        secQr = QrCode.saveScreenShot()
        time.sleep(1)
        secQr = QrCode.retQrVal(secQr)
        if isinstance(secQr, bool):
            status = False
            logi.appendMsg('Video is not played correctly - second QR code was not displayed')
            
        if int(secQr) < int(firstQr):
            status = False
            logi.appendMsg('Video is not played correctly - took 2 QR code images one after the other from the video played, the first value is:' + firstQr + 'the second value should have been larger than the first and its value is:' +secQr)
        else:
            logi.appendMsg('Video played correctly')
            
        # verify manifest and license packets retrieve ok as response
        retManifest = mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\"')
        logi.appendMsg('looking for packet of manifest')
        if retManifest ==0:
            status = False
            logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
        else:
            retmanifResponse = mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
            if int(retmanifResponse.http.response_code)!=200:
                if int(retmanifResponse.http.response_code)== 302:
                    logi.appendMsg('the manifest request was redirect to cdn')
                else:
                    print('did not find packet of manifest response')
                    logi.appendMsg('did not get \"OK\" response for the Manifest packet')
                    status = False
                    logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
            else:
                logi.appendMsg('the response should have been 200 and so it is') 
            
        retLicense = mpsh.retFromCaptureFile(pcapngFile,'ip.dst == 192.168.193.48 and http contains "rightsmanager.asmx"')
        logi.appendMsg('looking for packet of license')
        if retLicense ==0:
            status = False
            logi.appendMsg('looking for packet of License, did not found after 60 seconds of listening to network')
        else:
            retLicResponse = mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retLicense.tcp.stream) + ' and http and frame.number > ' + str(retLicense.number))
            if int(retLicResponse.http.response_code)!=200:
                logi.appendMsg('did not get \"OK\" response for the license packet')
                status = False
                logi.appendMsg('the response should have been 200 and it is: ' + retLicResponse.http.response_code + ' - ' + retLicResponse.http.response_phrase) 
            else:
                logi.appendMsg('the response should have been 200 and so it is')
         
        
             
        if status:
            #testTeardownclass.exeTear()
            assert True
        else:
            
            logi.reportTest('fail')
            assert False 
        
        
        
        
        
    