################################################################
#
# this function library contain all the reusable functions  
#
# this file contains all the objects mapping of New Kmc
#
# date created: 7.5.17
#
# author: Adi Miller
#
################################################################
import datetime
import os
import platform
import sys
import requests
import wget
import zipfile
import time
from datetime import datetime

from selenium import webdriver

if platform.system() == 'Linux':
    print("LINUX")
    try:
        # import pyderman as driver
        # pathChromedriver = driver.install(browser=driver.chrome, file_directory='/usr/local/bin', verbose=True, chmod=True, overwrite=False, version=None, filename=None, return_info=False)
        # print('Installed chromedriver driver to path: %s' % pathChromedriver)
        pathChromedriver = '/usr/local/bin/chromedriver'
    except:
        pass
else:
    print('WINDOWS')
    pathChromedriver = r'C:\Program Files\Python39\webdrivers\chromedriver.exe'

print(pathChromedriver)


pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)


class seleniumWebDrive:
    
    '''--------- CONSTANTS -----------'''
    LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND   = 'qaCoreBackEnd'
    GRID_HOST                                   = "http://il-SeleniumHub-qa.dev.kaltura.com:4444/wd/hub" #hub address 
    BROWSER_IE                                  = "internet explorer"
    BROWSER_CHROME                              = "chrome"
    BROWSER_FIREFOX                             = "firefox"
    BROWSER_SAFARI                              = "Safari"
    RUN_REMOTE                                  = True
    
    def __init__(self):
        self.my = None

        # get chrome web driver updated date and ignore the installation if it is today date
        chromeWebDriverExe = r'C:\Program Files\Python39\webdrivers\chromedriver.exe'
        lastModified = datetime.strptime(time.ctime(os.path.getmtime(chromeWebDriverExe)), "%a %b %d %H:%M:%S %Y")
        lastModified = str(lastModified.day) + str(lastModified.month) + str(lastModified.year)
        todayDate = datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        todayDate = str(todayDate.day) + str(todayDate.month) + str(todayDate.year)

        '''INSTALL NEW CHROME WEB DRIVER VERSION'''
        if lastModified!=todayDate:
            # get the latest chrome driver version number
            url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
            response = requests.get(url)
            version_number = response.text

            # build the donwload url
            download_url = "https://chromedriver.storage.googleapis.com/" + version_number + "/chromedriver_win32.zip"

            # download the zip file using the url built above
            latest_driver_zip = wget.download(download_url, 'chromedriver.zip')

            # extract the zip file
            with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
                zip_ref.extractall(r'C:\Program Files\Python39\webdrivers')  # you can specify the destination folder path here
            # delete the zip file downloaded above
            os.remove(latest_driver_zip)

    def RetWebDriverLocalOrRemote(self, hostBrowser, localDriver=True, myProxy=None, fakeWebcam=False, SaveToC=False):
        if localDriver:
            self.RUN_REMOTE = False
            
        if(localDriver):
            try:
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
                        wd = webdriver.Firefox(firefox_profile=fp)

                    else:
                        wd= webdriver.Firefox()

                    wd.implicitly_wait(30)
                    return wd

                    ''' CHROME'''
                elif(hostBrowser == self.BROWSER_CHROME):
                    chrome_options = webdriver.ChromeOptions()

                    # ==============================================================================
                    # SaveToC makes download and export great again
                    # when old path - default_directory:'z:\test' - doesn't exist on test machines
                    # ==============================================================================
                    if SaveToC:
                        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                        prefs = {'download.default_directory': pth, 'download.prompt_for_download': False,
                                 'download.directory_upgrade': True, }
                    else:
                        prefs = {'download.default_directory': r'z:\test', 'download.prompt_for_download': False,
                                 'download.directory_upgrade': True, }

                    chrome_options.add_argument("--incognito")
                    chrome_options.add_argument("--start-maximized")
                    chrome_options.add_argument("--ignore-certificate-errors")

                    #Special options for webex recording from webcam
                    if fakeWebcam:
                        chrome_options.add_argument("--use-fake-device-for-media-stream")
                        chrome_options.add_argument("--use-fake-ui-for-media-stream")
                    chrome_options.add_experimental_option('excludeSwitches', ['disable-component-update'])
                    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
                    chrome_options.add_experimental_option('prefs', prefs)
                    chrome_options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
                    if (myProxy != None):
                        chrome_options.add_argument('--proxy-server=http://' + myProxy.proxy)

                    # headers_extension = "C:\Program Files\Python39\webdrivers\capture.crx"
                    # chrome_options.add_argument("--allow-running-insecure-content")
                    # chrome_options.add_extension(headers_extension)
                    # dd = chrome_options.extensions.count()
                    # chrome_options.extensions.__getitem__(0)

                    wd = webdriver.Chrome(pathChromedriver, options=chrome_options)
                    wd.implicitly_wait(30)
                    return wd

                    ''' IE '''
                elif(hostBrowser == self.BROWSER_IE):
                    wd= webdriver.Ie(r'C:\Program Files\Python39\webdrivers\IEDriverServer.exe',capabilities={'ignoreZoomSetting':True,"nativeEvents": False,"unexpectedAlertBehaviour": "accept","ignoreProtectedModeSettings": True,"disable-popup-blocking": True,"enablePersistentHover": True})
                    wd.implicitly_wait(30)
                    return wd

            except Exception as Exp:
                print("***************** could not set web driver due to exception: " + str(Exp))
        else: #remote, capture traffic using proxy
            if (myProxy != None):
                if (hostBrowser == self.BROWSER_IE):
                    wd = webdriver.Remote(command_executor=self.GRID_HOST,proxy=myProxy, desired_capabilities={'unexpectedAlertBehaviour':'accept', 'browserName': hostBrowser,'requireWindowFocus':True,'ignoreZoomSetting':True,"nativeEvents": False,"unexpectedAlertBehaviour": "accept","ignoreProtectedModeSettings": True,"disable-popup-blocking": True,"enablePersistentHover": True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                else:
                    wd = webdriver.Remote(command_executor=self.GRID_HOST,proxy=myProxy, desired_capabilities={'browserName': hostBrowser,'requireWindowFocus':True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                wd.implicitly_wait(30)
                return wd
            
            else:
                if (hostBrowser == self.BROWSER_IE):
                    wd = webdriver.Remote(command_executor=self.GRID_HOST,desired_capabilities={'unexpectedAlertBehaviour':'accept','browserName': hostBrowser,'requireWindowFocus':True,'ignoreZoomSetting':True,"nativeEvents": False,"unexpectedAlertBehaviour": "accept","ignoreProtectedModeSettings": True,"disable-popup-blocking": True,"enablePersistentHover": True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                     
                elif(hostBrowser == self.BROWSER_FIREFOX):
                    wd = webdriver.Remote(command_executor=self.GRID_HOST, desired_capabilities={'proxy': '{"proxyType":"DIRECT"}', 'browserName': hostBrowser,'requireWindowFocus':True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND})
                else:
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument("--incognito")
                    chrome_options.add_argument("--start-maximized")
                    chrome_options.add_argument("--ignore-certificate-errors")
                    #Special options for webex recording from webcam
                    if fakeWebcam:
                        chrome_options.add_argument("--use-fake-device-for-media-stream")
                        chrome_options.add_argument("--use-fake-ui-for-media-stream")
                    prefs = {'download.default_directory' :  'Z:\\test',
                                 'download.prompt_for_download': False,
                                 'download.directory_upgrade': True,
                                 'safebrowsing.enabled': False,
                                 'safebrowsing.disable_download_protection': True,
                                 "profile.default_content_setting_values.media_stream_mic": 1, 
                                 "profile.default_content_setting_values.media_stream_camera": 1,
                                 "profile.default_content_setting_values.geolocation": 1, 
                                 "profile.default_content_setting_values.notifications": 1}
                    print("************************** from chrome web driver options **************************")
                    chrome_options.add_experimental_option('prefs', prefs)
                    
                    
                    #===========================================================
                    # 
                    # prefs = {'download.default_directory' : r'z:\test','download.prompt_for_download': False,'download.directory_upgrade': True,}
                    # chrome_options.add_argument("--incognito")
                    # chrome_options.add_argument("--start-maximized")
                    # chrome_options.add_experimental_option('excludeSwitches', ['disable-component-update'])
                    # chrome_options.add_experimental_option('prefs', prefs)
                    # chrome_options.add_argument('--user-data-dir=' + r'C:\temp\Default_auto')
                    #===========================================================
                    wd =  webdriver.Remote(command_executor=self.GRID_HOST, desired_capabilities={'setNoProxy': '' , 'browserName': hostBrowser,'requireWindowFocus':True,"applicationName": self.LOCAL_SETTINGS_SELENIUM_GRID_POOL_BACKEND},options=chrome_options)
                    

                
                wd.implicitly_wait(30)
                return wd
                
                
    
    # this function inserts value to a text box, Return False if text box not found
    def valToTextbox(self, webdrvr, objXpath, txt):
        
        try:
            edtField = webdrvr.find_element_by_xpath(objXpath)
        except Exception as Exp:
            print(Exp)
            return False
        
        edtField.send_keys(txt)
        
    # wait for object to appear on webdriver browser
    def Sync(self,webdrvr,objxPath):
        
        webdrvr.implicitly_wait(10)
        try:
            return webdrvr.find_element_by_xpath(objxPath)
        except:
            return False
        
        
    
