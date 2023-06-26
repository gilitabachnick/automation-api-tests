import math
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import json
import pickle

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class playerV2:
    '''--------- CONSTANTS -----------'''
    LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND = 'qaCoreBackEnd'
    GRID_HOST = "http://il-SeleniumHub-qa.dev.kaltura.com:4444/wd/hub"  # hub address
    BROWSER_IE = "internet explorer"
    BROWSER_CHROME = "chrome"
    BROWSER_FIREFOX = "firefox"
    BROWSER_SAFARI = "Safari"

    # Selenium objects mapping
    # SLIDER_ELEMENT                      = "//div[contains(@class,'comp scrubber display-medium ui-slider ui-slider-horizontal ui-widget ui-widget-content ui-corner-all')]"
    SLIDER_ELEMENT = "//div[contains(@class,'ui-slider')]"
    SLIDER_ELEMENTV7 = "//div[@class='playkit-seek-bar playkit-live']"
    # CONTROL_BAR_CURRENT_TIME_ELEMENT    = "//div[contains(@class,'currentTimeLabel')]"
    SLIDER_ROLE1 = "//div[contains(@role,'slider')]"  # add moran
    SLIDER_ROLE = "//div[contains(@role,'slider')]"
    V7PLAYERPROGRESS = "//div[@class='playkit-progress']"
    CONTROL_BAR_DURATION_TIME_ELEMENT = "//div[contains(@class,'durationLabel')]"
    CONTROL_BAR_BACK_TO_LIVE = "//div[@class='btn timers comp liveStatus display-high live-off-sync-icon icon-off-air live-icon']"
    CONTROL_BAR_BACK_TO_LIVEV7 = "//div[@class='playkit-live-tag playkit-non-live-playhead']"
    PLAYHEAD_BUTTON = "//a[contains(@class,'ui-slider-handle ui-state-default ui-corner-all playHead PIE')]"
    CONTROL_BAR_DURATION_TIME_ELEMENT = "//div[contains(@class,'durationLabel')]"

    # Multi audio player v7
    PLAYER_INTERACTIVE_AREA_V7 = "//div[@class='playkit-interactive-area']"
    PLAYER_MULTIAUDIO_ICON_LANGUAGE_V7 = "//div[contains(@class,'playkit-control-button-container playkit-control-settings')]"
    PLAYER_CAPTION_MAIN_BUTTON="//i[contains(@class,'playkit-icon playkit-icon-closed-captions')]"
    PLAYER_MULTIAUDIO_DROPDOWN_LANGUAGE_V7 = "//div[contains(@class,'playkit-dropdown') and contains(@name, 'TEXTTOREPLACE')]"
    PLAYER_MULTIAUDIO_SELECT_LANGUAGE_V7 = "//div[contains(@name,'TMP_DropDownType')]//span[contains(text(),'TEXTTOREPLACE')]"
    #Source selector
    PLAYER_ICON_FLAVOUR_SELECTOR_V7 = "//i[contains(@class,'playkit-icon playkit-icon-settings')]"
    PLAYER_FLAVOUR_SELECTOR_DROPDOWN_V7 = "//i[contains(@class,'playkit-icon-arrow-down')]"
    PLAYER_FLAVOUR_SELECTOR_SELECT_V7 = "//span[contains(text(),'TEXTTOREPLACE')]"

    playerHostName = "http://externaltests.dev.kaltura.com/"
    playerDivID = ""

    def __init__(self, divID):
        self.playerDivID = divID

    def clickPlay(self, driver):
        driver.find_element_by_xpath('//*[@title="Play clip"]').click()

    def clickPause(self, driver):
        driver.find_element_by_xpath('//*[@title="Pause clip"]').click()

    def clickSeek(self, driver):
        driver.find_element_by_css_selector(".watched").click()

    def clickRePlay(self, driver):
        driver.find_element_by_xpath('//*[@title="Replay"]').click()

    def existRePlay(self, driver):
        try:
            driver.find_element_by_xpath('//*[@title="Replay"]')
        except NoSuchElementException:
            return False
        return True

    def switchToPlayerIframe(self, driver):
        driver.switch_to.frame(driver.find_element_by_css_selector('#' + self.playerDivID + '_ifp'))

    def switchToPlayerHostPage(self, driver):
        driver.switch_to.default_content()

    def vastAdsClickSkip(self, driver):
        driver.find_element_by_id("kaltura_player_1421673043_ad_skipBtn").click()

    def setWebDriverLocalRemote(self, selDriver, loaclDriver=False, boolproxy=False):
        ''' LOCAL WEB DRIVER '''
        if loaclDriver == True:

            driverdict = {0: 'webdriver.Firefox()',
                          1: 'webdriver.Ie(r\'C:\Python27\webdrivers\IEDriverServer.exe\')'}

            if selDriver == 2:
                options = webdriver.ChromeOptions()
                options.add_experimental_option('excludeSwitches', ['disable-component-update'])
                options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
                self.driver = webdriver.Chrome(r'C:\Python27\webdrivers\chromedriver.exe', chrome_options=options)
            else:
                self.driver = eval(driverdict[selDriver])

            try:
                self.driver.get(self.baseUrl)
            except:
                print('url set to browser')

            ''' REMOTE WEB DRIVER'''
        else:
            if selDriver == 0:
                browzer = 'firefox'
            elif selDriver == 1:
                browzer = 'ie'
            else:
                browzer = 'chrom'

            self.driver = webdriver.Remote(command_executor=self.GRID_HOST,
                                           desired_capabilities={'browserName': browzer, 'requireWindowFocus': True,
                                                                 "applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})

        return self.driver

    def testWebDriverLocalOrRemote(self, hostBrowser, loaclDriver=False, myProxy=None, sniffer=None):
        if (loaclDriver):
            ''' FIREFOX'''
            if (hostBrowser == self.BROWSER_FIREFOX):
                if (myProxy != None):
                    PROXY_HOST = myProxy.proxy[:myProxy.proxy.index(":")]
                    PROXY_PORT = myProxy.proxy[myProxy.proxy.index(":") + 1:]
                    fp = webdriver.FirefoxProfile()
                    fp.set_preference("network.proxy.type", 1)
                    fp.set_preference("network.proxy.http", PROXY_HOST)
                    fp.set_preference("network.proxy.http_port", int(PROXY_PORT))
                    fp.set_preference("network.proxy.https", PROXY_HOST)
                    fp.set_preference("network.proxy.https_port", int(PROXY_PORT))
                    fp.set_preference("network.proxy.ssl", PROXY_HOST)
                    fp.set_preference("network.proxy.ssl_port", int(PROXY_PORT))
                    fp.set_preference("network.proxy.ftp", PROXY_HOST)
                    fp.set_preference("network.proxy.ftp_port", int(PROXY_PORT))
                    fp.set_preference("network.proxy.socks", PROXY_HOST)
                    fp.set_preference("network.proxy.socks_port", int(PROXY_PORT))
                    fp.set_preference("general.useragent.override",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A")
                    fp.update_preferences()
                    return webdriver.Firefox(firefox_profile=fp)
                else:
                    return webdriver.Firefox()

                ''' CHROME'''
            elif (hostBrowser == self.BROWSER_CHROME):
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_experimental_option('excludeSwitches', ['disable-component-update'])
                chrome_options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
                if (myProxy != None):
                    chrome_options.add_argument('--proxy-server=http://' + myProxy.proxy)

                # headers_extension = "C:\Program Files\Python39\webdrivers\capture.crx"
                # chrome_options.add_extension(headers_extension)
                ##################Add for sniffer
                if sniffer != None:
                    caps = DesiredCapabilities.CHROME
                    caps['loggingPrefs'] = {'performance': 'ALL'}
                    chrome_options.add_experimental_option('w3c', False)
                ################

                return webdriver.Chrome(r'C:\Program Files\Python39\webdrivers\chromedriver.exe',
                                        chrome_options=chrome_options, desired_capabilities=caps)

                ''' IE '''
            elif (hostBrowser == self.BROWSER_IE):
                return webdriver.Ie(r'C:\Program Files\Python39\webdrivers\IEDriverServer.exe',
                                    capabilities={'ignoreZoomSetting': True, "nativeEvents": False,
                                                  "unexpectedAlertBehaviour": "accept",
                                                  "ignoreProtectedModeSettings": True, "disable-popup-blocking": True,
                                                  "enablePersistentHover": True})
        else:  # remote, capture traffic using proxy
            if (myProxy != None):
                if (hostBrowser == self.BROWSER_IE):
                    return webdriver.Remote(command_executor=self.GRID_HOST, proxy=myProxy,
                                            desired_capabilities={'unexpectedAlertBehaviour': 'accept',
                                                                  'browserName': hostBrowser,
                                                                  'requireWindowFocus': True, 'ignoreZoomSetting': True,
                                                                  "nativeEvents": False,
                                                                  "unexpectedAlertBehaviour": "accept",
                                                                  "ignoreProtectedModeSettings": True,
                                                                  "disable-popup-blocking": True,
                                                                  "enablePersistentHover": True,
                                                                  "applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                else:
                    return webdriver.Remote(command_executor=self.GRID_HOST, proxy=myProxy,
                                            desired_capabilities={'browserName': hostBrowser,
                                                                  'requireWindowFocus': True,
                                                                  "applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
            else:
                if (hostBrowser == self.BROWSER_IE):
                    return webdriver.Remote(command_executor=self.GRID_HOST,
                                            desired_capabilities={'unexpectedAlertBehaviour': 'accept',
                                                                  'browserName': hostBrowser,
                                                                  'requireWindowFocus': True, 'ignoreZoomSetting': True,
                                                                  "nativeEvents": False,
                                                                  "unexpectedAlertBehaviour": "accept",
                                                                  "ignoreProtectedModeSettings": True,
                                                                  "disable-popup-blocking": True,
                                                                  "enablePersistentHover": True,
                                                                  "applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                elif (hostBrowser == self.BROWSER_FIREFOX):
                    return webdriver.Remote(command_executor=self.GRID_HOST,
                                            desired_capabilities={'proxy': '{"proxyType":"DIRECT"}',
                                                                  'browserName': hostBrowser,
                                                                  'requireWindowFocus': True,
                                                                  "applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                else:
                    return webdriver.Remote(command_executor=self.GRID_HOST,
                                            desired_capabilities={'setNoProxy': '', 'browserName': hostBrowser,
                                                                  'requireWindowFocus': True,
                                                                  "applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})

    # ==============================================================================================================
    # Click on the slider bar on a given position.
    # Set the percentage of the slider, where you want to click on the slider.
    # percentage - Set where you want to release on the seekbar, percentage represent the width of the seekbar.
    #             e.g. '50' is 50% of the width of the seekbar (proximately in the middle)
    # ==============================================================================================================
    def clickOnSlider(self, driver, percentage, isV7=False):
        # Get the Slider size (with)
        if isV7:
            action = ActionChains(driver)
            element = driver.find_element_by_xpath(
                "//div[@class='playkit-interactive-area']")  # or your another selector here
            action.move_to_element(element)
            action.perform()
            sliderElement = driver.find_element_by_xpath(self.SLIDER_ELEMENTV7)
        else:
            #add
            action = ActionChains(driver)
            element = driver.find_element_by_xpath("//div[contains(@class,'ui-slider')]")  # or your another selector here
            action.move_to_element(element)
            action.perform()
            action.click()
            #action.perform() #added
            sliderElement = driver.find_element_by_xpath(self.SLIDER_ELEMENT)
        if sliderElement == None:
            return False
        ############
        #if percentage !=0 or isV7==False:
        sliderWidth = int(sliderElement.size["width"])#General option(old)
        halfSliderWitdh = sliderWidth / 2
        valueToSet = (sliderWidth - math.ceil(((percentage * sliderWidth) / 100) + halfSliderWitdh)) * (-1)
        if isV7==False:#if player v2
            valueToSet=valueToSet+5
        else:#player v3
            valueToSet = valueToSet + 10
        '''else:#percentage =0 and isV7==True
            sliderWidth = int(driver.find_element_by_xpath(self.SLIDER_ELEMENTV7).get_attribute("aria-valuemax"))
            #sliderWidth = math.floor(float(driver.find_element_by_xpath(self.SLIDER_ELEMENT).get_attribute("aria-valuemax")))
            valueToSet = (sliderWidth - math.ceil(((percentage * sliderWidth) / 100))) * (-1)'''
        ############
        playheadElement = self.getPlayerPlayheadEelement(driver)
        if playheadElement == None:
            return False
        time.sleep(2)
        # Click on the slidebar
        ActionChains(driver).move_to_element(sliderElement).move_by_offset(valueToSet, 0).click().perform()
        time.sleep(1)
        ActionChains(driver).move_to_element(sliderElement).move_by_offset(valueToSet, 0).click().perform()

        return True

    # ==============================================================================================================
    # Moran.Cohen
    # Get the timer current time of playing in the player.
    # Return: currentTime[0]=DVR point time ,currentTime[1]=Total live time
    # ==============================================================================================================
    def getCurrentTimeLabel(self, driver):
        try:
            # currentTime = driver.find_element_by_xpath(self.CONTROL_BAR_CURRENT_TIME_ELEMENT)
            currentTime = str(driver.find_element_by_xpath(self.SLIDER_ROLE).get_attribute("aria-valuetext")).split(
                ', Use the left and right arrow keys to adjust video progress')[0].split('of')
        except NoSuchElementException:
            print('No Time element found')
            return False
        return currentTime

    def clickLiveIconBackToLive(self, driver, isV7=False):
        try:
            if isV7:
                action = ActionChains(driver)
                element = driver.find_element_by_xpath("//div[@class='playkit-interactive-area']")
                action.move_to_element(element)
                action.perform()
                #driver.find_element_by_xpath("//div[@class='playkit-bottom-bar']").click()
                driver.find_element_by_xpath(self.CONTROL_BAR_BACK_TO_LIVEV7).click()
            else:
                # add
                action = ActionChains(driver)
                element = driver.find_element_by_xpath("//div[contains(@class,'ui-slider')]")  # or your another selector here
                action.move_to_element(element)
                action.perform()
                driver.find_element_by_xpath("//div[@class='controlsContainer']").click()
                driver.find_element_by_xpath(self.CONTROL_BAR_BACK_TO_LIVE).click()
            return True
        except NoSuchElementException:
            print('could not find Back to live element')
            return False

    def getPlayerPlayheadEelement(self, driver):
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
        # =======================================================================
        # if durationStr == expectedDuration:
        #     return True
        # else:
        #     return False
        # =======================================================================

    # ==============================================================================================================
    # Moran.Cohen
    # Get the timer current time of playing in the player.
    # Return: currentTime[0]=DVR point time ,currentTime[1]=Total live time
    # ==============================================================================================================
    def getCurrentDVRTimeFromLive(self, driver):
        try:
            # currentTime = driver.find_element_by_xpath(self.CONTROL_BAR_CURRENT_TIME_ELEMENT)
            currentTime = str(driver.find_element_by_xpath(self.SLIDER_ROLE1).get_attribute("aria-valuetext")).split(', Use the left and right arrow keys to adjust video progress')[0].split('of')
        except NoSuchElementException:
            print('No Time element found')
            return False
        return currentTime


    def approveBcakToLive(self, driver):
        try:
            scrollerWidth = str(driver.find_element_by_xpath(self.V7PLAYERPROGRESS).get_attribute("style"))
            if scrollerWidth.find("100%") >=0:
                return True
            else:
                return False
        except NoSuchElementException:
            print('No Time element found')
            return False