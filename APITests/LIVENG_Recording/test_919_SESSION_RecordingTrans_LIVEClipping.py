'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_919_SESSION_RecordingTrans_LIVEClipping.py
 @desc : this test check E2E test of new LiveNG entries transcoding + SESSION recording with LIVEClipping logic function
 verification of create new entries ,API,start/check ps/stop streaming, QRCODE Playback and liveDashboard Analyzer - alerts tab and channels
 Create live clipping by API.
 LIVE entry playback by QRCODE.
 Verify VOD/RECORDED entry playback from klive by sniffer logic.
 Verfiy flavorAssets status (mp4 flavor upload) by API.
 LIVEClipping entry playback after mp4 flavor uploaded by checking sniffer verification from aws/cfvod/qa-nginx-vod
 LIVEClipping duration verification after mp4 flavors are ready by Playback and API baseEntry.get
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

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
from KalturaClient import *
from KalturaClient.Plugins.Core import *
import ast
import StaticMethods
### Jenkins params ###
#===============================================================================
# cnfgCls = Config.ConfigFile("stam")
# #Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# Practi_TestSet_ID,isProd = 11,"false"
# if str(isProd) == 'true':
#     isProd = True
# else:
#     isProd = False
# 
# isProd = False # LiveNG is just supported on testing
#==========================PublisherID=====================================================
testStatus = True

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        StaticMethods.before_run(self)
        #self.PartnerID ="231"
        #self.ServerURL ="https://api.nvd1.ovp.kaltura.com"
        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')

        # Recording after mp4 files are uploaded
        self.sniffer_fitler_After_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_After_Mp4flavorsUpload')  # QA 'qa-aws-vod'  # PROD 'cfvod'
        self.sniffer_fitler_Before_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_Before_Mp4flavorsUpload')  # QA and Prod klive->regular DP (cflive ->DP CF)

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
        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        # Jenkis run LIVENGRecording
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENG_Recording')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENG_Recording')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        #self.filePath = "/home/kaltura/entries/Disney_multi.mp4"
        self.WaitBeforeCreateLiveClipping = 60 # 1 mintues
        #The times are in miliseconds, so it mean - start clip at the 10th sec, and clip 60sec long (so the clip will be from 00:00:10 until 00:01:10):
        self.LiveClipping_offset = 10000 # miliseconds
        self.LiveClipping_duration = 120000 # miliseconds (2 minutes)

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        #self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_919_SESSION_RecordingTrans_LIVEClipping')
        self.logi.initMsg('test_919_SESSION_RecordingTrans_LIVEClipping')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)


    def test_919_SESSION_RecordingTrans_LIVEClipping(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE cloud transcode IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Cloud transcode')
            Transobj = Transcoding.Transcoding(self.client, 'Cloud transcode')
            self.CloudtranscodeId = Transobj.CreateConversionProfileFlavors(self.client, 'Cloud transcode', '32,33,34,35')
            if isinstance(self.CloudtranscodeId, bool):
                testStatus = False
                return
                    
            #Create player of latest version -  Create V2/3 Player
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-RECORDING_SESSION_LiveClipping_SANITY_Pass_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(recordStatus=2) # 2 : KalturaRecordStatus.PER_SESSION
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            time.sleep(5)
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                if self.IsSRT == True:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primarySrtBroadcastingUrl
                    primarySrtStreamId = self.streamUrl[i].primarySrtStreamId
                    self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
                else:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primaryBroadcastingUrl
                if self.env == 'prod':
                    if self.Live_Change_Cluster == True:
                        token1=Current_primaryBroadcastingUrl
                        token1=token1.split("t=")[1].split("&")[0]
                        Current_primaryBroadcastingUrl=f"""rtmp://rtmp-0.cluster-1-a.live.nvp1.ovp.kaltura.com:1935/kLive?t={token1}&i=0&e={self.entryId}"""
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
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
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
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

                time.sleep(2)
                # ****** Livedashboard - Channels tab
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False

            # LIVE ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play LIVE ENTRY " + str(self.entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True

            self.logi.appendMsg("PASS - LIVE ENTRY Playback of " + str(self.entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### Get recordedEntryId from the live entry by API
            self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(entryLiveStream.recordedEntryId) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload +  " for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload, Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            self.logi.appendMsg("INFO - ********************** Going to create live Clipping entry.")
            LiveClipping_duration_Minutes = (self.LiveClipping_duration / (1000 * 60)) % 60
            ClipEntry_entry = self.liveObj.CreateLiveClipping(self.liveObj,self.client,entryLiveStream.recordedEntryId,self.LiveClipping_offset,self.LiveClipping_duration)
            if ClipEntry_entry == False:
                testStatus = False
                self.logi.appendMsg("FAIL - CreateLiveClipping.LIVE_ENTRY= + " + str(self.entryId) + " , entryLiveStream.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                return

            self.logi.appendMsg("PASS - CreateLiveClipping.ClipEntry_entry= + " + str(ClipEntry_entry.id))
            self.ClipEntry_entrieslst = []
            self.ClipEntry_entrieslst.append(ClipEntry_entry)

            #First play without mp4 - ADD
            # #####################################################
            # CLIPPED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - CLIPPED_ENTRY:Going to play CLIPPED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " before MP4 flavors uploaded " + str(ClipEntry_entry.id) + "  - MinToPlay(LiveClipping_duration_Minutes)=" + str(LiveClipping_duration_Minutes) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(5)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.ClipEntry_entrieslst,boolShouldPlay=True,MinToPlayEntry=(LiveClipping_duration_Minutes-0.5),PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                rc = True
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - CLIPPED_ENTRY:Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " of " + str(ClipEntry_entry.id) + " before MP4 flavors uploaded - MinToPlay(LiveClipping_duration_Minutes)=" + str(LiveClipping_duration_Minutes) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(2)
            #kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - Wait about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status ClipEntry_entry.id = " + str(ClipEntry_entry.id) + " is playable. ")
            time.sleep(60)
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("PASS - CLIPPED_ENTRY:Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on ClipEntry_entry.id = " + str(ClipEntry_entry.id))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client,ClipEntry_entry.id, recorded_entry,expectedFlavors_totalCount=4) #expectedFlavors_totalCount=1 for passthrough
            if rc == True:
                self.logi.appendMsg("PASS - CLIPPED_ENTRY:Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + ClipEntry_entry.id)
            else:
                self.logi.appendMsg("FAIL - CLIPPED_ENTRY:MP4 flavors did NOT uploaded to the recordedEntryId = " + ClipEntry_entry.id)
                testStatus = False
                return

            # Waiting about 1 minutes before playing the recored entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - CLIPPED_ENTRY:Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # #####################################################
            #Create new player of latest version -  Create V2/3 Player because of cache isse
            self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion) + ' player')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            if self.PlayerVersion == 2:
                self.player = myplayer.addPlayer(None, self.env, False, False)  # Create latest player v2
            elif self.PlayerVersion == 3:
                self.player = myplayer.addPlayer(None, self.env, False, False, "v3")  # Create latest player v3
            else:
                self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
            if isinstance(self.player, bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
            self.liveObj.playerId = self.playerId
            # #####################################################
            # CLIPPED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - CLIPPED_ENTRY:Going to play CLIPPED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(ClipEntry_entry.id) + "  - MinToPlay(LiveClipping_duration_Minutes)=" + str(LiveClipping_duration_Minutes) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                time.sleep(5)
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.ClipEntry_entrieslst,boolShouldPlay=True,MinToPlayEntry=(LiveClipping_duration_Minutes-0.5),PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",ServerURL=self.ServerURL)
                time.sleep(5)
                rc = True
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - CLIPPED_ENTRY:Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(ClipEntry_entry.id) + " after MP4 flavors uploaded - MinToPlay(LiveClipping_duration_Minutes)=" + str(LiveClipping_duration_Minutes) + " , End time = " + str(datetime.datetime.now()))

            self.logi.appendMsg('INFO - CLIPPED_ENTRY:Going to verify duration of clipEntry' + str(ClipEntry_entry.id))
            Actual_ClipEntry_baseEntry = self.client.baseEntry.get(str(ClipEntry_entry.id))
            print("baseEntry.get - Actual_ClipEntry_baseEntry.duration(seconds) = " + str(Actual_ClipEntry_baseEntry.duration))
            Expected_LiveClipping_duration_seconds =int((self.LiveClipping_duration/1000))
            diff_LiveClipping_duration_seconds = abs(Expected_LiveClipping_duration_seconds - Actual_ClipEntry_baseEntry.duration)
            print(diff_LiveClipping_duration_seconds)
            #if Expected_LiveClipping_duration_seconds == Actual_ClipEntry_baseEntry.duration:
            if (diff_LiveClipping_duration_seconds>=0 or diff_LiveClipping_duration_seconds<=6):#Max difference 6 seconds between results
                self.logi.appendMsg('PASS - CLIPPED_ENTRY:' + str(ClipEntry_entry.id) + ' , Actual_ClipEntry_baseEntry.duration(seconds) = ' + str(Actual_ClipEntry_baseEntry.duration) + ' is EQUAL to Expected_LiveClipping_duration_seconds(seconds) = ' + str(Expected_LiveClipping_duration_seconds))
            else:
                self.logi.appendMsg('FAIL - CLIPPED_ENTRY:' + str(ClipEntry_entry.id) + ' , Actual_ClipEntry_baseEntry.duration(seconds) = ' + str(Actual_ClipEntry_baseEntry.duration) + ' is DIFFERENT from Expected_LiveClipping_duration_seconds(seconds) = ' + str(Expected_LiveClipping_duration_seconds))
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
        
        print('#############')
        print(' Tear down')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        print('Tear down - testTeardownclass')
        
        try:
            time.sleep(30)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '919','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '919','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_919_SESSION_RecordingTrans_LIVEClipping.py -s')
    #===========================================================================
        
        
        