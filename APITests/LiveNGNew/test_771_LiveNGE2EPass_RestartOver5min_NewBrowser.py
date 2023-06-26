
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_771_LiveNGE2EPass_RestartOver5min_NewBrowser.py
 Test #3772 | 07.Live - Stop-start streaming for over 5 minutes (No recording, No DVR)  -> Verify live entry playback by opening new browser and livedashboard state
 
 @desc : This test check E2E test of new LiveNG entries Passthrough by creating New Player v2 and start streaming and then
 restart streaming for X time(over 5 minutes)-> Verify live entry playback by refreshing/opening new browser 
 
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
#pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
#sys.path.insert(1,pth)

import pytest
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
import StaticMethods
### Jenkins params ###
#===============================================================================
# cnfgCls = Config.ConfigFile("stam")
# #self.Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# self.Practi_TestSet_ID,isProd = 11,"false"
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
        #***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"     

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.RestartDowntime = 300 #(seconds) -  Stop-start streaming for over 5 minutes (60x5=300min)
        self.PlayerVersion = 3 # Set player version 2 or 3
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_771_LiveNGE2EPass_RestartOver5min_NewBrowser')
        self.logi.initMsg('test_771_LiveNGE2EPass_RestartOver5min_NewBrowser')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)

    def test_771_LiveNGE2EPass_RestartOver5min_NewBrowser(self):
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_LINUX_LiveEntry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
                
            time.sleep(2)    

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
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
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
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
                

            time.sleep(10)
            if self.env == 'prod':
                time.sleep(10)
         
            #Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
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
                                        
            self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))  
                      
            # kill ffmpeg ps   
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId))
                testStatus = False
                return    
            
            ##################################
            time.sleep(5)
            if self.env == 'prod':
                time.sleep(10)
            # Playback verification of all entries
            self.logi.appendMsg("INFO - boolShouldPlay=False --> Going to verify NO playback on after stopping streaming " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:
                    #boolShouldPlay=False -> Meaning the entry should not play
                    time.sleep(5)
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entryList=self.entrieslst, boolShouldPlay=False,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True

            self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) of " +  str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            #######################################
            
            #After at least 5 minute has passed since stop streaming , restart the streaming
            self.logi.appendMsg("INFO - Stop streaming for " + str(self.RestartDowntime) + " seconds")
            time.sleep(self.RestartDowntime)
            #Restart steaming 
            self.logi.appendMsg("INFO - ************** Going to RESTART STREAMING after " + str(self.RestartDowntime) + "  - Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            if self.IsSRT == True:
                ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
            else:
                ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
            rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
            if rc == False:
                self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return
                
            #verify that entry playback after restart stream
            ####### Add verify entry state on livedashboard - playback
            time.sleep(5)
            # Playback verification of all entries
            self.logi.appendMsg("INFO - Going to verify playback After restart for " + str(self.RestartDowntime) + ", boolShouldPlay=True --> Going to PLAY " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:   
                    #boolShouldPlay=True -> Meaning the entry should play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True
                        
            self.logi.appendMsg("PASS - Playback(boolShouldPlay=True) of " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            
            # kill ffmpeg ps   
            self.logi.appendMsg("INFO - Going to END streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId))
                testStatus = False
                return
            
            
            #**** Login LiveDashboard 
            time.sleep(5)
            self.Wdobj = MySelenium.seleniumWebDrive()         
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            time.sleep(5)
            self.logi.appendMsg("INFO - Going to perform again invokeLiveDashboardLogin.")
            #rc = self.LiveDashboard.invokeLiveDashboardLogin(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL)
            rc = self.LiveDashboard.invokeLiveDashboardLoginByKS(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL,self.PublisherID, self.ServerURL, self.UserSecret,self.env)
            if(rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:       
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                testStatus = False
                return
            time.sleep(5)
            #****** Verify live dashbaord state after stopping streaming     
            navigateTo= "Channels"
            self.logi.appendMsg("INFO - Going to verify liveDashboard state after stopping streaming -> perform navigateToLiveDashboardTabs.navigateTo = " + navigateTo)
            rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo)
            if(rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
            else:       
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                testStatus = False
                return
            # Return row data from Channels - Expected PrimaryState=Stopped after 10-15 sec from stopped streaming
            if not self.isProd:  # currently not appear in prod, because it is disapear untill live dashboard is open
                self.logi.appendMsg("INFO - Going to verify the Channels of return RowData, Expected PrimaryState=Stopped after 10-15 sec from stopped streaming:")
                time.sleep(10) # David is investigating why 25 sec and not less
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo,True,env=self.env)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Channels of return RowData, Expected PrimaryState=Stopped after 10-15 sec:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,PrimaryState="Stopped",env=self.env,Live_Cluster_Primary=self.Live_Cluster_Primary)
                    if(rc):
                        self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on Channels tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        if self.env == 'testing':
                            testStatus = False
                else:
                    self.logi.appendMsg("**2***FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
            # Return row data from Channels - Expected remove live entry from Channels tab after ~2 minutes from stopped streaming
            self.logi.appendMsg("INFO - Going to verify the Channels of return RowData, Expected PrimaryState=removed ~2 minutes from stopped streaming:")
            time.sleep(120) #2 minutes waiting for live entry to be removed from live dashboard
            rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo,True,env=self.env)
            rowsNum=len(RowData)
            if(rc == False):         
                if rowsNum == 0:
                    self.logi.appendMsg("PASS - Removed Channel record after stopping streaming . entryId: " + self.entryId + ", ************ENTRY" + str(i))
                else:
                    self.logi.appendMsg("FAIL - Channels VerifyReturnRowDataLiveDashboard - Channel record is NOT removed from livedashboard after stopping streaming. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
            else:       
                self.logi.appendMsg("**3***FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
               
            # LiveDashboard - Alerts tab
            navigateTo= "Alerts"
            self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo= " + navigateTo)
            rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd,navigateTo)
            if(rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
            else:       
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo + ",  entryId: " + self.entryId + ", ************ENTRY" + str(i))
                testStatus = False
                return
             # Return row data from Alerts
            rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
            rowsNum=len(RowData)
            if(rc):
                self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,env=self.env)
                if(rc):
                    self.logi.appendMsg("PASS -VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                else:
                    self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False    
            else:       
                self.logi.appendMsg("FAIL -ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                testStatus = False
                return
            try:
                #Close LiveDashboard window
                self.logi.appendMsg("INFO - Going to close again the LiveDashboard.")
                self.Wd.quit()
                time.sleep(5)
            except Exception as Exp:
                print(Exp)
                pass
                       
        except Exception as e:
            print(e)
            testStatus = False
            pass
             
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    
    def teardown_method(self):
        
        global testStatus
        
        print('#############')
        print(' Tear down')
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        
        try:
            print('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '771','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '771','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
        
        
            
    #===========================================================================
    pytest.main (args=['test_771_LiveNGE2EPass_RestartOver5min_NewBrowser.py', '-s'])
    #===========================================================================
        
        
        