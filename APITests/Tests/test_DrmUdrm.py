#from pip._vendor.requests.packages.urllib3.util.connection import select
import _thread
import os
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
import ClienSession
import Config
import Entry
import reporter
import AdminSettings
import uiconf
import accessControl
import strclass
import Transcoding
#import myPyShark
import clsPlayerV2
import tearDownclass
import myPyShark
import QrcodeReader

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree


#py.test kaltest.py -m "ready"

class TestClass:
    
    @pytest.fixture(scope='module',params=[pytest.mark.t('testing')]) # ,pytest.mark.p('production')
    def initfix(self,request):
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if request.param=='testing':
            print('TESTING ENV')
            return Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        else:
            print('PRODUCTION ENV')
            return Config.ConfigFile(os.path.join(pth, 'ProdParams.ini')) 
    
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
   
    @pytest.mark.ready
    def test_DrmPlayReady(self,initfix):
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        inifile = initfix
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret =  inifile.RetIniVal('Environment', 'UserSecret') 
        self.FileName =  inifile.RetIniVal('Entry', 'DrmPlayReadfile')
        self.FileName = os.path.join(pth,self.FileName)
        testTeardownclass = tearDownclass.teardownclass()
        self.status = True
        
        logi = reporter.Reporter('Drm PlayReady test')
        logi.initMsg('DrmPlayReady test')
        logi.appendMsg('start create admin session for Drm profile')
            
        adminKmc = AdminSettings.AdminSettings()
        ExsitProfileId = adminKmc.drmprofileExsistByname('autotestDRMPlayReady')
        if ExsitProfileId!=0:
            print('DRM PRIFLE EXSIT')
            adminKmc.deleteDrmProfile(ExsitProfileId)
            time.sleep(3)
        logi.appendMsg('going to create DRM play ready profile')    
        drmProfile= adminKmc.createDrmProfile(self.PublisherID,'autotestDRMPlayReady')
        if isinstance(drmProfile,bool):
            logi.appendMsg('could not create DRM play ready profile')
            logi.reportTest('fail')
            assert False
            
        logi.appendMsg('DRM profile play ready created successfully for partner id:' + self.PublisherID + ' THE DRM PROFILE ID IS: ' +  str(drmProfile.id))
        testTeardownclass.addTearCommand(adminKmc,'deleteDrmProfile(' + str(drmProfile.id) + ')')
        time.sleep(3)    
        
        # update delivery profile for 891 and 831
        logi.appendMsg('update delivery profile for remove 891 if exist and set 831')
        adminKmc.updateDeliveryProfile(self.PublisherID,r'{"mpegdash":[831]}')
        time.sleep(2)
           
        logi.appendMsg('start create session for partenr: ' + self.PublisherID)
        mySess = ClienSession.clientSession(inifile.RetIniVal('Environment', 'PublisherID'),inifile.RetIniVal('Environment', 'ServerURL'),inifile.RetIniVal('Environment', 'UserSecret'))
        client = mySess.OpenSession()
        
        # Create player with uDRM plugin 
        myplayer = uiconf.uiconf(client)
        player = myplayer.addPlayer('multiDrm')
        logi.appendMsg('new player was add, conf ID=' + str(player.id))
        
        if isinstance(player,bool):
            logi.appendMsg('new player was not added')
            logi.reportTest('fail')
            testTeardownclass.exeTear()
            assert False
            
        testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(player.id) + ')')
        time.sleep(3)
        
        # Create transcoding profile name Drmautotest
        logi.appendMsg('Create transcoding profile name Drmautotest')
        Trans = Transcoding.Transcoding(client,'Drmautotest')
        transProfileId = Trans.getTranscodingProfileIDByName('Drmautotest')
        if transProfileId != None:
            print('profile exsit')
            Trans.deleteTranscodingProfile(transProfileId)
            time.sleep(3)
            
        profile = Trans.addTranscodingProfile(0, '2,3,4,5,6,7,201,221,241,251,261,271,281,291,301,331,341,351,361,311')
        if isinstance(profile,bool):
            logi.reportTest('fail')
            testTeardownclass.exeTear()
            assert False
        time.sleep(3)
            
        Trans.EditConversionProfileFlavors('2,3,4,5,6,7,201,221,271,281,291,301,311', profile.id) 
        Trans.EditConversionProfileFlavors('251',profile.id,'ready')
        logi.appendMsg('transcoding profile created with profile ID=' + str(profile.id))
        testTeardownclass.addTearCommand(Trans,'deleteTranscodingProfile(' + str(profile.id) + ')')
        time.sleep(3)
        
        # get play ready access control default
        acontrol = accessControl.accessControl(client)
        acontrolId = acontrol.getaccessControlIdBySysName('play_ready_default_' + self.PublisherID)
        logi.appendMsg('play ready access control ID is:' + str(acontrolId))
        
        # upload new entry with the transcoding profile just created 
        logi.appendMsg('going to upload new entry')
        myentry = Entry.Entry(client,"DrmPlayReadyAuto", "Drm Play Ready Automatiion test", "Drm tag", "Admintag", "adi category", 0, open(self.FileName,'rb+'), profile.id, acontrolId)
        entry = myentry.AddNewEntryWithFile(300)
        if isinstance(entry,bool):
            logi.appendMsg('Entry was not uploaded after 5 minutes')
            logi.reportTest('fail')
            testTeardownclass.exeTear()
            assert False
        else:
            logi.appendMsg('Finished upload file to new entry id :' + entry.id)
        
        testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(entry.id) + '\')')
        
        # get user KS
        logi.appendMsg('getting user Ks')
        startSess = ClienSession.clientSession(inifile.RetIniVal('Environment', 'PublisherID'),inifile.RetIniVal('Environment', 'ServerURL'),inifile.RetIniVal('Environment', 'UseruserSecret'))
        userKS = startSess.GetKs(0,'scenario_default:*')[2]
        logi.appendMsg('User Ks is:' + userKS)
        
        # build URL for player page
        baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>&ks=<KS>%3D%3D&drmServerURL=http%3A%2F%2F192.168.193.48%2Fplayready%2Frightsmanager.asmx'      
        strcls = strclass.strclass(baseUrl)
        newParams = str(self.PublisherID) + ',' + str(player.id) + ',' + entry.id + ',' + userKS
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
            self.status = False
            assert False
        
        ''' read QR code'''
        QrCode = QrcodeReader.QrCodeReader()
        firstQr = QrCode.saveScreenShot()
        time.sleep(1)
        firstQr = QrCode.retQrVal(firstQr)
        if isinstance(firstQr, bool):
            self.status = False
            logi.appendMsg('Video is not played correctly - first QR code displayed')
        time.sleep(3)
        
        secQr = QrCode.saveScreenShot()
        time.sleep(1)
        secQr = QrCode.retQrVal(secQr)
        if isinstance(secQr, bool):
            self.status = False
            logi.appendMsg('Video is not played correctly - second QR code was not displayed')
            
        if int(secQr) < int(firstQr):
            self.status = False
            logi.appendMsg('Video is not played correctly - took 2 QR code images one after the other from the video played, the first value is:' + firstQr + 'the second value should have been larger than the first and its value is:' +secQr)
        else:
            logi.appendMsg('Video played correctly')
            
        # verify manifest and license packets retrieve ok as response
        retManifest = mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\"')
        logi.appendMsg('looking for packet of manifest')
        if retManifest ==0:
            self.status = False
            logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
        else:
            retmanifResponse = mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
            if int(retmanifResponse.http.response_code)!=200:
                if int(retmanifResponse.http.response_code)== 302:
                    logi.appendMsg('the manifest request was redirect to cdn')
                else:
                    print('did not find packet of manifest response')
                    logi.appendMsg('did not get \"OK\" response for the Manifest packet')
                    self.status = False
                    logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
            else:
                logi.appendMsg('the response should have been 200 and so it is') 
            
        retLicense = mpsh.retFromCaptureFile(pcapngFile,'http contains \"http://192.168.193.48/playready/rightsmanager.asmx\"')
        logi.appendMsg('looking for packet of license')
        if retLicense ==0:
            self.status = False
            logi.appendMsg('looking for packet of License, did not found after 60 seconds of listening to network')
        else:
            retLicResponse = mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retLicense.tcp.stream) + ' and http and frame.number > ' + str(retLicense.number))
            if int(retLicResponse.http.response_code)!=200:
                logi.appendMsg('did not get \"OK\" response for the license packet')
                self.status = False
                logi.appendMsg('the response should have been 200 and it is: ' + retLicResponse.http.response_code + ' - ' + retLicResponse.http.response_phrase) 
            else:
                logi.appendMsg('the response should have been 200 and so it is')
         
        
        driver.close()
             
        if self.status:
            #testTeardownclass.exeTear()
            assert True
        else:
            logi.reportTest('fail')
            assert False
            
            
   