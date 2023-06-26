'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_949_LiveNG_Transcoding_DVR_DPredirect_CFtokanization.py
 @desc : this test check E2E test of new LiveNG and CF tokanization requests permissions entries Transcoding with DVR - including scroll to start point - REWIND ,Scroll to middle point - REWIND, BACK TO LIVE button
host access run ffmpeg cmd 
verification of create new entries ,API,start/check ps/stop streaming, Playback and liveDashboard Analyzer - alerts tab and channels
Verify the playback url m3u8 on CF tokanization requests permissions
Verify the invalid Policy on CF tokanization requests permissions

***** Delivery profile ********
Create access control with cf (It can be used instead of config partner delivery profile in admin console that affect all the entries on the partner) -
Create access control by API:
kaltura api session:ks
service:accessconrolProfile
action:add
AccessControlProfile=KalturaAccessControlProfile
name:CF tokenized
item0(kalturaRule)=KalturaRule
forceAdminValidation=TRUE_VALUE
item0(KalturaRuleAction)=KalturaAccessControlLimitDeliveryProfile
DeliveryProfileIds:1132 ( Live NG-CF_Redirect - HLS)

TESTING QA env-partner 6611:
applehttp VOD 1096 default aws hls,1113 hls short segment-simulive-aws
applehttp LIVE 1095 live ng,1132: Live NG-CF_Redirect - HLS--- >Access control = 26854 on QA env
mpegdash LIVE 1119 live ng-dash

