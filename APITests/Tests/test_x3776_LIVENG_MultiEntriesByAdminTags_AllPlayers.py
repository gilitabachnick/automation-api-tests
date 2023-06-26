'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_x3776_LIVENG_MultiEntriesByAdminTags_AllPlayers.py
 @desc : this test create multi entries(+Updating adminTags) with LiveNG  Passthrough + streaming by new logic function.  
 Verify playback on AllPlayers=True meaning player v2 and v3
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

from KalturaClient.Plugins.Core import *

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
import Transcoding

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
isProd =  os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
isProd = False
class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            # Streaming details
            self.url= "www.kaltura.com"
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            print('PRODUCTION ENVIRONMENT')
            
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            self.PublisherID = "6651"
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            print('TESTING ENVIRONMENT') 
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS-2 LINUX
        self.remote_host = "3.220.44.72"
        self.remote_user = "root"
        self.remote_pass = "Vc9Qvx%J5PJNxG%$Wo@ad9xZAHJEg?P9"
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"      

        self.NumOfEntries = 2
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 2 # player version 2 or 3
        self.AllPlayers = False # If True running the two version in a loop/ If False running just self.PlayerVersion
        #self.adminTags = "kalturaclassroom"#Options None/kalturaclassroom
        self.adminTags = None
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('1327')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()         
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")                   
        self.logi = reporter2.Reporter2('test_3776_LIVENG_MultiEntriesByAdminTags_AllPlayers')
        self.logi.initMsg('test_3776_LIVENG_MultiEntriesByAdminTags_AllPlayers')     
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
        self.Wd = None
        self.LiveDashboard = None
        self.QrCode = None

    def test_3776_LIVENG_MultiEntriesByAdminTags_AllPlayers(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('start create session for partenr: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
                      
            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            Transobj = Transcoding.Transcoding(self.client,'Passthrough')
            self.passtrhroughId = Transobj.getTranscodingProfileIDByName('Passthrough')
            if self.passtrhroughId==None:
                self.passtrhroughId = Transobj.addTranscodingProfile(1,'32,36,37')
                if isinstance(self.passtrhroughId,bool):
                    testStatus = False
                    return
            if self.AllPlayers == False:        
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
                self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
                 
            else: #Play all player version - v2 and v3
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
                self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
                         
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
                self.liveObj_v3 = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId_v3)    
                                           
            
                       
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                if self.adminTags != None:
                    Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_LINUX_LiveEntry_' + str(i) + '_' + str(self.adminTags) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                else:    
                    Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_LINUX_LiveEntry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
                self.logi.appendMsg('INFO - Create ENTRY#' + str(i) + ' , EntryId ='  + str(self.entry.id))
                # Set kalturaclassroom admintag
                if self.adminTags != None:
                    base_entry = KalturaBaseEntry()
                    base_entry.adminTags = self.adminTags
                    result = self.client.baseEntry.update(self.entry.id, base_entry)
                    self.logi.appendMsg('INFO - Perform API baseEntry.Update adminTags ' + str(self.adminTags) + ' to ENTRY#' + str(i) + ' , EntryId ='  + str(self.entry.id))
                

           
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id) 
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)    
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
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
                
            if self.AllPlayers == False:
                #Playback verification of all entries
                self.logi.appendMsg("INFO - Going to play live entries on PlayerVersion=" + str(self.PlayerVersion) + " on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll==False:   
                        rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion)
                        time.sleep(5)
                        if not rc:
                            testStatus = False
                            return
                        if self.seenAll_justOnce_flag ==True:
                            seenAll = True
            else:#AllPlayers=True check versio 2 and 3
                for CurrentplayerVersion in range(2,4):
                    #Playback verification of all entries with all player version = 2 and 3
                    self.logi.appendMsg("INFO - ************** AllPlayers=True:Going to play live entries on PlayerVersion= "+ str(CurrentplayerVersion) +"  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                    limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                    seenAll = False
                    while datetime.datetime.now() <= limitTimeout and seenAll==False:   
                            if CurrentplayerVersion == 3:
                                rc = self.liveObj_v3.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion)
                            else:
                                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion)
                            time.sleep(5)
                            if not rc:
                                testStatus = False
                                return
                            if self.seenAll_justOnce_flag ==True:
                                seenAll = True

                    self.logi.appendMsg("PASS - AllPlayers=True:Playback of PlayerVersion= " + str(CurrentplayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))  
                      
            #kill ffmpeg ps   
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID)
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
        #print ' Tear down - Wd.quit'
        #=======================================================================
        # try:
        #     self.Wd.quit()
        # except:
        #     pass
        #=======================================================================

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
           self.practitest.post(Practi_TestSet_ID, '3776','1') 
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '3776','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x3776_LIVENG_MultiEntriesByAdminTags_AllPlayers.py -s')
    #===========================================================================
        
        
        