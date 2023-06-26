import datetime
import os
import sys
import time

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#import BrowserProxy
import ClienSession
import reporter
import Config
import tearDownclass
import Entry
import Transcoding
import uiconf
import QrcodeReader
import live
import Email


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
FFMPEGPATH =  'ffmpeg'   

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
    
        inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        self.env = 'prod'
        
        self.PublisherID = inifile.RetIniVal('Environment', 'PublisherID')
        self.PAServerUrl = inifile.RetIniVal('Environment', 'PAServerURL')
        self.NySrverUrl = inifile.RetIniVal('Environment', 'NYServerURL')
        self.UserSecret =  inifile.RetIniVal('Environment', 'UserSecret') 
        primaryBroadcastingServers = inifile.RetIniVal('LiveProdServers', 'Servers')
        self.primaryBroadcastingUrllst =  primaryBroadcastingServers.split(';')
        
        self.testTeardownclass = tearDownclass.teardownclass()
        self.logi = reporter.Reporter('LiveProdServers')
        self.logi.initMsg('LiveProdServers setup')
        
        # create client session for pa
        self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.PAServerUrl,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)
        
       
        ''' RETRIEVE TRANSCODING ID AND CREATE SOURCE ONLY IF NOT EXIST'''
        Transobj = Transcoding.Transcoding(self.client,'source only')
        self.sourceonlyId =  Transobj.getTranscodingProfileIDByName('SourceOnly')
        if self.sourceonlyId==None:
            self.sourceonlyId = Transobj.addTranscodingProfile(1,'0') 
            if isinstance(self.sourceonlyId,bool):
                self.logi.reportTest('fail')
                self.testTeardownclass.exeTear()
                assert False
                
        # Create player of latest version 
        myplayer = uiconf.uiconf(self.client, 'livePlayer')  
        self.player = myplayer.addPlayer(None,'prod',False, False)
        if isinstance(self.player,bool):
            self.logi.reportTest('fail')
            self.testTeardownclass.exeTear()
            assert False
        else:
            self.playerId = self.player.id
            
        self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')
        
        self.entrieslst = []
        # Create 36 live entries, 2 for each server (one for NY and one for PA)        
        for i in range(0,len(self.primaryBroadcastingUrllst)-1):
            Entryobj = Entry.Entry(self.client, self.primaryBroadcastingUrllst[i] + '_' + str(datetime.datetime.now()), "Live Automation test", "Live tag", "Admintag", "adi category", 1,None,self.sourceonlyId)
            
            self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
            self.entrieslst.append(self.entry)
            self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
             
    
    def test_LiveProdServers(self):
        
        self.logi.initMsg('LIVE PRODUCTION WOWZA SERVERS test')
        liveObj = live.Livecls(None, self.logi, self.testTeardownclass, True, self.PublisherID, self.playerId)
        globMessage = ''
        errMail = Email.email(None,None)
        mailAttach = [0]
        # stream through the 18 servers each from 2 entries one from pa 1_XXX and the other from NY 0_XXX
        for i in range(0,len(self.primaryBroadcastingUrllst)-1):
            ''' Stream one entry from NY and one from PA with the same wowza server '''
            for j in range(0,2):
                if j==0:
                    self.driver = liveObj.Entryandstrem(self.sourceonlyId, 0, 0, self.entrieslst[i], self.primaryBroadcastingUrllst[i],'/home/ubuntu/MediaUpload/QR_05_minutes.mp4',1,1)
                    
                if j==1:
                    self.driver = liveObj.Entryandstrem(self.sourceonlyId, 0, 0, self.entrieslst[i], self.primaryBroadcastingUrllst[i],'/home/ubuntu/MediaUpload/QR_05_minutes.mp4',1,2)
                    
                #===============================================================
                # if j==2:
                #     self.driver = liveObj.Entryandstrem(self.sourceonlyId, 0, 0, self.entrieslst[i], self.primaryBroadcastingUrllst[i],'/home/ubuntu/MediaUpload/QR_05_minutes.mp4',2,1)
                #     
                # if j==3:
                #     self.driver = liveObj.Entryandstrem(self.sourceonlyId, 0, 0, self.entrieslst[i], self.primaryBroadcastingUrllst[i],'/home/ubuntu/MediaUpload/QR_05_minutes.mp4',2,2)
                #===============================================================
                    
                    
                negmailMessage = 'FAIL - Stream from server ' + str(self.primaryBroadcastingUrllst[i]) + ' did not worked with entry Id=' + str(self.entrieslst[i].id)
                posmessage = 'PASS - Stream from server ' + str(self.primaryBroadcastingUrllst[i]) + ' worked OK with entry Id=' + str(self.entrieslst[i].id)
                
                QrCode = QrcodeReader.QrCodeReader('liveQrCodes',self.driver,self.logi)
                qrfile = QrCode.saveScreenShot()
                qrval = QrCode.retQrVal(qrfile)
                if isinstance(qrval, bool):
                    mailAttach[0] = qrfile
                    self.logi.appendMsg(negmailMessage)
                    try:
                        errMail.sendEmailAddStitching(negmailMessage, mailAttach)
                    except:
                        print("COULD NOT SEND MAIL CHECK EMAIL PASSWORD")
                    print('did not find QR')
                    globMessage = globMessage + negmailMessage 
                else:
                    os.remove(qrfile)
                    self.logi.appendMsg(posmessage)
                    print(('Find QR val= ' + str(qrval)))
                    globMessage = globMessage + posmessage + ' \n- '
                    
                os.system('killall ffmpeg')
                self.driver.quit()
                time.sleep(20)
                
        
        errMail.sendEmailStartFinTest('LIVE PRODUCTION SERVERS','finish',['adi.miller@kaltura.com','alona.zakota@kaltura.com'],globMessage)      
    ''' ***********        
    @tearDown 
    ************'''
                
    def teardown_class(self):
        print('tear down')
        self.testTeardownclass.exeTear()         
        
 
#===============================================================================
    pytest.main('test_LiveRTMPprodServers.py -s')        
#===============================================================================
        