'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen
https://github.com/kaltura/live/wiki/How-to#non-interactive-mode
@test_name: test_0_911_RestartRTMP_CreateTrans_kubernetesThreads.py
 @desc : this test check E2E test of new LiveNG entries transcoding - host access run ffmpeg cmd
 verification of create new entries ,API,start/check ps/stop streaming, QRCODE Playback and liveDashboard Analyzer - alerts tab and channels
 Running multi threading LIVE entry playback by QRCODE
 Check kubernetes only on QA env:
     Perform LIVE entry playback QRcode verification during two monitor restart
     kubectl  delete pod rtmp-1
     Verify LIVE entry playback by QRCODE during threading - Playback(and stream) should be failed during rtmp restart
     Verify that live dashboard error should not presented for the transcoding entry
     Restart streaming of the same entry + Verify playback is ok.

Restart rtmp --> kubectl delete pod rtmp
    Verify that the playback of the live entry is stopped during rtmp restart.
    Verify that it should influence the running streams - Disconnect stream.
    Cause failure to who trying to connect new stream at the moment that the rtmp is down
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
import Kubernetes
import LiveDashboard
import Transcoding
import QrcodeReader
from KalturaClient.Plugins.Core import *
import re
import threading
import queue
import ast # Change string(False/True) to BOOL


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

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

