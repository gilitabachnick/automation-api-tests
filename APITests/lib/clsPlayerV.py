'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

 @desc : Basic function of players v2 and v3
 for player v2 send divID = kaltura_player_1418811966
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''



import math
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver





class playerV:
   
    '''--------- CONSTANTS -----------'''
    LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND  = 'qaCoreBackEnd'
    GRID_HOST = "http://il-SeleniumHub-qa.dev.kaltura.com:4444/wd/hub" #hub address 
    BROWSER_IE                   = "internet explorer"
    BROWSER_CHROME               = "chrome"
    BROWSER_FIREFOX              = "firefox"
    BROWSER_SAFARI               = "Safari"
    
   
    
    
    playerHostName = "http://externaltests.dev.kaltura.com/" 
    playerDivID    = ""

    def __init__(self,divID,version=2):
        self.playerDivID = divID
        self.returnLocators(version)
        
        
    def  returnLocators(self,selfPVersion=2):
        if selfPVersion == 2:
            # Selenium objects mapping
            self.SLIDER_ELEMENT1 = "//div[contains(@class,'playkit-buffered')]"

            #self.SLIDER_ELEMENT1                      = "//div[contains(@class,'ui-slider')]"
            #CONTROL_BAR_CURRENT_TIME_ELEMENT    = "//div[contains(@class,'currentTimeLabel')]"
            self.SLIDER_ROLE1                         = "//div[contains(@role,'slider')]"
            self.CONTROL_BAR_DURATION_TIME_ELEMENT   = "//div[contains(@class,'durationLabel')]"
            self.CONTROL_BAR_BACK_TO_LIVE            = "//div[@class='btn timers comp liveStatus display-high live-off-sync-icon icon-off-air live-icon']"
            self.PLAYHEAD_BUTTON                     = "//a[contains(@class,'ui-slider-handle ui-state-default ui-corner-all playHead PIE')]"
            self.CONTROL_BAR_DURATION_TIME_ELEMENT   = "//div[contains(@class,'durationLabel')]"
        elif selfPVersion==3:
            # Selenium objects mapping 
            self.SLIDER_ELEMENT1                    = "//div[contains(@class,'playkit-buffered')]"
            #CONTROL_BAR_CURRENT_TIME_ELEMENT    = "//div[contains(@class,'currentTimeLabel')]"
            self.SLIDER_ROLE                         = "//div[contains(@role,'slider')]"
            self.CONTROL_BAR_DURATION_TIME_ELEMENT   = "//div[contains(@class,'durationLabel')]"
            self.CONTROL_BAR_BACK_TO_LIVE            = "//div[@class='btn timers comp liveStatus display-high live-off-sync-icon icon-off-air live-icon']"
            self.PLAYHEAD_BUTTON                     = "//a[contains(@class,'ui-slider-handle ui-state-default ui-corner-all playHead PIE')]"
            self.CONTROL_BAR_DURATION_TIME_ELEMENT   = "//div[contains(@class,'durationLabel')]"
                

    def clickPlay(self,driver):
        driver.find_element_by_xpath('//*[@title="Play clip"]').click()

    def clickPause(self,driver):
        driver.find_element_by_xpath('//*[@title="Pause clip"]').click()

    def clickSeek(self,driver):
        driver.find_element_by_css_selector(".watched").click()

    def clickRePlay(self,driver):
        driver.find_element_by_xpath('//*[@title="Replay"]').click()	

    def existRePlay(self,driver):
        try:
            driver.find_element_by_xpath('//*[@title="Replay"]')
        except NoSuchElementException:
                return False
        return True

    def switchToPlayerIframe(self,driver):#only v2
            driver.switch_to.frame(driver.find_element_by_css_selector('#' + self.playerDivID + '_ifp'))

    def switchToPlayerHostPage(self,driver):
            driver.switch_to.default_content()
            
    def vastAdsClickSkip(self,driver):
            driver.find_element_by_id("kaltura_player_1421673043_ad_skipBtn").click()
            
    def setWebDriverLocalRemote(self, selDriver, loaclDriver=False, boolproxy=False):
        ''' LOCAL WEB DRIVER '''
        if loaclDriver == True:
            
            driverdict = {0:'webdriver.Firefox()',
                          1:'webdriver.Ie(r\'C:\Python27\webdrivers\IEDriverServer.exe\')'}
         
            if selDriver==2:
                options = webdriver.ChromeOptions()
                options.add_experimental_option('excludeSwitches', ['disable-component-update'])
                options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
                self.driver = webdriver.Chrome(r'C:\Python27\webdrivers\chromedriver.exe',chrome_options=options)
            else:
                self.driver = eval(driverdict[selDriver])
             
            try:
                self.driver.get(self.baseUrl)
            except:
                print('url set to browser')
                
            ''' REMOTE WEB DRIVER'''
        else:
            if selDriver == 0:
                browzer= 'firefox'
            elif selDriver == 1:
                browzer= 'ie'
            else:
                browzer= 'chrom'
                
                    
            self.driver = webdriver.Remote(command_executor=self.GRID_HOST, desired_capabilities={'browserName': browzer,'requireWindowFocus':True,"applicationName":self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
            
        return self.driver
    
    def testWebDriverLocalOrRemote (self,hostBrowser, loaclDriver=False, myProxy=None):
        if(loaclDriver):
            ''' FIREFOX'''
            if(hostBrowser == self.BROWSER_FIREFOX):
                if (myProxy != None): 
                    PROXY_HOST = myProxy.proxy[:myProxy.proxy.index(":")]
                    PROXY_PORT = myProxy.proxy[myProxy.proxy.index(":")+1:]                  
                    fp = webdriver.FirefoxProfile()
                    fp.set_preference("network.proxy.type", 1)
                    fp.set_preference("network.proxy.http",PROXY_HOST)
                    fp.set_preference("network.proxy.http_port",int(PROXY_PORT))
                    fp.set_preference("network.proxy.https",PROXY_HOST)
                    fp.set_preference("network.proxy.https_port",int(PROXY_PORT))
                    fp.set_preference("network.proxy.ssl",PROXY_HOST)
                    fp.set_preference("network.proxy.ssl_port",int(PROXY_PORT))  
                    fp.set_preference("network.proxy.ftp",PROXY_HOST)
                    fp.set_preference("network.proxy.ftp_port",int(PROXY_PORT))   
                    fp.set_preference("network.proxy.socks",PROXY_HOST)
                    fp.set_preference("network.proxy.socks_port",int(PROXY_PORT))   
                    fp.set_preference("general.useragent.override","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A")
                    fp.update_preferences()
                    return webdriver.Firefox(firefox_profile=fp)
                else:
                    return webdriver.Firefox()
                    
                ''' CHROME'''
            elif(hostBrowser == self.BROWSER_CHROME):
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_experimental_option('excludeSwitches', ['disable-component-update'])
                chrome_options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
                if (myProxy != None): 
                    chrome_options.add_argument('--proxy-server=http://' + myProxy.proxy)
                
                return webdriver.Chrome(r'C:\Python27\webdrivers\chromedriver.exe',chrome_options=chrome_options)
                
                ''' IE '''
            elif(hostBrowser == self.BROWSER_IE):
                return webdriver.Ie(r'C:\Python27\webdrivers\IEDriverServer.exe',capabilities={'ignoreZoomSetting':True,"nativeEvents": False,"unexpectedAlertBehaviour": "accept","ignoreProtectedModeSettings": True,"disable-popup-blocking": True,"enablePersistentHover": True})
        else: #remote, capture traffic using proxy
            if (myProxy != None):
                if (hostBrowser == self.BROWSER_IE):
                    return webdriver.Remote(command_executor=self.GRID_HOST,proxy=myProxy, desired_capabilities={'unexpectedAlertBehaviour':'accept', 'browserName': hostBrowser,'requireWindowFocus':True,'ignoreZoomSetting':True,"nativeEvents": False,"unexpectedAlertBehaviour": "accept","ignoreProtectedModeSettings": True,"disable-popup-blocking": True,"enablePersistentHover": True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                else:
                    return webdriver.Remote(command_executor=self.GRID_HOST,proxy=myProxy, desired_capabilities={'browserName': hostBrowser,'requireWindowFocus':True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
            else:
                if (hostBrowser == self.BROWSER_IE):
                    return webdriver.Remote(command_executor=self.GRID_HOST,desired_capabilities={'unexpectedAlertBehaviour':'accept','browserName': hostBrowser,'requireWindowFocus':True,'ignoreZoomSetting':True,"nativeEvents": False,"unexpectedAlertBehaviour": "accept","ignoreProtectedModeSettings": True,"disable-popup-blocking": True,"enablePersistentHover": True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                elif(hostBrowser == self.BROWSER_FIREFOX):
                    return webdriver.Remote(command_executor=self.GRID_HOST, desired_capabilities={'proxy': '{"proxyType":"DIRECT"}', 'browserName': hostBrowser,'requireWindowFocus':True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                else:
                    return webdriver.Remote(command_executor=self.GRID_HOST, desired_capabilities={'setNoProxy': '' , 'browserName': hostBrowser,'requireWindowFocus':True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
    

    #==============================================================================================================
    # Click on the slider bar on a given position.
    # Set the percentage of the slider, where you want to click on the slider.
    # percentage - Set where you want to release on the seekbar, percentage represent the width of the seekbar.
    #             e.g. '50' is 50% of the width of the seekbar (proximately in the middle)
    #==============================================================================================================
    def clickOnSlider(self, driver, percentage):
        #Get the Slider size (with)
        sliderElement = driver.find_element_by_xpath(self.SLIDER_ELEMENT1)
        if sliderElement == None:
            return False
        sliderWidth = int(sliderElement.size["width"])
        halfSliderWitdh = sliderWidth / 2
        valueToSet = (sliderWidth - math.ceil(((percentage * sliderWidth) / 100) + halfSliderWitdh)) * (-1)
        
        playheadElement = self.getPlayerPlayheadEelement(driver)
        if playheadElement == None:
            return False      
       
        #Click on the slidebar
        ActionChains(driver).move_to_element(sliderElement).move_by_offset(valueToSet, 0).click().perform()
        playheadElement = self.getPlayerPlayheadEelement(driver)
         
        return True
    #==============================================================================================================
    # Moran.Cohen
    # Get the timer current time of playing in the player.
    # Return: currentTime[0]=DVR point time ,currentTime[1]=Total live time
    #==============================================================================================================
    def getCurrentDVRTimeFromLive(self,driver):
        try:
            #currentTime = driver.find_element_by_xpath(self.CONTROL_BAR_CURRENT_TIME_ELEMENT)
            currentTime = str(driver.find_element_by_xpath(self.SLIDER_ROLE1).get_attribute("aria-valuetext")).split(', Use the left and right arrow keys to adjust video progress')[0].split('of')
        except NoSuchElementException:
            print('No Time element found')
            return False
        return currentTime   
     
    
    def clickLiveIconBackToLive(self,driver):
            try:
                driver.find_element_by_xpath(self.CONTROL_BAR_BACK_TO_LIVE).click()
                return True
            except NoSuchElementException:
                print('could not find Back to live element')
                return False 
    
    def getPlayerPlayheadEelement(self,driver):
            try:
                element = driver.find_element_by_xpath(self.PLAYHEAD_BUTTON)
            except NoSuchElementException:
                
                return False
            return element                 
    
    
    def getDuration(self, driver):  
        durationStr = driver.find_element_by_xpath(self.CONTROL_BAR_DURATION_TIME_ELEMENT).text
        if durationStr == None:
            return False
        durationStr = durationStr.replace("/ ", "")
        return durationStr
        #=======================================================================
        # if durationStr == expectedDuration:
        #     return True
        # else:
        #     return False
        #=======================================================================
    
        