PRODUCTION ENV - partner 2930571:
mpegdash	Live	16921 Live DASH
applehttp	Live	X Live NG-CF_Redirect  --> Access control = ????? on PROD env ---Don't have this one in PROD
affect all the entries this way->If you using access control you don't need to add this delivery profile to your partner config

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
'''


import datetime
import os
import sys
import time

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter2
import Config
import Practitest
import Entry
import uiconf
import tearDownclass
import MySelenium

import live
import LiveDashboard
import Transcoding
import QrcodeReader
import clsPlayerV2
import ast
from KalturaClient.Plugins.Core import *
#import requests
import StaticMethods
### Jenkins params ###
#===============================================================================
testStatus = True

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):

        StaticMethods.before_run(self)
        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')

        # Environment BE server URL
        if self.ServerURL is None:
            self.ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')
        print("ServerURL = " + self.ServerURL)
        # LiveNG config partner:
        if self.PartnerID != None:
            self.PublisherID = self.PartnerID
            self.UserSecret = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'LIVENG_UserSecret')
        else:
            self.PublisherID = self.inifile.RetIniVal(self.section, 'LIVENG_PublisherID')  # QA 6611/ PROD 2930571
            self.UserSecret = self.inifile.RetIniVal(self.section, 'LIVENG_UserSecret')
        # CF tokanization access control
        self.access_control_id_CFtokanization_Redirect = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'access_control_id_CFtokanization_Redirect')  # QA 26854#Prod ""

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        #self.sniffer_fitler = '/scf/' #search in sniffer playback for -CF Tokenized hls
        self.sniffer_fitler = 'cflive'#'cflive;/hls/'  # search in sniffer playback for -CF Tokenized hls
        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LiveNG_5')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNG_5')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"      

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True
        self.PlayerVersion = 3 # player version 2 or 3

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project LIVENG
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_949_LiveNG_Transcoding_DVR_DPredirect_CFtokanization')
        self.logi.initMsg('test_949_LiveNG_Transcoding_DVR_DPredirect_CFtokanization')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_949_LiveNG_Transcoding_DVR_DPredirect_CFtokanization(self):
        global testStatus
        try:
            if self.env == 'prod':
                self.logi.appendMsg('INFO - This tests is NOT running on PRODUCTION - ONLY QA env')
                return
            # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE cloud transcode IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Cloud transcode')
            Transobj = Transcoding.Transcoding(self.client, 'Cloud transcode')
            self.CloudtranscodeId = Transobj.CreateConversionProfileFlavors(self.client, 'Cloud transcode','32,33,34,35')
            if isinstance(self.CloudtranscodeId, bool):
                testStatus = False
                return

            # Create player of latest version -  Create V2/3 Player
            self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion)  + ' player')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            if self.PlayerVersion == 2:
                self.player = myplayer.addPlayer(None,self.env,False, False) # Create latest player v2
            elif self.PlayerVersion == 3:
                self.player = myplayer.addPlayer(None,self.env,False, False,"v3") # Create latest player v3
            else:
                self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
            if isinstance(self.player,bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')

            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)

            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveEntry_DVR_Trans_CFtokanization_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.CloudtranscodeId)
                #Add stream entry    # recordStatus - send 0 for disable, 1 for append, 2 for per_session # dvrStatus - send 0 for disable, 1 for enable
                self.entry = Entryobj.AddEntryLiveStream(None, None, recordStatus=0, dvrStatus=1)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)


            time.sleep(5)

            # Set accessControl
            self.logi.appendMsg('INFO - Going to set AccessControl id  with CF tokanization' + str(self.access_control_id_CFtokanization_Redirect) + 'EntryId =' + str(self.entry.id))
            base_entry = KalturaBaseEntry()
            base_entry.accessControlId = self.access_control_id_CFtokanization_Redirect
            result = self.client.baseEntry.update(self.entry.id, base_entry)

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                time.sleep(2)
                self.entryId = str(self.entrieslst[i].id)
                if self.IsSRT == True:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primarySrtBroadcastingUrl
                    primarySrtStreamId = self.streamUrl[i].primarySrtStreamId
                    self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
                else:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primaryBroadcastingUrl
                if self.env == 'testing':
                    if self.Live_Change_Cluster == True:
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByffmpegCmd.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
                # ******* CHECK CPU usage of streaming machine
                #cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
                self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))
                cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"
                rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine)
                if rc == True:
                    self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
                else:
                    self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                    testStatus = False
                    return

                '''# Verify requests of CF tokanization
                m3u8_url = f"""https://{self.url}/p/{self.PublisherID}/playManifest/entryId/{self.entryId}/protocol/https/format/applehttp/a.m3u8"""
                m3u8_url = f"""{self.ServerURL}/p/{self.PublisherID}/playManifest/entryId/{self.entryId}/protocol/https/format/applehttp/a.m3u8"""
                rc = self.liveObj.requests_CFtokanization(m3u8_url, self.entryId)
                if rc == True:
                    self.logi.appendMsg("PASS - requests_CFtokanization.Details: m3u8_url=" + str(m3u8_url) + " , entryId=" + self.entryId)
                else:
                    self.logi.appendMsg("FAIL - requests_CFtokanization.Details: m3u8_url=" + str(m3u8_url) + " , entryId=" + self.entryId)
                    testStatus = False
                    # return'''

                # ****** Livedashboard - Channels tab
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False
            # Verify DVR
            rc = self.liveObj.DVR_Verification(self.liveObj, self.entrieslst, self.entryId, self.MinToPlay,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler,Protocol="http",ServerURL=self.ServerURL)
            if rc == True:
                self.logi.appendMsg("PASS  - DVR_Verification. entryId = " + str(self.entryId))
            else:
                self.logi.appendMsg("FAIL  - DVR_Verification. entryId = " + str(self.entryId))
                testStatus = False

            #Stop streaming - kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return

        except Exception as e:
            print(e)
            testStatus = False
            pass


    #===========================================================================
    # TEARDOWN
    #===========================================================================

    def teardown_class(self):

        global testStatus

        print ('#############')
        print (' Tear down - Wd.quit')

        try:
            self.PlayBrowserDriver.quit()
        except Exception as Exp:
            print (Exp)
            pass

        try:
            self.Wd.quit()
        except Exception as Exp:
            print (Exp)
            pass
        try:
            print ('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
            print ('#############')
        except Exception as Exp:
            print (Exp)
            pass

        if testStatus == False:
            print ("fail")
            self.practitest.post(self.Practi_TestSet_ID, '949', '1', self.logi.msg)
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            print ("pass")
            self.practitest.post(self.Practi_TestSet_ID, '949', '0', self.logi.msg)
            self.logi.reportTest('pass', self.sendto)
            assert True



    #===========================================================================
    #pytest.main(['test_949_LiveNG_Transcoding_DVR_DPredirect_CFtokanization.py','-s'])
    #===========================================================================
        
        
        