'''

this class lib includes reusable functions for live tests ,stream types , API

'''

import _thread
import datetime
import os
import sys
import time
from subprocess import Popen, PIPE


from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import Entry
import strclass
import clsPlayerV2
import QrcodeReader
import paramiko
import KmcBasicFuncs
import uiconf
import requests
import re
import subprocess


from selenium.webdriver.common.action_chains import ActionChains
from io import open
import json
import pickle

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Caption import *
import paramiko
from KalturaClient import *
from KalturaClient.Plugins.Schedule import *

from KalturaClient.Plugins.Reach import *


pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)
import Entrypage

FFMPEGPATH = 'ffmpeg'

############ Environment parameters - Remote or Mocal streamer machine connection: g_LocalCheckpointKey="" empty (=remote), g_LocalCheckpointKey = private CheckpointKey_X.pem
import Config
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
sys.path.insert(1,pth)
inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
g_LocalCheckpointKey = inifile.RetIniVal('NewLive', 'LocalCheckpointKey')
if g_LocalCheckpointKey!="":

    g_SSH_CONNECTION = "LINADMIN_SSH" #local machine access
else:
    g_SSH_CONNECTION = "KEY_SSH" #remote machine access
###########
'''
g_Testing_ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
sys.path.insert(1,pth)
inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
g_Prod_ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
g_Testing_ServerURL="https://api.nvd1.ovp.kaltura.com"'''
############
class Livecls():

    def __init__(self, client, logi, tearobj, isProd, publisherId, playerId):
        self.client = client
        self.logi = logi
        self.testTeardownclass = tearobj
        self.isProd = isProd
        self.publisherId = publisherId
        self.playerId = playerId


    def StreamFromFfmpeg(self, primaryBroadcastingUrl, entry, fileTostream='/home/ubuntu/MediaUpload/LiveQr30min.mp4',udpTcp=None):
        if udpTcp==None:
            comand = FFMPEGPATH +' -re -i ' + fileTostream + ' -c:v copy -c:a copy -f flv  -rtmp_live 1 "' + primaryBroadcastingUrl + '/' + entry.id + '_1" > /dev/null 2>&1 &'
        elif udpTcp in range(1,3):
            if udpTcp==1:
                comand = FFMPEGPATH +' -re -i ' + fileTostream + ' -c:v copy -c:a copy  -f rtsp -rtsp_transport tcp "' + primaryBroadcastingUrl + '" > /dev/null 2>&1 &'
            else:
                comand = FFMPEGPATH +' -re -i ' + fileTostream + ' -c:v copy -c:a copy  -f rtsp -rtsp_transport udp "' + primaryBroadcastingUrl + '" > /dev/null 2>&1 &'
        #=======================================================================
        # elif udpTcp in range(3,5):
        #     if udpTcp==3:
        #         comand = FFMPEGPATH +' -re -i ' + fileTostream + ' -c:v copy -c:a copy  -f rtmp -rtmp_transport tcp "' + primaryBroadcastingUrl + '" > /dev/null 2>&1 &'
        #     else:
        #         comand = FFMPEGPATH +' -re -i ' + fileTostream + ' -c:v copy -c:a copy  -f rtmp -rtmp_transport udp "' + primaryBroadcastingUrl + '" > /dev/null 2>&1 &'
        #=======================================================================
        print(comand)
        _thread.start_new_thread(os.system,(comand,))
        #self.testTeardownclass.addTearCommand(os,'system(\'killall ffmpeg\')')


    def Entryandstrem(self, conversionProfileId, recordStatus=0, dvrStatus=0, Kentry=None, serverName=None, fileTostream=None, rtsp=None, udpTcp=None):
        #conversionProfileId=self.sourceonlyId

        ''' UPLOAD NEW LIVE ENTRYT '''
        if Kentry == None:
            # Upload entry with the above transcoding profile
            self.logi.appendMsg('going to upload new live entry ')
            myentry = Entry.Entry(self.client,"autoLive_" + str(datetime.datetime.now()), "Live Automation test", "Live tag", "Admintag", "adi category", 1,None,conversionProfileId)  # file(filePth,'rb')
            self.entry = myentry.AddEntryLiveStream(None, None, recordStatus, dvrStatus)
            if isinstance(self.entry,bool):
                self.logi.appendMsg('Entry was not uploaded after 5 minutes')
                self.logi.reportTest('fail')
                self.testTeardownclass.exeTear()
                assert False
            elif isinstance(self.entry, str):
                self.logi.appendMsg('Entry got error when trying to upload it')
                self.logi.reportTest('fail')
                self.testTeardownclass.exeTear()
                assert False
            else:
                self.logi.appendMsg('Finished upload new live entry, id = ' + str(self.entry.id))
                self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(self.entry.id) + '\')')

        else:
            self.entry = Kentry


        self.primaryBroadcastingUrl = self.entry.primaryBroadcastingUrl
        if serverName != None:
            urlParts = self.primaryBroadcastingUrl.split('?')
            #===================================================================
            # if rtsp==None:
            #     self.primaryBroadcastingUrl = 'rtmp://' + self.entry.id + '.p.us.' + serverName + '.kpublish.kaltura.com:1935/kLive?' + urlParts[-1]
            #===================================================================
            if rtsp==None:
                self.primaryBroadcastingUrl = 'rtmp://' + self.entry.id + '.p.zy.' + serverName + '.kpublish.kaltura.com:1935/kLive?' + urlParts[-1]
            elif rtsp in range(1,3):
                if rtsp == 1:
                    self.primaryBroadcastingUrl = 'rtsp://' + self.entry.id + '.p.zy.' + serverName + '.kpublish.kaltura.com/kLive/' + self.entry.id + "_1/?" + urlParts[1]
                elif rtsp == 2:
                    self.primaryBroadcastingUrl = 'rtsp://' + self.entry.id + '.p.l3.' + serverName + '.kpublish.kaltura.com/kLive/' + self.entry.id + "_1/?" + urlParts[1]



            #===================================================================
            # elif rtsp in range(3,5):
            #     if rtsp == 3:
            #         self.primaryBroadcastingUrl = 'rtsp://' + self.entry.id + '.p.zy.' + serverName + '.kpublish.kaltura.com/kLive/' + self.entry.id + "_1/?" + urlParts[1]
            #     elif rtsp == 4:
            #         self.primaryBroadcastingUrl = 'rtsp://' + self.entry.id + '.p.l3.' + serverName + '.kpublish.kaltura.com/kLive/' + self.entry.id + "_1/?" + urlParts[1]
            #===================================================================



        ''' START STREAMING FROM FFMPEG '''  #self.primaryBroadcastingUrl = self.primaryBroadcastingUrl.replace("centos-01","centos-03")
        self.StreamFromFfmpeg(self.primaryBroadcastingUrl, self.entry, fileTostream,rtsp)

        # build URL for player page
        self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>'
        if self.isProd:
            self.baseUrl = self.baseUrl + '&env=production'

        strcls = strclass.strclass(self.baseUrl)
        newParams = str(self.publisherId) + ',' + str(self.playerId) + ',' + self.entry.id
        self.baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,', newParams)
        self.logi.appendMsg('player page url is:' + self.baseUrl)

        '''PLAY THE STREAMED VIDEO '''
        selDriver = 2
        time.sleep(60)

        if selDriver==0:
            selDriver = "firefox"
        elif selDriver==1:
            selDriver = "internet explorer"
        elif selDriver==2:
            selDriver = "chrome"

        self.player = clsPlayerV2.playerV2("kaltura_player_1418811966")
        self.driver = self.player.testWebDriverLocalOrRemote(selDriver)

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
        if Kentry == None:
            return self.entry
        else:
            return self.driver


    def PlayEntry(self, selDriver, entryId):

        self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>'
        if self.isProd:
            self.baseUrl = self.baseUrl + '&env=production'

        strcls = strclass.strclass(self.baseUrl)
        newParams = str(self.publisherId) + ',' + str(self.playerId) + ',' + entryId
        self.baseUrl = strcls.multipleReplace('<PartID>,<PlayID>,<EntrID>,', newParams)
        self.logi.appendMsg('player page url is:' + self.baseUrl)

        '''PLAY THE STREAMED VIDEO '''
        if selDriver==0:
            selDriver = "firefox"
        elif selDriver==1:
            selDriver = "internet explorer"
        elif selDriver==2:
            selDriver = "chrome"

        player = clsPlayerV2.playerV2("kaltura_player_1418811966")
        self.driver1 = player.testWebDriverLocalOrRemote(selDriver)

        try:
            self.driver1.get(self.baseUrl)
        except:
            self.logi.appendMsg('could not get to the player base url- might be connection problem')
            self.logi.reportTest('fail')
            return False

        if selDriver==0 or selDriver==1:
            self.driver1.maximize_window()
        time.sleep(5)

        # allow the pop up streaming
        if selDriver==0:
            Webelement = self.driver1.find_element_by_xpath('//body')
            Webelement.send_keys(Keys.ALT+'a')
            time.sleep(1)
            Webelement.send_keys(Keys.ALT+'r')
            time.sleep(2)

        timeisfinish = False
        timer = 0
        player.switchToPlayerIframe(self.driver1)

        while not timeisfinish:
            try:
                time.sleep(1)
                timer = timer + 1
                if timer == 300:  # THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE
                    timeisfinish = True
                    self.logi.appendMsg('THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE')
                    self.logi.reportTest('fail')
                    assert False

                self.player.clickPlay(self.driver1)
                print(' play clicked ok')
                timeisfinish = True

            except Exception as exp:
                print('no play')
                return False


    def EntryandstremNew(self, conversionProfileId, recordStatus=0, dvrStatus=0, Kentry=None, primaryBroadcastingUrl=None, fileTostream=None, rtsp=None):
        # conversionProfileId=self.sourceonlyId
        try:
            ''' UPLOAD NEW LIVE ENTRYT '''
            if Kentry == None:
                # Upload entry with the above transcoding profile
                self.logi.appendMsg('going to upload new live entry ')
                myentry = Entry.Entry(self.client, "autoLive_" + str(datetime.datetime.now()), "Live Automation test",
                                      "Live tag", "Admintag", "adi category", 1, None,
                                      conversionProfileId)  # file(filePth,'rb')
                self.entry = myentry.AddEntryLiveStream(None, None, recordStatus, dvrStatus)
                if isinstance(self.entry, bool):
                    self.logi.appendMsg('Entry was not uploaded after 5 minutes')
                    self.logi.reportTest('fail')
                    self.testTeardownclass.exeTear()
                    assert False
                elif isinstance(self.entry, str):
                    self.logi.appendMsg('Entry got error when trying to upload it')
                    self.logi.reportTest('fail')
                    self.testTeardownclass.exeTear()
                    assert False
                else:
                    self.logi.appendMsg('Finished upload new live entry, id = ' + str(self.entry.id))
                    self.testTeardownclass.addTearCommand(myentry, 'DeleteEntry(\'' + str(self.entry.id) + '\')')

            else:
                self.entry = Kentry

            self.primaryBroadcastingUrl = primaryBroadcastingUrl

            ''' START STREAMING FROM FFMPEG '''  # self.primaryBroadcastingUrl = self.primaryBroadcastingUrl.replace("centos-01","centos-03")
            self.StreamFromFfmpeg(self.primaryBroadcastingUrl, self.entry, fileTostream, rtsp)

            return True

        except Exception as Exp:
            print(("FAIL in EntryandstremNew " + str(Exp)))
            return False





    def PlayEntryNew(self, selDriver, entryId,PlayerVersion=3,flashvars=None,Protocol='https',ServerURL=None):

        try:
            if flashvars == None:
                #self.baseUrl = 'https://<envurl>/index.php/extwidget/preview/partner_id/<PartID>/uiconf_id/<PlayID>/entry_id/<EntrID>/embed/dynamic'
                self.baseUrl = Protocol + '://<envurl>/index.php/extwidget/preview/partner_id/<PartID>/uiconf_id/<PlayID>/entry_id/<EntrID>/embed/dynamic'
            else:#add flashvars
                #self.baseUrl = 'https://<envurl>/index.php/extwidget/preview/partner_id/<PartID>/uiconf_id/<PlayID>/entry_id/<EntrID>/embed/dynamic' + "?" +flashvars
                self.baseUrl = Protocol + '://<envurl>/index.php/extwidget/preview/partner_id/<PartID>/uiconf_id/<PlayID>/entry_id/<EntrID>/embed/dynamic' + "?" +flashvars

            '''if self.isProd:
                #envurl = 'www.kaltura.com'
                if g_Prod_ServerURL.find('https://') >= 0:
                    envurl = g_Prod_ServerURL.replace('https://', '')
                else:
                    envurl = g_Prod_ServerURL.replace('http://', '')
                env = 'prod'
            else:
                #envurl = 'qa-apache-php7.dev.kaltura.com'
                if g_Testing_ServerURL.find('https://') >= 0:
                    envurl = g_Testing_ServerURL.replace('https://', '')
                else:
                    envurl = g_Testing_ServerURL.replace('http://', '')
                env = 'testing'
                '''
            if ServerURL == None:#Old env support
                if self.isProd:
                    envurl = 'www.kaltura.com'
                    env = 'prod'
                else:
                    envurl = 'qa-apache-php7.dev.kaltura.com'
                    env = 'testing'
            else:# Region clouds support
                #ADD working on
                if self.isProd:
                    # envurl = 'www.kaltura.com'
                    if ServerURL.find('https://') >= 0:
                        envurl = ServerURL.replace('https://', '')
                    else:
                        envurl = ServerURL.replace('http://', '')
                    env = 'prod'
                else:
                    # envurl = 'qa-apache-php7.dev.kaltura.com'
                    if ServerURL.find('https://') >= 0:
                        envurl = ServerURL.replace('https://', '')
                    else:
                        envurl = ServerURL.replace('http://', '')
                    env = 'testing'
            ###############

            #self.baseUrl = 'http://externaltests.dev.kaltura.com/player-inhouse/playerAPI.php?partnerID=<PartID>&playerID=<PlayID>&entryID=<EntrID>'
            #if self.isProd:
            #    self.baseUrl = self.baseUrl + '&env=production'

            strcls = strclass.strclass(self.baseUrl)
            newParams = envurl + ',' + str(self.publisherId) + ',' + str(self.playerId) + ',' + entryId
            self.baseUrl = strcls.multipleReplace('<envurl>,<PartID>,<PlayID>,<EntrID>,', newParams)
            self.logi.appendMsg('player page url is:' + self.baseUrl)
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()

            '''PLAY THE STREAMED VIDEO '''
            if selDriver == 0:
                selDriver = "firefox"
            elif selDriver == 1:
                selDriver = "internet explorer"
            elif selDriver == 2:
                selDriver = "chrome"

            player = clsPlayerV2.playerV2("kaltura_player_1418811966")
            self.driver1 = player.testWebDriverLocalOrRemote(selDriver,True,sniffer=True)#True- running playback from local computer,False- running playback from 192.168.163.35
            time.sleep(4)
        except Exception as Exp:
            return False,self.driver1

        try:
            self.driver1.get(self.baseUrl)
        except:
            self.logi.appendMsg('could not get to the player base url- might be connection problem')
            self.logi.reportTest('fail')
            return False,self.driver1

        if selDriver == 0 or selDriver == 1:
            self.driver1.maximize_window()
        time.sleep(5)

        # allow the pop up streaming
        if selDriver == 0:
            Webelement = self.driver1.find_element_by_xpath('//body')
            Webelement.send_keys(Keys.ALT + 'a')
            time.sleep(1)
            Webelement.send_keys(Keys.ALT + 'r')
            time.sleep(2)

        timeisfinish = False
        timer = 0
        #player.switchToPlayerIframe(self.driver1)

        while not timeisfinish:
            try:
                time.sleep(1)
                timer = timer + 1
                if timer == 60:  # THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE
                    timeisfinish = True
                    self.logi.appendMsg('THE PLAY BUTTON DID NOT APPEAR AFTER 5 MINUTES - PLAYER COULD NOT PLAY LIVE')
                    self.logi.reportTest('fail')
                    return False,self.driver1

                if PlayerVersion == 2:
                    #self.driver1.execute_script('document.getElementById("kaltura_player").play()')#problem v2
                    #self.driver1.execute_script("document.getElementsByTagName('video')[0].play()")#problem v2
                    entryPage = Entrypage.entrypagefuncs(self.driver1,self.logi)
                    time.sleep(4)
                    rc = entryPage.PreviewAndEmbed(env,PlayerVersion=2, JustPlayOnBrowser =True)

                    if rc == False:
                        print('No play - V2')
                        self.logi.appendMsg('INFO - No play on V2')
                        return False,self.driver1 #ADDED

                else:
                    ClickOK=False
                    ButtonIndex=len(self.driver1.find_elements_by_xpath("//i[@class='playkit-icon playkit-icon-play']"))
                    for i in range(0, ButtonIndex):
                        try:
                            self.driver1.find_elements_by_xpath("//i[@class='playkit-icon playkit-icon-play']")[i].click()
                            ClickOK=True
                        except:
                            pass
                    if ClickOK == False:#if not play ->return false
                        print('No play')
                        self.logi.appendMsg('INFO - NO play')
                        return False,self.driver1 #ADDED

                print('Play clicked ok')

                self.logi.appendMsg('INFO - Play clicked OK')
                timeisfinish = True

            except Exception as exp:
                print('No play')
                self.logi.appendMsg('INFO - NO play')
                return False,self.driver1 #ADDED

        # wait till live is actually played after press the play button

        self.logi.appendMsg('video with QR code is playing')
        time.sleep(20)
        return "Play OK",self.driver1

    # this def verify for x seconds that a live stream play ok and QR code progress on it
    #
    def verifyLiveisplaying(self, wd=None):

        if wd == None:
            wd = self.driver1

        QrCode = QrcodeReader.QrCodeReader(wd, self.logi)
        qrfile = QrCode.saveScreenShot()#problem
        qrval = QrCode.retQrVal(qrfile)
        if isinstance(qrval, bool):
            self.logi.appendMsg("FAIL - could not find QR code on the player - the video did NOT play")
            return False
        else:
            self.logi.appendMsg("PASS -  find QR code on the player - the video did play")
            return True

    # this def verifies that a list of entries is played or not
    # if the entries should play, send True in boolShouldPlay, if not send False
    def verifyAllEntriesPalyOrNot(self, entryList, boolShouldPlay):
        defStatus = True
        for entry in self.entrieslst:
            rc = self.PlayEntryNew(0, entry)
            if isinstance(rc, bool):
                self.logi.appendMsg("FAILE - could not play the entry - " + str(entry))
                return False
            else:
                isPlaying = self.verifyLiveisplaying(rc)
                if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                    defStatus = False
                rc.quit()
        return defStatus


    ''' Moran.Cohen 
    This function login to linux ssh and then run shellscript with ffmpeg cmds after that closing the ssh.
    Example for parameters:
    remote_host = "liveng-core3-automation.kaltura.com"
    remote_user = "root"
    remote_pass = "testingqa"
    filePath = "/home/kaltura/tests/stream_liveNG_custom_entry_AUTOMATION_tmp.sh"
    entryId = "0_a779a16k"
    UiConfig = "15225574"
    partnerId = "6611"
    url= "qa-apache-php7.dev.kaltura.com"
    '''

    def streamEntryByShellScript(self, host, user, passwd, filePath, entryId, entrieslst, partnerId, uiConfig, url,MinToPlayEntry=1, timoutMax=8, boolShouldPlay=True, PlayerVersion=3, cmdLine="",QRcode=True, env='testing', BroadcastingUrl=None):

        try:
            self.logi.appendMsg(
                "INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))
            # was timeout=5

            connection = ssh.invoke_shell()

            cmdLine = filePath + " " + cmdLine
            self.logi.appendMsg("INFO - Going to run ssh cmdLine = " + str(cmdLine))

            ssh.exec_command("sudo su -" + "\n")
            stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=3, get_pty=True)
            # Waiting to process to end - timoutMax = 8 x 10wait=> meaning waiting for 80sec until verify the stream
            timeout = 0
            while not stdout.channel.exit_status_ready():
                time.sleep(10)
                if stdout.channel.recv_ready() and stdout.channel.exit_status_ready():
                    print("=========================================================================================================================")
                    print(("Process is finished - Verify result -  ssh.exec_command " + cmdLine))
                    print("=========================================================================================================================")
                    break
                if timeout > timoutMax:  # timout
                    print("=========================================================================================================================")
                    print(("Timeout - Process is running - Not finished - ssh.exec_command" + cmdLine))
                    print("=========================================================================================================================")
                    break
                print("ssh.exec_command is processing.")
                timeout = timeout + 1

            time.sleep(30)

            # Check that ffmpeg is running by ps aux|grep ffmpeg
            # rc = self.SearchPsAuxffmpeg(host, user, passwd, entryId, partnerId,timoutMax,env=env)
            rc = self.SearchPsAuxffmpeg(host, user, passwd, entryId, partnerId, timoutMax, env=env,
                                        BroadcastingUrl=BroadcastingUrl)
            if rc == False:
                self.logi.appendMsg(
                    "FAIL - SearchPsAuxffmpeg:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(
                        datetime.datetime.now()))
                print('Return error from ffmpeg cmd:')
                return False, "Return error from ffmpeg cmd:"

            if QRcode == True:
                rc = self.verifyAllEntriesPlayOrNoBbyQrcode(entrieslst, True, PlayerVersion=PlayerVersion)
            else:
                rc = self.verifyAllEntriesPlayOrNoBbyOnlyPlayback(entrieslst, True, PlayerVersion=PlayerVersion)
            time.sleep(5)
            if not rc:
                self.logi.appendMsg("FAIL - verifyAllEntriesPlayOrNoBbyQrcode - Entry - " + str(entryId))
                return False, "PlayStatus=False"

            # Close ffmpet by ssh
            ssh.close()
            result = str(stdout.read())
            result = result.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            if result:
                print(result)
                return True, result
            else:
                False, result
        except Exception as err:
            print(err)
            return False, err

    '''Moran.Cohen
    This function verifies the result from streaming the entry by shellscript
    '''
    def VerifyResultFromStreamEntryByShellScript(self, resultData):

        try:
            resultData.lower()
            if resultData.find("error") > 0:
                print(resultData)
                #print "ffmpeg gets error."
                return False
            elif resultData.find("frame=") > 0 and resultData.find("fps=") > 0 and resultData.find("size=") > 0 and resultData.find("time=") > 0:
                print("ffmpeg is running OK.")
                self.logi.appendMsg("PASS - ffmpeg is running OK")
                return True
            else:
                #print resultData
                #print "ffmpeg process run without valid result data."
                self.logi.appendMsg("FAIL - ffmpeg process run without valid result data.resultData = " + str(resultData))
                return True
        except Exception as err:
            print(err)
            return False


    ''' Moran.Cohen 
    This function login to linux ssh and then Start shellscript return ssh without closing .
    Example for parameters:
    remote_host = "liveng-core3-automation.kaltura.com"
    remote_user = "root"
    remote_pass = "testingqa"
    filePath = "/home/kaltura/tests/stream_liveNG_custom_entry_AUTOMATION_tmp.sh"
    entryId = "0_a779a16k"
    UiConfig = "15225574"
    partnerId = "6611"
    url= "qa-apache-php7.dev.kaltura.com"
    '''
    def Start_StreamEntryByShellScript(self, host, user, passwd,filePath, entryId,partnerId,uiConfig,url ,streamDuration=5,timoutMax=10):

        try:
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            statusStreaming = False
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            connection = ssh.invoke_shell()
            cmdLine= filePath + " " + entryId + " " + partnerId + " " + uiConfig+ " " + url
            stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=3, get_pty=True)

            time.sleep(streamDuration)
            # Write ssh cmd line
            remote_conn = ssh.invoke_shell()

            self.logi.appendMsg("INFO - Interactive SSH - Going to run ps aux|grep ffmpeg")
            output = remote_conn.recv(1000)
            remote_conn.send("\n")
            remote_conn.send("sudo su -" + "\n")
            remote_conn.send("ps aux|grep ffmpeg\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            # Waiting to ffmpeg to run
            timeout= 0
            for timeout in range(0, timoutMax):
                time.sleep(5)
                if output.find("p=" + partnerId + "&e=" + entryId) > 0:
                    print(("ffmpeg is streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId))
                    statusStreaming = True
                    self.logi.appendMsg("PASS - ffmpeg is streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId)
                    break
                if timeout > timoutMax:
                    print(("TIMEOUT - ffmpeg is NOT streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId))
                    self.logi.appendMsg("FAIL - ffmpeg is NOT streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId)
                    statusStreaming = False
                    break
                print("Waiting to ffmpeg ps - ssh.exec_command is processing.")
                remote_conn.send("ps aux|grep ffmpeg\n")
                output = str(remote_conn.recv(10000))
                output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
                print(output)
                timeout=timeout+1

            if statusStreaming ==False:
                return False,ssh,stdout

            return True,ssh,stdout


        except Exception as err:
            print(err)
            return False,ssh,stdout

    '''Moran.Cohen
    This function killall ffmpeg and closes the ssh. 
    '''
    def End_StreamEntryByShellScript(self, ssh,stdout,entryId,partnerId,streamDuration=5,timoutMax=8):
        try:

            # Write ssh cmd line
            remote_conn = ssh.invoke_shell()
            self.logi.appendMsg("INFO - Interactive SSH - Going to run killall ffmpeg")
            output = remote_conn.recv(1000)
            remote_conn.send("\n")
            #remote_conn.send("xstatus Cameras\n")
            remote_conn.send("killall -9 ffmpeg\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            remote_conn.send("\n")
            remote_conn.send("ps aux|grep ffmpeg\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            if output.find("p=" + partnerId + "&e=" + entryId) > 0:
                print(("ffmpeg is streaming:Details: partnerId = " + partnerId))
                return False
            else:
                print(("END STREAM - ffmpeg is NOT streaming:Details: partnerId = " + partnerId))
                return True

        except Exception as err:
            print(err)
            return False


    #SSH_CONNECTION = run streamer on local computer OR remote streamer machine by user&key OR remote streamer machine by user&pwd
    def Start_StreamEntryByffmpegCmd(self, host, user, passwd, ffmpegCmdLine, entryId, partnerId, timoutMax=10,env='testing', BroadcastingUrl=None, FoundByProcessId=False,timout_SearchPsAux=5, MultiArrProcessIds=False, srtPass=None,SSH_CONNECTION=g_SSH_CONNECTION, LocalCheckpointKey=g_LocalCheckpointKey):

        try:
            # Create SSH Connection for streamer
            rc,remote_conn,ssh=self.SSH_Connection(host=host,user=user,passwd=passwd,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
            if rc==False:
                self.logi.appendMsg("FAIL - SSH_Connection host= " + host + " , user=" + user)

            self.logi.appendMsg("INFO - Interactive SSH - Going to run ffmpegCmdLine = " + ffmpegCmdLine)
            self.logi.appendMsg("INFO - Interactive SSH - ffmpegCmdLine datetime " + str(datetime.datetime.now()))
            remote_conn.send(ffmpegCmdLine + "\n")
            time.sleep(15)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n',os.linesep).replace('\\r',os.linesep)
            self.logi.appendMsg("INFO - ffmpegCmdLine output = " + str(output))
            time.sleep(timout_SearchPsAux)
            #Check that ffmpeg is running by ps aux|grep ffmpeg
            if FoundByProcessId == False:
                rc = self.SearchPsAuxffmpeg(host, user, passwd, entryId, partnerId,timoutMax,env=env,BroadcastingUrl=BroadcastingUrl)
            else:
                if MultiArrProcessIds == True:#support multi processIds option
                    ffmpeg_ByProcessId=[]
                    rc, ffmpeg_ByProcessId = self.SearchPsAuxffmpeg_MultiArrProcessIds(host, user, passwd, entryId,partnerId, timoutMax, env=env,BroadcastingUrl=BroadcastingUrl,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
                else:#regular stream
                    rc, ffmpeg_ByProcessId = self.SearchPsAuxffmpeg_ByProcessId(host, user, passwd, entryId, partnerId,timoutMax, env=env,BroadcastingUrl=BroadcastingUrl,srtPass=srtPass,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
            if rc ==False:
                self.logi.appendMsg("FAIL - SearchPsAuxffmpeg:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                print('Return error from ffmpeg cmd: ')
                ################### Solution for remote_conn.recv(10000) stuck
                not_done = True
                max_loops=2
                i=0
                MAX_BUFFER=1000
                while (not_done) and (i <= max_loops):
                    time.sleep(1)
                    i += 1
                    # Keep reading data as long as available (up to max_loops)
                    if remote_conn.recv_ready():
                        output += str(remote_conn.recv(MAX_BUFFER))
                        output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
                    else:
                        not_done = False

                self.logi.appendMsg("INFO - ffmpegCmdLine output Error = " + str(output))
                time.sleep(2)
                return False,"NoProcessId_" + str(output)

            if FoundByProcessId == True:
                return True,ffmpeg_ByProcessId

            return True, "Streaming"

        except Exception as err:
            print(err)
            return False,err

    def Start_StreamEntryByffmpegCmd_OLD(self, host, user, passwd, ffmpegCmdLine, entryId, partnerId, timoutMax=10,env='testing', BroadcastingUrl=None, FoundByProcessId=False, timout_SearchPsAux=5,MultiArrProcessIds=False, srtPass=None):

        try:
            statusStreaming = False
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)

            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            remote_conn = ssh.invoke_shell()
            # print("Interactive SSH - Going to run.ffmpegCmdLine = " + ffmpegCmdLine)
            self.logi.appendMsg("INFO - Interactive SSH - Going to run ffmpegCmdLine = " + ffmpegCmdLine)
            self.logi.appendMsg("INFO - Interactive SSH - ffmpegCmdLine datetime " + str(datetime.datetime.now()))
            output = remote_conn.recv(1000)
            remote_conn.send("\n")
            remote_conn.send("sudo su -" + "\n")
            time.sleep(1)
            remote_conn.send(ffmpegCmdLine + "\n")
            time.sleep(15)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            self.logi.appendMsg("INFO - ffmpegCmdLine output = " + str(output))
            time.sleep(timout_SearchPsAux)
            # Check that ffmpeg is running by ps aux|grep ffmpeg
            if FoundByProcessId == False:
                rc = self.SearchPsAuxffmpeg(host, user, passwd, entryId, partnerId, timoutMax, env=env,BroadcastingUrl=BroadcastingUrl)
            else:
                # rc,ffmpeg_ByProcessId = self.SearchPsAuxffmpeg_ByProcessId(host, user, passwd, entryId, partnerId, timoutMax, env=env,BroadcastingUrl=BroadcastingUrl)
                if MultiArrProcessIds == True:  # support multi processIds option
                    ffmpeg_ByProcessId = []
                    rc, ffmpeg_ByProcessId = self.SearchPsAuxffmpeg_MultiArrProcessIds(host, user, passwd, entryId,partnerId, timoutMax, env=env,BroadcastingUrl=BroadcastingUrl)
                else:  # regulr stream
                    rc, ffmpeg_ByProcessId = self.SearchPsAuxffmpeg_ByProcessId(host, user, passwd, entryId, partnerId,timoutMax, env=env,BroadcastingUrl=BroadcastingUrl,srtPass=srtPass)
            if rc == False:
                self.logi.appendMsg("FAIL - SearchPsAuxffmpeg:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                print('Return error from ffmpeg cmd: ')
                ################### Solution for remote_conn.recv(10000) stuck
                not_done = True
                max_loops = 2
                i = 0
                MAX_BUFFER = 1000
                while (not_done) and (i <= max_loops):
                    time.sleep(1)
                    i += 1
                    # Keep reading data as long as available (up to max_loops)
                    if remote_conn.recv_ready():
                        # output += remote_conn.recv(MAX_BUFFER)
                        output += str(remote_conn.recv(MAX_BUFFER))
                        output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
                    else:
                        not_done = False

                #################
                self.logi.appendMsg("INFO - ffmpegCmdLine output Error = " + str(output))
                time.sleep(2)
                return False, "NoProcessId_" + str(output)

            if FoundByProcessId == True:
                return True, ffmpeg_ByProcessId

            return True, "Streaming"

        except Exception as err:
            print(err)
            return False, err

    ''' Moran.Cohen 
    This function login to linux ssh and then searching for ffmpeg process.
    Example for parameters:
    remote_host = "liveng-core3-automation.kaltura.com"
    remote_user = "root"
    self.remote_pass = "testingqa"
    entryId = "0_a779a16k"
    partnerId = "6611"  
    timoutMax = max timout for waiting to ffmpeg process.
    env=testing/prod
    HybridCDN = adminconsole.config window ->if HybridCDN=True different url from the entry.BroadcastingUrl(from kmc drilldown)
    '''
    def SearchPsAuxffmpeg(self,host, user, passwd,entryId,partnerId,timoutMax=10,env='testing',BroadcastingUrl=None,HybridCDN=False):
        try:
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            statusStreaming = False
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))
            # Write ssh cmd line
            remote_conn = ssh.invoke_shell()
            self.logi.appendMsg("INFO - Interactive SSH - Going to run ps aux|grep ffmpeg . Date = "  + str(datetime.datetime.now()))
            remote_conn.send("\n")
            remote_conn.send("sudo su -" + "\n")
            time.sleep(5)
            remote_conn.send("date ; ps aux|grep ffmpeg\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            self.logi.appendMsg("INFO - Result of cmd ps aux|grep ffmpeg: " + str(output))

            if BroadcastingUrl == None or HybridCDN == True:
                if env == 'prod':
                    searchPSstring=entryId + ".p.kpublish.kaltura.com:1935"
                else:#testing
                    searchPSstring="p=" + partnerId + "&e=" + entryId
            else:
                searchPSstring=str(BroadcastingUrl)

            timeout= 0
            for timeout in range(0, timoutMax):
                time.sleep(5)
                #if output.find("p=" + partnerId + "&e=" + entryId) > 0:
                if output.find(searchPSstring) > 0:
                    #print "ffmpeg is streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId
                    statusStreaming = True
                    self.logi.appendMsg("PASS - ffmpeg is streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                    break
                if timeout > timoutMax:
                    #print "TIMEOUT - ffmpeg is NOT streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId
                    statusStreaming = False
                    self.logi.appendMsg("FAIL - TIMEOUT - ffmpeg is NOT streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                    break
                print("Waiting to ffmpeg ps - ssh.exec_command is processing.")
                remote_conn.send("date ; ps aux|grep ffmpeg\n")
                output = str(remote_conn.recv(10000))
                output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
                print(output)
                timeout=timeout+1

            if statusStreaming ==False:
                return False

            return True

        except Exception as err:
            print(err)
            return False


    ''' Moran.Cohen 
    This function login to linux ssh and then ending ffmpeg process(killall -9 ffmpeg).
    Example for parameters:
    remote_host = "liveng-core3-automation.kaltura.com"
    remote_user = "root"
    self.remote_pass = "testingqa"
    entryId = "0_a779a16k"
    partnerId = "6611"  
    FoundByProcessId=ffmpeg ProcessId to delete - Default delete all Processes Id type ffmpeg 
    '''
    def End_StreamEntryByffmpegCmd_OLD(self,host, user, passwd,entryId,partnerId,FoundByProcessId=False):
        try:
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            # Write ssh cmd line
            remote_conn = ssh.invoke_shell()
            #print("Interactive SSH - Going to run killall -9 ffmpeg")
            self.logi.appendMsg("INFO - Interactive SSH - Going to run kill -9 ffmpeg")
            output = remote_conn.recv(1000)
            remote_conn.send("\n")
            remote_conn.send("sudo su -" + "\n")
            #remote_conn.send("killall -9 ffmpeg\n")
            if FoundByProcessId == False:
                remote_conn.send("date ; killall -9 ffmpeg\n")
            else:
                remote_conn.send("date ; kill -9 " + str(FoundByProcessId) + "\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            remote_conn.send("\n")
            remote_conn.send("date ; ps aux|grep ffmpeg\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            #if output.find("p=" + partnerId + "&e=" + entryId) > 0:
            if output.find(entryId) > 0:
                #print "ffmpeg is streaming:Details: entryId = " + entryId + "  , partnerId = " + partnerId
                self.logi.appendMsg("FAIL - ffmpeg is streaming:Details: entryId = " + entryId + "  , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                return False
            else:
                #print "END STREAM - ffmpeg is NOT streaming:Details: entryId = " + entryId + "  , partnerId = " + partnerId
                self.logi.appendMsg("PASS - END STREAM - ffmpeg is NOT streaming: partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                return True

        except Exception as err:
            print(err)
            return False

    ''' Moran.Cohen 
    This function login to linux ssh and then ending ffmpeg process(killall -9 ffmpeg).
    FoundByProcessId=ffmpeg ProcessId to delete - Default delete all Processes Id type ffmpeg 
    '''
    def End_StreamEntryByffmpegCmd(self,host, user, passwd,entryId,partnerId,FoundByProcessId=False,SSH_CONNECTION=g_SSH_CONNECTION,LocalCheckpointKey=g_LocalCheckpointKey):
        try:
            # Create SSH Connection
            rc, remote_conn, ssh = self.SSH_Connection(host=host, user=user, passwd=passwd,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
            if rc == False:
                self.logi.appendMsg("FAIL - SSH_Connection host= " + host + " , user=" + user)

            if FoundByProcessId == False:
                self.logi.appendMsg("INFO - Interactive SSH - killall -9 ffmpeg")
                remote_conn.send("date ; killall -9 ffmpeg\n")
            else:
                self.logi.appendMsg("INFO - Interactive SSH - kill -9 " + str(FoundByProcessId))
                remote_conn.send("date ; kill -9 " + str(FoundByProcessId) + "\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            remote_conn.send("\n")
            remote_conn.send("date ; ps aux|grep ffmpeg\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            if output.find(entryId) > 0:
                self.logi.appendMsg("FAIL - ffmpeg is streaming:Details: entryId = " + entryId + "  , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                return False
            else:
                self.logi.appendMsg("PASS - END STREAM - ffmpeg is NOT streaming: partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                return True

        except Exception as err:
            print(err)
            return False


    # Moran.Cohen
    # This function verifies that a list of entries is played or not by Qrcode
    # if the entries should play, send True in boolShouldPlay, if not send False
    # MinToPlayEntry = playable QRcode verification time for each entry.
    # PlayerVersion = player version 2/3
    # sniffer_fitler = Set filter to wireshark if needed
    # Protocol = https(default)/http
    def verifyAllEntriesPlayOrNoBbyQrcode(self, entryList, boolShouldPlay,MinToPlayEntry=1,PlayerVersion=3,flashvars=None,sniffer_fitler=None,Protocol='https',SourceSelector=None,flavorList=None,sniffer_filter_per_flavor_list=None,QrCodecheckProgress=4,MatchValue=False,ClosedCaption=False,languageList_Caption="English;",ServerURL=None):
        defStatus = True
        #i=1
        i=0
        for entry in entryList:
            self.logi.appendMsg("INFO - Going to click playing on entry - " + str(entry.id))
            rc,PlayBrowser = self.PlayEntryNew(2, entry.id,PlayerVersion,flashvars,Protocol,ServerURL=ServerURL)
            if isinstance(rc, bool):
                self.logi.appendMsg("FAIL - could not play the entry - " + str(entry.id))
                if boolShouldPlay == True:#If the entry should play-->return false
                    return False
                else:
                ##########ADDED#elif --> boolShouldPlay==false Need to add option of wn live test to search no playing(Currently not broadcasting/video will play once broadcasting starts alert)
                    self.logi.appendMsg("INFO - *********** Going to verify that there is NO playback by QRcoder (boolShouldPlay==false) on:************ENTRY#" + str(i) + " , entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , Start datetime = " + str(datetime.datetime.now()))
                    #isPlaying = self.verifyLiveisPlayingOverTime(PlayBrowser,MinToPlayEntry)
                    isPlaying = self.verifyLiveisPlayingOverTime(PlayBrowser, MinToPlayEntry,boolShouldPlay)
                    if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                        defStatus = False
                    else:
                        self.logi.appendMsg("PASS - NO Playback verification(boolShouldPlay==false) by QRCode on entry = "+ str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                    i=i+1
            else:
                try:  # Perform sniffer if needed
                    if sniffer_fitler != None:
                        self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                        MatchValue = self.ReturnMultiSnifferResutlByFitler(PlayBrowser, sniffer_fitler)
                        if MatchValue == False:
                            self.logi.appendMsg("FAIL - SNIFFER -  ReturnSnifferResutlByFitler-NOT Found for sniffer_fitler=" + str(sniffer_fitler))
                            defStatus = False
                    ###########
                    if SourceSelector == True:
                        self.logi.appendMsg("INFO - Going to verify SourceSelector on entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        rc = self.verifyFlavorSelector(PlayBrowser, flavorList=flavorList,sniffer_filter_per_flavor_list=sniffer_filter_per_flavor_list)
                        if rc == True:
                            self.logi.appendMsg("PASS - SourceSelector:Found flavors Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        else:
                            self.logi.appendMsg("FAIL - SourceSelector:NO flavors Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                            defStatus = False
                except Exception as err:
                    print(err)
                    defStatus = False
                    pass

                if ClosedCaption == True:
                    self.logi.appendMsg("INFO - Going to verify ClosedCaption on entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                    # rc = self.verifyLanguageSelector(PlayBrowser,languageList="English;")
                    rc = self.verifyLanguageSelector(PlayBrowser, languageList=languageList_Caption,DropDownType="captions")
                    if rc == True:
                        self.logi.appendMsg("PASS - ClosedCaption:Found language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        time.sleep(2)
                    else:
                        self.logi.appendMsg("FAIL - ClosedCaption:NO language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        defStatus = False

                self.logi.appendMsg("INFO - *********** Going to verify playback by QRcoder on:************ENTRY#" + str(i) + " , entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , Start datetime = " + str(datetime.datetime.now()))
                if QrCodecheckProgress==4:
                    isPlaying = self.verifyLiveisPlayingOverTime(PlayBrowser, MinToPlayEntry, boolShouldPlay)
                    #isPlaying = self.verifyLiveisPlayingOverTime_CheckRequestValue(wd=PlayBrowser, MinToPlayEntry=MinToPlayEntry, boolShouldPlay=boolShouldPlay,sniffer_fitler=sniffer_fitler)
                else:#trashhold between QRCode verification
                    isPlaying = self.verifyLiveisPlayingOverTime_trashhold(PlayBrowser, MinToPlayEntry, boolShouldPlay,QrCodecheckProgress=QrCodecheckProgress)
                if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                    defStatus = False
                    self.logi.appendMsg("FAIL - Playback verification by QRCode on entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                else:
                    self.logi.appendMsg("PASS - Playback verification by QRCode on entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                i=i+1

            try:
                PlayBrowser.quit()
            except:
                pass
            if MatchValue != False and defStatus == True:  # if you find your sniffer MatchValue on playback return it on True state
                defStatus = MatchValue

        '''ADD THE FOLDER CONTENT DELETION'''
        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'QRtemp'))
            filelist = [f for f in os.listdir(pth) if f.endswith(".png")]
            for f in filelist:
                os.remove(os.path.join(pth, f))
        except Exception as Exp:
            print("Exception while try to delete QRtemp folder - " + str(Exp))

        return defStatus

      
    # Moran.cohen
    # This function verifies for x minutes that a live stream plays ok and QR code progress on it
    # MinToPlayEntry = playable QRcode verification time for each entry.  
    def verifyLiveisPlayingOverTime(self, wd=None,MinToPlayEntry=1,boolShouldPlay=True,sniffer_fitler=None,DVR_BACK=False):
        time.sleep(1)
        try:
            if wd == None:
                wd = self.driver1
            PreviousTime_VTT = "00:00:00.000"
            QrCode = QrcodeReader.QrCodeReader(wbDriver=wd, logobj=self.logi)
            QrCode.initVals()
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlayEntry*60)
            while datetime.datetime.now() <= limitTimeout:        
                rc = QrCode.placeCurrPrevScr()
                if rc:
                    time.sleep(4)
                    rc = QrCode.placeCurrPrevScr()
                    if rc:
                        rc = QrCode.checkProgress(4)
                        if rc:
                            if boolShouldPlay == True:
                                self.logi.appendMsg("PASS - QrCode Video played as expected.datetime = " + str(datetime.datetime.now()))
                                # LIVE CAPTION VTT verification
                                if sniffer_fitler == 'vtt':  # sniffer_fitler != None:
                                    self.logi.appendMsg("INFO - Going to get LiveCaption_VerifyPlaybackVTT= " + str(datetime.datetime.now()))
                                    MatchValue = self.GetRequestFromPlayback(PlayBrowser=wd,sniffer_fitler=sniffer_fitler)
                                    rc_MatchValue, VTTContent, LastTimeOnCurrentVTT = self.LiveCaption_VerifyPlaybackVTT(rc_MatchValue=MatchValue)
                                    if rc_MatchValue == False:
                                        self.logi.appendMsg("FAIL - LiveCaption_VerifyPlaybackVTT MatchValue, Current datetime= " + str(datetime.datetime.now()))
                                        return False
                                    if (PreviousTime_VTT < LastTimeOnCurrentVTT and DVR_BACK==False) or PreviousTime_VTT == "00:00:00.000":  # Verify follower times between different VTT
                                        self.logi.appendMsg("PASS - Verify follower times between different VTTs: PreviousTime_VTT " + str(PreviousTime_VTT) + " < LastTimeOnCurrentVTT " + str(LastTimeOnCurrentVTT) + ", Current datetime= " + str(datetime.datetime.now()))
                                        PreviousTime_VTT = LastTimeOnCurrentVTT
                                        time.sleep(8)
                                    elif PreviousTime_VTT > LastTimeOnCurrentVTT and DVR_BACK==True: # DVR point back case
                                        self.logi.appendMsg("PASS - Verify back times between different VTTs because of DVR: PreviousTime_VTT " + str(PreviousTime_VTT) + " > LastTimeOnCurrentVTT " + str(LastTimeOnCurrentVTT) + ", Current datetime= " + str(datetime.datetime.now()))
                                        PreviousTime_VTT = LastTimeOnCurrentVTT
                                        time.sleep(6)
                                    else:
                                        self.logi.appendMsg("FAIL - Verify follower times between different VTTs: PreviousTime_VTT " + str(PreviousTime_VTT) + " >= LastTimeOnCurrentVTT " + str(LastTimeOnCurrentVTT) + ", Current datetime= " + str(datetime.datetime.now()))
                            else:
                                self.logi.appendMsg("FAIL - QrCode Video played despite that boolShouldPlay=False.datetime = " + str(datetime.datetime.now()))
                                return True #Case of return isPlaying=true when boolShouldPlay=False ->stop playing and return result
                        else:
                            self.logi.appendMsg("FAIL - Video was not progress by the QrCode displayed in it." + str(datetime.datetime.now()))
                            return False
                               
                    else:
                        self.logi.appendMsg("FAIL - Could not take second time QR code value after playing the entry." + str(datetime.datetime.now()))
                        return False
                else:
                    self.logi.appendMsg("FAIL - Could not take the QR code value after playing the entry." + str(datetime.datetime.now()))
                    return False
                
            return True
        except Exception as err:
            print(err)
            return False
    
       
    # Moran.cohen
    # This function return ffmpegCmdString with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_OLD(self,filePath,BroadcastingUrl,entryId):
        
        #BroadcastingUrl="'" + str(BroadcastingUrl) + "/" + str(entryId) + "_1" + "'"
        BroadcastingUrl='"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1' + '"'
        ffmpegCmdLine="date ; ffmpeg -re -stream_loop -1  -i " + str(filePath) + " -vcodec copy -acodec copy -f flv " + str(BroadcastingUrl) + " ; date "
        
        return ffmpegCmdLine

    # Moran.cohen
    # This function return ffmpegCmdString with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    #streamName = _%i previous BE config, New multi BE Region cloud 1/0
    def ffmpegCmdString(self, filePath, BroadcastingUrl, streamName):

        print("streamName = " + str(streamName))
        if streamName.find('%i') >= 0:
            streamName = streamName.replace('%i', '1')
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '"'
        else:#Support old logic-until changing all tests locations
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"'

        ffmpegCmdLine = "date ; ffmpeg -re -stream_loop -1  -i " + str(filePath) + " -vcodec copy -acodec copy -f flv " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine

    # Moran.cohen
    # This function return ffmpegCmdString of multi flaovrs  with printing start & end date
    # source_file1,source_file2,source_file3 = file Paths of wanted files to multi stream flavors , for example source_file1 = "/home/kaltura/entries/LongCloDvRec.mp4"
    # primaryBroadcastingUrl = primaryBroadcastingUrl for each entry.   
    def ffmpegCmdString_MultiFlavors_OLD(self,partnerId,primaryBroadcastingUrl,entryId,source_file1,source_file2,source_file3):
     
        source_stream1='"' + str(primaryBroadcastingUrl) + '/' + str(entryId) + '_1' + '"' 
        source_stream2='"' + str(primaryBroadcastingUrl) + '/' + str(entryId) + '_2' + '"'
        source_stream3='"' + str(primaryBroadcastingUrl) + '/' + str(entryId) + '_3' + '"'     
        #Need to check why libmp3lame is not working?   
        #ffmpegCmdLine="date ; ffmpeg -re -i " + source_file1 + " -re -i " + source_file2 + " -re -i " + source_file3 + " -map 0 -c:v copy -c:a libmp3lame -f flv " + source_stream1 + " -map 1 -c:v copy -c:a libmp3lame -f flv " + source_stream2 + " -map 2 -c:v copy -c:a libmp3lame -f flv " + source_stream3 + " ; date"
        ffmpegCmdLine="date ; ffmpeg -re -i " + source_file1 + " -re -i " + source_file2 + " -re -i " + source_file3 + " -map 0 -c:v copy -c:a copy -f flv " + source_stream1 + " -map 1 -c:v copy -c:a copy -f flv " + source_stream2 + " -map 2 -c:v copy -c:a copy -f flv " + source_stream3 + " ;date"

        return ffmpegCmdLine

    # Moran.cohen
    # This function return ffmpegCmdString of multi flaovrs  with printing start & end date
    # source_file1,source_file2,source_file3 = file Paths of wanted files to multi stream flavors , for example source_file1 = "/home/kaltura/entries/LongCloDvRec.mp4"
    # primaryBroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_MultiFlavors(self, partnerId, primaryBroadcastingUrl, streamName, source_file1,source_file2, source_file3):
        print("streamName = " + str(streamName))
        if streamName.find('%i') >= 0:
            source_stream1 = '"' + str(primaryBroadcastingUrl) + '/1' + '"'
            source_stream2 = '"' + str(primaryBroadcastingUrl) + '/2' + '"'
            source_stream3 = '"' + str(primaryBroadcastingUrl) + '/3' + '"'
        elif streamName.find('_%i') >= 0:  # Support old logic-until changing all tests locations
            streamName = streamName.replace('%i','')
            source_stream1 = '"' + str(primaryBroadcastingUrl) + '/' + str(streamName) + '_1' + '"'
            source_stream2 = '"' + str(primaryBroadcastingUrl) + '/' + str(streamName) + '_2' + '"'
            source_stream3 = '"' + str(primaryBroadcastingUrl) + '/' + str(streamName) + '_3' + '"'
        # Need to check why libmp3lame is not working?
        ffmpegCmdLine = "date ; ffmpeg -re -i " + source_file1 + " -re -i " + source_file2 + " -re -i " + source_file3 + " -map 0 -c:v copy -c:a copy -f flv " + source_stream1 + " -map 1 -c:v copy -c:a copy -f flv " + source_stream2 + " -map 2 -c:v copy -c:a copy -f flv " + source_stream3 + " ;date"

        return ffmpegCmdLine
    # Moran.cohen
    # This function return result streaming return from ffmpeg 
    # errorDescription - The string error that should be found on ffmpegOutputString
    def VerifyResultStringReturnFromffmpeg(self,ffmpegOutputString,errorDescription):
        
        errorDescription=errorDescription.lower()
        if ffmpegOutputString.lower().find(errorDescription) >= 0:
            self.logi.appendMsg("PASS - VerifyResultStringReturnFromffmpeg.datetime = " + str(datetime.datetime.now()) + " , errorDescription = " + errorDescription + " is found on ffmpegOutputString")
            return True
        else:
            self.logi.appendMsg("FAIL - VerifyResultStringReturnFromffmpeg.datetime = " + str(datetime.datetime.now()) + " , errorDescription = " + errorDescription + " is NOT found on ffmpegOutputString = " + ffmpegOutputString)
            return False
    
    # Moran.cohen
    # This function return result cpu load on linux/window machine (=Linux / Windows)
    # cmdline - the cmd line for cpu use
    def VerifyCPU_UsageMachine_OLD(self, host, user, passwd,cmdLine,machine="Linux"):
        try:
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd )
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            # Write ssh cmd line
            remote_conn = ssh.invoke_shell()
            self.logi.appendMsg("INFO - Interactive SSH - Going to run ps aux|grep ffmpeg") 
            output = remote_conn.recv(1000)
            remote_conn.send("\n")
            remote_conn.send("sudo su -" + "\n")
            remote_conn.send(cmdLine + "\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)                         
            time.sleep(2)
            return True,str(output)
          
        except Exception as err:
            print(err)
            return False,str(output)

    # Moran.cohen
    # This function return result cpu load on linux/window machine (=Linux / Windows)
    # cmdline - the cmd line for cpu use
    def VerifyCPU_UsageMachine(self, host, user, passwd, cmdLine,SSH_CONNECTION=g_SSH_CONNECTION,LocalCheckpointKey=g_LocalCheckpointKey):
        try:
            # Create SSH Connection
            rc, remote_conn, ssh = self.SSH_Connection(host=host, user=user, passwd=passwd,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
            if rc == False:
                self.logi.appendMsg("FAIL - SSH_Connection host= " + host + " , user=" + user)
            # Run cmdLine
            remote_conn.send(cmdLine + "\n")
            time.sleep(5)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            print(output)
            time.sleep(2)
            return True, str(output)

        except Exception as err:
            print(err)
            return False, str(output)

    # Moran.Cohen     
    # This function verifies that a list of entries is played or not by Capture2Text
    # if the entries should play, send True in boolShouldPlay, if not send False
    # MinToPlayEntry = playable Capture2Text verification time for each entry.
    # PlayerVersion = player version 2/3
    # boolShouldPlay - If the entry should play = True, else False
    # sniffer_fitler = Sniffer search string in the playback
    # AudioOnly - Set False as default.
    # MultiAudio (bool flag) and languageList(Options selection)
    # ClosedCaption(bool flag) languageList_Caption(Options selection)
    # sleepUntil_PlaybackVerifications - Sleep/wait time before performing playback verifications
    # languageList="Spanish;English" or Español on delivery profile LowL/redirect
    def verifyAllEntriesPlayOrNoBbyOnlyPlayback(self, entryList, boolShouldPlay, MinToPlayEntry=1, PlayerVersion=3,sniffer_fitler=None,sleepUntilCloseBrowser=0,ServerURL=None,flashvars=None, AudioOnly=False, MultiAudio=False,ClosedCaption=False,Protocol='https',languageList="Spanish;English", languageList_Caption="English;",sleepUntil_PlaybackVerifications=2,MatchValue=False,ClosedCaptionSingle=False):
        defStatus = True
        #i=1
        i=0
        for entry in entryList:
            self.logi.appendMsg("INFO - ****************** Going to click playing on ENTRY - " + str(entry.id))
            rc,PlayBrowser = self.PlayEntryNew(2, entry.id,PlayerVersion,flashvars,Protocol,ServerURL=ServerURL)
            time.sleep(sleepUntil_PlaybackVerifications)
            if isinstance(rc, bool):
                self.logi.appendMsg("FAIL - could not play the entry - " + str(entry.id))
                if boolShouldPlay == True:#If the entry should play-->return false
                    return False
                else:
                ##########ADDED#elif --> boolShouldPlay==false Need to add option of wn live test to search no playing(Currently not broadcasting/video will play once broadcasting starts alert)
                    self.logi.appendMsg("INFO - *********** Going to verify that there is NO playback by QRcoder (boolShouldPlay==false) on:************ENTRY#" + str(i) + " , entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , Start datetime = " + str(datetime.datetime.now())) 
                    isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(PlayBrowser,MinToPlayEntry)
                    if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                        defStatus = False
                    else:
                        self.logi.appendMsg("PASS - NO Playback verification(boolShouldPlay==false) by Capture2Text on entry = "+ str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                    i=i+1
                    try:
                        PlayBrowser.quit()
                    except:
                        pass
            else:
                try:  # Perform sniffer if needed
                    if sniffer_fitler != None:
                        # start pyshark on different thread
                        self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                        isMatch = 0
                        #searchTerm = 'm4s'
                        #saveToFile = 1
                        #saveOnlyMatchedEntry = 1
                        #FileName = "c:\Temp\PythonChromeTraceJson.txt"
                        #a_file = open(FileName, "w")
                        for row in PlayBrowser.get_log('performance'):
                            #if saveToFile == 1:#save all content log in file
                                #json.dump(row, a_file)
                            # print(row.get('message'))
                            if row.get('message', {}).find(sniffer_fitler) > -1:
                                isMatch = 1
                                # json.dump(row, a_file)#save just rows with the filter
                                break
                        #a_file.close()
                        if isMatch == 1:
                            self.logi.appendMsg("PASS - SNIFFER -  Found for sniffer_fitler = " + sniffer_fitler)
                            if MatchValue != False:
                                MatchValue=row.get('message', {})
                        else:
                            self.logi.appendMsg("FAIL - SNIFFER -  Did NOT find sniffer_fitler = " + sniffer_fitler)
                            defStatus = False

                except Exception as err:
                    print(err)
                    defStatus = False
                    pass
                if MultiAudio == True:
                    self.logi.appendMsg("INFO - Going to verify MultiAudio on entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                    rc = self.verifyLanguageSelector(PlayBrowser,languageList=languageList,DropDownType="audio")
                    if rc == True:
                        self.logi.appendMsg("PASS - verifyMultiAudio:Found language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        time.sleep(2)
                    else:
                        self.logi.appendMsg("FAIL - verifyMultiAudio:NO language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        defStatus = False
                if ClosedCaption == True:
                    self.logi.appendMsg("INFO - Going to verify ClosedCaption on entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                    rc = self.verifyLanguageSelector(PlayBrowser=PlayBrowser,languageList=languageList_Caption,DropDownType="captions",ClosedCaptionSingle=ClosedCaptionSingle)
                    if rc == True:
                        self.logi.appendMsg("PASS - ClosedCaption:Found language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        time.sleep(2)
                    else:
                        self.logi.appendMsg("FAIL - ClosedCaption:NO language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        defStatus = False

                self.logi.appendMsg("INFO - *********** Going to verify playback by Capture2Text on:************ENTRY#" + str(i) + " , entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , Start datetime = " + str(datetime.datetime.now()))
                #isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(PlayBrowser,MinToPlayEntry,AudioOnly)
                isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(wd=PlayBrowser,MinToPlayEntry=MinToPlayEntry,AudioOnly=AudioOnly,sniffer_fitler=sniffer_fitler)
                if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                    defStatus = False
                else:
                    self.logi.appendMsg("PASS - Playback verification by Capture2Text on entry = "+ str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                i=i+1
                time.sleep(sleepUntilCloseBrowser)
                try:
                    PlayBrowser.quit()
                except:
                    pass
                if MatchValue!=False and defStatus==True:#if you find your sniffer MatchValue on playback return it on True state
                    defStatus=MatchValue
        return defStatus

    # Moran.cohen
    # This function verifies for x minutes that a live stream plays ok by Capture2Text progress on it
    # MinToPlayEntry = playable Capture2Text verification time for each entry.  
    def verifyLiveisPlayingOverTimeByOnlyPlayback(self, wd=None,MinToPlayEntry=1,AudioOnly=False,sniffer_fitler=None,boolShouldPlay=True,DVR_BACK=False):
        try:
            if wd == None:
                wd = self.driver1
            PreviousTime_VTT="00:00:00.000"
            QrCode = QrcodeReader.QrCodeReader(wbDriver=wd, logobj=self.logi)
            QrCode.initVals()
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlayEntry*60)
            while datetime.datetime.now() <= limitTimeout:
                rc = QrCode.placeCurrPrevScr_OnlyPlayback()
                if rc:
                    time.sleep(4)
                    rc = QrCode.placeCurrPrevScr_OnlyPlayback()
                    if rc:
                        rc = QrCode.checkProgress_OnlyPlayback(4,AudioOnly)
                        if rc:
                            if boolShouldPlay == True:
                                self.logi.appendMsg("PASS - QrCode Video played as expected.datetime = " + str(datetime.datetime.now()))
                                # LIVE CAPTION VTT verification
                                if sniffer_fitler == '.vtt':  # sniffer_fitler != None:
                                    self.logi.appendMsg("INFO - Going to get LiveCaption_VerifyPlaybackVTT= " + str(datetime.datetime.now()))
                                    MatchValue = self.GetRequestFromPlayback(PlayBrowser=wd,sniffer_fitler=sniffer_fitler)
                                    rc_MatchValue, VTTContent, LastTimeOnCurrentVTT = self.LiveCaption_VerifyPlaybackVTT(rc_MatchValue=MatchValue)
                                    if rc_MatchValue == False:
                                        self.logi.appendMsg("FAIL - LiveCaption_VerifyPlaybackVTT MatchValue, Current datetime= " + str(datetime.datetime.now()))
                                        return False
                                    if (PreviousTime_VTT < LastTimeOnCurrentVTT and DVR_BACK == False) or PreviousTime_VTT == "00:00:00.000":  # Verify follower times between different VTT
                                        self.logi.appendMsg("PASS - Verify follower times between different VTTs: PreviousTime_VTT " + str(PreviousTime_VTT) + " < LastTimeOnCurrentVTT " + str(LastTimeOnCurrentVTT) + ", Current datetime= " + str(datetime.datetime.now()))
                                        PreviousTime_VTT = LastTimeOnCurrentVTT
                                        time.sleep(10)
                                    elif PreviousTime_VTT > LastTimeOnCurrentVTT and DVR_BACK == True:  # DVR point back case
                                        self.logi.appendMsg("PASS - Verify back times between different VTTs because of DVR: PreviousTime_VTT " + str(PreviousTime_VTT) + " > LastTimeOnCurrentVTT " + str(LastTimeOnCurrentVTT) + ", Current datetime= " + str(datetime.datetime.now()))
                                        PreviousTime_VTT = LastTimeOnCurrentVTT
                                        time.sleep(6)
                                    else:
                                        self.logi.appendMsg("FAIL - Verify follower times between different VTTs: PreviousTime_VTT " + str(PreviousTime_VTT) + " >= LastTimeOnCurrentVTT " + str(LastTimeOnCurrentVTT) + ", Current datetime= " + str(datetime.datetime.now()))
                            else:
                                self.logi.appendMsg("FAIL - QrCode Video played despite that boolShouldPlay=False.datetime = " + str(datetime.datetime.now()))
                                return True  # Case of return isPlaying=true when boolShouldPlay=False ->stop playing and return result
                        else:
                            self.logi.appendMsg("FAIL - Video was not progress by the QrCode displayed in it." + str(
                                datetime.datetime.now()))
                            return False
                else:
                    self.logi.appendMsg("FAIL - Could not take the Capture2Text value after playing the entry." + str(datetime.datetime.now()))
                    return False

            return True
        except Exception as err:
            print(err)
            return False

    # Moran.Cohen - WORKING ON
    # This function verifies that a list of entries is played or not by Qrcode
    # if the entries should play, send True in boolShouldPlay, if not send False
    # MinToPlayEntry = playable QRcode verification time for each entry.
    # PlayerVersion = player version 2/3
    # sniffer_fitler - sniffer string search on playback network
    #def verifyAllEntriesPlayOrNoBbyQrcode_DVR(self, entryList, boolShouldPlay,MinToPlayEntry=1,PlayerVersion=3,flashvars=None,CloseBrowser=True,sniffer_fitler=None,Protocol='https'):
    def verifyAllEntriesPlayOrNoBbyQrcode_DVR(self, entryList, boolShouldPlay, MinToPlayEntry=1, PlayerVersion=3, sniffer_fitler=None, CloseBrowser=True, flashvars=None, AudioOnly=False, MultiAudio=False, ClosedCaption=False, Protocol='https', languageList="Spanish;English", languageList_Caption="English;",MatchValue=False,QRCODE=True,ServerURL=None):
        defStatus = True
        #i=1
        i=0
        for entry in entryList:
            self.logi.appendMsg("INFO - Going to click playing on entry - " + str(entry.id))
            rc,PlayBrowser = self.PlayEntryNew(2, entry.id,PlayerVersion,flashvars,Protocol,ServerURL=ServerURL)
            if isinstance(rc, bool):
                self.logi.appendMsg("FAIL - could not play the entry - " + str(entry.id))
                if boolShouldPlay == True:#If the entry should play-->return false
                    return False,PlayBrowser
                else:
                ##########ADDED#elif --> boolShouldPlay==false Need to add option of wn live test to search no playing(Currently not broadcasting/video will play once broadcasting starts alert)
                    self.logi.appendMsg("INFO - *********** Going to verify that there is NO playback by QRcoder (boolShouldPlay==false) on:************ENTRY#" + str(i) + " , entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , Start datetime = " + str(datetime.datetime.now())) 
                    isPlaying = self.verifyLiveisPlayingOverTime(rc,MinToPlayEntry)
                    if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                        defStatus = False
                    else:
                        self.logi.appendMsg("PASS - NO Playback verification(boolShouldPlay==false) by QRCode on entry = "+ str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                    i=i+1     
                    PlayBrowser.quit()#move this option
            else:
                try:  # Perform sniffer if needed
                    if sniffer_fitler != None:
                        # start pyshark on different thread
                        self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                        isMatch = 0
                        # searchTerm = 'm4s'
                        # saveToFile = 1
                        # saveOnlyMatchedEntry = 1
                        # FileName = "c:\Temp\PythonChromeTraceJson.txt"
                        # a_file = open(FileName, "w")
                        for row in PlayBrowser.get_log('performance'):
                            # if saveToFile == 1:#save all content log in file
                            # json.dump(row, a_file)
                            # print(row.get('message'))
                            if row.get('message', {}).find(sniffer_fitler) > -1:
                                isMatch = 1
                                # json.dump(row, a_file)#save just rows with the filter
                                break
                        # a_file.close()
                        if isMatch == 1:
                            self.logi.appendMsg("PASS - SNIFFER -  Found for sniffer_fitler = " + sniffer_fitler)
                            if MatchValue != False:
                                MatchValue=row.get('message', {})
                        else:
                            self.logi.appendMsg("FAIL - SNIFFER -  Did NOT find sniffer_fitler = " + sniffer_fitler)
                            defStatus = False

                except Exception as err:
                    print(err)
                    defStatus = False
                    pass
                if MultiAudio == True:
                    self.logi.appendMsg("INFO - Going to verify MultiAudio on entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                    rc = self.verifyLanguageSelector(PlayBrowser,languageList=languageList,DropDownType="audio")
                    if rc == True:
                        self.logi.appendMsg("PASS - verifyMultiAudio:Found language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        time.sleep(2)
                    else:
                        self.logi.appendMsg("FAIL - verifyMultiAudio:NO language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        defStatus = False
                if ClosedCaption == True:
                    self.logi.appendMsg("INFO - Going to verify ClosedCaption on entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                    #rc = self.verifyLanguageSelector(PlayBrowser,languageList="English;")
                    rc = self.verifyLanguageSelector(PlayBrowser,languageList=languageList_Caption,DropDownType="captions")
                    if rc == True:
                        self.logi.appendMsg("PASS - ClosedCaption:Found language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        time.sleep(2)
                    else:
                        self.logi.appendMsg("FAIL - ClosedCaption:NO language Element on player entry = " + str(entry.id) + ", datetime = " + str(datetime.datetime.now()))
                        defStatus = False

                self.logi.appendMsg("INFO - *********** Going to verify playback by QRcoder on:************ENTRY#" + str(i) + " , entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , Start datetime = " + str(datetime.datetime.now()))
                if QRCODE==True:
                    isPlaying = self.verifyLiveisPlayingOverTime(wd=PlayBrowser,MinToPlayEntry=MinToPlayEntry,boolShouldPlay=boolShouldPlay,sniffer_fitler=sniffer_fitler)
                else:
                    isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(wd=PlayBrowser, MinToPlayEntry=MinToPlayEntry,sniffer_fitler=sniffer_fitler)
                if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                    defStatus = False
                else:
                    self.logi.appendMsg("PASS - Playback verification by QRCode on entry = "+ str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                i=i+1
                if CloseBrowser == True:    
                    PlayBrowser.quit()
                if MatchValue != False and defStatus == True:  # if you find your sniffer MatchValue on playback return it on True state
                    defStatus = MatchValue
                 
        return defStatus,PlayBrowser
     
    
    # Moran.Cohen
    # This function Create Simulive or Manual live Webcast schedule event By ASSAF PHP script - Return entryid
    # sessionEndOffset - Add default 5 minutes playback from  start time  
    #===================================================================
        # createWebcastEnv_Simulive_ManualLive.php
        # $sessionStart = $argv[1];
        # $sessionEnd = $argv[2];
        # $configFile = $argv[3];
        # $isSimulive = $argv[4]; #isSimulive="false" or "true"
        # $manualLiveHlsUrl = $argv[5];
        # $manualLiveBackupHlsUrl = $argv[6];
    #===================================================================
    def CreateSimuliveWecastByPHPscript_Linux(self, host, user, passwd,configFile,isSimulive=1,manualLiveHlsUrl="'" + "'",manualLiveBackupHlsUrl="'" + "'",timoutMax=5,sessionEndOffset=5,startTime=None,sessionTitle="AUTOMATION_BECore_Simulive_ManualLive",env="prod",PublisherID=None,UserSecret=None,url=None,conversionProfileID=None,kwebcastProfileId=None,eventsProfileId=None,vodId=None):

        import paramiko

        try:
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print ("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            time.sleep(5)
            if startTime == None:
                startTime = time.time()
            sessionStart = int(startTime)
            endTime = startTime + sessionEndOffset*60
            sessionEnd = int(endTime)#add 5 minutes
            self.logi.appendMsg('INFO - CreateSimuliveWecastByPHPscript LONG format sessionStart: ' + str(sessionStart) + ", sessionEnd = " + str(sessionEnd))
            self.logi.appendMsg('INFO - CreateSimuliveWecastByPHPscript DATE format sessionStart: ' + str(datetime.datetime.fromtimestamp(sessionStart).strftime('%Y-%m-%d %H:%M:%S')) + ", sessionEnd = " + str(datetime.datetime.fromtimestamp(sessionEnd).strftime('%Y-%m-%d %H:%M:%S')))
            datetime.datetime.fromtimestamp(sessionStart).strftime('%Y-%m-%d %H:%M:%S')
            
            if isSimulive==1:#simulive
                #Sef cmd live for php script
                #Simulive
                cmdLine = "php Moran_AUTOMATION/createWebcast/createWebcastEnv_argv.php " + str(sessionStart) + " " + str(sessionEnd) + " " + str(configFile) + " " + str(sessionTitle) + " " + str(PublisherID) + " " + str(UserSecret) + " " + str(url) + " " + str(conversionProfileID) + " " + str(kwebcastProfileId) + " " + str(eventsProfileId) + " " + str(vodId)

            else:#Manual live
                cmdLine="php Moran_AUTOMATION/createWebcast/createWebcastEnv_Simulive_ManualLive.php " +  str(sessionStart) + " " +  str(sessionEnd) + " " +  str(configFile)  + " " +  str(isSimulive) + " " +  str(manualLiveHlsUrl)  + " " +  str(manualLiveBackupHlsUrl)  + " " +  str(sessionTitle)
            self.logi.appendMsg('INFO - Going to run cmdLine: ' + str(cmdLine))

            ssh.exec_command("sudo su -" + "\n")
            stdin, stdout, stderr = ssh.exec_command(cmdLine)
            time.sleep(10)
            #############
            #Waiting to process to end - timoutMax = 8 x 10wait=> meaning waiting for 80sec until verify the stream
            self.logi.appendMsg('INFO - Waiting to process to end in CreateSimuliveWecastByPHPscript - cmdLine = ' + cmdLine) 
            timeout = 1
            while not stdout.channel.exit_status_ready():
                time.sleep(10)
                if stdout.channel.recv_ready() and stdout.channel.exit_status_ready():
                    print("Process is finished - Verify result -  ssh.exec_command " + cmdLine)
                    break
                if timeout > timoutMax:#timout
                    print("Timeout - Process is running - Not finished - ssh.exec_command" + cmdLine)
                    self.logi.appendMsg('INFO - Timeout - Process is running - Not finished - ssh.exec_command' + cmdLine)
                    break
                print("ssh.exec_command is processing.")
                self.logi.appendMsg('INFO - ssh.exec_command is processing')
                timeout=timeout+1              
            ###############
            ssh.close()
            result = stdout.read()
        
            if result == "" or result == "0":
                return False,"No entry return from php script"
                                    
            if result[0] == "0" and env =="prod":#if first character is 0
                result = result[1:] #remove first character
            result = str(result).split("'")[1].replace('\\n', '')
            if result[0:2] =="00" or result[0:2] =="01":
                result = result[1:]
            SimuliveEntryID=str(result.strip())#remove spaces and \n
            if SimuliveEntryID:
                return True,SimuliveEntryID
        except Exception as err:
            return False,err
    
    
    # Moran.Cohen
    # This function Create Simulive or Manual live Webcast schedule event By ASSAF PHP script - Return entryid
    # sessionEndOffset - Add default 5 minutes playback from  start time  
    #===================================================================
        # createWebcastEnv_Simulive_ManualLive.php
        # $sessionStart = $argv[1];
        # $sessionEnd = $argv[2];
        # $configFile = $argv[3];
        # $isSimulive = $argv[4]; #isSimulive="false" or "true"
        # $manualLiveHlsUrl = $argv[5];
        # $manualLiveBackupHlsUrl = $argv[6];
    #===================================================================
    #def CreateSimuliveWecastByPHPscript(self, host, user, passwd,configFile,isSimulive=1,manualLiveHlsUrl="'" + "'",manualLiveBackupHlsUrl="'" + "'",timoutMax=5,sessionEndOffset=5,env="prod",startTime=None):
    def CreateSimuliveWecastByPHPscriptSTRESS(self, host, user, passwd,configFile,isSimulive=1,manualLiveHlsUrl="'" + "'",manualLiveBackupHlsUrl="'" + "'",timoutMax=5,sessionEndOffset=5,startTime=None,sessionTitle="AUTOMATION_BECore_Simulive_ManualLive",env="prod",NumOfEntries=1):
        import paramiko

        try:
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            time.sleep(5)
            tmpTitle=sessionTitle
            ssh.exec_command("sudo su -" + "\n")
            for i in range(0, NumOfEntries):
                try:
                    sessionTitle = '08_ENTRY' + str(i) + '_'  + tmpTitle 
                    self.logi.appendMsg('INFO - ADD ENTRY: sessionTitle: ' + str(sessionTitle))
                    if startTime == None:
                        startTime = time.time()
                    sessionStart = int(startTime)
                    endTime = startTime + sessionEndOffset*60
                    sessionEnd = int(endTime)#add 5 minutes
                    self.logi.appendMsg('INFO - CreateSimuliveWecastByPHPscript LONG format sessionStart: ' + str(sessionStart) + ", sessionEnd = " + str(sessionEnd))
                    self.logi.appendMsg('INFO - CreateSimuliveWecastByPHPscript LONG format sessionStart: ' + str(datetime.datetime.fromtimestamp(sessionStart).strftime('%Y-%m-%d %H:%M:%S')) + ", sessionEnd = " + str(datetime.datetime.fromtimestamp(sessionEnd).strftime('%Y-%m-%d %H:%M:%S')))
                    datetime.datetime.fromtimestamp(sessionStart).strftime('%Y-%m-%d %H:%M:%S')
                    
                    if isSimulive==1:#simulive
                        # Sef cmd live for php script
                        #Simulive
                        cmdLine="php Moran_AUTOMATION/createWebcast/createWebcastEnv.php " +  str(sessionStart) + " " +  str(sessionEnd) + " " +  str(configFile)  + " " +  str(sessionTitle)
                    else:#Manual live
                        cmdLine="php Moran_AUTOMATION/createWebcast/createWebcastEnv_Simulive_ManualLive.php " +  str(sessionStart) + " " +  str(sessionEnd) + " " +  str(configFile)  + " " +  str(isSimulive) + " " +  str(manualLiveHlsUrl)  + " " +  str(manualLiveBackupHlsUrl)  + " " +  str(sessionTitle)
                    self.logi.appendMsg('INFO - Going to run cmdLine: ' + str(cmdLine))

                    stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=3, get_pty=True)
                    
                    time.sleep(10)
                    #ssh.close()
                    result = stdout.read()
                    if result[0] == "0" and env =="prod":#if first character is 0
                        result = result[1:] #remove first character
                    SimuliveEntryID=str(result.strip())#remove spaces and \n
                    self.logi.appendMsg('PASS - SimuliveEntryID: ' + str(SimuliveEntryID))
                except Exception as err:
                    print(err)
                    pass    
            
            ssh.close()
            return True
        except Exception as err:
            return False
    
    
    # Moran.cohen
    # This function return ffmpegCmdString_AudioOnly with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    # ffmpeg -re -i <AUDIO-FILE> -acodec aac -f flv "<URL>" 
    def ffmpegCmdString_AudioOnly(self,filePath,BroadcastingUrl,streamName):
        #BroadcastingUrl="'" + str(BroadcastingUrl) + "/" + str(entryId) + "_1" + "'"
        if streamName.find('%i') >= 0:
            streamName = streamName.replace('%i', '1')
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '"'
        else:  # Support old logic-until changing all tests locations
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"'
        ffmpegCmdLine="date ; ffmpeg -re -stream_loop -1  -i " + str(filePath) + " -vn -acodec aac -f flv " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine

    # Moran.cohen
    # This function return ffmpegCmdString with gop and bitrate +  printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_gop(self, filePath, BroadcastingUrl, streamName,IsSRT=False):

        if IsSRT==True:
            ffmpegCmdLine = "date ; ffmpeg  -re -stream_loop -1 -i " + str(filePath) + " -c:v libx264 -pix_fmt yuv420p -tune zerolatency -b:v 3M -g 120 -c:a copy -f mpegts " + str(BroadcastingUrl) + " ; date "
        else:
            #BroadcastingUrl = "'" + str(BroadcastingUrl) + "/" + str(entryId) + "_1" + "'"
            if streamName.find('%i') >= 0:
                streamName = streamName.replace('%i', '1')
                BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '"'
            else:  # Support old logic-until changing all tests locations
                BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"'
            ffmpegCmdLine = "date ; ffmpeg  -re -stream_loop -1 -i " + str(filePath) + " -c:v libx264 -pix_fmt yuv420p -tune zerolatency -b:v 3M -g 120 -c:a copy -f flv " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine

    #Moran.Cohen
    # This function return True or False if mp4 flavors uploaded with status ok (ready-2)
    # newEntryId = entry id of the recorded entry.
    # myentry = KalturaBaseEntry() object
    # Max_timeout for waiting to all flavors to finish status 2/4 - Default value 1200 , meaning 20 minutes
    def WaitForFlavorsMP4uploaded(self,client,newEntryId,myentry,expectedFlavors_totalCount=None,Max_timeout=1200):
        status = True
        time.sleep(60)
        if not isinstance(newEntryId, bool):
            time.sleep(15)
            startTime = time.time()
            timeisfinish = False
            interStatus = False
            while not timeisfinish:
                time.sleep(1)
                # Check that the flavors in status OK wait 20 minutes for that
                filter = KalturaAssetFilter()
                filter.entryIdEqual = newEntryId
                pager = KalturaFilterPager()
                EntryFlavors = client.flavorAsset.list(filter, pager)
                for i in range(0, EntryFlavors.totalCount):
                    if EntryFlavors.objects[i].status.value != 2 and EntryFlavors.objects[i].status.value != 4: #NOT_APPLICABLE = 4 READY = 2
                        interStatus = False
                        continue
                    else:
                        interStatus = True

                if interStatus:
                    if expectedFlavors_totalCount != None and expectedFlavors_totalCount != EntryFlavors.totalCount:
                        if time.time() - startTime > Max_timeout:
                            timeisfinish = True
                            self.logi.appendMsg("FAIL - The Entry actual flavors count don't match to expected after 20 minutes.newEntryId = " + newEntryId + " , expectedFlavors_totalCount = " + str(expectedFlavors_totalCount) + ", Actual EntryFlavors.totalCount=" + str(EntryFlavors.totalCount))
                            status = False
                            break
                        interStatus = False
                        continue# if not arrive to timeout -> continue to check flavors
                    else:
                        self.logi.appendMsg("PASS - The Entry got all EXPECTED flavors with status OK (ready-2/NA-4) after - " + str(time.time() - startTime) + " Seconds.newEntryId =" + newEntryId + " , Actual flavors totalCount = " + str(EntryFlavors.totalCount))
                        timeisfinish = True

                else:
                    if time.time() - startTime > Max_timeout:
                        timeisfinish = True
                        self.logi.appendMsg("FAIL - The Entry flavors did NOT get status OK(ready-2/NA-4) after 20 minutes.newEntryId = " + newEntryId)
                        status = False

        if status == False:
            return False
        else:
            return True

    # Moran.cohen
    # This function return ffmpegCmdString_MultiAudio with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    # the file disney_ma.mp4 is always video + eng + spanish - 1012 in this case is korean flavor but with eng audio (as eng is that audio),1013 is turkish
    def ffmpegCmdString_MultiAudio_OLD(self, filePath, BroadcastingUrl, entryId,languages=None):
        if languages==None:
            source_stream1 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1' + '"'  #video
            source_stream2 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1000' + '"' #eng
            source_stream3 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1001' + '"' #spanish
        elif languages=="KoreanTurkish":
            source_stream1 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1' + '"'  # video
            source_stream2 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1012' + '"' # 1012 in this case is korean flavor but with eng audio
            source_stream3 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1013' + '"' # 1013 is turkish but with spanish audio

        ffmpegCmdLine = "date ; ffmpeg -re -stream_loop -1 -i " + str(filePath) + " -map 0:0 -c:v copy -g 25 -c:a copy -bsf:a aac_adtstoasc -f flv -rtmp_live 1 " + str(source_stream1) + " -map 0:1 -c:a copy -bsf:a aac_adtstoasc -f flv -rtmp_live 1 " + str(source_stream2) + " -map 0:2 -c:a copy -bsf:a aac_adtstoasc -f flv -rtmp_live 1 " + str(source_stream3) + " ; date "

        return ffmpegCmdLine

    # Moran.cohen
    # This function return ffmpegCmdString_MultiAudio with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    # the file disney_ma.mp4 is always video + eng + spanish - 1012 in this case is korean flavor but with eng audio (as eng is that audio),1013 is turkish
    def ffmpegCmdString_MultiAudio(self, filePath, BroadcastingUrl, streamName,languages=None):
        print("streamName = " + str(streamName))
        if languages==None:
            if streamName.find('%i') >= 0:
                source_stream1 = '"' + str(BroadcastingUrl) + '/1' + '"' #video
                source_stream2 = '"' + str(BroadcastingUrl) + '/1000' + '"' #eng
                source_stream3 = '"' + str(BroadcastingUrl) + '/1001' + '"' #spanish
            elif streamName.find('_%i') >= 0:  # Support old logic-until changing all tests locations
                streamName = streamName.replace('%i', '')
                source_stream1 = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"' #video
                source_stream2 = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1000' + '"'#eng
                source_stream3 = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1001' + '"'#spanish
        elif languages=="KoreanTurkish":
            if streamName.find('%i') >= 0:
                source_stream1 = '"' + str(BroadcastingUrl) + '/1' + '"'  # video
                source_stream2 = '"' + str(BroadcastingUrl) + '/1012' + '"'  # 1012 in this case is korean flavor but with eng audio
                source_stream3 = '"' + str(BroadcastingUrl) + '/1013' + '"'  # 1013 is turkish but with spanish audio
            elif streamName.find('_%i') >= 0:  # Support old logic-until changing all tests locations
                streamName = streamName.replace('%i', '')
                source_stream1 = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"'  # video
                source_stream2 = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1012' + '"'   # 1012 in this case is korean flavor but with eng audio
                source_stream3 = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1013' + '"'  # 1013 is turkish but with spanish audio

        ffmpegCmdLine = "date ; ffmpeg -re -stream_loop -1 -i " + str(filePath) + " -map 0:0 -c:v copy -g 25 -c:a copy -bsf:a aac_adtstoasc -f flv -rtmp_live 1 " + str(source_stream1) + " -map 0:1 -c:a copy -bsf:a aac_adtstoasc -f flv -rtmp_live 1 " + str(source_stream2) + " -map 0:2 -c:a copy -bsf:a aac_adtstoasc -f flv -rtmp_live 1 " + str(source_stream3) + " ; date "

        return ffmpegCmdLine


    # Moran.cohen
    # This function return ffmpegCmdString_ClosedCaption with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/close-caption.txt"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_ClosedCaption(self, filePath, BroadcastingUrl, streamName):
        #source_stream1 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1' + '"'
        if streamName.find('%i') >= 0:
            streamName = streamName.replace('%i', '1')
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '"'
        elif streamName.find('_%i') >= 0:  # Support old logic-until changing all tests locations
            streamName = streamName.replace('%i', '')
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"'

        ffmpegCmdLine = "date ; ffmpeg -re -f concat -safe 0 -i  " + str(filePath) + "  -c:v copy -c:a copy -c:s copy -f flv   " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine

    # Moran.cohen
    # This function return ffmpegCmdString_ClosedCaption with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/close-caption.txt"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_ClosedCaption_OLD(self, filePath, BroadcastingUrl, streamName):
        # source_stream1 = '"' + str(BroadcastingUrl) + '/' + str(entryId) + '_1' + '"'
        if streamName.find('%i') >= 0:
            streamName = streamName.replace('%i', '1')
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '"'
        else:  # Support old logic-until changing all tests locations
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '/' + str(streamName) + '_1' + '"'

        # ffmpegCmdLine = "date ; ffmpeg -re -f concat -safe 0 -i  " + str(filePath) + "  -c:v copy -c:a copy -c:s copy -f flv   " + str(source_stream1) + " ; date "
        ffmpegCmdLine = "date ; ffmpeg -re -f concat -safe 0 -i  " + str(
            filePath) + "  -c:v copy -c:a copy -c:s copy -f flv   " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine
    # Moran.cohen
    # This function return verifyMultiAudio/ClosedCaption by verifyLanguageSelector exists True/false
    # languageList of the multi audio language options
    # isV7 - Select player v3/7 or player v2
    # DropDownType = "audio" or "captions"
    def verifyLanguageSelector(self,PlayBrowser,languageList="Spanish;English",isV7=True,DropDownType=None,ClosedCaptionSingle=False):
        try:
            if isV7:
                self.logi.appendMsg("INFO - Player V3/7:Going to check the Language selector. ")
                action = ActionChains(PlayBrowser)
                element = PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_INTERACTIVE_AREA_V7)  # select area of player v3/7
                action.move_to_element(element)
                action.perform()
            else:#Not ready - Player v2
                self.logi.appendMsg("INFO - Player V2 automation is not supported for now. ")

            #Move to player area
            ActionChains(PlayBrowser).move_to_element(element).perform()
            #press on language button
            #time.sleep(1) #removed last
            Timeout_cnt=0
            while Timeout_cnt < 2:
                try:
                    if ClosedCaptionSingle==True:
                        #PlayBrowser.find_element_by_xpath("//i[contains(@class,'playkit-icon playkit-icon-closed-captions')]").click()
                        PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_CAPTION_MAIN_BUTTON).click()
                    else:
                        PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_ICON_LANGUAGE_V7).click()

                    break
                except Exception as e:
                    action = ActionChains(PlayBrowser)
                    element = PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_INTERACTIVE_AREA_V7)  # select area of player v3/7
                    action.move_to_element(element)
                    action.perform()
                    if Timeout_cnt < 2:
                        Timeout_cnt = Timeout_cnt + 1
                        pass
                    else:
                        self.logi.appendMsg("FAIL - Timeout_cnt:Language selector on player.Exception_Err = " + str(e))
                        return False

            time.sleep(1)
            if ClosedCaptionSingle == True:# Finish test if Closed caption
                self.logi.appendMsg("PASS - Closed caption - Language " + str(languageList[0]) + " on player.")
                return True

            if languageList.find(";") >= 0:  # Multi LANGUAGE options
                arrlanguageList = languageList.split(";")
                for currentLanguage in arrlanguageList:
                    if currentLanguage == "":
                        break
                    Timeout_cnt = 0
                    while Timeout_cnt < 2:
                        try:
                            if DropDownType!=None:#if there is type audio/captions
                                PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_DROPDOWN_LANGUAGE_V7.replace("TEXTTOREPLACE",DropDownType)).click()
                            else:
                                # Press on dropdown
                                PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_DROPDOWN_LANGUAGE_V7).click()
                            break
                        except Exception as e:
                            action = ActionChains(PlayBrowser)
                            element = PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_INTERACTIVE_AREA_V7)  # select area of player v3/7
                            action.move_to_element(element)
                            action.perform()
                            PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_ICON_LANGUAGE_V7).click()
                            if Timeout_cnt < 2:
                                Timeout_cnt = Timeout_cnt + 1
                                pass
                            else:
                                self.logi.appendMsg("FAIL - Timeout_cnt:Language selector on player-PLAYER_MULTIAUDIO_DROPDOWN_LANGUAGE_V7.Exception_Err = " + str(e))
                                return False


                    #PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_SELECT_LANGUAGE_V7.replace("TEXTTOREPLACE",currentLanguage)).click()#Select the current Language
                    PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_SELECT_LANGUAGE_V7.replace("TEXTTOREPLACE",currentLanguage).replace("TMP_DropDownType",DropDownType)).click()  # Select the current Language

                    # select language
                    time.sleep(4)
                    self.logi.appendMsg("PASS - Language " + str(currentLanguage) + " was selected on player.")
            else:
                self.logi.appendMsg("FAIL - languageList - Missing ; on languageList.languageList = " + languageList )
                return False
            #Close language button
            PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_MULTIAUDIO_ICON_LANGUAGE_V7).click()

            return True


        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - Language selector on player.")
            return False

    ''' Moran.Cohen 
    This function login to linux ssh and then searching for ffmpeg process.
    SSH_CONNECTION = run streamer on local computer OR remote streamer machine by user&key OR remote streamer machine by user&pwd
    timoutMax = max timout for waiting to ffmpeg process.
    env=testing/prod
    HybridCDN = adminconsole.config window ->if HybridCDN=True different url from the entry.BroadcastingUrl(from kmc drilldown)
    '''
    def SearchPsAuxffmpeg_ByProcessId(self,host, user, passwd,entryId,partnerId,timoutMax=10,env='testing',BroadcastingUrl=None,HybridCDN=False,srtPass=None,SSH_CONNECTION=g_SSH_CONNECTION,LocalCheckpointKey=g_LocalCheckpointKey):
        try:
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            statusStreaming = False

            if srtPass==None:
                BroadcastingUrl = '"' + str(BroadcastingUrl) + '"'
            cmdLine = "ps aux |grep -v bash |grep ffmpeg | grep -F " + BroadcastingUrl #-v is for remove bash

            # Create SSH Connection
            rc, remote_conn, ssh = self.SSH_Connection(host=host, user=user, passwd=passwd,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
            if rc == False:
                self.logi.appendMsg("FAIL - SSH_Connection host= " + host)
            # Run cmdLine and then get ProcessId
            remote_conn.send(cmdLine + "\n")
            time.sleep(2)
            stdout = str(remote_conn.recv(1000))
            output_ProcessId = stdout.split("root")[2]

            ###### Get ProcessId from cmd output_ProcessId
            if output_ProcessId:
                ssh.close()
                print(str(output_ProcessId))
                arrProcessId=[]
                arrProcessId=output_ProcessId.split(" ")
                for i in arrProcessId:
                    if i !="" and i != 'root' and i.isdigit():
                        output_ProcessId=i
                        statusStreaming = True
                        break
                if statusStreaming==True:
                    output_ProcessId=str(int(output_ProcessId))
                    return True,output_ProcessId
                else:
                    return False, "NoProcessId"

            #Try again to search for ProcessId until timeout
            timeout = 0
            for timeout in range(0, timoutMax):
                time.sleep(5)
                print("Waiting to ffmpeg ps - ssh.exec_command is processing.cmdLine" + cmdLine)
                if g_SSH_CONNECTION == "LINADMIN_SSH":# Run on linadmin streamer
                    stdin, stdout, stderr = ssh.exec_command(f"""ssh -i  nva1-live-streamers-key {user}@{host} {cmdLine}""",timeout=10, get_pty=True)
                else:#Run on remote machine
                    stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=10, get_pty=True)
                #subprocess.Popen(f"ssh -i  nva1-live-streamers-key {user}@{host} {cmdLine}", shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                output_ProcessId = stdout.read().decode('ascii')
                if output_ProcessId:
                    statusStreaming = True
                    self.logi.appendMsg("PASS - ffmpeg is streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                    break
                if timeout > timoutMax:
                    statusStreaming = False
                    self.logi.appendMsg("FAIL - TIMEOUT - ffmpeg is NOT streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                    break

                timeout = timeout + 1

            if statusStreaming == False:
                return False, "NoProcessId"

            ssh.close()
            print(str(output_ProcessId))
            arrProcessId = []
            arrProcessId = output_ProcessId.split(" ")
            for i in range(0, len(arrProcessId)):
                if arrProcessId[i] != "" and arrProcessId[i] != 'root' and arrProcessId[i].isdigit() and arrProcessId[i-1]=="root":
                    output_ProcessId = i
                    statusStreaming = True
                    break
            if statusStreaming == True:
                output_ProcessId = str(int(output_ProcessId))
                return True, output_ProcessId
            else:
                return False, "NoProcessId"

        except Exception as err:
            print(err)
            return False, "NoProcessId"

    def SearchPsAuxffmpeg_ByProcessId_OLD(self, host, user, passwd, entryId, partnerId, timoutMax=10, env='testing',BroadcastingUrl=None, HybridCDN=False, srtPass=None):
        try:
            self.logi.appendMsg(
                "INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            statusStreaming = False
            # cmdLine ="pidof ffmpeg '" + BroadcastingUrl + "'"
            # ##############
            # if BroadcastingUrl == None or HybridCDN == True:
            #     if env == 'prod':
            #         searchPSstring = entryId + ".p.kpublish.kaltura.com:1935"
            #     else:  # testing
            #         searchPSstring = "p=" + partnerId + "&e=" + entryId
            # else:
            #     searchPSstring = str(BroadcastingUrl)
            # ###############
            if srtPass == None:
                BroadcastingUrl = '"' + str(BroadcastingUrl) + '"'
            cmdLine = "ps aux |grep -v bash |grep ffmpeg | grep -F " + BroadcastingUrl  # -v is for remove bash
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            connection = ssh.invoke_shell()
            ssh.exec_command("sudo su -" + "\n")
            stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=60, get_pty=True)  # timeout=10
            time.sleep(5)
            # ssh.close()
            output_ProcessId = stdout.read().decode('ascii')
            # if output_ProcessId.find("bash")>=0 and output_ProcessId.find("\n") <= 0:
            #    return False, "NoProcessId"
            if output_ProcessId:
                ssh.close()
                print(str(output_ProcessId))
                arrProcessId = []
                arrProcessId = output_ProcessId.split(" ")
                for i in arrProcessId:
                    if i != "" and i != 'root' and i.isdigit():
                        output_ProcessId = i
                        statusStreaming = True
                        break
                if statusStreaming == True:
                    output_ProcessId = str(int(output_ProcessId))
                    return True, output_ProcessId
                else:
                    return False, "NoProcessId"

            timeout = 0
            for timeout in range(0, timoutMax):
                time.sleep(5)
                print("Waiting to ffmpeg ps - ssh.exec_command is processing.cmdLine" + cmdLine)

                stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=10, get_pty=True)
                output_ProcessId = stdout.read().decode('ascii')
                if output_ProcessId:
                    statusStreaming = True
                    self.logi.appendMsg("PASS - ffmpeg is streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                    break
                if timeout > timoutMax:
                    statusStreaming = False
                    self.logi.appendMsg("FAIL - TIMEOUT - ffmpeg is NOT streaming:Details: entryId = " + entryId + " , partnerId = " + partnerId + " , Date = " + str(datetime.datetime.now()))
                    break

                timeout = timeout + 1

            if statusStreaming == False:
                return False, "NoProcessId"

            ssh.close()
            print(str(output_ProcessId))
            arrProcessId = []
            arrProcessId = output_ProcessId.split(" ")
            for i in arrProcessId:
                if i != "" and i != 'root' and i.isdigit():
                    output_ProcessId = i
                    statusStreaming = True
                    break
            if statusStreaming == True:
                output_ProcessId = str(int(output_ProcessId))
                return True, output_ProcessId
            else:
                return False, "NoProcessId"

        except Exception as err:
            print(err)
            return False, "NoProcessId"

    # Moran.cohen
    # This function return FlavorSelector by verifyverifyFlavorSelector exists True/false
    # flavor list of the multi audio language options
    # isV7 - Select player v3/7 or player v2
    def verifyFlavorSelector(self,PlayBrowser,flavorList="Auto;720p;480p;360p",isV7=True,sniffer_filter_per_flavor_list=None):
        try:
            status=True
            if isV7:
                self.logi.appendMsg("INFO - Player V3/7:Going to check the flavor selector. ")
                action = ActionChains(PlayBrowser)
                element = PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_INTERACTIVE_AREA_V7)  # select area of player v3/7
                action.move_to_element(element)
                action.perform()
            else:#Not ready - Player v2
                self.logi.appendMsg("INFO - Player V2 automation is not supported for now. ")

            #Move to player area
            ActionChains(PlayBrowser).move_to_element(element).perform()
            #press on flavor selector button
            time.sleep(1)
            PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_ICON_FLAVOUR_SELECTOR_V7).click()
            time.sleep(1)
            i=0
            if flavorList.find(";") >= 0:  # Multi flavors options
                arrflavorList = flavorList.split(";")
                for currentFlavor in arrflavorList:
                    if currentFlavor == "":
                        break
                    try:
                        # Press on dropdown
                        PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_FLAVOUR_SELECTOR_DROPDOWN_V7).click()
                    except Exception as e:
                        print(e)
                        PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_ICON_FLAVOUR_SELECTOR_V7).click()
                        pass
                    PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_FLAVOUR_SELECTOR_SELECT_V7.replace("TEXTTOREPLACE",currentFlavor)).click()
                    # select flavor
                    time.sleep(6)
                    self.logi.appendMsg("PASS - Flavor " + str(currentFlavor) + " was selected on player.")
                    #######################################
                    if sniffer_filter_per_flavor_list != None:
                        # start pyshark on different thread
                        self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                        #####################
                        if sniffer_filter_per_flavor_list.find(";") >= 0:  # Multi flavors options
                            try:
                                arr_sniffer_filter_per_flavor_list = sniffer_filter_per_flavor_list.split(";")

                                currentFlavorSniffer=arr_sniffer_filter_per_flavor_list[i]
                                if currentFlavorSniffer == "":
                                    break
                                if arr_sniffer_filter_per_flavor_list.__len__() !=arrflavorList.__len__():
                                    self.logi.appendMsg('FAIL  - SNIFFER count:arr_sniffer_filter_per_flavor_list' + str(arr_sniffer_filter_per_flavor_list.__len__())) + ' different from arrflavorList' + str(arrflavorList.__len__())
                                    status=False
                                    break
                                # Press on dropdown
                                #PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_FLAVOUR_SELECTOR_DROPDOWN_V7).click()
                                isMatch = 0
                                # searchTerm = 'm4s'
                                # saveToFile = 1
                                # saveOnlyMatchedEntry = 1
                                # FileName = "c:\Temp\PythonChromeTraceJson.txt"
                                # a_file = open(FileName, "w")
                                for row in PlayBrowser.get_log('performance'):
                                    # if saveToFile == 1:#save all content log in file
                                    # json.dump(row, a_file)
                                    # print(row.get('message'))
                                    if row.get('message', {}).find(currentFlavorSniffer) > -1:
                                        isMatch = 1
                                        self.logi.appendMsg("PASS - SNIFFER:Found currentFlavorSniffer= " + str(currentFlavorSniffer) + " for Flavor " + str(currentFlavor) + " was selected on player.")
                                        i=i+1
                                        # json.dump(row, a_file)#save just rows with the filter
                                        break
                                if isMatch == 0:
                                    self.logi.appendMsg("FAIL - SNIFFER:NO Found currentFlavorSniffer= " + str(currentFlavorSniffer) + " for Flavor " + str(currentFlavor) + " was selected on player.")
                                    status = False
                            except Exception as e:
                                print(e)
                                self.logi.appendMsg("FAIL - SNIFFER Flavor:NOT found " + str(currentFlavor) + " with  currentFlavorSniffer=" + str(currentFlavorSniffer))
                      ##########################################
            else:
                self.logi.appendMsg("FAIL - flavorList - Missing ; on flavorList.flavorList = " + flavorList)
                return False
            time.sleep(2)

            self.logi.appendMsg("INFO - Return BACK to first on the flavorList = " + arrflavorList[0])
            try:
                # Press on dropdown
                PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_FLAVOUR_SELECTOR_DROPDOWN_V7).click()
            except Exception as e:
                print(e)
                PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_ICON_FLAVOUR_SELECTOR_V7).click()
                pass
            # Return back to Auto - first on the list
            PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_FLAVOUR_SELECTOR_SELECT_V7.replace("TEXTTOREPLACE", arrflavorList[0])).click()
            time.sleep(2)
            # Close flavor selector button
            PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_ICON_FLAVOUR_SELECTOR_V7).click()
            time.sleep(2)
            time.sleep(4)#added time

            return status

        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - Flavor selector on player.")
            return False

    # Moran.cohen
    # This function return ffmpegCmdString of multi flavors  with printing start & end date according to MAP
    # primaryBroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_MultiFlavors_MAP_OLD(self, partnerId, primaryBroadcastingUrl, entryId):

        source_stream1 = '"' + str(primaryBroadcastingUrl) + '/' + str(entryId) + '_1' + '"'
        source_stream2 = '"' + str(primaryBroadcastingUrl) + '/' + str(entryId) + '_2' + '"'
        source_stream3 = '"' + str(primaryBroadcastingUrl) + '/' + str(entryId) + '_3' + '"'
        #ffmpegCmdLine='date;ffmpeg -re -f concat -safe 0 -i source -re -f concat -safe 0 -i 480p -re -f concat -safe 0 -i 360p -map 0 -c:v copy -c:a copy -f flv "'"rtmp://rtmp-0.cluster-1-a.live.nvq1.ovp.kaltura.com:1935/kLive?p=231&e=0_6as76tby&i=0&t=cec57e01/0_6as76tby_1"'" -map 1 -c:v copy -c:a copy -f flv "'"rtmp://rtmp-0.cluster-1-a.live.nvq1.ovp.kaltura.com:1935/kLive?p=231&e=0_6as76tby&i=0&t=cec57e01/0_6as76tby_2"'" -map 2 -c:v copy -c:a copy -f flv "'"rtmp://rtmp-0.cluster-1-a.live.nvq1.ovp.kaltura.com:1935/kLive?p=231&e=0_6as76tby&i=0&t=cec57e01/0_6as76tby_3"'" ;date -c:a copy -f flv "'"rtmp://rtmp-0.cluster-1-a.live.nvq1.ovp.kaltura.com:1935/kLive?p=231&e=0_6as76tby&i=0&t=cec57e01/0_6as76tby_3"'" ;date'
        ffmpegCmdLine = 'date;ffmpeg -re -f concat -safe 0 -i source -re -f concat -safe 0 -i 480p -re -f concat -safe 0 -i 360p -map 0 -c:v copy -c:a copy -f flv '+ source_stream1 + ' -map 1 -c:v copy -c:a copy -f flv ' + source_stream2 + ' -map 2 -c:v copy -c:a copy -f flv ' + source_stream3 + ' ;date -c:a copy -f flv ' + source_stream3 + ' ;date'
        print(ffmpegCmdLine)

        return ffmpegCmdLine

        # Moran.cohen
        # This function return ffmpegCmdString of multi flavors  with printing start & end date according to MAP
        # primaryBroadcastingUrl = primaryBroadcastingUrl for each entry.

    def ffmpegCmdString_MultiFlavors_MAP(self, partnerId, primaryBroadcastingUrl, streamName):

        print("streamName = " + str(streamName))
        if streamName.find('%i') >= 0:
            source_stream1 = '"' + str(primaryBroadcastingUrl) + '/1' + '"'
            source_stream2 = '"' + str(primaryBroadcastingUrl) + '/2' + '"'
            source_stream3 = '"' + str(primaryBroadcastingUrl) + '/3' + '"'
        elif streamName.find('_%i') >= 0:  # Support old logic-until changing all tests locations
            streamName = streamName.replace('_%i','')
            source_stream1 = '"' + str(primaryBroadcastingUrl) + '/' + str(streamName) + '_1' + '"'
            source_stream2 = '"' + str(primaryBroadcastingUrl) + '/' + str(streamName) + '_2' + '"'
            source_stream3 = '"' + str(primaryBroadcastingUrl) + '/' + str(streamName) + '_3' + '"'

        ffmpegCmdLine = 'date;ffmpeg -re -f concat -safe 0 -i source -re -f concat -safe 0 -i 480p -re -f concat -safe 0 -i 360p -map 0 -c:v copy -c:a copy -f flv ' + source_stream1 + ' -map 1 -c:v copy -c:a copy -f flv ' + source_stream2 + ' -map 2 -c:v copy -c:a copy -f flv ' + source_stream3 + ' ;date -c:a copy -f flv ' + source_stream3 + ' ;date'
        print(ffmpegCmdLine)

        return ffmpegCmdLine

    # #######################################
    # Moran.Cohen
    # This function Create draft entry and then set it as live clipping
    # Entryobj - for addTearCommand delete entry
    # client - for baseEntry/media API
    # recordedEntryId of the live entry
    # LiveClipping_offset, LiveClipping_duration fo the live clipping
    def CreateLiveClipping(self, Entryobj,client ,recordedEntryId, LiveClipping_offset,LiveClipping_duration):
        try:
            ################## CREATE LIVE CLIPPING
            # Create Draft entry - empty
            self.logi.appendMsg("INFO - Going to create Draft entry.")
            entry = KalturaMediaEntry()
            entry.name = "AUTOMATION - Draft entry_LiveClipping" + str(datetime.datetime.now())
            entry.mediaType = 1  # SELECT VIDEO
            DraftEntry = client.media.add(entry)
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(DraftEntry.id) + '\')')
            self.logi.appendMsg("PASS - Created DRAFT entry DraftEntry.id = " + str(DraftEntry.id))
            self.logi.appendMsg("INFO - Going to create LIVE CLIPPING from recordedEntryId = " + str(recordedEntryId) + " to DraftEntry.id = " + str(DraftEntry.id))
            # Create live clip entry
            entry_id = DraftEntry.id
            resource = KalturaOperationResource()
            resource.resource = KalturaEntryResource()
            resource.resource.entryId = recordedEntryId
            resource.operationAttributes = []
            resource.operationAttributes.append(KalturaClipAttributes())
            resource.operationAttributes[0].offset = LiveClipping_offset
            resource.operationAttributes[0].duration = LiveClipping_duration
            conversion_profile_id = 0
            advanced_options = KalturaEntryReplacementOptions()
            ClipEntry = client.baseEntry.updateContent(entry_id, resource, conversion_profile_id, advanced_options)

            ClipEntry_entry = KalturaBaseEntry()
            ClipEntry_entry = client.baseEntry.update(ClipEntry.id, ClipEntry_entry)
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(ClipEntry.id) + '\')')
            ClipEntry_entry = KalturaBaseEntry()
            ClipEntry_entry = client.baseEntry.update(ClipEntry.id, ClipEntry_entry)
            self.logi.appendMsg("PASS - Created LIVE CLIPPING from ClipEntry_entry.id = " + str(ClipEntry_entry.id))
            time.sleep(2)
            return ClipEntry_entry
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - CreateLiveClipping.Exception_ERR" + str(e))
            return False


    # #######################################
    # Moran.Cohen
    # This function CreateStreamContainer for closed caption by multi/single languages.
    # KalturaStreamContainerArray of languages order by id,type,language,label - For example - 3 languages:
    # [["SERVICE1", "closedCaptions","eng","English"], ["SERVICE2", "closedCaptions","spa","Spanish"],["SERVICE3", "closedCaptions","deu","German"]]
    # entryId - Live entry for liveStream.update API
    def CreateStreamContainer(self, client,KalturaStreamContainerArray,entryId):
        try:

            ######## ADD adminTag to liveStream entry - It is required for VOD caption
            live_stream_entry = KalturaLiveStreamEntry()
            #live_stream_entry.adminTags = "createvodcaption"
            ############ Add KalturaStreamContainer to the live entry for caption use
            live_stream_entry.streams = []
            for i in range(0, int(len(KalturaStreamContainerArray))):
                live_stream_entry.streams.append(KalturaStreamContainer())
                for j in range(0, int(len(KalturaStreamContainerArray[i]))):
                    if j == 0:
                        live_stream_entry.streams[i].id = KalturaStreamContainerArray[i][j]
                    if j == 1:
                        live_stream_entry.streams[i].type = KalturaStreamContainerArray[i][j]
                    if j == 2:
                        live_stream_entry.streams[i].language = KalturaStreamContainerArray[i][j]
                    if j == 3:
                        live_stream_entry.streams[i].label = KalturaStreamContainerArray[i][j]
                        self.logi.appendMsg("PASS - Update liveStream.KalturaStreamContainer.label - Language label = " + str(KalturaStreamContainerArray[i][j]))

            result = client.liveStream.update(entryId, live_stream_entry)
            print("liveStream.update adminTags = createvodcaption , " + str(result))
            self.logi.appendMsg("PASS - liveStream.KalturaStreamContainer UPDATE.Number of language = " + str(len(KalturaStreamContainerArray)))
            return True

        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - CreateStreamContainer.Exception_ERR" + str(e))
            return False

 # #######################################
    # Moran.Cohen
    # This function verify captionAssets On VODentry for closed caption.
    # KalturaStreamContainerArray of languages order by id,type,language,label - For example - 3 languages:
    # [["SERVICE1", "closedCaptions","eng","English"], ["SERVICE2", "closedCaptions","spa","Spanish"],["SERVICE3", "closedCaptions","deu","German"]]
    # recordedEntryId - VOD/recording entry of liveStream - API
    # CntOfCaptions - Number of expected captions
    def captionAssetOnVODentry_OLD(self, client,KalturaStreamContainerArray,recordedEntryId,CntOfCaptions,AssetStatus=2):
        try:
            #######################CAPTION ASSETS ON VOD entry
            filter = KalturaAssetFilter()
            filter.entryIdEqual = recordedEntryId
            pager = KalturaFilterPager()
            captionAssetList_result = client.caption.captionAsset.list(filter, pager)
            print(captionAssetList_result)
            if CntOfCaptions != int(captionAssetList_result.totalCount):
                self.logi.appendMsg("FAIL -  VOD entry has wrong captionAssetList_result.recordedEntryId = " + str(recordedEntryId) + " , Expected CntOfCaptions = " + str(CntOfCaptions) + " , Actual API captionAssetList_result.totalCount = " + str(captionAssetList_result.totalCount))
                return False
            for i in range(0, int(captionAssetList_result.totalCount)):
                if (str(captionAssetList_result.objects[i].label) != str(KalturaStreamContainerArray[i][3])) or int(captionAssetList_result.objects[i].status.value) != AssetStatus:  # 'English' 2 = READY STATUS
                    self.logi.appendMsg("FAIL - VOD entry has wrong captionAssetList_result.recordedEntryId = " + recordedEntryId + " , captionAssetList_result.objects[" + str(i) + "  ].id(ASSET_ID) = " + str(captionAssetList_result.objects[i].id) + " , Actual_Result_captionAssetList.label = " + str(captionAssetList_result.objects[i].label) + " ,Actual_Result_captionAssetList.status= " + str(captionAssetList_result.objects[i].status.value) + " , Expected_Label" + str(self.KalturaStreamContainerArray[i][3]) + " Expected_STATUS_READY = " + str(AssetStatus))
                    return False
            self.logi.appendMsg("PASS - VOD entry captionAssetList_result verification.recordedEntryId = " + str(recordedEntryId) + ", Actual number of captionAssets = " + str(captionAssetList_result.totalCount))

            return True

        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - captionAssetOnVODentry.Exception_ERR" + str(e))
            return False

    ###############start
    # #######################################
    # Moran.Cohen
    # This function verify captionAssets On VODentry for closed caption.
    # KalturaStreamContainerArray of languages order by id,type,language,label - For example - 3 languages:
    # [["SERVICE1", "closedCaptions","eng","English"], ["SERVICE2", "closedCaptions","spa","Spanish"],["SERVICE3", "closedCaptions","deu","German"]]
    # recordedEntryId - VOD/recording entry of liveStream - API
    # CntOfCaptions - Number of expected captions
    def captionAssetOnVODentry(self, client, KalturaStreamContainerArray, recordedEntryId, CntOfCaptions, AssetStatus=2,Maxtimeout=2):
        try:
            #######################CAPTION ASSETS ON VOD entry
            teststatus = True
            timeout = 0
            while timeout < Maxtimeout:  # wait until max 2 min(avoid races) until caption assets are created after entry flavors mp4 are on ready
                filter = KalturaAssetFilter()
                filter.entryIdEqual = recordedEntryId
                pager = KalturaFilterPager()
                captionAssetList_result = client.caption.captionAsset.list(filter, pager)
                print(captionAssetList_result)
                if CntOfCaptions != int(captionAssetList_result.totalCount):
                    self.logi.appendMsg("FAIL -  VOD entry has wrong captionAssetList_result.recordedEntryId = " + str(recordedEntryId) + " , Expected CntOfCaptions = " + str(CntOfCaptions) + " , Actual API captionAssetList_result.totalCount = " + str(captionAssetList_result.totalCount))
                    timeout = timeout + 1
                    teststatus = False
                    time.sleep(60)
                    # return False
                else:
                    teststatus = True
                    break
            for i in range(0, int(captionAssetList_result.totalCount)):
                if (str(captionAssetList_result.objects[i].label) != str(KalturaStreamContainerArray[i][3])) or int(captionAssetList_result.objects[i].status.value) != AssetStatus:  # 'English' 2 = READY STATUS
                    self.logi.appendMsg("FAIL - VOD entry has wrong captionAssetList_result.recordedEntryId = " + recordedEntryId + " , captionAssetList_result.objects[" + str(i) + "  ].id(ASSET_ID) = " + str(captionAssetList_result.objects[i].id) + " , Actual_Result_captionAssetList.label = " + str(captionAssetList_result.objects[i].label) + " ,Actual_Result_captionAssetList.status= " + str(captionAssetList_result.objects[i].status.value) + " , Expected_Label" + str(self.KalturaStreamContainerArray[i][3]) + " Expected_STATUS_READY = " + str(AssetStatus))
                    teststatus = False
                    # return False
            self.logi.appendMsg("PASS - VOD entry captionAssetList_result verification.recordedEntryId = " + str(recordedEntryId) + ", Actual number of captionAssets = " + str(captionAssetList_result.totalCount))

            return teststatus

        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - captionAssetOnVODentry.Exception_ERR" + str(e))
            return False

    ###############end
    # Moran.Cohen
    # This function return multi process ids that are streams by array
    def SearchPsAuxffmpeg_MultiArrProcessIds_OLD(self,host, user, passwd,entryId,partnerId,timoutMax=10,env='testing',BroadcastingUrl=None,HybridCDN=False):
        try:
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            statusStreaming = False
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '"'
            cmdLine = "ps aux |grep -v bash |grep ffmpeg | grep " + BroadcastingUrl #-v is for remove bash
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("STRAT SSH CONNECTING")
            try:
                ssh.connect(hostname=host, username=user, pkey=cert)
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            connection = ssh.invoke_shell()
            ssh.exec_command("sudo su -" + "\n")
            stdin, stdout, stderr = ssh.exec_command(cmdLine,timeout=60, get_pty=True)# timeout=10
            time.sleep(5)
            output_ProcessId = stdout.read().decode('ascii')
            Result_ProcessIds=[]
            if output_ProcessId == "":
                return False, "NoProcessId"
            if output_ProcessId:
                ssh.close()
                print(str(output_ProcessId))
                arrProcessId_Rows = []
                arrProcessId_Rows = output_ProcessId.split("\n")
                for j in range(0, len(arrProcessId_Rows)):
                    arrProcessId=[]
                    if arrProcessId_Rows[j] != "":
                        arrProcessId=arrProcessId_Rows[j].split(" ")
                        for i in arrProcessId:
                            if i !="" and i != 'root' and i.isdigit():
                                Result_ProcessIds.append(i)
                                statusStreaming = True
                                break
                if statusStreaming==True:
                    #output_ProcessId=str(int(Result_ProcessIds[i]))
                    for i in range(0, len(Result_ProcessIds)):
                        print("Result_ProcessIds " + str(int(Result_ProcessIds[i])))
                    return True,Result_ProcessIds
                else:
                    return False, "NoProcessId"


        except Exception as err:
            print(err)
            return False,"NoProcessId"

    # Moran.cohen
    # This function return ffmpegCmdString With out Channel id of multi flavors  with printing start & end date according to MAP
    # primaryBroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_MultiFlavors_MAP_WithoutChannelid(self, primaryBroadcastingUrl):

        source_stream1 = '"' + str(primaryBroadcastingUrl) + '/1' + '"'
        source_stream2 = '"' + str(primaryBroadcastingUrl) + '/2' + '"'
        source_stream3 = '"' + str(primaryBroadcastingUrl) + '/3' + '"'
        ffmpegCmdLine = 'date;ffmpeg -re -f concat -safe 0 -i source -re -f concat -safe 0 -i 480p -re -f concat -safe 0 -i 360p -map 0 -c:v copy -c:a copy -f flv ' + source_stream1 + ' -map 1 -c:v copy -c:a copy -f flv ' + source_stream2 + ' -map 2 -c:v copy -c:a copy -f flv ' + source_stream3 + ' ;date -c:a copy -f flv ' + source_stream3 + ' ;date'
        print(ffmpegCmdLine)

        return ffmpegCmdLine

    # Moran.cohen
    # This function verifies for x minutes that a live stream plays ok and QR code progress on it
    # MinToPlayEntry = playable QRcode verification time for each entry.
    # QrCodecheckProgress= trashhold between QRCode verification
    def verifyLiveisPlayingOverTime_trashhold(self, wd=None, MinToPlayEntry=1, boolShouldPlay=True,QrCodecheckProgress=4,sniffer_fitler='.ts;.m3u8'):
        time.sleep(1)
        try:
            if wd == None:
                wd = self.driver1

            QrCode = QrcodeReader.QrCodeReader(wbDriver=wd, logobj=self.logi)
            QrCode.initVals()
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlayEntry * 60)
            Fail_count = 1
            interval_playback=4
            while datetime.datetime.now() <= limitTimeout:
                rc = QrCode.placeCurrPrevScr()
                if rc:
                    time.sleep(interval_playback)#4
                    rc = QrCode.placeCurrPrevScr()
                    if rc:
                        rc = QrCode.checkProgress(interval_playback)
                        if rc:
                            if boolShouldPlay == True:
                                self.logi.appendMsg("PASS - QrCode Video played as expected.datetime = " + str(datetime.datetime.now()))#Regular case - good playback
                                interval_playback=4 #return to 4 if live entry plays ok

                            else:
                                self.logi.appendMsg("FAIL - QrCode Video played despite that boolShouldPlay=False.datetime = " + str(datetime.datetime.now()))
                                return True  # Case of return isPlaying=true when boolShouldPlay=False ->stop playing and return result
                        else:
                            self.logi.appendMsg("FAIL - Video was not progress by the QrCode displayed in it." + str(datetime.datetime.now()))
                            if Fail_count >= (QrCodecheckProgress - Fail_count*interval_playback):#>QrCodecheckProgress-if more than one fail->Fail the test
                                self.logi.appendMsg("FAIL - After trashhold wait - Video was not progress by the QrCode displayed in it.Fail_count=" + str(Fail_count) + ", QrCodecheckProgress= " + str(QrCodecheckProgress) + ", datetime = " + str(datetime.datetime.now()))
                                Playback_Result=self.ReturnSnifferResutlByFitler(wd,sniffer_fitler)
                                for i in range(0, len(Playback_Result)):
                                    self.logi.appendMsg("FAIL -  SNIFFER - ReturnSnifferResutlByFitler,playbackResult = " + str(Playback_Result[i]) + " ,  datetime = " + str(datetime.datetime.now()))
                                return False
                            Fail_count = Fail_count +1
                            self.logi.appendMsg("INFO - Playback FAIL without waiting to trashhold - Video was not progress by the QrCode displayed in it.Fail_count=" + str(Fail_count) + ", QrCodecheckProgress= " + str(QrCodecheckProgress) + ", datetime = " + str(datetime.datetime.now()))
                            #time.sleep(QrCodecheckProgress - 4)#set param to 1 sec
                            interval_playback = 1
                    else:
                        self.logi.appendMsg("FAIL - Could not take second time QR code value after playing the entry." + str(datetime.datetime.now()))
                        if Fail_count >= (QrCodecheckProgress - Fail_count*interval_playback):
                            self.logi.appendMsg("FAIL - After trashhold wait - Video was not progress by the QrCode displayed in it.Fail_count=" + str(Fail_count) + ", QrCodecheckProgress= " + str(QrCodecheckProgress) + ", datetime = " + str(datetime.datetime.now()))
                            Playback_Result = self.ReturnSnifferResutlByFitler(wd, sniffer_fitler)
                            for i in range(0, len(Playback_Result)):
                                self.logi.appendMsg("FAIL -  SNIFFER - ReturnSnifferResutlByFitler,playbackResult = " + str(Playback_Result[i]) + " ,  datetime = " + str(datetime.datetime.now()))
                            return False
                        Fail_count = Fail_count +1
                        self.logi.appendMsg("INFO - Playback FAIL without waiting to trashhold - Video was not progress by the QrCode displayed in it.Fail_count=" + str(Fail_count) + ", QrCodecheckProgress= " + str(QrCodecheckProgress) + ", datetime = " + str(datetime.datetime.now()))
                        #time.sleep(QrCodecheckProgress - 4)
                        interval_playback = 1
                else:
                    self.logi.appendMsg("FAIL - Could not take the QR code value after playing the entry." + str(datetime.datetime.now()))
                    if Fail_count >= (QrCodecheckProgress - Fail_count*interval_playback):
                        self.logi.appendMsg("FAIL - After trashhold wait - Video was not progress by the QrCode displayed in it.Fail_count=" + str(Fail_count) + ", QrCodecheckProgress= " + str(QrCodecheckProgress) + ", datetime = " + str(datetime.datetime.now()))
                        Playback_Result = self.ReturnSnifferResutlByFitler(wd, sniffer_fitler)
                        for i in range(0, len(Playback_Result)):
                            self.logi.appendMsg("FAIL -  SNIFFER - ReturnSnifferResutlByFitler,playbackResult = " + str(Playback_Result[i]) + " ,  datetime = " + str(datetime.datetime.now()))
                        return False
                    Fail_count = Fail_count +1
                    self.logi.appendMsg("INFO - Playback FAIL without waiting to trashhold - Video was not progress by the QrCode displayed in it.Fail_count=" + str(Fail_count) + ", QrCodecheckProgress= " + str(QrCodecheckProgress) + ", datetime = " + str(datetime.datetime.now()))
                    #time.sleep(QrCodecheckProgress - 4)
                    interval_playback = 1

            return True
        except Exception as err:
            print(err)
            return False

    # Moran.cohen
    # This function return the result on playback according to sniffer_fitler
    # sniffer_fitler = The string filter on the network of player , for example return result of sniffer_fitler='.ts;.m3u8' - Use ; as separator.
    def ReturnSnifferResutlByFitler(self,PlayBrowser,sniffer_fitler):
        try:
            arr_sniffer_fitler=sniffer_fitler.split(';')
            Playback_Result =[]
            for i in range(0, len(arr_sniffer_fitler)):
                # start pyshark on different thread
                self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                isMatch = 0
                # searchTerm = 'm4s'
                # saveToFile = 1
                # saveOnlyMatchedEntry = 1
                # FileName = "c:\Temp\PythonChromeTraceJson.txt"
                # a_file = open(FileName, "w")
                for row in PlayBrowser.get_log('performance'):
                    # if saveToFile == 1:#save all content log in file
                    # json.dump(row, a_file)
                    # print(row.get('message'))
                    if row.get('message', {}).find(arr_sniffer_fitler[i]) > -1:
                        isMatch = 1
                        Playback_Result.append(row.get('message', {}))
                        # json.dump(row, a_file)#save just rows with the filter
                        break
            # a_file.close()
            if isMatch == 1:
                self.logi.appendMsg("PASS - SNIFFER -  Found for sniffer_fitler = " + sniffer_fitler)
                return Playback_Result
            else:
                self.logi.appendMsg("FAIL - SNIFFER -  Did NOT find sniffer_fitler = " + sniffer_fitler)
                defStatus = False
                return False
        except Exception as err:
            print(err)
            return False

    # Moran.cohen
    # This function return the result on playback according to sniffer_fitler
    # sniffer_fitler = The string filter on the network of player , for example return result of sniffer_fitler='.ts;.m3u8' - Use ; as separator.
    def FirstRecordingVerification(self, client,recordedEntryId,recorded_entry,expectedFlavors_totalCount,start_streaming,stop_time,FirstRecording_EntryID,recorded_entrieslst,sniffer_fitler_After_Mp4flavorsUpload,MinToPlay,env,seenAll_justOnce_flag,PlayerVersion=3,ServerURL=None):
        try:
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("INFO - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(recordedEntryId))
            rc = self.WaitForFlavorsMP4uploaded(client,recordedEntryId, recorded_entry,expectedFlavors_totalCount=expectedFlavors_totalCount)  # expectedFlavors_totalCount=6 for transcording HD
            if rc == True:
                self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + recordedEntryId)
                durationFirstRecording = int(client.baseEntry.get(recorded_entry.id).duration)  # Save the duration of the recording entry after mp4 flavors uploaded
            else:
                self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + recordedEntryId)
                #testStatus = False
                return False

            # Create new player of latest version -  Create V2/3 Player because of cache isse
            self.logi.appendMsg('INFO - Going to create latest V' + str(PlayerVersion) + ' player')
            myplayer = uiconf.uiconf(client, 'livePlayer')
            if PlayerVersion == 2:
                player = myplayer.addPlayer(None, env, False, False)  # Create latest player v2
            elif PlayerVersion == 3:
                player = myplayer.addPlayer(None, env, False, False, "v3")  # Create latest player v3
            else:
                self.logi.appendMsg('FAIL - There is no player version =  ' + str(PlayerVersion))
            if isinstance(player, bool):
                return False
            else:
                playerId = player.id
            self.logi.appendMsg('INFO - Created latest V' + str(PlayerVersion) + ' player.self.playerId = ' + str(playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(player.id) + ')')
            self.playerId = playerId
            time.sleep(5)

            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(recordedEntryId) + "  - MinToPlay=" + str(MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.verifyAllEntriesPlayOrNoBbyQrcode(recorded_entrieslst, True,PlayerVersion=PlayerVersion,sniffer_fitler=sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",ServerURL=ServerURL)
                time.sleep(5)
                if not rc:
                    return False
                if seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + sniffer_fitler_After_Mp4flavorsUpload + " of " + str(recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            # Verify DURATION for the first recording
            recordingTime1 = int(stop_time - start_streaming)
            self.logi.appendMsg("INFO - Going to verify DURATION for the first recording. recordedEntryId = " + str(recordedEntryId))
            if (0 <= recordingTime1 % durationFirstRecording <= 40) or (0 <= durationFirstRecording % recordingTime1 <= 40):  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:VOD entry:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:VOD entry:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                return False

            return True
        except Exception as err:
            print(err)
            return False


    # Moran.Cohen
    # This function verifies that a list of entries is played or not by Qrcode
    # if the entries should play, send True in boolShouldPlay, if not send False
    # MinToPlayEntry = playable QRcode verification time for each entry.
    # sniffer_fitler = Set sniffer filter
    # QRCode = Use Qrcode (True-default) or captionText(False) playback logic
    # verifyPlayback = Don't use playback verification (False-default) or use playback (True) playback logic
    def verifyLiveisPlayingOverTime_Sniffer(self,PlayBrowser, entryList, boolShouldPlay, MinToPlayEntry=1,sniffer_fitler=None,QRCode=True,verifyPlayback=False,QrCodecheckProgress=4):
       defStatus = True
       flavorList=sniffer_fitler
       i=0
       try:
           if PlayBrowser == None:
                PlayBrowser = self.driver1
           for entry in entryList:
                # Perform sniffer if needed
                if sniffer_fitler.find(";") >= 0:  # Multi flavors options
                    arrflavorList = flavorList.split(";")
                    for currentFlavor in arrflavorList:
                        if currentFlavor == "":
                            break
                        time.sleep(5)#2
                        if sniffer_fitler != None:
                            # start pyshark on different thread
                            self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                            #####################
                            if sniffer_fitler.find(";") >= 0:  # Multi flavors options
                                try:
                                    arr_sniffer_filter_per_flavor_list = sniffer_fitler.split(";")

                                    currentFlavorSniffer = arr_sniffer_filter_per_flavor_list[i]
                                    if currentFlavorSniffer == "":
                                        break
                                    if arr_sniffer_filter_per_flavor_list.__len__() != arrflavorList.__len__():
                                        self.logi.appendMsg('FAIL  - SNIFFER count:arr_sniffer_filter_per_flavor_list' + str(arr_sniffer_filter_per_flavor_list.__len__())) + ' different from arrflavorList' + str(arrflavorList.__len__())
                                        defStatus = False
                                        break
                                    # Press on dropdown
                                    # PlayBrowser.find_element_by_xpath(clsPlayerV2.playerV2.PLAYER_FLAVOUR_SELECTOR_DROPDOWN_V7).click()
                                    isMatch = 0
                                    # searchTerm = 'm4s'
                                    # saveToFile = 1
                                    # saveOnlyMatchedEntry = 1
                                    # FileName = "c:\Temp\PythonChromeTraceJson.txt"
                                    # a_file = open(FileName, "w")
                                    for row in PlayBrowser.get_log('performance'):
                                        #time.sleep(2)
                                        # if saveToFile == 1:#save all content log in file
                                        # json.dump(row, a_file)
                                        # print(row.get('message'))
                                        if row.get('message', {}).find(currentFlavorSniffer) > -1:
                                            isMatch = 1
                                            self.logi.appendMsg("PASS - SNIFFER:Found currentFlavorSniffer= " + str(currentFlavorSniffer) + " for Flavor " + str(currentFlavor) + " was selected on player.")
                                            i = i + 1
                                            # json.dump(row, a_file)#save just rows with the filter
                                            break
                                    if isMatch == 0:
                                        self.logi.appendMsg("FAIL - SNIFFER:NO Found currentFlavorSniffer= " + str(currentFlavorSniffer) + " for Flavor " + str(currentFlavor) + " was selected on player.")
                                        defStatus = False
                                except Exception as e:
                                    print(e)
                                    self.logi.appendMsg("FAIL - SNIFFER Flavor:NOT found " + str(currentFlavor) + " with  currentFlavorSniffer=" + str(currentFlavorSniffer))
                        ##########################################
                if verifyPlayback == True:
                    if QRCode == True and QrCodecheckProgress == 4:
                        isPlaying = self.verifyLiveisPlayingOverTime(PlayBrowser, MinToPlayEntry, boolShouldPlay)
                    else: #QrCodecheckProgress !=4:#playback without QRCODE
                        #isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(PlayBrowser, MinToPlayEntry)
                        isPlaying = self.verifyLiveisPlayingOverTime_trashhold(PlayBrowser, MinToPlayEntry, boolShouldPlay,QrCodecheckProgress=QrCodecheckProgress)
                    if (not isPlaying and boolShouldPlay) or (isPlaying and not boolShouldPlay):
                        defStatus = False
                        self.logi.appendMsg("FAIL - Playback verification by QRCode on entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                    else:
                        self.logi.appendMsg("PASS - Playback verification by QRCode on entry = " + str(entry.id) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))


           return defStatus
       except Exception as err:
            print(err)
            return False

    # Moran.cohen
    # This function return ffmpegCmdString_SRT with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    # passphrase - SRT pass encrpyted value
    def ffmpegCmdString_SRT(self, filePath, BroadcastingUrl, SrtStreamId,passphrase=None):

        if passphrase == None:
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '?streamid=' + str(SrtStreamId) + '"'
        else:
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '?streamid=' + str(SrtStreamId) + '&passphrase=' + str(passphrase) + '"'
        ffmpegCmdLine = "date ; ffmpeg -re -stream_loop -1  -i " + str(filePath) + " -c copy -f mpegts  " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine,BroadcastingUrl

    ''' Moran.cohen
    This function return ffmpegCmdString_SRT_VideoOnly with printing start & end date an is video only
    filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
    BroadcastingUrl = primaryBroadcastingUrl for each entry.
    -an is video only:
    ffmpeg -re -stream_loop 20 -i Ronclock.mp4 -c:v copy -an -f mpegts "srt://srtlb.cluster-1-c.live.nvp1.ovp.kaltura.com:7045?streamid=#:::name=1_hkvlu2hw,type=p,token=5ca714df,index=1" ;date
    -vn is audio only:
    ffmpeg -re -stream_loop 20 -i Ronclock.mp4 -vn -c:a copy -f mpegts "srt://srtlb.cluster-1-c.live.nvp1.ovp.kaltura.com:7045?streamid=#:::name=1_hkvlu2hw,type=p,token=5ca714df,index=1" ;date
    '''
    def ffmpegCmdString_SRT_VideoOnly(self, filePath, BroadcastingUrl, SrtStreamId):

        BroadcastingUrl = '"' + str(BroadcastingUrl) + '?streamid=' + str(SrtStreamId) + '"'
        ffmpegCmdLine = "date ; ffmpeg -re -stream_loop -1  -i " + str(filePath) + " -c:v copy -an -f mpegts " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine,BroadcastingUrl

    ''' Moran.cohen
       This function return ffmpegCmdString_SRT_VideoOnly with printing start & end date an is video only
       filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
       BroadcastingUrl = primaryBroadcastingUrl for each entry.
       -an is video only:
       ffmpeg -re -stream_loop 20 -i Ronclock.mp4 -c:v copy -an -f mpegts "srt://srtlb.cluster-1-c.live.nvp1.ovp.kaltura.com:7045?streamid=#:::name=1_hkvlu2hw,type=p,token=5ca714df,index=1" ;date
       -vn is audio only:
       ffmpeg -re -stream_loop 20 -i Ronclock.mp4 -vn -c:a copy -f mpegts "srt://srtlb.cluster-1-c.live.nvp1.ovp.kaltura.com:7045?streamid=#:::name=1_hkvlu2hw,type=p,token=5ca714df,index=1" ;date
       '''
    def ffmpegCmdString_SRT_AudioOnly(self, filePath, BroadcastingUrl, SrtStreamId):

        BroadcastingUrl = '"' + str(BroadcastingUrl) + '?streamid=' + str(SrtStreamId) + '"'
        ffmpegCmdLine = "date ; ffmpeg -re -stream_loop -1 -i " + str(filePath) + " -vn -c:a copy -f mpegts " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine,BroadcastingUrl

    # Moran.cohen
    # This function return ffmpegCmdString_ClosedCaption with printing start & end date
    # filePath = file Path of wanted file to stream , for example filePath = "/home/kaltura/entries/close-caption.txt"
    # BroadcastingUrl = primaryBroadcastingUrl for each entry.
    def ffmpegCmdString_SRT_ClosedCaption(self, filePath, BroadcastingUrl, SrtStreamId):
        BroadcastingUrl = '"' + str(BroadcastingUrl) + '?streamid=' + str(SrtStreamId) + '"'

        ffmpegCmdLine = "date ; ffmpeg -re -f concat -safe 0 -i  " + str(filePath) + "  -c:v copy -c:a copy -c:s copy -f mpegts  " + str(BroadcastingUrl) + " ; date "

        return ffmpegCmdLine,BroadcastingUrl

    # Moran.cohen
    # This function return result of CF tokanization requests permissions
    # m3u8_url = playback url of m3u8 , for example 'https://qa-apache-php7.dev.kaltura.com/p/9006956/playManifest/entryId/0_brajp84k/protocol/https/format/applehttp/a.m3u8'
    # entryId
    def requests_CFtokanization(self, m3u8_url, entryId):
        try:
            self.logi.appendMsg("INFO - Going to verify m3u8_url Request on entry = " + str(entryId) + " , m3u8_url= " + str(m3u8_url) + " , datetime = " + str(datetime.datetime.now()))
            r = requests.get(m3u8_url)
            print(r.text)
            if r.status_code == 200:
              self.logi.appendMsg("PASS - m3u8_url on status_code = " + str(r.status_code) + " , Entry = " + str(entryId) + " , m3u8_url= " + str(m3u8_url) + " , datetime = " + str(datetime.datetime.now()))
            else:
              self.logi.appendMsg("FAIL - m3u8_url on status_code = " + str(r.status_code) + " , Entry = " + str(entryId) + " , m3u8_url= " + str(m3u8_url) + " , datetime = " + str(datetime.datetime.now()))
              return False
            result=r.text[r.text.rfind("EXT-X-STREAM"):]

            if result.find("https") >=0:#AdminConsole->deliveryProilfe->Should redirect=FALSE(Take https url from response)
                arrResponseUrl = result.split("https")
                ResponseUrl = "https" + arrResponseUrl[1]
                ResponseUrl = ResponseUrl.strip()  # remove spaces
            else:#AdminConsole->deliveryProilfe->Should redirect=TRUE (Bulid url from master)
                print(str(r.url))
                arrResponseUrl=r.url.split("master")
                Response_index_url=r.text.split("index-")
                ResponseUrl_tmp = arrResponseUrl[0] + "index-" + str(Response_index_url[1])
                ResponseUrl=ResponseUrl_tmp.split("#EXT-X-STREAM-INF:")[0].strip()

            self.logi.appendMsg("INFO - Going to verify ResponseUrl Request on entry = " + str(entryId) + " , ResponseUrl= " + str(ResponseUrl) + " , datetime = " + str(datetime.datetime.now()))
            r = requests.get(ResponseUrl)
            if r.status_code == 200:
                self.logi.appendMsg("PASS - ResponseUrl on status_code = " + str(r.status_code) + " , Entry = " + str(entryId) + " , ResponseUrl= " + str(ResponseUrl) + " , datetime = " + str(datetime.datetime.now()))
            else:
                self.logi.appendMsg("FAIL - ResponseUrl on status_code = " + str(r.status_code) + " , Entry = " + str(entryId) + " , ResponseUrl= " + str(ResponseUrl) + " , datetime = " + str(datetime.datetime.now()))
                return False
            # Creating list of String elements
            lst_ResponseUrl = list(ResponseUrl)
            print(lst_ResponseUrl)
            index = lst_ResponseUrl.index("?")
            # Assigning value to the list
            lst_ResponseUrl[index + 8] = "X"  # set value X after string "?Policy="
            print(lst_ResponseUrl)
            # use join function to convert list into string
            InvalidResponseUrl = "".join(lst_ResponseUrl)
            self.logi.appendMsg("INFO - Going to verify InvalidResponseUrl Request  on entry = " + str(entryId) + " , InvalidResponseUrl= " + str(InvalidResponseUrl) + " , datetime = " + str(datetime.datetime.now()))
            r = requests.get(InvalidResponseUrl)
            if r.status_code == 403:
                self.logi.appendMsg("PASS - InvalidResponseUrl on status_code = " + str(r.status_code) + " , Entry = " + str(entryId) + " , InvalidResponseUrl= " + str(InvalidResponseUrl) + " , datetime = " + str(datetime.datetime.now()))
            else:
                self.logi.appendMsg("FAIL - InvalidResponseUrl on status_code = " + str(r.status_code) + " , Entry = " + str(entryId) + " , InvalidResponseUrl= " + str(InvalidResponseUrl) + " , datetime = " + str(datetime.datetime.now()))
                return False

            return True
        except Exception as err:
            print(err)
            return False

    # Moran.cohen
    # This function return result of DVR verification
    # liveObj = live object
    # entryId,entryList
    # MinToPlay the entryId
    # PlayerVersion
    #def DVR_Verification(self,liveObj, entryList,entryId ,MinToPlay,PlayerVersion=3,sniffer_fitler=None,Protocol='https'):
    def DVR_Verification(self, liveObj,entryList,entryId,MinToPlay, boolShouldPlay=True, MinToPlayEntry=1, PlayerVersion=3, sniffer_fitler=None, CloseBrowser=True, flashvars=None, AudioOnly=False, MultiAudio=False, ClosedCaption=False, Protocol='https', languageList="Spanish;English", languageList_Caption="English;",MatchValue=False,QRCODE=True,ServerURL=None):

        try:
            seenAll_justOnce_flag = True
            testStatus = True
            if PlayerVersion == 3:
                isV7=True
            else:
                isV7=False
            ''' read QR code for 2 minutes of play'''
            self.logi.appendMsg("Going to read QR code for 2 minutes of play")
            ''' ----- first play 2 minutes -------'''
            # Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play " + str(entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc, PlayBrowserDriver = liveObj.verifyAllEntriesPlayOrNoBbyQrcode_DVR(entryList=entryList,boolShouldPlay=boolShouldPlay,PlayerVersion=PlayerVersion,CloseBrowser=False,ClosedCaption=ClosedCaption,sniffer_fitler=sniffer_fitler,Protocol=Protocol,MatchValue=MatchValue,QRCODE=QRCODE,ServerURL=ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return False
                if seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("Playback of " + str(entryId) + " live entries on preview&embed page during - MinToPlay=" + str(MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            if testStatus == True:
                self.logi.appendMsg("PASS - First 2 minutes played video OK. EntryId = " + str(entryId))
            else:
                self.logi.appendMsg("FAIL - First 2 minutes did NOT play the video ok. EntryId = " + str(entryId))
                return False

            ''' Going to scroll to start point - REWIND '''
            self.logi.appendMsg("INFO - DVR - Going to scroll to start point - REWIND. EntryId = " + str(entryId))
            kaltplayer = clsPlayerV2.playerV2("kaltura_player_1418811966")
            rc = kaltplayer.clickOnSlider(PlayBrowserDriver, 0, isV7)
            if (not rc):
                testStatus = False
                self.logi.appendMsg("FAIL - Scroll to start point - REWIND. EntryId = " + str(entryId))
                return False
            else:
                self.logi.appendMsg("PASS - Scroll to start point - REWIND. EntryId = " + str(entryId))
            currentTimeArr = kaltplayer.getCurrentDVRTimeFromLive(PlayBrowserDriver)
            TotalLive = currentTimeArr[1].split(":")
            Totaltime_in_minutes = 60 * int(TotalLive[0]) + int(TotalLive[1])  # time in minutes
            DVRTime = currentTimeArr[0].split(":")
            DVRtime_in_minutes = 60 * int(DVRTime[0]) + int(DVRTime[1])  # time in minutes
            # Check DVR return result is not above 3 seconds when moving to start point
            if DVRtime_in_minutes in range(20) and Totaltime_in_minutes > DVRtime_in_minutes:
                self.logi.appendMsg("PASS - DVR -DVR Point time Scroll to start point. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
            else:
                testStatus = False
                self.logi.appendMsg("FAIL - DVR- DVR Point time Scroll to start point. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]) + "  , DVRtime_in_minutes = " + str(DVRtime_in_minutes))
                return False

            ''' ----- second play 1 minutes -------'''
            self.logi.appendMsg("INFO - DVR -Going to read QR code for 1 minute of play - after Rewind to start point. EntryId = " + str(entryId))
            MinToPlayEntry = 1  # 1 minutes playback
            if QRCODE==True:
                isPlaying = liveObj.verifyLiveisPlayingOverTime(wd=PlayBrowserDriver, MinToPlayEntry=MinToPlayEntry)
            else:
                isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(wd=PlayBrowserDriver,MinToPlayEntry=MinToPlayEntry)
            if (not isPlaying):
                testStatus = False
                self.logi.appendMsg("FAIL - DVR - 1 minute of played video after Rewind to start point, did NOT play the video OK. Details:Entry = " + str(entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                return False
            else:
                self.logi.appendMsg("PASS - DVR - 1 minute of played video after Rewind to start point, played OK.Details:Entry = " + str(entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
            if testStatus == True:
                self.logi.appendMsg("PASS - DVR - 1 minute of played video after Rewind to start point, played OK.EntryId = " + str(entryId))
            else:
                self.logi.appendMsg("FAIL - DVR - 1 minute of played video after Rewind to start point, did NOT play the video OK.EntryId = " + str(entryId))
                return False

            ''' ----- Going to scroll to middle point - Forward -------'''
            self.logi.appendMsg("INFO - DVR - Going to scroll to middle point - Forward to start point. EntryId = " + str(entryId))
            rc = kaltplayer.clickOnSlider(PlayBrowserDriver, 50, isV7)  # 50% equal to DVR float(0.5)
            if (not rc):
                testStatus = False
                self.logi.appendMsg("FAIL - DVR - Scroll to middle point - REWIND. EntryId = " + str(entryId))
                return False
            else:
                self.logi.appendMsg("PASS - DVR - Scroll to middle point - REWIND. EntryId = " + str(entryId))
            self.logi.appendMsg("INFO - DVR - Going to calculate DVR. EntryId = " + str(entryId))
            currentTimeArr = kaltplayer.getCurrentDVRTimeFromLive(PlayBrowserDriver)
            TotalLive = currentTimeArr[1].split(":")
            Totaltime_in_minutes = 60 * int(TotalLive[0]) + int(TotalLive[1])  # time in minutes
            DVRTime = currentTimeArr[0].split(":")
            DVRtime_in_minutes = 60 * int(DVRTime[0]) + int(DVRTime[1])  # time in minutes
            resultDVR = float(DVRtime_in_minutes) / float(Totaltime_in_minutes)  # float: 0.505067567568
            # Check DVR return result 50% is 0.5 -Round a number to the given number of decimal places
            if round(resultDVR, 1) == float(0.5) and Totaltime_in_minutes > DVRtime_in_minutes:  # WORKING ON
                self.logi.appendMsg("PASS - DVR - DVR Point time Middle point. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
            else:
                testStatus = False
                self.logi.appendMsg("FAIL - DVR - DVR Point time Middle point. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]) + "  , DVRtime_in_minutes = " + str(DVRtime_in_minutes))
                return False

            ''' ----- third play 1 minutes -------'''
            self.logi.appendMsg("INFO - DVR - Going to read QR code for 1 minute of play - after Rewind to middle point. EntryId = " + str(entryId))
            MinToPlayEntry = 1  # 1 minutes playback
            if QRCODE == True:
                isPlaying = liveObj.verifyLiveisPlayingOverTime(wd=PlayBrowserDriver, MinToPlayEntry=MinToPlayEntry)
            else:
                isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(wd=PlayBrowserDriver,MinToPlayEntry=MinToPlayEntry)
            if (not isPlaying):
                testStatus = False
                self.logi.appendMsg("FAIL - DVR - 1 minute of played video after Rewind to middle point, did NOT play the video OK. Details:Entry = " + str(entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                return False
            else:
                self.logi.appendMsg("PASS - DVR - 1 minute of played video after Rewind to middle point, played OK.Details:Entry = " + str(entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))

            if testStatus == True:
                self.logi.appendMsg("PASS - DVR - 1 minute of played video after Forward to middle point, played OK. EntryId = " + str(entryId))
            else:
                self.logi.appendMsg("FAIL - DVR - 1 minute of played video after Forward to middle point did NOT play the video OK. EntryId = " + str(entryId))
                return False

            ''' Going to perform BACK TO LIVE '''
            self.logi.appendMsg("INFO - DVR - Going to Press the BACK TO LIVE button. EntryId = " + str(entryId))
            currentTimeArr = kaltplayer.getCurrentTimeLabel(PlayBrowserDriver)  # WORKING ON
            print("DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
            rc = kaltplayer.clickLiveIconBackToLive(PlayBrowserDriver, isV7)
            if (not rc):
                testStatus = False
                self.logi.appendMsg("FAIL - DVR - clickLiveIconBackToLive - BACK TO LIVE . EntryId = " + str(entryId))
                return False
            else:
                self.logi.appendMsg("PASS - DVR - clickLiveIconBackToLive. EntryId = " + str(entryId))
            time.sleep(25)  # Wait for change of click to live to
            self.logi.appendMsg("INFO - DVR - Going to calculate DVR. EntryId = " + str(entryId))
            if isV7==True:
                rc = kaltplayer.approveBcakToLive(PlayBrowserDriver)
                # Check DVR return result equal to total live time when moving back to live
                if rc:
                    self.logi.appendMsg("PASS - DVR - DVR Point time BACK TO LIVE. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
                else:
                    testStatus = False
                    self.logi.appendMsg("FAIL - DVR - DVR Point time BACK TO LIVE. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
                    return False
            else:

                currentTimeArr = kaltplayer.getCurrentDVRTimeFromLive(PlayBrowserDriver)
                # Check DVR return result equal to total live time when moving back to live
                # calculator first digit - minutes
                if int(currentTimeArr[0].strip().split(":")[0]) != int(currentTimeArr[1].strip().split(":")[0]):
                    self.logi.appendMsg("FAIL - DVR - DVR Point time BACK TO LIVE-Difference minutes. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
                    return False
                # calculator first digit - seconds
                distanceDVRSeconds=abs(int(currentTimeArr[0].strip().split(":")[1])-int(currentTimeArr[1].strip().split(":")[1]))
                if distanceDVRSeconds not in range(0, 3):#Except only difference of 1 and 2 seconds
                    self.logi.appendMsg("FAIL - DVR - DVR Point time BACK TO LIVE-Difference seconds. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))
                    return False
                self.logi.appendMsg("PASS - DVR Point time BACK TO LIVE. EntryId = " + str(entryId) + " , DVR Point time = " + str(currentTimeArr[0]) + "Total live time = " + str(currentTimeArr[1]))


            ''' check scroll is at the end of it'''
            ''' ----- forth play 1 minutes -------'''
            self.logi.appendMsg("INFO - DVR - Going to read QR code for 1 minute of play - after BACK TO LIVE. EntryId = " + str(entryId))
            MinToPlayEntry = 1  # 1 minutes playback
            if QRCODE == True:
                isPlaying = liveObj.verifyLiveisPlayingOverTime(wd=PlayBrowserDriver, MinToPlayEntry=MinToPlayEntry)
            else:
                isPlaying = self.verifyLiveisPlayingOverTimeByOnlyPlayback(wd=PlayBrowserDriver,MinToPlayEntry=MinToPlayEntry)
            if (not isPlaying):
                testStatus = False
                self.logi.appendMsg("FAIL - DVR - 1 minute of played video after BACK TO LIVE, did NOT play the video OK. Details:Entry = " + str(entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
                return False
            else:
                self.logi.appendMsg("PASS - DVR - 1 minute of played video after BACK TO LIVE, played OK.Details:Entry = " + str(entryId) + " , during MinToPlayEntry= " + str(MinToPlayEntry) + " , datetime = " + str(datetime.datetime.now()))
            if testStatus == True:
                self.logi.appendMsg("PASS - DVR - 1 minute of played video after BACK TO LIVE, played OK.EntryId = " + str(entryId))
            else:
                self.logi.appendMsg("FAIL - DVR - 1 minute of played video after BACK TO LIVE, did NOT play the video OK.EntryId = " + str(entryId))
                return False

            # Close self.PlayBrowserDriver window
            try:
                self.logi.appendMsg("INFO - Going to close the PlayBrowserDriver.")
                PlayBrowserDriver.quit()
                time.sleep(2)
            except Exception as Exp:
                print(Exp)
                pass

            return True
        except Exception as err:
            print(err)
            return False


    # Moran.cohen
    # This function return result of PrimaryBackupStreaming
    # liveObj = live object
    # entryId
    #  filePath,url,remote_host,remote_user,remote_pass,env,PublisherID
    # Current_primaryBroadcastingUrl,Current_secondaryBroadcastingUrl
    # IsSRT,secondarySrtStreamId primarySrtStreamId
    # srtPass
    # Flag_FailedStreamResult - default False - Stream OK state of streaming is expected result , True - Stream Failed state of streaming is expected result
    def PrimaryBackupStreaming(self, liveObj,entryId, filePath,remote_host,remote_user,remote_pass,env,PublisherID,Current_primaryBroadcastingUrl, primarySrtStreamId,Current_secondaryBroadcastingUrl=None,secondarySrtStreamId=None,srtPass=None,IsSRT=None,Flag_FailedStreamResult=False):
        try:
            if IsSRT == True:
                ffmpegCmdLine,Current_primaryBroadcastingUrl = liveObj.ffmpegCmdString_SRT(filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId, passphrase=srtPass)
            else:
                ffmpegCmdLine = liveObj.ffmpegCmdString(filePath, str(Current_primaryBroadcastingUrl),entryId)
            rc, ffmpegOutputString1 = liveObj.Start_StreamEntryByffmpegCmd(remote_host, remote_user,remote_pass, ffmpegCmdLine,entryId,PublisherID,env=env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True,srtPass=srtPass)
            if rc == Flag_FailedStreamResult:
                self.logi.appendMsg("FAIL - Start_StreamEntryByffmpegCmd - primaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + remote_host + " , " + remote_user + " , " + remote_pass + " , " + filePath + " ," + entryId + " , " + PublisherID + " , " + url + " , primaryBroadcastingUrl = " + str(Current_primaryBroadcastingUrl))
                if Flag_FailedStreamResult == False:
                    return False

            # Stream to Backup
            if Current_secondaryBroadcastingUrl != None:
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd to secondaryBroadcastingUrl.********** ENTRY# , Datetime = " + str(datetime.datetime.now()) + " , " + remote_host + " , " + remote_user + " , " + remote_pass + " , " + filePath + " ," + entryId + " , " + PublisherID + ", secondaryBroadcastingUrl = " + str(Current_secondaryBroadcastingUrl))
                if IsSRT == True:
                    ffmpegCmdLine,Current_secondaryBroadcastingUrl = liveObj.ffmpegCmdString_SRT(filePath, str(Current_secondaryBroadcastingUrl),secondarySrtStreamId, passphrase=srtPass)
                else:
                    ffmpegCmdLine = liveObj.ffmpegCmdString(filePath, str(Current_secondaryBroadcastingUrl),entryId)
                rc, ffmpegOutputString2 = liveObj.Start_StreamEntryByffmpegCmd(remote_host, remote_user,remote_pass, ffmpegCmdLine,entryId, PublisherID,env=env,BroadcastingUrl=Current_secondaryBroadcastingUrl,FoundByProcessId=True,srtPass=srtPass)
                if rc == Flag_FailedStreamResult:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByffmpegCmd - secondaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + remote_host + " , " + remote_user + " , " + remote_pass + " , " + filePath + " ," + entryId + " , " + PublisherID + ", secondaryBroadcastingUrl = " + str(Current_secondaryBroadcastingUrl))
                    if Flag_FailedStreamResult==False:
                        return False
            time.sleep(5)

            ffmpegOutputString = str(ffmpegOutputString1) + " " + (ffmpegOutputString2)
            return True,ffmpegOutputString
        except Exception as err:
            print(err)
            return False


    # Moran.cohen
    # This function Check Playback For All Delivery profiles according to the access_control_id_DP_list
    # access_control_id_DP_list=[['access control profile id','name of DP','dp_id1,dp_id2'],['access control profile id','name of DP','dp_id1,dp_id2']]
    # entryId,entryList
    # MinToPlay the entryId
    # PlayerVersion
    def CheckPlaybackForAllDP(self,access_control_id_DP_list,client,entryList,boolShouldPlay,env,PlayerVersion=3,flashvars=None,MinToPlay=10,sniffer_fitler=None,Protocol='https',RefreshPlayer_Timeout=False,ServerURL=None):
        try:
            seenAll_justOnce_flag = True

            # Set accessControl that contain delivery profiles limit/access
            print("Count access_control_id_DP_list=" + str(len(access_control_id_DP_list)))
            for i in range(0, len(access_control_id_DP_list)):
                if access_control_id_DP_list[i] != None:
                    for entry in entryList:
                        self.logi.appendMsg('INFO - $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ access_control_id_DP_list[' + str(i) + '] Going to set AccessControl id ' + str(access_control_id_DP_list[i][0]) + ', DP name= '  + str(access_control_id_DP_list[i]) + ', DP ids= ' + str(access_control_id_DP_list[i][2]) + ' EntryId = ' + str(entry.id))
                        base_entry = KalturaBaseEntry()
                        base_entry.accessControlId = access_control_id_DP_list[i][0]#set access control id - first column
                        if access_control_id_DP_list[i][0]=='29293':#If LLHLS -->['29293','LLHLS - NG','1131']
                            base_entry.adminTags = "lowlatency" #Required adminTag of lowlatency
                            self.logi.appendMsg('INFO - Set base_entry.adminTags =lowlatency')
                        else:
                            base_entry.adminTags = ""
                        result = client.baseEntry.update(entry.id, base_entry)

                time.sleep(5)
                if env == 'testing' and sniffer_fitler!=None:
                    sniffer_fitler='qa-aws-vod' # if regular vod on testing env
                    if sniffer_fitler.find('vod') >= 0 and access_control_id_DP_list[i][1].find("CF") >= 0:
                        sniffer_fitler='qa-vod-cf' #if clound front on testing env

                # Playback verification of all entries
                self.logi.appendMsg("INFO - Going to play " + str(entryList) + "  live entries on preview&embed page during - MinToPlay=" + str(MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlay * 60)
                seenAll = False
                if RefreshPlayer_Timeout == True:
                    timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    time.sleep(2)
                    rc= self.verifyAllEntriesPlayOrNoBbyQrcode(entryList,boolShouldPlay=boolShouldPlay,PlayerVersion=PlayerVersion,flashvars=flashvars,sniffer_fitler=sniffer_fitler,Protocol=Protocol,ServerURL=ServerURL)
                    time.sleep(5)
                    if RefreshPlayer_Timeout ==True:#Try Playback until arriving to RefreshPlayer_Timeout
                        timeout = timeout + 1
                        if rc == False and timeout < 2:
                            self.logi.appendMsg("INFO - ****** Going to play AGAIN after player CACHE ISSUE RECORDED ENTRY from " + sniffer_fitler + " after MP4 flavors uploaded " + str(entry.id) + "  - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                            time.sleep(90)  # Time for player cache issue
                        if not rc and timeout >= 3:  # Change condition
                            print("FAIL - Play ENTRY after mp4 conversion - Retry count:timeout = " + str(timeout))
                            self.logi.appendMsg("FAIL - Playback verification of entryId =" + str(entry.id) + " with access_control_id_DP_list= " + str(access_control_id_DP_list[i]) + " , CurrentTime = " + str(datetime.datetime.now()))
                            return False
                        if seenAll_justOnce_flag == True and rc != False:  # Change condition
                            seenAll = True
                            break
                    else:#Regular playback without refresh until arriving to RefreshPlayer_Timeout
                        if not rc:
                            self.logi.appendMsg("FAIL - Playback verification of entryId =" + str(entry.id) + " with access_control_id_DP_list= " + str(access_control_id_DP_list[i]) + " , CurrentTime = " + str(datetime.datetime.now()))
                            return False
                        if seenAll_justOnce_flag == True:
                            seenAll = True

                self.logi.appendMsg("PASS -$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Playback verification of entryId =" + str(entry.id) + " with access_control_id_DP_list= " + str(access_control_id_DP_list[i]) + " , CurrentTime = " + str(datetime.datetime.now()))
            return True
        except Exception as err:
            print(err)
            return False


    # Moran.cohen
    # This function create KalturaLiveStreamScheduleEvent and then Return scheduleEventId
    def Create_KalturaLiveStreamScheduleEvent_ADD(self, client,summary,startDate,endDate,templateEntryId):
        try:
            schedule_event = KalturaLiveStreamScheduleEvent()
            schedule_event.summary = summary
            schedule_event.startDate = startDate
            schedule_event.endDate = endDate
            schedule_event.recurrenceType = KalturaScheduleEventRecurrenceType.NONE
            schedule_event.templateEntryId = templateEntryId

            result_scheduleEvent = client.schedule.scheduleEvent.add(schedule_event)
            print(str(result_scheduleEvent.id))
            return True,result_scheduleEvent.id

        except Exception as err:
            print(err)
            return False,None


    # Moran.cohen
    # This function create KalturaEntryVendorTask and then Return entryVendorTaskId
    def Create_KalturaEntryVendorTask_ADD(self, client,entryId,reachProfileId,catalogItemId,scheduledEventId):

        try:
            entry_vendor_task = KalturaEntryVendorTask()
            entry_vendor_task.entryId = entryId
            entry_vendor_task.reachProfileId = reachProfileId
            entry_vendor_task.catalogItemId = catalogItemId
            entry_vendor_task.taskJobData = KalturaScheduledVendorTaskData()
            entry_vendor_task.taskJobData.scheduledEventId = scheduledEventId

            result_entryVendorTask = client.reach.entryVendorTask.add(entry_vendor_task)
            #print(str(result_entryVendorTask.id))
            self.logi.appendMsg("INFO - entryVendorTask.id= " + str(result_entryVendorTask.id) + " of entryId = " + str(entryId))
            #Add verfication of status ---> entryVendorTask.status - first 1 scheduled , 3 processing
            return True,result_entryVendorTask.id

        except Exception as err:
            print(err)
            return False,None

    ''' Moran.cohen
    Add verfication of Expected_STATUS ---> entryVendorTask.status 
    interface EntryVendorTaskStatus extends BaseEnum
    {
       const PENDING           = 1;
       const READY             = 2;
       const PROCESSING         = 3;
       const PENDING_MODERATION   = 4;
       const REJECTED              = 5;
       const ERROR             = 6;
       const ABORTED           = 7;
       const PENDING_ENTRY_READY  = 8;
       const SCHEDULED          = 9;
    }'''
    def Create_KalturaEntryVendorTask_VerifyStatus(self, client,id,Expected_STATUS):

        try:
            result_entryVendorTask = client.reach.entryVendorTask.get(id)
            if result_entryVendorTask.status.value==Expected_STATUS:
                self.logi.appendMsg("PASS - Actual result of entryVendorTaskId= " + str(id) + " entryVendorTask.status= " + str(result_entryVendorTask.status.value) + " , order id(externalTaskId)=" + str(result_entryVendorTask.externalTaskId))
                return True
            else:
                self.logi.appendMsg("FAIL - Actual result of entryVendorTaskId= " + str(id) + " entryVendorTask.status= " + str(result_entryVendorTask.status.value) + " , order id(externalTaskId)=" + str(result_entryVendorTask.externalTaskId))
                return False

        except Exception as err:
            print(err)
            return False

    # Moran.cohen
    # This function Verify LiveCaption_PlaybackVTT
    def LiveCaption_VerifyPlaybackVTT(self, rc_MatchValue, SearchVtt_str1='"referrerPolicy":"strict-origin-when-cross-origin","url":"', SearchVtt_str2=".vtt"):

        try:
            testStatus = True
            subStr = ""
            LastTimeOnCurrentVTT=""
            for i in range(rc_MatchValue.index(SearchVtt_str1) + len(SearchVtt_str1), rc_MatchValue.index(SearchVtt_str2)):
                subStr = subStr + rc_MatchValue[i]
            Result_Url = subStr + ".vtt"
            self.logi.appendMsg("PASS - Got VTT url = " + str(Result_Url))
            self.logi.appendMsg("INFO - Going to get caption content from VTT url")
            r = requests.get(Result_Url)
            self.logi.appendMsg("PASS - Got caption content from VTT URL = " + str(r.text))

            self.logi.appendMsg("INFO - Going to verify vtt url status_code")
            if r.status_code == 200:
                self.logi.appendMsg("PASS -  status_code=200 VTT url")
            else:
                self.logi.appendMsg("FAIL - status_code different from 200 of VTT url: status_code = " + str(r.status_code))
                testStatus = False

            self.logi.appendMsg("INFO - Going to verify the caption content text on vtt - Number of rows not empty")
            if len(r.text.split("\n")) <= 5 or r.text.find(" --> ") < 0:  # 5 is number for having at least one caption text on vtt
                self.logi.appendMsg("FAIL -  VTT return caption text: Number of rows = " + str(r.text))
                testStatus = False
            else:
                self.logi.appendMsg("PASS -  VTT return caption text-Number of rows not empty")# " + str(r.text))

            if testStatus == False:
                return False,"NoVTTcontent","NO_LastTimeOnCurrentVTT"

            # Verify that there are valid times on the VTT(Follower time)
            self.logi.appendMsg("INFO -  Going to verify Follower time inside VTT content")# = " + str(r.text))
            Times_From_VTT_Content = re.findall(r'\s(\d{2}\:\d{2}:\d{2}.\d{3})', r.text)
            print(re.findall(r'\s(\d{2}\:\d{2}:\d{2}.\d{3})', r.text))
            for i in range(0, len(Times_From_VTT_Content)-1):
                LastTimeOnCurrentVTT = Times_From_VTT_Content[i+1]
                if (Times_From_VTT_Content[i] > Times_From_VTT_Content[i+1]):
                    self.logi.appendMsg("FAIL - LiveCaption_VerifyPlaybackVTT -Times_From_VTT_Content." + str(r.text) + " , datetime = " + str(datetime.datetime.now()))
                    return False
            self.logi.appendMsg("PASS - VTT content and inside Follower time")#" + str(r.text))

            return True,str(r.text),str(LastTimeOnCurrentVTT)
        except Exception as err:
            print(err)
            return False,"NoVTTcontent","NO_LastTimeOnCurrentVTT"


    # Moran.cohen
    # This function Verify create LiveCaption using Reach
    def LiveCaption_Create(self, client,startTime,endTime,entryId,catalogItemId,reachProfileId):
        try:
            #############LiveCaption

            # Create SchedulerEvent
            rc, scheduleEventId = self.Create_KalturaLiveStreamScheduleEvent_ADD(client=client,summary='AUTO_LiveStreamScheduleEvent' + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')) + '_' + str(datetime.datetime.now()),startDate=startTime,endDate=endTime,templateEntryId=entryId)
            if rc == False:
                self.logi.appendMsg("FAIL - Create_KalturaLiveStreamScheduleEvent.Details: entryid=" + entryId + " , startTime= " + str(startTime) + " , endTime= " + str(endTime))
                #testStatus = False
                return False,""
            self.logi.appendMsg("PASS - Create_KalturaLiveStreamScheduleEvent.Details: entryid=" + entryId + " , startTime= " + str(startTime) + " , endTime= " + str(endTime) + " , scheduleEventId= " + str(scheduleEventId))

            # Create EntryVendorTask
            self.logi.appendMsg("INFO - Going to add KalturaEntryVendorTask.Details: entryid=" + entryId + " , reachProfileId= " + str(reachProfileId) + " , catalogItemId= " + str(catalogItemId) + " , scheduleEventId= " + str(scheduleEventId))
            rc, EntryVendorTaskId = self.Create_KalturaEntryVendorTask_ADD(client=client,entryId=entryId,reachProfileId=reachProfileId,catalogItemId=catalogItemId,scheduledEventId=scheduleEventId)
            if rc == False:
                self.logi.appendMsg("FAIL - Create_KalturaEntryVendorTask_ADD.Details: entryid=" + entryId + " , reachProfileId= " + str(reachProfileId) + " , catalogItemId= " + str(catalogItemId) + " , scheduleEventId= " + str(scheduleEventId) + " , EntryVendorTaskId= " + str(EntryVendorTaskId))
                #testStatus = False
                return False,""

            return True,EntryVendorTaskId
        except Exception as err:
            print(err)
            return False,""

    # Moran.cohen
    # This function Verify create LiveCaption using Reach
    def GetRequestFromPlayback(self,PlayBrowser, sniffer_fitler):
        try:
            MatchValue = False
            if sniffer_fitler != None:
                # start pyshark on different thread
                self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                isMatch = 0
                # searchTerm = 'm4s'
                # saveToFile = 1
                # saveOnlyMatchedEntry = 1
                # FileName = "c:\Temp\PythonChromeTraceJson.txt"
                # a_file = open(FileName, "w")
                for row in PlayBrowser.get_log('performance'):
                    # if saveToFile == 1:#save all content log in file
                    # json.dump(row, a_file)
                    # print(row.get('message'))
                    if row.get('message', {}).find(sniffer_fitler) > -1:
                        isMatch = 1
                        # json.dump(row, a_file)#save just rows with the filter
                        break
                # a_file.close()
                if isMatch == 1:
                    self.logi.appendMsg("PASS - SNIFFER -  Found for sniffer_fitler = " + sniffer_fitler)
                    MatchValue = row.get('message', {})
                else:
                    self.logi.appendMsg("FAIL - SNIFFER -  Did NOT find sniffer_fitler = " + sniffer_fitler)
                    MatchValue = False

                return MatchValue
        except Exception as err:
            print(err)
            return False, ""

    # Moran.cohen
    # This function verifies for x minutes that a live stream plays ok and QR code progress on it
    # MinToPlayEntry = playable QRcode verification time for each entry.
    def verifyLiveisPlayingOverTime_CheckRequestValue(self, wd=None, MinToPlayEntry=1, boolShouldPlay=True,sniffer_fitler=None):
        time.sleep(1)
        try:
            if wd == None:
                wd = self.driver1

            QrCode = QrcodeReader.QrCodeReader(wbDriver=wd, logobj=self.logi)
            QrCode.initVals()
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlayEntry * 60)
            while datetime.datetime.now() <= limitTimeout:
                rc = QrCode.placeCurrPrevScr()
                if rc:
                    time.sleep(4)
                    rc = QrCode.placeCurrPrevScr()
                    if rc:
                        rc = QrCode.checkProgress(4)
                        if rc:
                            if boolShouldPlay == True:
                                self.logi.appendMsg("PASS - QrCode Video played as expected.datetime = " + str(datetime.datetime.now()))
                                if sniffer_fitler != None:
                                    self.logi.appendMsg("INFO - Going to get LiveCaption_VerifyPlaybackVTT= " + str(datetime.datetime.now()))
                                    MatchValue=self.GetRequestFromPlayback(PlayBrowser=wd, sniffer_fitler=sniffer_fitler)
                                    rc_MatchValue,VTTContent=self.LiveCaption_VerifyPlaybackVTT(rc_MatchValue=MatchValue)
                                    if rc_MatchValue == False:
                                        return False
                                    self.logi.appendMsg("PASS - LiveCaption_VerifyPlaybackVTT.VTTContent = " + str(VTTContent))
                                # Return True # on Regular case continue to play until the limitTimeout
                            else:
                                self.logi.appendMsg("FAIL - QrCode Video played despite that boolShouldPlay=False.datetime = " + str(datetime.datetime.now()))
                                return True  # Case of return isPlaying=true when boolShouldPlay=False ->stop playing and return result
                        else:
                            self.logi.appendMsg("FAIL - Video was not progress by the QrCode displayed in it." + str(datetime.datetime.now()))
                            return False

                    else:
                        self.logi.appendMsg("FAIL - Could not take second time QR code value after playing the entry." + str(datetime.datetime.now()))
                        return False
                else:
                    self.logi.appendMsg("FAIL - Could not take the QR code value after playing the entry." + str(datetime.datetime.now()))
                    return False

            return True
        except Exception as err:
            print(err)
            return False


    # Moran.cohen
    # This function return the result on playback according to sniffer_fitler
    # sniffer_fitler = The string filter on the network of player , for example return result of sniffer_fitler='.ts;.m3u8' - Use ; as separator.
    def ReturnMultiSnifferResutlByFitler(self,PlayBrowser,sniffer_fitler):
        try:
            arr_sniffer_fitler=sniffer_fitler.split(';')
            Playback_Result =[]
            for i in range(0, len(arr_sniffer_fitler)):
                # start pyshark on different thread
                self.logi.appendMsg('INFO  - Start SNIFFER on browser')
                isMatch = 0
                # searchTerm = 'm4s'
                # saveToFile = 1
                # saveOnlyMatchedEntry = 1
                # FileName = "c:\Temp\PythonChromeTraceJson.txt"
                # a_file = open(FileName, "w")
                for row in PlayBrowser.get_log('performance'):
                    # if saveToFile == 1:#save all content log in file
                    # json.dump(row, a_file)
                    # print(row.get('message'))
                    if row.get('message', {}).find(arr_sniffer_fitler[i]) > -1:
                        isMatch = 1
                        Playback_Result.append(row.get('message', {}))
                        # json.dump(row, a_file)#save just rows with the filter
                        break
                # a_file.close()
                if isMatch == 1:
                    self.logi.appendMsg("PASS - SNIFFER -  Found for sniffer_fitler[" + str([i]) + "] = " + str(arr_sniffer_fitler[i]))
                    time.sleep(10)
                    #return Playback_Result
                else:
                    self.logi.appendMsg("FAIL - SNIFFER -  Not found sniffer_fitler[" + str([i]) + "] = " + str(arr_sniffer_fitler[i]))
                    return False

            return Playback_Result
        except Exception as err:
            print(err)
            return False


    # Moran.Cohen
    # This function connect to your local linadmin and return ssh connection to the streaming machine
    def SSH_linadmin_Connection(self, SSH_streamingLinux_Machine,remote_user_LiveNGNew,LocalCheckpointKey):

        try:
            cmdline = f"ssh -i  nva1-live-streamers-key {remote_user_LiveNGNew}@{SSH_streamingLinux_Machine}"
            ssh = paramiko.SSHClient()
            cert = paramiko.RSAKey.from_private_key_file(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', LocalCheckpointKey)))
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("START SSH CONNECTING")
            try:
                ssh.connect(hostname="ssh.us-2.checkpoint.security",username="nva1-linadmin-dev",pkey=cert,timeout=120,disabled_algorithms=dict(pubkeys=["rsa-sha2-512", "rsa-sha2-256"]))
            except Exception as Exp:
                print("this exception happened when trying to connect ssh with pem file: " + str(Exp))

            remote_conn = ssh.invoke_shell()
            self.logi.appendMsg("INFO - Interactive SSH - Going to run ffmpegCmdLine = " + cmdline)
            self.logi.appendMsg("INFO - Interactive SSH - ffmpegCmdLine datetime " + str(datetime.datetime.now()))
            time.sleep(1)
            #stdin, stdout, stderr = remote_conn.exec_command("hostname")
            remote_conn.send(cmdline + "\n")
            time.sleep(2)
            output = str(remote_conn.recv(10000))
            #output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
            self.logi.appendMsg("INFO - ffmpegCmdLine output = " + str(output))
            #time.sleep(timout_SearchPsAux)
            if output.find("Last login")>=0:
                self.logi.appendMsg("PASS - Connection to linadmin - Last login.output = " + str(output))
            else:
                self.logi.appendMsg("FAIL -  Connection to linadmin - Last login.output = " + str(output))
                return False
            time.sleep(1)
            remote_conn.send("\n")
            remote_conn.send("sudo su -" + "\n")
            time.sleep(1)

            return remote_conn,ssh
        except Exception as err:
            print(err)
            return False

    # Create Simulive Wecast By PHP script on Window machine
    def CreateSimuliveWecastByPHPscript(self, host, user, passwd, configFile, isSimulive=1, manualLiveHlsUrl="'" + "'",manualLiveBackupHlsUrl="'" + "'", timoutMax=5, sessionEndOffset=5,startTime=None, sessionTitle="AUTOMATION_BECore_Simulive_ManualLive",env="prod", PublisherID=None, UserSecret=None, url=None,conversionProfileID=None, kwebcastProfileId=None, eventsProfileId=None,vodId=None):
        import paramiko
        try:

            if startTime == None:
                startTime = time.time()
            sessionStart = int(startTime)
            endTime = startTime + sessionEndOffset * 60
            sessionEnd = int(endTime)  # add 5 minutes
            self.logi.appendMsg('INFO - CreateSimuliveWecastByPHPscript LONG format sessionStart: ' + str(sessionStart) + ", sessionEnd = " + str(sessionEnd))
            self.logi.appendMsg('INFO - CreateSimuliveWecastByPHPscript DATE format sessionStart: ' + str(datetime.datetime.fromtimestamp(sessionStart).strftime('%Y-%m-%d %H:%M:%S')) + ", sessionEnd = " + str(datetime.datetime.fromtimestamp(sessionEnd).strftime('%Y-%m-%d %H:%M:%S')))
            datetime.datetime.fromtimestamp(sessionStart).strftime('%Y-%m-%d %H:%M:%S')

            if isSimulive == 1:  # simulive
                # Set cmd live for php script
                # Simulive
                #scriptLocation = '"' + 'C:\Program Files (x86)\Kaltura\createWebcast\createWebcastEnv_argv.php' + '"' #origin
                #scriptLocation = '"' + r'C:\Program Files (x86)\Kaltura\createWebcast\createWebcastEnv_argv.php' + '"'
                #scriptLocation = '"' + r'C:\temp\createWebcast\createWebcastEnv_argv.php' + '"'
                scriptLocation = '"' + r'C:\php\createWebcast\createWebcastEnv_argv.php' + '"'
                #scriptLocation = '"' + os.path.abspath(os.path.join(os.path.dirname( __file__ ))) + '\createWebcastEnv_argv.php' + '"'
                cmdLine = 'php ' + scriptLocation + ' ' + str(sessionStart) + ' ' + str(sessionEnd) + ' ' + str(configFile) + ' ' + str(sessionTitle) + ' ' + str(PublisherID) + ' ' + str(UserSecret) + ' ' + str(url) + ' ' + str(conversionProfileID) + ' ' + str(kwebcastProfileId) + ' ' + str(eventsProfileId) + ' ' + str(vodId)

            else:  # Manual live
                scriptLocation = '"' + 'C:\Program Files (x86)\Kaltura\createWebcast\createWebcastEnv_Simulive_ManualLive.php' + '"'
                cmdLine = 'php ' + scriptLocation + ' ' + str(sessionStart) + " " + str(sessionEnd) + " " + str(configFile) + " " + str(isSimulive) + " " + str(manualLiveHlsUrl) + " " + str(manualLiveBackupHlsUrl) + " " + str(sessionTitle)
            self.logi.appendMsg('INFO - Going to run cmdLine: ' + str(cmdLine))

            #from subprocess import Popen, PIPE
            print("Executing build")
            self.logi.appendMsg('INFO - Going to execute php script' + str(cmdLine))
            pipe = Popen(cmdLine, stdout=PIPE, stderr=PIPE)
            result = pipe.stdout.readline()
            print("result from stdout = " + str(result))

            if result == "" or result == "0":
                return False, "No entry return from php script"

            '''if result[0] == "0" and env == "prod":  # if first character is 0
                result = result[1:]  # remove first character'''
            result = str(result).split("'")[1].replace('\\n', '')
            result = str(result).replace('\\r', '')
            '''if result[0:2] == "00" or result[0:2] == "01":
                result = result[1:]'''
            SimuliveEntryID = str(result.strip())  # remove spaces and \n
            if SimuliveEntryID:
                return True, SimuliveEntryID
        except Exception as err:
            print("Exception occured -" + str(err))
            return False, err



    ###############end
    # Moran.Cohen
    # This function return multi process ids that are streams by array
    def SearchPsAuxffmpeg_MultiArrProcessIds(self,host, user, passwd,entryId,partnerId,timoutMax=10,env='testing',BroadcastingUrl=None,HybridCDN=False,SSH_CONNECTION=g_SSH_CONNECTION,LocalCheckpointKey=g_LocalCheckpointKey):
        try:
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            statusStreaming = False
            BroadcastingUrl = '"' + str(BroadcastingUrl) + '"'
            cmdLine = "ps aux |grep -v bash |grep ffmpeg | grep " + BroadcastingUrl #-v is for remove bash

            # Create SSH Connection for streamer
            rc, remote_conn, ssh = self.SSH_Connection(host=host, user=user, passwd=passwd,SSH_CONNECTION=SSH_CONNECTION,LocalCheckpointKey=LocalCheckpointKey)
            if rc == False:
                self.logi.appendMsg("FAIL - SSH_Connection host= " + host)
            # Run cmdLine
            if g_SSH_CONNECTION=="LINADMIN_SSH":#Run on local computer - linadmin
                stdin, stdout, stderr = ssh.exec_command(f"""ssh -i  nva1-live-streamers-key {user}@{host} {cmdLine}""",timeout=60, get_pty=True)
            else:#Run on remote machine - Regular ssh connection for streamer
                stdin, stdout, stderr = ssh.exec_command(cmdLine, timeout=60, get_pty=True)  # timeout=10
            time.sleep(5)
            output_ProcessId = stdout.read().decode('ascii')
            Result_ProcessIds=[]
            if output_ProcessId == "":
                return False, "NoProcessId"
            if output_ProcessId:
                ssh.close()
                print(str(output_ProcessId))
                arrProcessId_Rows = []
                arrProcessId_Rows = output_ProcessId.split("\n")
                for j in range(0, len(arrProcessId_Rows)):
                    arrProcessId=[]
                    if arrProcessId_Rows[j] != "":
                        arrProcessId=arrProcessId_Rows[j].split(" ")
                        for i in arrProcessId:
                            if i !="" and i != 'root' and i.isdigit():
                                Result_ProcessIds.append(i)
                                statusStreaming = True
                                break
                if statusStreaming==True:
                    #output_ProcessId=str(int(Result_ProcessIds[i]))
                    for i in range(0, len(Result_ProcessIds)):
                        print("Result_ProcessIds " + str(int(Result_ProcessIds[i])))
                    return True,Result_ProcessIds
                else:
                    return False, "NoProcessId"


        except Exception as err:
            print(err)
            return False,"NoProcessId"


    '''
    moran.cohen
    This function create SSH_Connection by:
    SSH_CONNECTION = Run streamer on local computer("LINADMIN_SSH") OR remote streamer machine by user&key("KEY_SSH") OR remote streamer machine by user&pwd("Regular_SSH")
    '''
    def SSH_Connection(self, host, user, passwd,SSH_CONNECTION="KEY_SSH",LocalCheckpointKey=None):
        try:
            statusStreaming = False
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user )
            if SSH_CONNECTION == "KEY_SSH":  # access SSH with KEY
                ssh = paramiko.SSHClient()
                cert = paramiko.RSAKey.from_private_key_file(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nva1-live-streamers-key.pem')))
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print("START SSH CONNECTING")
                try:
                    ssh.connect(hostname=host, username=user, pkey=cert)
                except Exception as Exp:
                    print("this exception happened when trying to connect ssh with pem file: " + str(Exp))
                remote_conn = ssh.invoke_shell()
                self.logi.appendMsg("INFO - Interactive SSH - Going to run sudo su - " + str(datetime.datetime.now()))
                output = remote_conn.recv(1000)
                remote_conn.send("\n")
                remote_conn.send("sudo su -" + "\n")
                time.sleep(1)

            elif SSH_CONNECTION == "Regular_SSH":  # OLD SSH access
                self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd )
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, username=user, password=passwd, timeout=60)  # was timeout=5
                remote_conn = ssh.invoke_shell()

            elif SSH_CONNECTION == "LINADMIN_SSH":  # For local computer streaming: ACCESS by linadmin
                self.logi.appendMsg("INFO - Going to perform linadmin connection. datetime=" + str(datetime.datetime.now()))
                remote_conn, ssh = self.SSH_linadmin_Connection(SSH_streamingLinux_Machine=host, remote_user_LiveNGNew=user,LocalCheckpointKey=LocalCheckpointKey)
                if remote_conn == False:
                    self.logi.appendMsg("FAIL - SSH_linadmin_Connection host= " + host)
                    return False, "NoProcessId_ERR_SSH_linadmin_Connection" + str(remote_conn),"No SSH"
                time.sleep(2)
            else:
                self.logi.appendMsg("FAIL - NO config way to connect SSH")
                return False, "NO config way to connect SSH","No SSH"

            return True,remote_conn,ssh
        except Exception as err:
            print(err)
            return False,str(err),"No Connection"



    '''
    Moran.Cohen
    This function play the recording after END LIVE previewMode/stop streaming and wait for the mp4 files
    '''
    def PLAY_RECORDING_After_END_LIVE(self,client,recorded_entrieslst,Recording_EntryID,recorded_entry,GO_LIVE_time,END_LIVE_time,PlayerVersion,env,testTeardownclass,sniffer_fitler_After_Mp4flavorsUpload,MinToPlay,seenAll_justOnce_flag,expectedFlavors_totalCount):
        try:
            #####################################*********** PLAY RECORDING after END LIVE
            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - Wait about 1 minutes after END LIVE and then start to check the mp4 flavors upload status recordedEntryId = " + str(Recording_EntryID) + " is playable. ")
            time.sleep(60)
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(Recording_EntryID))
            rc = self.WaitForFlavorsMP4uploaded(client, Recording_EntryID, recorded_entry,expectedFlavors_totalCount=expectedFlavors_totalCount)  # expectedFlavors_totalCount=1 for passthrough
            if rc == True:
                self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2/NA-4) .recordedEntryId" + Recording_EntryID)
                ######## Get conversion version of VOD entry
                filter = KalturaAssetFilter()
                pager = KalturaFilterPager()
                filter.entryIdEqual = Recording_EntryID
                First_RecordedEntry_Version = client.flavorAsset.list(filter, pager).objects[0].version
                timeout = 0
                while First_RecordedEntry_Version == None or First_RecordedEntry_Version == 0:
                    time.sleep(20)
                    First_RecordedEntry_Version = client.baseEntry.getContextData(Recording_EntryID,context_data_params).flavorAssets[0].version
                    timeout = timeout + 1
                    if timeout >= 30:  # 10 minutes timeout for waiting to version update
                        self.logi.appendMsg("FAIL - TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + Recording_EntryID)
                        testStatus = False
                        return False

                durationFirstRecording = int(client.baseEntry.get(Recording_EntryID).duration)  # Save the duration of the recording entry after mp4 flavors uploaded
                self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - First_RecordedEntry_Version = " + str(First_RecordedEntry_Version) + ", recordedEntryId = " + Recording_EntryID)
            else:
                self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + Recording_EntryID)
                testStatus = False
                return False

            # Waiting about 1 minutes before playing the recorded entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - Wait about 1.5 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(Recording_EntryID) + " is playable. ")
            time.sleep(90)
            # #####################################################
            # Create new player of latest version -  Create V2/3 Player because of cache isse
            self.logi.appendMsg('INFO - Going to create latest V' + str(PlayerVersion) + ' player')
            myplayer = uiconf.uiconf(client, 'livePlayer')
            if PlayerVersion == 2:
                player = myplayer.addPlayer(None, env, False, False)  # Create latest player v2
            elif PlayerVersion == 3:
                player = myplayer.addPlayer(None, env, False, False, "v3")  # Create latest player v3
            else:
                self.logi.appendMsg('FAIL - There is no player version =  ' + str(PlayerVersion))
            if isinstance(player, bool):
                testStatus = False
                return False
            else:
                playerId = player.id
            self.logi.appendMsg('INFO - Created latest V' + str(PlayerVersion) + ' player.self.playerId = ' + str(playerId))
            testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(player.id) + ')')

            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(Recording_EntryID) + "  - MinToPlay=" + str(MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlay * 60)
            seenAll = False
            timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
            while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 3:  # Change condition
                rc = self.verifyAllEntriesPlayOrNoBbyQrcode(recorded_entrieslst, True,PlayerVersion=PlayerVersion,sniffer_fitler=sniffer_fitler_After_Mp4flavorsUpload,Protocol="http")
                time.sleep(5)
                timeout = timeout + 1
                if rc == False and timeout < 2:
                    self.logi.appendMsg("INFO - ****** timeout:Going to play AGAIN after player CACHE ISSUE RECORDED ENTRY from " + sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(Recording_EntryID) + "  - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                    time.sleep(90)  # Time for player cache issue
                if not rc and timeout >= 3:  # Change condition
                    print("FAIL - timeout:Going to play RECORDED ENTRY with caption after mp4 conversion - Retry count:timeout = " + str(timeout))
                    testStatus = False
                    return False
                if seenAll_justOnce_flag == True and rc != False:  # Change condition
                    seenAll = True
                    break

            ########### DURATION Compare for recording entry
            # Cal recording duration after mp4 flavors are uploaded
            self.logi.appendMsg("INFO - AFTER END LIVE:Going to verify DURATION of recorded entry.FirstRecording_EntryID = " + str(Recording_EntryID))
            recordingTime1 = int(END_LIVE_time - GO_LIVE_time)
            if recordingTime1 > int(durationFirstRecording):
                deltaRecording1 = recordingTime1 - durationFirstRecording
            else:
                deltaRecording1 = durationFirstRecording - recordingTime1
            if 0 <= deltaRecording1 <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                self.logi.appendMsg("PASS - AFTER END LIVE:VOD entry1:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(Recording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER END LIVE:VOD entry1:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(Recording_EntryID)
                testStatus = False

            return True
        except Exception as err:
            print(err)
            return False



    '''
    Moran.Cohen
    This function Add AccessControlLimitDeliveryProfilesAction with deliveryProfileIds
    '''
    def Add_KalturaAccessControlLimitDeliveryProfilesAction(self, client, deliveryProfileIds, name):
        try:
            access_control_profile = KalturaAccessControlProfile()
            access_control_profile.name = name#"name"
            access_control_profile.rules = []
            access_control_profile.rules.append(KalturaRule())
            access_control_profile.rules[0].forceAdminValidation = KalturaNullableBoolean.TRUE_VALUE
            access_control_profile.rules[0].actions = []
            access_control_profile.rules[0].actions.append(KalturaAccessControlLimitDeliveryProfilesAction())
            access_control_profile.rules[0].actions[0].deliveryProfileIds = deliveryProfileIds

            rc_access_control_profile = client.accessControlProfile.add(access_control_profile)

            return rc_access_control_profile
        except Exception as err:
            print(err)
            return False

    '''
    Moran.Cohen
    This function wait for EntryVendorTask Status=X
    Expected_STATUS= Set the expected status
    MAXtimeout= Set the max timeout time in minutes for waiting to VendorTask.Status
    '''
    def WaitingForEntryVendorTaskStatus(self,client, EntryVendorTaskId,Expected_STATUS=3,MAXtimeout=5):
        try:
            # Verify VendorTask Status - 3 processing after arriving to startTime --> will update for sure just after arriving to startTime and start stream for 10sec
            rc = self.Create_KalturaEntryVendorTask_VerifyStatus(client=client, id=EntryVendorTaskId,Expected_STATUS=Expected_STATUS)  # entryVendorTask.status - first 1 scheduled , 3 processing
            # if rc == False:
            timeout = 0
            while rc == False:
                self.logi.appendMsg("INFO - Expected STATUS is NOT 3 processing - After arriving to schedulingEvent.startTime:Create_KalturaEntryVendorTask_VerifyStatus.Details:  EntryVendorTaskId= " + str(EntryVendorTaskId))
                self.logi.appendMsg("INFO - Wait another 1 minutes until getting STATUS=3(processing) or getting timeout after 5 minutes")
                timeout = timeout + 1
                time.sleep(60)
                if timeout > MAXtimeout:  # 5minutes timeout
                    self.logi.appendMsg("FAIL - TIMEOUT:Create_KalturaEntryVendorTask_VerifyStatus.Details: EntryVendorTaskId= " + str(EntryVendorTaskId) + " , Expected_STATUS= 3 processing")
                    #testStatus = False
                    return False
                # Verify if getting Expected_STATUS=3 processing
                rc = self.Create_KalturaEntryVendorTask_VerifyStatus(client=client, id=EntryVendorTaskId,Expected_STATUS=Expected_STATUS)  # entryVendorTask.status - first 1 scheduled , 3 processing
            return True
        except Exception as err:
            print(err)
            return False