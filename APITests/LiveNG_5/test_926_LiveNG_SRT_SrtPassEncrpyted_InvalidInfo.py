'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_926_LiveNG_SRT_SrtPassEncrpyted_InvalidInfo.py
 
 @desc : This test check E2E test of new LiveNG entries SRT streaming both Primary +  Backup -> Same URL playback - Passthrough.
 Update SrtPass and then stream with invalid info  Encrpyted / passphrase -- > Verify the the primary+ backup are streaming ok.
    1)No passphrase info:
    "srt://srtlb.cluster-1-a.live.nvq1.ovp.kaltura.com:7045/kLive?streamid=#:::e=0_tihujbqw,st=0,ep=Y1E5adAqHj-_huAryCbXiA" - error
    Connection setup failure: connection rejected.
    Last message repeated 1 times
    srt://srtlb.cluster-1-a.live.nvq1.ovp.kaltura.com:7045/kLive?streamid=#:::e=0_tihujbqw,st=0,ep=Y1E5adAqHj-_huAryCbXiA: Unknown error occurred
    Mon Mar 28 12:34:21 UTC 2022

    2)No passphrase value:
    "srt://srtlb.cluster-1-a.live.nvq1.ovp.kaltura.com:7045/kLive?streamid=#:::e=0_tihujbqw,st=0,ep=Y1E5adAqHj-_huAryCbXiA&passphrase=" - error
    Connection setup failure: connection rejected.
    Last message repeated 1 times
    srt://srtlb.cluster-1-a.live.nvq1.ovp.kaltura.com:7045/kLive?streamid=#:::e=0_tihujbqw,st=0,ep=Y1E5adAqHj-_huAryCbXiA&passphrase=: Unknown error occurred
    Mon Mar 28 12:34:47 UTC 2022

    3)Wrong passphrase value:
    "srt://srtlb.cluster-1-a.live.nvq1.ovp.kaltura.com:7045/kLive?streamid=#:::e=0_tihujbqw,st=0,ep=Y1E5adAqHj-_huAryCbXiA&passphrase=1" - error
    failed to set option SRTO_PASSPHRASE on socket: Operation not supported: Bad parameters.
    Last message repeated 1 times
    srt://srtlb.cluster-1-a.live.nvq1.ovp.kaltura.com:7045/kLive?streamid=#:::e=0_tihujbqw,st=0,ep=Y1E5adAqHj-_huAryCbXiA&passphrase=1: Input/output error
    Mon Mar 28 12:35:03 UTC 2022
 Start SRT streaming by new logic function - host access run ffmpeg cmd.
 verification of create new entries ,API,start/check ps/stop streaming, Playback with the created player v2+v3 and liveDashboard Analyzer - alerts tab and channels

    e - entry id
    st - 0/1 for primary/secondary
    p - for token
 SRT PROD,example:
 ffmpeg -re -i Disney_multi.ts -c copy -f mpegts "srt://srtlb.cluster-1-c.live.nvp1.ovp.kaltura.com:7045?streamid=#:::name=1_bh0563x7,type=p,token=786c8f0c,index=1"
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
#pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
#sys.path.insert(1,pth)


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
import ast
from KalturaClient import *
from KalturaClient.Plugins.Core import *
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
        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LiveNG_5')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNG_5')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        #Update srtPass value
        self.srtPass="1234567890"

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        #self.PlayerVersion = 2 # Player version 2 or 3
        #self.AllPlayers = True # If True running the two version in a loop/ If False running just self.PlayerVersion
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        self.logi = reporter2.Reporter2('test_926_LiveNG_SRT_SrtPassEncrpyted_InvalidInfo')
        self.logi.initMsg('test_926_LiveNG_SRT_SrtPassEncrpyted_InvalidInfo')

    def test_926_LiveNG_SRT_SrtPassEncrpyted_InvalidInfo(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Passthrough')
            Transobj = Transcoding.Transcoding(self.client, 'Passthrough')
            self.passtrhroughId = Transobj.CreateConversionProfileFlavors(self.client, 'Passthrough', '32,36,37')
            if isinstance(self.passtrhroughId, bool):
                testStatus = False
                return
                             
            # Create player of latest version -  Create V2/3 Player
            self.logi.appendMsg('INFO - Going to create latest V2')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            self.player = myplayer.addPlayer(None,self.env,False, False) # Create latest player v2
            if isinstance(self.player,bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest player V2 ' + str(self.playerId))       
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')    
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
                     
            self.logi.appendMsg('INFO - Going to create latest V3')
            myplayer3 = uiconf.uiconf(self.client, 'livePlayer')
            self.player_v3 = myplayer3.addPlayer(None,self.env,False, False,"v3") # Create latest player v3
            if isinstance(self.player_v3,bool):
                testStatus = False
                return
            else:
                self.playerId_v3 = self.player_v3.id
            #Create live object with current player_v3
            self.logi.appendMsg('INFO - Created latest player V3 ' + str(self.player_v3))       
            self.testTeardownclass.addTearCommand(myplayer3,'deletePlayer(' + str(self.player_v3.id) + ')')
            #Create live object with current player
            self.liveObj_v3 = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId_v3)
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-SRT_PRIMARYBACKUP_PASS_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                # Updated srtPass value on the live entry
                live_stream_entry = KalturaLiveStreamEntry()
                live_stream_entry.srtPass = self.srtPass
                result = self.client.liveStream.update(self.entry.id, live_stream_entry)
                #print(result)
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            # Stream only backup - > Get entryId and secondaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                Current_primaryBroadcastingUrl=self.streamUrl[i].primarySrtBroadcastingUrl
                primarySrtStreamId=self.streamUrl[i].primarySrtStreamId
                Current_secondaryBroadcastingUrl=self.streamUrl[i].secondarySrtBroadcastingUrl
                secondarySrtStreamId=self.streamUrl[i].secondarySrtStreamId
                if self.env == 'testing':
                    if self.Live_Change_Cluster == True:
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                        Current_secondaryBroadcastingUrl = Current_secondaryBroadcastingUrl.replace("1-b",self.Live_Cluster_Backup)
                # Invalid case:SRT INVALID INFO - No passphrase info
                self.logi.appendMsg("INFO - ************** SRT INVALID INFO - No passphrase info -Going to stream BOTH PRIMARY AND BACKUP **************** ENTRY#" + str(i) + " , EntryId = " + str(self.entryId))
                rc, ffmpegOutputString = self.liveObj.PrimaryBackupStreaming(liveObj=self.liveObj, entryId=self.entryId,filePath=self.filePath,remote_host=self.remote_host,remote_user=self.remote_user,remote_pass=self.remote_pass, env=self.env,PublisherID=self.PublisherID,Current_primaryBroadcastingUrl=Current_primaryBroadcastingUrl,primarySrtStreamId=primarySrtStreamId,Current_secondaryBroadcastingUrl=Current_secondaryBroadcastingUrl,secondarySrtStreamId=secondarySrtStreamId,srtPass=None, IsSRT=True,Flag_FailedStreamResult=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - PrimaryBackupStreaming - SRT INVALID INFO - No passphrase info. details: entryId=" + str(self.entryId))
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - PrimaryBackupStreaming - FAILED streaming because of SRT INVALID INFO - No passphrase info. details: entryId=" + str(self.entryId))

                # Invalid case:SRT INVALID INFO - No passphrase value
                self.logi.appendMsg("INFO - ************** SRT INVALID INFO - No passphrase value -Going to stream BOTH PRIMARY AND BACKUP **************** ENTRY#" + str(i) + " , EntryId = " + str(self.entryId))
                rc, ffmpegOutputString = self.liveObj.PrimaryBackupStreaming(liveObj=self.liveObj,entryId=self.entryId,filePath=self.filePath,remote_host=self.remote_host,remote_user=self.remote_user,remote_pass=self.remote_pass,env=self.env,PublisherID=self.PublisherID,Current_primaryBroadcastingUrl=Current_primaryBroadcastingUrl,primarySrtStreamId=primarySrtStreamId,Current_secondaryBroadcastingUrl=Current_secondaryBroadcastingUrl,secondarySrtStreamId=secondarySrtStreamId,srtPass="", IsSRT=True,Flag_FailedStreamResult=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - PrimaryBackupStreaming - SRT INVALID INFO - No passphrase value. details: entryId=" + str(self.entryId))
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - PrimaryBackupStreaming - FAILED streaming because of SRT INVALID INFO - No passphrase value. details: entryId=" + str(self.entryId))

                # Invalid case:SRT INVALID INFO - Wrong passphrase value
                self.logi.appendMsg("INFO - ************** SRT INVALID INFO - Wrong passphrase value -Going to stream BOTH PRIMARY AND BACKUP **************** ENTRY#" + str(i) + " , EntryId = " + str(self.entryId))
                rc, ffmpegOutputString = self.liveObj.PrimaryBackupStreaming(liveObj=self.liveObj,entryId=self.entryId,filePath=self.filePath,remote_host=self.remote_host,remote_user=self.remote_user,remote_pass=self.remote_pass,env=self.env,PublisherID=self.PublisherID,Current_primaryBroadcastingUrl=Current_primaryBroadcastingUrl,primarySrtStreamId=primarySrtStreamId,Current_secondaryBroadcastingUrl=Current_secondaryBroadcastingUrl,secondarySrtStreamId=secondarySrtStreamId,srtPass="1", IsSRT=True,Flag_FailedStreamResult=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - PrimaryBackupStreaming - SRT INVALID INFO - Wrong passphrase value. details: entryId=" + str(self.entryId))
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - PrimaryBackupStreaming - FAILED streaming because of SRT INVALID INFO - Wrong passphrase value. details: entryId=" + str(self.entryId))
                # Valid case
                self.logi.appendMsg("INFO - ************** VALID CASE: Going to stream BOTH PRIMARY AND BACKUP **************** ENTRY#" + str(i) + " , EntryId = " + str(self.entryId))
                # stream plays
                rc,ffmpegOutputString=self.liveObj.PrimaryBackupStreaming(liveObj=self.liveObj,entryId=self.entryId,filePath=self.filePath,remote_host=self.remote_host,remote_user=self.remote_user,remote_pass=self.remote_pass,env=self.env,PublisherID=self.PublisherID,Current_primaryBroadcastingUrl=Current_primaryBroadcastingUrl, primarySrtStreamId=primarySrtStreamId,Current_secondaryBroadcastingUrl=Current_secondaryBroadcastingUrl,secondarySrtStreamId=secondarySrtStreamId,srtPass=self.srtPass,IsSRT=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - PrimaryBackupStreaming. details: entryId=" + str(self.entryId))
                    testStatus = False
                    return
                self.logi.appendMsg("PASS - VALID CASE:Both PRIMARY + BACKUP are streaming OK -PrimaryBackupStreaming -.Details:  ENTRY#" + str(i) + " , entryId= " + self.entryId)
                #******* CHECK CPU usage of streaming machine
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

                # ****** Livedashboard verification
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary,ServersStreaming="Both_Primary_Backup")
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False

            if self.env == 'prod':
                time.sleep(10)
            time.sleep(2)
            for CurrentplayerVersion in range(2,4):
                time.sleep(2)
                #Playback verification of all entries with all player version = 2 and 3
                self.logi.appendMsg("INFO - ************** Going to play live entries on PlayerVersion= "+ str(CurrentplayerVersion) +"  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll==False:   
                        if CurrentplayerVersion == 3:
                            rc = self.liveObj_v3.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion,ServerURL=self.ServerURL)
                        else:
                            rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion,ServerURL=self.ServerURL)
                        time.sleep(5)
                        if not rc:
                            testStatus = False
                            return
                        if self.seenAll_justOnce_flag ==True:
                            seenAll = True
    
                self.logi.appendMsg("PASS - Playback of PlayerVersion= " + str(CurrentplayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                      
            # kill ffmpeg ps   
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId))
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
        #=======================================================================
        # try:
        #     self.Wd.quit()
        # except Exception as Exp:
        #     print Exp
        #     pass
        #=======================================================================
        try:
            print('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
            print('#############')
        except Exception as Exp:
           print(Exp)
           pass
        
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '926','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '926','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_926_LiveNG_SRT_SrtPassEncrpyted_InvalidInfo.py -s')
    #===========================================================================
        
        
        