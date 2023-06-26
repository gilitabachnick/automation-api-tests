'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_1907_SIP_ZOOM_API.py
 
 @desc : this test check the SIP pexip.listRooms and ZOOM zoomVendor.recordingComplete

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import os
import re
import sys
import time

from KalturaClient import *
from KalturaClient.Plugins.Core import *

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter2
import Config
import Practitest
import tearDownclass
import MySelenium

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

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
            print('PRODUCTION ENVIRONMENT')
            self.ServerURL = inifile.RetIniVal(section, 'SIP_ServerURL')
            self.RoomSuffix = "@vc.kaltura.com"
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            print('TESTING ENVIRONMENT')
            self.ServerURL = inifile.RetIniVal(section, 'ServerURL')
            self.RoomSuffix = "@vc-stg.kaltura.com"
            
        # #KMC account
        self.PublisherID = inifile.RetIniVal(section, 'SIP_PublisherID')
        self.UserSecret =  inifile.RetIniVal(section, 'SIP_AdminSecret')            
        self.url    = inifile.RetIniVal(section, 'Url')
        self.sendto = inifile.RetIniVal(section, 'sendto')
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('4586')
        self.Wdobj = MySelenium.seleniumWebDrive()                            
        self.logi = reporter2.Reporter2('test_1907_SIP_ZOOM_API')
        self.logi.initMsg('test_1907_SIP_ZOOM_API')            
        
         # create client session
        self.logi.appendMsg('start create session for partner: ' + self.PublisherID)
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
        self.client = mySess.OpenSession()
        time.sleep(2)

    def test_1907_SIP_ZOOM_API(self):
        global testStatus
        try:
            YOUR_PARTNER_ID = self.PublisherID
            YOUR_KALTURA_SECRET = self.UserSecret
            YOUR_USER_ID="moran.cohen@kaltura.com" 
            
            config = KalturaConfiguration()
            config.serviceUrl = self.ServerURL
            client = KalturaClient(config)
            ks = client.session.start(
                  YOUR_KALTURA_SECRET,
                  YOUR_USER_ID,
                  KalturaSessionType.ADMIN,
                  YOUR_PARTNER_ID)
            client.setKs(ks)
            
            self.logi.appendMsg("INFO - Going to perform zoomVendor recording complete ")
            rc = self.client.vendor.zoomVendor.recordingComplete     
            if rc == False:
                self.logi.appendMsg("FAIL - zoomVendor.recordingComplete" )
                testStatus = False
                return
            else:
                if str(rc.__self__.__class__) == "<class 'KalturaClient.Plugins.Vendor.KalturaZoomVendorService'>":
                    self.logi.appendMsg("PASS - zoomVendor.recordingComplete. im_class is valid." )
                else:    
                    self.logi.appendMsg("FAIL - zoomVendor.recordingComplete. im_class is invalid." )
                    testStatus = False
                    return
            self.logi.appendMsg("INFO - Going to perform zoomVendor oauthValidation ")    
            rc = self.client.vendor.zoomVendor.oauthValidation
            if rc == False:
                self.logi.appendMsg("FAIL - zoomVendor.oauthValidation" )
                testStatus = False
                return  
            self.logi.appendMsg("INFO - Going to perform zoomVendor deAuthorization ")
            rc = self.client.vendor.zoomVendor.deAuthorization
            if rc == False:
                self.logi.appendMsg("FAIL - zoomVendor.deAuthorization" )
                testStatus = False
                return
            self.logi.appendMsg("INFO - Going to perform zoomVendor fetchRegistrationPage ")  
            tokens_data = ""
            iv = ""
            try:
                rc = self.client.vendor.zoomVendor.fetchRegistrationPage(tokens_data, iv)         
            except Exception as e:
                print(e)
                if str(e) == "no element found: line 1, column 0 (-2)":    
                    pass
                else:
                    testStatus = False
                    self.logi.appendMsg("FAIL - zoomVendor.fetchRegistrationPage" )
                    pass    
    
            offset = 0
            page_size = 500
            active_only = False
            self.logi.appendMsg("INFO - Going to sip list rooms")
            rc = self.client.sip.pexip.listRooms(offset, page_size, active_only)
            if rc == False:
                self.logi.appendMsg("FAIL - sip.pexip.listRooms" )
                testStatus = False
                return
            else:
                contentRoomData=rc[0].value # get all room list
                countRooms = len([m.start() for m in re.finditer(self.RoomSuffix, contentRoomData)])
                if countRooms <= 0:
                    self.logi.appendMsg("FAIL - sip.pexip.listRooms doesn't return rooms.countRooms = " + str(countRooms))
                    testStatus = False
                    return
                else:
                    if isProd == True:#If production it should be more then 400 rooms
                        if countRooms < 400:
                            self.logi.appendMsg("FAIL - sip.pexip.listRooms doesn't return enough rooms.countRooms = " + str(countRooms))
                            testStatus = False
                            return
                    self.logi.appendMsg("PASS -  sip.pexip.listRooms.countRooms = " + str(countRooms) )    
       
                    
        except Exception as e:
            print(e)
            testStatus = False
            pass
             
        
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
       
    def teardown_class(self):
        
        print('#############')
        print(' Tear down')
        print('#############')
        
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '1907','1') 
           self.logi.reportTest('fail',self.sendto)
           
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '1907','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    # pytest.main('test_1907_SIP_ZOOM_API.py -s')    
    #===========================================================================
        
        
        