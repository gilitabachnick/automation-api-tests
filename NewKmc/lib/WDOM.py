################################################################
#
# DOM = Document Object Mapping
#
# This file contains all the objects mapping of Webex
#
#
# author: Ilia Vitlin
#
################################################################


'''
@LOGIN
'''

SIGNIN_BTN          = ".el-button--medium:nth-child(1)"
EMAIL_FIELD         = "IDToken1"
EMAIL_SUBMIT        = "IDButton2"
PASSWORD_FIELD      = "IDToken2"
PASSWORD_SUBMIT     = "Button1"
SPLASH_SCREEN_OFF   = "/html/body/div[5]/div[3]"
COOKIES_ACCEPT      = "//span[contains(text(),'Accept')]"
HELP_OK             = "//span[contains(text(),'Done')]"
'''
@START_MEETING
'''

START_MTG_BTN       = "//span[contains(text(),'Start')]"
MTG_MODE_SELECT     = ".el-dropdown__caret-button"
WEB_APP             = "//li[contains(text(),'Use web app')]"
SKIP_WELCOME        = ".style-theme-dark-iYE87"

'''
@RECORDING
'''

START_MTG           = "//button[contains(text(),'Start meeting')]"
SOURCE_SELECT       = "/html/body/div[2]/div/div[2]/div[3]/div/button/div/span[2]"
SOURCE_COMPUTER     = "/html/body/div[2]/div/div[2]/div[3]/div[2]/ul/li[1]/span"
START_VIDEO        = "/html/body/div[1]/div/div[3]/div[2]/div[2]/div/div/button"
RECORD_MENU         = "/html/body/div[3]/div/div[1]/div[3]/div[2]/div[3]/div[4]/div/div/button"
WHITEBOARD_POPUP = "//button[contains(text(), 'Got it')]"
RECORD_MENU         = "//button[contains(@title,'Record')]"
START_RECORDING     = "/html/body/div[3]/div/div[1]/div[3]/div[2]/div[2]/div[4]/div/div[2]/div/div/div/div/button/span"
STOP_RECORDING      = "/html/body/div[3]/div/div[1]/div[3]/div[2]/div[2]/div[4]/div/div[2]/div/div/div/button[2]"
CONFIRM_STOP        = "/html/body/div[3]/div/div[4]/div/div/div/div[3]/div/button[1]"

'''
@END_MEETING
'''

END_MENU            = "//button[contains(@aria-label,'Leave or end meeting')]"
END_BTN             = "/html/body/div[3]/div/div[1]/div[3]/div[2]/div[2]/div[7]/div/div[2]/div/div/button"
CONFIRM_END         = "/html/body/div[3]/div/div[4]/div/div/div/div[3]/div/button[2]"

'''
@RECORDED_MEETINGS
'''
SECOND_SPLASH       = "/html/body/div[8]/div[3]"
MEETINGS            = "//span[contains(text(),'Meetings')]"
RECORDED_LIST       = "//div[contains(text(),'Recordings')]"
GENERATING          = "//span[contains(text(),' Generating...')]"
ENTRY_NAME          = "//div[@class='recording_list_topic']//a//span"
