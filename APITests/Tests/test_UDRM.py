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
import AdminSettings
import uiconf

import accessControl
import strclass
import QrcodeReader
import Transcoding
import tearDownclass

import clsPlayerV2
import Practitest
#import BrowserProxy



try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree

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
    
''' ****************** IF HTML% VERSION NOT APPEAR MUST UPDATE STUDIO AND KMC AGAIN ****************'''


class TestClass: 
    
    
    status = True
    GRID_HOST       ='http://52.17.242.149:4444/wd/hub'
    BROWSER_IE      = "internet explorer"
    BROWSER_CHROME  = "chrome"
    BROWSER_FIREFOX = "firefox"
    BROWSER_SAFARI  = "Safari" 
     
    
     
    # this function play the video sniff the ethernet and check for QR code displayed
    # selDriver - send 2 for chrom selenium web driver, 0 for firefox, 1 for IE
    def playandsniff(self, selDriver, loaclDriver=False):
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
        #=======================================================================
        
        #play video 
        self.logi.appendMsg('play the video')
        
        ''' RUN PLAYER LOCALLY '''
        #=======================================================================
        # if loaclDriver == True:
        #     player = clsPlayerV2.playerV2("kaltura_player_1418811966")
        #     driverdict = {0:'webdriver.Firefox()',
        #                   1:'webdriver.Ie(r\'C:\Python27\webdrivers\IEDriverServer.exe\')'}
        #  
        #     if selDriver==2:
        #         options = webdriver.ChromeOptions()
        #         options.add_experimental_option('excludeSwitches', ['disable-component-update'])
        #         options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
        #         self.driver = webdriver.Chrome(r'C:\Python27\webdrivers\chromedriver.exe',chrome_options=options)
        #     else:
        #         self.driver = eval(driverdict[selDriver])
        #      
        #     try:
        #         self.driver.get(self.baseUrl)
        #     except:
        #         print 'url set to browser'
        #         
        #     ''' RUN PLAYER REMOTELY'''
        # else:
        #     if selDriver == 0:
        #         browzer= 'firefox'
        #     elif selDriver == 1:
        #         browzer= 'ie'
        #     else:
        #         browzer= 'chrom'
        #         
        #             
        #     self.driver = webdriver.Remote(command_executor=self.GRID_HOST, desired_capabilities={'browserName': browzer,'requireWindowFocus':True})
        #=======================================================================
        
        ########################################################################################
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
        self.driver = player.testWebDriverLocalOrRemote (selDriver)
        
        try:
            self.driver.get(self.baseUrl)
        except:
            self.logi.appendMsg('could not get to the player base url- might be connection problem')
            self.logi.reportTest('fail')
            
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
        
        player.switchToPlayerIframe(self.driver)
        time.sleep(5)
        try:
            player.clickPlay(self.driver)
            time.sleep(30)
        except Exception as exp:
            self.logi.appendMsg('got the following exception when trying to play the video-' + str(exp))
            self.logi.reportTest('fail')
            self.status = False
            
        
        ''' read QR code'''
        if self.status:
            QrCode = QrcodeReader.QrCodeReader('liveQrCodes',self.driver, self.logi)
            firstQr = QrCode.saveScreenShot()
            time.sleep(1)
            firstQr = QrcodeReader.retQrVal(firstQr)
            if isinstance(firstQr, bool):
                self.status = False
                self.logi.appendMsg('FAIL-Video is not played correctly - first QR code displayed')
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
        
        self.practitest = Practitest.practitest()
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        print('TESTING ENV')
        inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        #inifile = initfix
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret =  inifile.RetIniVal('Environment', 'UserSecret') 
        self.FileName =  inifile.RetIniVal('Entry', 'UDrmfile')
        self.FileName = os.path.join(pth,self.FileName)
        self.testTeardownclass = tearDownclass.teardownclass()
        
        self.logi = reporter.Reporter('UDRM')
        self.logi.initMsg('UDrm setup')
        self.logi.appendMsg('start create admin session for UDrm profile')
        
        # create drm profile CENC and playready for FF
        adminKmc = AdminSettings.AdminSettings()
        ExsitProfileId = adminKmc.drmprofileExsistByname('autotestUDrmCENC')
        if ExsitProfileId==0:
            self.logi.appendMsg('going to create CENC DRM profile')    
            drmProfile= adminKmc.createDrmProfile(self.PublisherID,'autotestUDrmCENC',2)
            if isinstance(drmProfile,bool):
                self.logi.reportTest('fail')
                assert False
        
        time.sleep(2)
        
        ExsitProfileId = adminKmc.drmprofileExsistByname('autotestDRMPlayReady')
        if ExsitProfileId==0:
            self.logi.appendMsg('going to create DRM play ready profile')    
            drmPRProfile= adminKmc.createDrmProfile(self.PublisherID,'autotestDRMPlayReady')
            if isinstance(drmPRProfile,bool):
                self.logi.reportTest('fail')
                assert False
            else:
                self.logi.appendMsg('DRM profile CENC created successfully for partner id:' + self.PublisherID + ' the profile ID is: ' + str(drmProfile.id))
            
            time.sleep(2)
        #self.testTeardownclass.addTearCommand(adminKmc,'deleteDrmProfile(' + str(drmProfile.id) + ')')
        
        
        # update delivery profile for 891 and 831
        self.logi.appendMsg('update delivery profile for 891 and 831')
        adminKmc.updateDeliveryProfile(self.PublisherID)
        time.sleep(2)
        
        # create drm policy and get its ID for debug_msl150_vmguid_self.PublisherID 
        self.logi.appendMsg('create drm policy and get its ID for debug_msl150_vmguid_' + str(self.PublisherID))
        udrmPolicyID = ''
        DrmPolicies = adminKmc.getDRMpolicy(self.PublisherID,1)
        for ind in range(DrmPolicies.totalCount):
            if str(DrmPolicies.objects[ind].name) == 'debug_msl150_vmguid_'+ str(self.PublisherID):
                res = adminKmc.deleteDrmPolicy(DrmPolicies.objects[ind].id)
                break
        
        # retrieve udrm policy Id
        udrmPolicyID = adminKmc.drmPolicy(self.PublisherID).id
        self.logi.appendMsg('drm policy ID=' + str(udrmPolicyID))
        self.testTeardownclass.addTearCommand(adminKmc,'deleteDrmPolicy('+str(udrmPolicyID) + ')')
        time.sleep(2)
        
        # retrieve play ready rules id's
        logstr = ''
        playreadyPolicies = adminKmc.getDRMpolicy(self.PublisherID)
        for ind in range(playreadyPolicies.totalCount):
            key = str(playreadyPolicies.objects[ind].name).split('_')[0]
            if ind==0:
                dictPlayreadyPolicyIds = {key : playreadyPolicies.objects[ind].id}
            else:
                dictPlayreadyPolicyIds[key]= playreadyPolicies.objects[ind].id  
            
            if ind== playreadyPolicies.totalCount:
                logstr =  logstr + key + '=' + str(playreadyPolicies.objects[ind].id)
            else:
                logstr =  logstr + key + '=' + str(playreadyPolicies.objects[ind].id) + ', ' 
        
        time.sleep(2)        
      
        # create access control that supports on the fly encryption and DRM flavors only
        self.logi.appendMsg('Going to create access control that supports on the fly encryption and DRM flavors only')
        self.logi.appendMsg('Access control parameters: name=UdrmaccessCenc, System Name=UdrmaccessCencSys, desc=UdrmaccessCencSys, udrmPolicyID=' + str(udrmPolicyID) +', layreadyPolicyIds=[' + logstr +'], IsDefault =NO') 
        self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
        
        self.logi.appendMsg('going to create UDrm access Control profile')             
        DrmaccessControl = accessControl.accessControl(self.client)
        accsControl = DrmaccessControl.CreatAccessUDRMprofile('UdrmaccessCenc', 'UdrmaccessCencSys', 'UdrmaccessCencDesc', udrmPolicyID, dictPlayreadyPolicyIds,'831,891', accIsDefault=0)
        time.sleep(2)
        if isinstance(accsControl,bool):
            self.logi.appendMsg('got an exception while trying to create UDrm access Control profile, stop running this test')
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
        elif isinstance(accsControl,str):
            print(accsControl)
            accsControl = DrmaccessControl.getaccessControlIdBySysName('UdrmaccessCencSys')
            acontrolId = accsControl
        else:
            acontrolId = accsControl.id
            
        self.testTeardownclass.addTearCommand(DrmaccessControl,'deleteAccessControlProfile(' +str(acontrolId) + ')') 
        self.logi.appendMsg('Create access control profile successfully')
               
        # Create transcoding profile name Drmautotest
        self.logi.appendMsg('Create transcoding profile name UDrmCENCautotest')
        Trans = Transcoding.Transcoding(self.client,'UDrmCENCautotest')
        transProfileId = Trans.getTranscodingProfileIDByName('UDrmCENCautotest')
        if transProfileId != None:
            print('profile exist deleting it and recreate')
            Trans.deleteTranscodingProfile(transProfileId)
            time.sleep(3)
            
        profile = Trans.addTranscodingProfile(0, '2,3,4,5,6,7,561')
        if isinstance(profile,bool):
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
       
        time.sleep(2)
        
        Trans.EditConversionProfileFlavors('561',profile.id,'ready')   
        self.logi.appendMsg('transcoding profile created with profile ID=' + str(profile.id)) 
        self.testTeardownclass.addTearCommand(Trans,'deleteTranscodingProfile('+str(profile.id) + ')')
        time.sleep(3)
            
        # Upload entry with the above transcoding profile
        self.logi.appendMsg('going to upload new entry with the above transcoding profile')
        myentry = Entry.Entry(self.client,"UDrmCENCauto", "UDrm CENC Automation test", "UDrm tag", "Admintag", None, 0, open(self.FileName,'rb+'), profile.id, acontrolId)
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
            self.logi.appendMsg('Finished upload file to new entry id :' + entry.id)
        
        self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(entry.id) + '\')')
        
        # Create  player with uDRM plugin 
        self.logi.appendMsg('going to add 2 new players, one with uDRM plugin ')
        myplayer = uiconf.uiconf(self.client)  
        self.player = myplayer.addPlayer('multiDrm')
        self.logi.appendMsg('new player was add, conf ID=' + str(self.player.id))
        if isinstance(self.player,bool):
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
           
        self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')
        
        # get user KS
        self.logi.appendMsg('getting user Ks')
        startSess = ClienSession.clientSession(self.PublisherID,self.ServerURL,inifile.RetIniVal('Environment', 'UseruserSecret'))
        self.userKS = startSess.GetKs(0,'scenario_default:*')[2]
        self.logi.appendMsg('User Ks is:' + self.userKS)
        
        # build URL for player page
        self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>&ks=<KS>'      
        strcls = strclass.strclass(self.baseUrl)
        newParams = str(self.PublisherID) + ',' + str(self.player.id) + ',' + entry.id + ',' + self.userKS
        self.baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,<KS>,', newParams)
        self.logi.appendMsg('player page url is:' + self.baseUrl)
        
        
          
    # TEST CENC WIDEVINE    
    def test_UdrmCENCwidevine(self):
         
        print('FROM ######## UdrmCENCwidevine')
        self.logi.initMsg('UDrm CENC widevine test')
         
        self.status = self.playandsniff(2)
        #self.status = self.playandsniff(2)
         
        #=======================================================================
        # # play with chrome
        # pcapngFile = self.playandsniff(2)
        #     
        # # verify manifest and license packets retrieve ok as response
        # retManifest = self.mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\" and http contains \".mpd\"')
        # self.logi.appendMsg('looking for packet of manifest')
        # if retManifest ==0:
         
        #     self.status = False
        #     self.logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
        # else:
        #     retmanifResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
        #     if int(retmanifResponse.http.response_code)<>200:
        #         if int(retmanifResponse.http.response_code)== 302:
        #             self.logi.appendMsg('the manifest request was redirect to cdn')
        #         else:
        #             print 'did not find packet of manifest response'
        #             self.logi.appendMsg('did not get \"OK\" response for the Manifest packet')
        #             self.status = False
        #             self.logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
        #     else:
        #         self.logi.appendMsg('the response should have been 200 and so it is') 
        #     
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
         
        self.driver.close()
         
         
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
    # '''TEST CENC PLAY READY ON THE FLY '''    
    #  
    # def test_udrmPlayReadyOnFly(self):
    #        
    #     print 'FROM ######## udrmPlayReadyOnFly'
    #     self.logi.initMsg('UDrm CENC widevine test')
    #     self.status = self.playandsniff(0,True)  
    #      
    #      
    #     #=======================================================================
    #     # # play with FF
    #     # pcapngFile = self.playandsniff(0)   
    #     #       
    #     # # verify manifest and license packets retrieve ok as response
    #     # retManifest = self.mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\" and http contains \".ism\"')
    #     # self.logi.appendMsg('looking for packet of manifest')
    #     # if retManifest ==0:
    #     #     self.status = False
    #     #     self.logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
    #     # else:
    #     #     retmanifResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
    #     #     if int(retmanifResponse.http.response_code)<>200:
    #     #         if int(retmanifResponse.http.response_code)== 302:
    #     #             self.logi.appendMsg('the manifest request was redirect to cdn')
    #     #         else:
    #     #             print 'did not find packet of manifest response'
    #     #             self.logi.appendMsg('did not get \"OK\" response for the Manifest packet')
    #     #             self.status = False
    #     #             self.logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
    #     #     else:
    #     #         self.logi.appendMsg('the response should have been 200 and so it is') 
    #     #       
    #     # retLicense = retLicense = self.mpsh.retFromCaptureFile(pcapngFile,'http contains "/playready/license"')
    #     # self.logi.appendMsg('looking for packet of license')
    #     # if retLicense ==0:
    #     #     self.status = False
    #     #     self.logi.appendMsg('looking for packet of License, did not found after 60 seconds of listening to network')
    #     # else:
    #     #     retLicResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retLicense.tcp.stream) + ' and http and frame.number > ' + str(retLicense.number))
    #     #     if int(retLicResponse.http.response_code)<>200:
    #     #         self.logi.appendMsg('did not get \"OK\" response for the license packet')
    #     #         self.status = False
    #     #         self.logi.appendMsg('the response should have been 200 and it is: ' + retLicResponse.http.response_code + ' - ' + retLicResponse.http.response_phrase) 
    #     #     else:
    #     #         self.logi.appendMsg('the response should have been 200 and so it is')
    #     #         
    #      
    #     self.driver.close()
    #       
    #      
    #     if self.status == False:
    #         self.logi.reportTest('fail')
    #         self.practitest.post(Practi_TestSet_ID, '2356','1')
    #         assert False 
    #     else:
    #         self.logi.reportTest('pass')
    #         self.practitest.post(Practi_TestSet_ID, '2356','0')
    #         assert True
    #      
    #      
    #     time.sleep(10) 
    #===========================================================================
        
    #===========================================================================
    # TEST CENC PLAY READY    
    #===========================================================================    
    def test_udrmCENCPlayReady(self):
           
        print('FROM ######## udrmCENCPlayReady')
        self.logi.initMsg('UDrm CENC widevine test')
        self.status = self.playandsniff(1)  
        
        #=======================================================================
        # # play with FF
        # pcapngFile = self.playandsniff(1)   
        #        
        # # verify manifest and license packets retrieve ok as response
        # retManifest = self.mpsh.retFromCaptureFile(pcapngFile,'http contains \"playManifest\" and http contains \".mpd\"')
        # self.logi.appendMsg('looking for packet of manifest')
        # if retManifest ==0:
        #     self.status = False
        #     self.logi.appendMsg('looking for packet of manifest, did not found after 60 seconds of listening to network')
        # else:
        #     retmanifResponse = self.mpsh.retFromCaptureFile(pcapngFile,'tcp.stream eq ' +  str(retManifest.tcp.stream) + ' and http and frame.number > ' + str(retManifest.number))
        #     if int(retmanifResponse.http.response_code)<>200:
        #         if int(retmanifResponse.http.response_code)== 302:
        #             self.logi.appendMsg('the manifest request was redirect to cdn')
        #         else:
        #             print 'did not find packet of manifest response'
        #             self.logi.appendMsg('did not get \"OK\" response for the Manifest packet')
        #             self.status = False
        #             self.logi.appendMsg('the response should have been 200 and it is:' + retmanifResponse.http.response_code + ' - ' + retmanifResponse.http.response_phrase)
        #     else:
        #         self.logi.appendMsg('the response should have been 200 and so it is') 
        #        
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
        self.driver.close()
        
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
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        if self.status == True:
            print('tear down')
            #self.testTeardownclass.exeTear()
            
            
            
            
            
    #===============================================================================
    #             
    pytest.main(['test_UDRM.py','-s'])
    #===============================================================================