class TestClass:

    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):

        os.system("taskkill /IM chromedriver.exe /F")
        os.system("taskkill /IM chrome.exe /F")
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            # Streaming details
            self.url= "www.kaltura.com"
            #self.playerId = "48120213"# DASH v3 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')#""
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.sniffer_fitler_After_Mp4flavorsUpload = 'cfvod'
            print('PRODUCTION ENVIRONMENT')

        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            #self.playerId = "15236707" #dash player v3
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.sniffer_fitler_After_Mp4flavorsUpload = 'qa-nginx-vod'#'qa-aws-vod'
            print('TESTING ENVIRONMENT')
            self.KubernetesCmdLine_clusterType = "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
            # self.KubernetesCmdLine_clusterType = "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
            self.Live_Cluster_Primary = None
            self.Live_Change_Cluster = ast.literal_eval(inifile.RetIniVal(section, 'Live_Change_Cluster'))#import ast # Change string(False/True) to BOOL
            if self.Live_Change_Cluster==True:
                self.Live_Cluster_Primary=inifile.RetIniVal(section, 'Live_Cluster_Primary')
                self.Live_Cluster_Backup=inifile.RetIniVal(section, 'Live_Cluster_Backup')
                self.CONTEXT_NAME=f"""arn:aws:eks:us-east-1:383697330906:cluster/nvq1-eks-live-cluster-{self.Live_Cluster_Primary}"""
                self.KubernetesCmdLine_clusterType = f"""aws eks update-kubeconfig --name nvq1-eks-live-cluster-{self.Live_Cluster_Primary} --region us-east-1"""
        self.sendto = "moran.cohen@kaltura.com;"
        #***** SSH streaming server - AWS LINUX
        self.remote_host = inifile.RetIniVal('NewLive', 'remote_host_LIVENG_Kubernetes')
        self.remote_user = inifile.RetIniVal('NewLive', 'remote_user_LIVENG_Kubernetes')
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        # Kubernetes details
        self.Kubernetes_remote_host = inifile.RetIniVal('Kubernetes', 'Kubernetes_remote_host')
        self.Kubernetes_remote_user = inifile.RetIniVal('Kubernetes', 'Kubernetes_remote_user')
        self.Kubernetes_remote_pass = inifile.RetIniVal('Kubernetes', 'Kubernetes_remote_pass')

        #"kubectl get pods|grep controller"
        self.Kubernetes_Component = "rtmp-1"#"--selector=component=rtmp" # cmd line for delete pod
        self.Kubernetes_SearchResult = f"""pod "rtmp-1""" # Text for search after delete Component

        self.NumOfEntries = 1
        self.MinToPlay = 8 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True
        self.PlayerVersion = 3 # player version 2 or 3
        self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
        self.MinToPlayEntry = 5 # Minutes to play the live entry
        self.QrCodecheckProgress=4 #No threshold of playback
        self.NumOfRestartComponent = 1 # Number of time to do restart to component like monitor
        #self.sniffer_filter_per_flavor_list = '.ts;.m3u8'
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_0_911_RestartRTMP_CreateTrans_kubernetesThreads')
        self.logi.initMsg('test_0_911_RestartRTMP_CreateTrans_kubernetesThreads')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
        self.KubernetesObj = Kubernetes.Kubernetes_Live(None, self.logi,isProd, self.PublisherID)

    def test_0_911_RestartRTMP_CreateTrans_kubernetesThreads(self):
        global testStatus
        try:
            if self.env =='prod':
                self.logi.appendMsg('INFO - This tests is NOT running on PRODUCTION - ONLY QA env')
                return
            #create client session
            self.logi.appendMsg('start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            Transobj = Transcoding.Transcoding(self.client,'Cloud transcode')
            self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('Cloud transcode')
            if self.CloudtranscodeId==None:
                self.CloudtranscodeId = Transobj.addTranscodingProfile(1,'32,33,34,35')
                if isinstance(self.CloudtranscodeId,bool):
                    testStatus = False
                    return

            # Create player of latest version -  Create V2/3 Player
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

            # Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID,self.playerId)

            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-RTMPRestart_Transcoding_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            time.sleep(5)
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                Current_primaryBroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl
                if self.Live_Change_Cluster == True and self.env == 'testing':
                    Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                #primaryBroadcastingUrl_rtmp_1 = self.streamUrl[i].primaryBroadcastingUrl
                primaryBroadcastingUrl_rtmp_1 = Current_primaryBroadcastingUrl.replace("rtmp-0","rtmp-1")  # set rtmp-1 instead of rtmp-0
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd from Primary only.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , " + primaryBroadcastingUrl_rtmp_1)
                ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath,str(primaryBroadcastingUrl_rtmp_1),self.entryId)
                start_streaming = datetime.datetime.now().timestamp()
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=primaryBroadcastingUrl_rtmp_1,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript secondaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , " + str(primaryBroadcastingUrl_rtmp_1))
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
                stop_time = datetime.datetime.now().timestamp()  # Save stop time of stream
                # Running as thread function Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode
                self.logi.appendMsg("INFO - Main : Before creating thread - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                que = queue.Queue()
                #x = threading.Thread(target=self.KubernetesObj.Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode, args=(self.liveObj,self.entrieslst,True,5,self.PlayerVersion,))
                x = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4, arg5, arg6: q.put(self.KubernetesObj.Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode(arg1, arg2, arg3, arg4, arg5, arg6)),args=(que, self.liveObj, self.entrieslst, True, self.MinToPlayEntry, self.PlayerVersion, self.QrCodecheckProgress))
                self.logi.appendMsg("INFO - Main : Before running thread - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode -  " + str(datetime.datetime.now()))
                x.start()
                self.logi.appendMsg("INFO - Main : Wait for the thread to start playing the entry - entryId = " + str(self.entryId) + " , CurrentTime = " + str(datetime.datetime.now()))
                #x.join()
                time.sleep(30) #Wait for the thread to start playing the entry

                for currentRestart in range(0, self.NumOfRestartComponent):
                    self.logi.appendMsg("INFO - ####### Going to RESTART RTMP-" + str(currentRestart) + " :currentMonitor=" + str(self.Kubernetes_Component))
                    if self.Live_Change_Cluster == True and self.env == 'testing':
                        rc = self.KubernetesObj.Kubernetes_ConfigUseContext(host=self.Kubernetes_remote_host,user=self.Kubernetes_remote_user,passwd=self.Kubernetes_remote_pass,entryId=self.entryId,partnerId=self.PublisherID,env=self.env,BroadcastingUrl=primaryBroadcastingUrl_rtmp_1,KubernetesCmdLine_clusterType=self.KubernetesCmdLine_clusterType,CONTEXT_NAME=self.CONTEXT_NAME)
                        if rc == True:
                            self.logi.appendMsg("PASS - Kubernetes_ConfigUseContext - CONTEXT_NAME-" + str(self.CONTEXT_NAME) + " is done.Kubernetes_Component = " + str(self.Kubernetes_Component))
                        else:
                            self.logi.appendMsg("FAIL - Kubernetes_ConfigUseContext-  CONTEXT_NAME-" + str(self.CONTEXT_NAME) + " is failed. Kubernetes_Component = " + str(self.Kubernetes_Component))
                            testStatus = False
                            return
                    rc = self.KubernetesObj.Kubernetes_RestartComponent(host=self.Kubernetes_remote_host,user=self.Kubernetes_remote_user,passwd=self.Kubernetes_remote_pass,entryId=self.entryId,partnerId=self.PublisherID,env=self.env,BroadcastingUrl=primaryBroadcastingUrl_rtmp_1,currentComponent=self.Kubernetes_Component,KubernetesCmdLine_clusterType=self.KubernetesCmdLine_clusterType,SearchResult=self.Kubernetes_SearchResult)
                    if rc == True:
                        self.logi.appendMsg("PASS - Start_KubernetesByCmd - RESTART RTMP-" + str(currentRestart) + " is done.Kubernetes_Component = " + str(self.Kubernetes_Component))
                    else:
                        self.logi.appendMsg("FAIL - Start_KubernetesByCmd-  RESTART RTMP-" + str(currentRestart) + " is failed. Kubernetes_Component = " + str(self.Kubernetes_Component))
                        testStatus = False
                        return

                self.logi.appendMsg("INFO  - Main: Wait for the thread to finish - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                x.join()
                rc = que.get()
                if rc == False:#rc==False is PASS result because the playback should be stopped during rtmp restart
                    self.logi.appendMsg("PASS  - Main: thread return result Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                else:
                    self.logi.appendMsg("FAIL -  Main: thread Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                    testStatus = False
                    #return
                time.sleep(5)

                # kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass,self.entryId, self.PublisherID,FoundByProcessId=ffmpegOutputString)
                if rc != False:
                    self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                else:
                    self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return

                time.sleep(15)
                # Get entryId and primaryBroadcastingUrl from live entries
                for i in range(0, self.NumOfEntries):
                    self.entryId = str(self.entrieslst[i].id)
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primaryBroadcastingUrl
                    if self.Live_Change_Cluster == True and self.env == 'testing':
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                    primaryBroadcastingUrl_rtmp_1 = Current_primaryBroadcastingUrl.replace("rtmp-0","rtmp-1")  # set rtmp-1 instead of rtmp-0
                    self.logi.appendMsg("INFO - ************** Going to RESTART ssh Start_StreamEntryByffmpegCmd after restart all transcoders.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , " + primaryBroadcastingUrl_rtmp_1)
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath,str(primaryBroadcastingUrl_rtmp_1),self.entryId)
                    start_streaming = datetime.datetime.now().timestamp()
                    rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host,self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=primaryBroadcastingUrl_rtmp_1,FoundByProcessId=True)
                    if rc == False:
                        self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript secondaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , " + str(primaryBroadcastingUrl_rtmp_1))
                        testStatus = False
                        return
                time.sleep(10)
                self.MinToPlayEntry = 1
                rc=self.KubernetesObj.Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode(self.liveObj, self.entrieslst, True, self.MinToPlayEntry, self.PlayerVersion, self.QrCodecheckProgress)
                if rc == True:
                    self.logi.appendMsg("PASS  - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode- Playback is OK for New transcording entry after restart all transcoders.entryId " + str(self.entryId ))
                else:
                    self.logi.appendMsg("FAIL  - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode- Playback is FAILED for New transcording entry after restart all transcoders.entryId " + str(self.entryId ))
                    testStatus = False
                    # return

                time.sleep(10)
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=True,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False
                # kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass,self.entryId, self.PublisherID,FoundByProcessId=ffmpegOutputString)
                if rc != False:
                    self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                else:
                    self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
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
        '''try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass'''
        print('Tear down - testTeardownclass')

        try:
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '911','1')
           self.logi.reportTest('fail',self.sendto)
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '911','0')
           self.logi.reportTest('pass',self.sendto)
           assert True


    #===========================================================================
    #pytest.main('test_0_911_RestartRTMP_CreateTrans_kubernetesThreads.py -s')
    #===========================================================================
        
        
        