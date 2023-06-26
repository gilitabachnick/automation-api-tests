import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter
import Config
import tearDownclass
import Entry
import Transcoding
import uiconf
import live

# ### Jenkins params ###
# cnfgCls = Config.ConfigFile("stam")
# Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# if str(isProd) == 'true':
#     isProd = True
# else:
#     isProd = False


isProd = False # LiveNG is just supported on testing
testStatus = True
Practi_TestSet_ID = 820


#===========================================================================
# Description :   20 Live test
#
# test scenario:  create 20 entries
#                 stream Randomly the entries in a range of 5 minutes
#                 verify they play correct,
#                 
#                 
# verifications:  video play (QRcode)
#                 manifest and license packets retrieve OK reply
#===========================================================================

''' ----- CONSTANTS ------- '''
FFMPEGPATH =  'ffmpeg'   

class TestClass:


    #self.Wd.find_elements_by_xpath("//i[@class='plaguykit-icon playkit-icon-play']")[2].click()
    #selectOneOfInvisibleSameObjects
    #import kmcbasicfuncs








    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        global testStatus

        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
        if isProd:
            self.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        else:
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))


        self.PublisherID    = inifile.RetIniVal('NewLive', 'PublisherID')
        self.UserSecret     =  inifile.RetIniVal('NewLive', 'AdminSecret')
        self.NumOfEntries   = int(inifile.RetIniVal('NewLive', 'NumOfEntries'))
        self.MinToSream     = int(inifile.RetIniVal('NewLive', 'MinToSream'))
        self.ServerURL      = inifile.RetIniVal('Environment', 'ServerURL')
        self.sendto = "adi.miller@kaltura.com;moran.cohen@kaltura.com"

        self.testTeardownclass = tearDownclass.teardownclass()
        self.logi = reporter.Reporter('test_3775Live20Entries')
        self.logi.initMsg('LiveProdServers setup')
        
        # create client session
        self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID, self.ServerURL, self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
        
       
        ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
        Transobj = Transcoding.Transcoding(self.client,'Passthrough')
        self.passtrhroughId = Transobj.getTranscodingProfileIDByName('Passthrough')
        if self.passtrhroughId==None:
            self.passtrhroughId = Transobj.addTranscodingProfile(1, '32,36,37')
            if isinstance(self.passtrhroughId, bool):
                testStatus = False
                return
                
        # Create player of latest version
        myplayer = uiconf.uiconf(self.client, 'livePlayer')
        self.player = myplayer.addPlayer(None, self.env, False, False)
        if isinstance(self.player, bool):
            testStatus = False
            return
        else:
            self.playerId = self.player.id
            
        self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
        
        self.entrieslst = []
        self.streamUrl = []
        # Create #self.NumOfEntries live entries
        for i in range(0, self.NumOfEntries-1):
            Entryobj = Entry.Entry(self.client, 'Live20Entry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
            self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
            self.entrieslst.append(self.entry)
            self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
            streamUrl = self.client.liveStream.get(self.entry.id)
            self.streamUrl.append(streamUrl)
             
    
    def test_NewLiveProdServers(self):

        global testStatus
        
        self.logi.initMsg('LIVE ' + str(self.NumOfEntries) + ' ENTRIES test')
        liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)

        #globMessage = ''
        #errMail = Email.email(None,None)
        #mailAttach = [0]

        # divide the 5 minutes over the number of the entries to stream - they all should start over the 5 minutes
        slepingTime = 300//len(self.entrieslst)

        # stream the  entries
        for i in range(0, len(self.entrieslst)-1):
                rc = liveObj.EntryandstremNew(self.passtrhroughId, 0, 0, self.entrieslst[i], self.self.streamUrl[i], '/home/ubuntu/MediaUpload/QR_05_minutes.mp4', None)
                time.sleep(slepingTime)
                if not rc:
                    self.logi.appendMsg("FAIL - could not start strem to entry: " + str(self.entrieslst[i]))
                    testStatus = False

        limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToSream*60)

        while datetime.datetime.now() <= limitTimeout:
            rc = liveObj.verifyAllEntriesPalyOrNot(self.entrieslst, True)
            if not rc:
                testStatus = False

            time.sleep(10)

        os.system('killall ffmpeg')
        time.sleep(10)

        # verify all stopped play
        rc = liveObj.verifyAllEntriesPalyOrNot(self.entrieslst, False)
        if not rc:
            testStatus = False

    ''' ***********        
    @tearDown 
    ************'''
                
    def teardown_class(self):
        global testStatus

        print('tear down')
        try:
            self.testTeardownclass.exeTear()
        except Exception as Exp:
            print(Exp)

        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '3775','1')
           self.logi.reportTest('fail',self.sendto)
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '3774','0')
           self.logi.reportTest('pass',self.sendto)
           assert True
        
 
