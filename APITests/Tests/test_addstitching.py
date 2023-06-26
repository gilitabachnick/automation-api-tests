import _thread
import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#import BrowserProxy
import ClienSession
import reporter
import Config
import tearDownclass
import Practitest
import Entry
import clsPlayerV2
import strclass
import QrcodeReader
import addStitching
import Email
import socket


# TEST PARAMETERS
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
#TestRunTime = int(os.getenv('TestRunTime'))
PartnerID = os.getenv('PartnerID')
UserSecret = os.getenv('UserSecret')
EntryID = os.getenv('EntryID')
UIconfId = os.getenv('UIconfId')
primaryBroadcastingUrl = os.getenv('primaryBroadcastingUrl')



#===============================================================================
# PartnerID = 5012
# UserSecret = ''
# EntryID = '0_x9530yoh'
# UIconfId = 15197770
# primaryBroadcastingUrl = 'jj'
# TestRunTime = 6
#===============================================================================
    
 
#===========================================================================
# Description :   add stitching 
#
# test scenario:  upload live entry
#                 stream the entry
#                 insert adds queue points,
#                 verify adds played correctly,
#                 
#                 
# verifications:  adds play (QRcode)
#                 
#===========================================================================

''' ----- CONSTANTS ------- '''
FFMPEGPATH =  '/home/ubuntu/ffmpeg'   
DEFAULT_PARTNER = 5012
DEFAULT_SECRET = 'fd************'
DEFAULT_ENTRY = '0_x9530yoh'
DEFAULT_UICONF = 15197770
DEFAULT_PRIMARYBROADCAST = 'rtmp://il-wowza-centos-01.dev.kaltura.com:1935/kLive/?p=5012&e=0_x9530yoh&i=0&t=8f3c2f81'

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        ''' Take the default parameters values from ini file for both testing and prod env '''
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
        else:
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
        
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.primaryBroadcastingUrl = primaryBroadcastingUrl
        if self.primaryBroadcastingUrl == DEFAULT_PRIMARYBROADCAST:
           self.primaryBroadcastingUrl = inifile.RetIniVal('AddStitching', 'primaryBrodcast') 
        self.PublisherID = int(PartnerID)
        if self.PublisherID == DEFAULT_PARTNER:
            self.PublisherID = inifile.RetIniVal('AddStitching', 'PublisherID')
        self.UserSecret = UserSecret 
        if self.UserSecret == DEFAULT_SECRET:
            self.UserSecret = inifile.RetIniVal('AddStitching', 'UserSecret')
        self.EntryID = EntryID
        if self.EntryID == DEFAULT_ENTRY:
            self.EntryID = inifile.RetIniVal('AddStitching', 'EntryID')
        self.UIconfId =int(UIconfId)
        if self.UIconfId == DEFAULT_UICONF:
            self.UIconfId = inifile.RetIniVal('AddStitching', 'UIconfId')
            
        self.testTeardownclass = tearDownclass.teardownclass()
        self.practitest = Practitest.practitest()
        self.logi = reporter.Reporter('AddStitching')
        self.logi.initMsg('Live setup')
                 
        # create client session
        self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
        
               
    def StreamFromFfmpeg(self, primaryBroadcastingUrl):
        filePth = '/home/ubuntu/MediaUpload/1_bedzjiif_1_irvibj5b_1.mp4'
        comand = FFMPEGPATH +' -re -i ' + filePth + ' -c:v copy -c:a copy -f flv  -rtmp_live 1 "' + primaryBroadcastingUrl + '/' + self.EntryID + '_1" > /dev/null 2>&1 &'
        print(comand)
        _thread.start_new_thread(os.system,(comand,))
        self.testTeardownclass.addTearCommand(os,'system(\'killall ffmpeg\')')
    
    def Entryandstrem(self):
                
        ''' GET ENTRY PRIMARY BROADCUST SERVER '''
        entryobj=Entry.Entry(self.client, None, None, None, None, None, None)
        self.entry = entryobj.getEntry(self.EntryID)
        #self.primaryBroadcastingUrl = self.entry.primaryBroadcastingUrl
                        
        ''' START STREAMING FROM FFMPEG '''  
        self.StreamFromFfmpeg(self.primaryBroadcastingUrl)
                
        # build URL for player page
        self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>'
        if isProd:
            self.baseUrl = self.baseUrl + '&env=production'   
               
        strcls = strclass.strclass(self.baseUrl)
        newParams = str(self.PublisherID) + ',' + str(self.UIconfId) + ',' + self.EntryID 
        self.baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,', newParams)
        self.logi.appendMsg('player page url is:' + self.baseUrl)
        
        '''PLAY THE STREAMED VIDEO '''
        selDriver = "chrome"
        time.sleep(90)
             
        self.player = clsPlayerV2.playerV2("kaltura_player_1418811966") 
        self.driver = self.player.testWebDriverLocalOrRemote (selDriver)
        
        try:
            print((self.baseUrl))
            self.driver.get(self.baseUrl)
        except:
            self.logi.appendMsg('could not get to the player base url- might be connection problem')
            self.logi.reportTest('fail')
            return False
       
        timeisfinish = False
        timer = 0
        self.player.switchToPlayerIframe(self.driver)
        
        while not timeisfinish:        
            try:
                time.sleep(1)
                timer = timer + 1
                if timer == 300:  # THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE
                    timeisfinish = True
                    self.logi.appendMsg('THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE')
                    self.logi.reportTest('fail')
                    assert False
                    
                self.player.clickPlay(self.driver)
                print(' play clicked ok')
                timeisfinish = True
            
            except Exception as exp:
                print('no play')
                return False
            
        # wait till live is actually played after press the play button
        self.logi.appendMsg('video with QR code is playing')
        time.sleep(20)
        return True
    
    
    def test_longStream(self):
        
        print((socket.gethostname()))
        self.logi.initMsg('ADD STITCHING LONG test')
        self.status = self.Entryandstrem() 
        quePointobj = addStitching.AddStitching(self.client,self.EntryID)
        numOfcues = (int(TestRunTime)*60)/10
        '''
            @to delete ''' 
        print(('num of cues=' + str(numOfcues)))
        triggerAt = 600
        t0 = int(time.time())
        quepointsList = []
        quepointsList2 = []
        quepointTimeList = []
        QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes',wbDriver=self.driver, logobj=self.logi)
        
        
        errMail = Email.email(None)
        testStatus = True
        
        # Delete old cuepoints
        cuePointsList = quePointobj.retCuePointsforEntry()
        if cuePointsList.totalCount>0:
            quePointobj.deletecuepointsFromEntry(cuePointsList)
        
        # insert queue points for adds every 10 minutes
        epoch = quePointobj.getnowEpochTime()
        for i in range(1,numOfcues):
            quepointTime = quePointobj.addCuePoint(triggerAt,epoch)
            quepointTimeList.append(quepointTime)
            #quepointsList.append(triggerAt)
            quepointsList.append(triggerAt+epoch)
            triggerAt = triggerAt + 600
        
        self.logi.appendMsg("going to read QR code for The adds every 10 minutes")
        #start stream the file
        for i in range(0,numOfcues-1):
            ''' 
            @wait_for_the_next_add '''
            print(('BEFORE add time = ' + str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))))
            print(('T0 = ' + str(t0)))
            print((' waiting ' + str(quepointsList[i]) + ' Seconds for add'))
            #while int(time.time())-t0 < quepointsList[i]:
            while quePointobj.getnowEpochTime()<=quepointsList[i]:
                print(('the Time that passed is: ' + str(int(time.time())-t0)))
                self.player.getPlayerPlayheadEelement(self.driver)
                time.sleep(1)
            print(('AFTER add time = ' + str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))))
            # check that add appears in 1 minute delay time
            AddAppear = False
            delayDone = False
            secCount = 0
            qrfileList = []
            while (not AddAppear) and (not delayDone):
                qrfile = QrCode.saveScreenShot()
                qrfileList.append(qrfile)
                qrval = QrCode.retQrVal(qrfile) 
                time.sleep(1)
                secCount = secCount+1
                if secCount>60:
                    delayDone = True
                try:
                    qrsecs = qrval[27:32]
                    print((str(qrsecs)))
                except:
                    qrsecs = None
                if (qrsecs=='00:00' or qrsecs=='00:01' or qrsecs=='00:02' or qrsecs=='00:03'):
                    AddAppear = True
                    if secCount>1:
                        mailMessage = 'Delay in queue point of time- ' + str(quepointTimeList[i]) + ' It appeared ' + str(secCount) + ' after the expected time'
                        testStatus = False 
              
                        
            ''' 
                @if_the_add_appear_check_it_progress
            '''
            if AddAppear:
                '''
                @delete ''' 
                print('THE ADD APPEARED')
                timeisfinish = False
                addTimer = 0                   
                while not timeisfinish:
                    rc = QrCode.placeCurrPrevScr()
                    time.sleep(1)
                    if rc:
                        rc = QrCode.checkProgress(1)
                        if not rc:
                            mailMessage = 'ADD Not progressing in queue point of time- ' + str(quepointTime[i]) + ' It did NOT progres after the ' + str(addTimer) + ' Second of the Add'
                            qrfile = QrCode.saveScreenShot()
                            quepointsList2.append(qrfile)
                            mailAttach = qrfileList2[-1]
                            testStatus = False 
                    addTimer = addTimer + 1
                    #if timer == 300:
                    if addTimer == 12:
                        timeisfinish = True    
             
             
            else:
                '''
                @delete ''' 
                print('THE ADD DID NOT APPEAR')
                testStatus = False 
                mailMessage = 'Fail in queue point of time- ' + str(quepointTime[i]) + ' It did NOT appeared at all'
                mailAttach = qrfileList[-1]
                
            ## SEND THE MAIL
            #errMail.sendEmailAddStitching(mailMessage, mailAttach)    
                 
            
            for i in range(0,len(qrfileList)-1):
                os.remove(qrfileList[i])
                
                
         
                
      
        
        
#pytest.main('test_addstitching.py -s')        
        
        
        
        
        