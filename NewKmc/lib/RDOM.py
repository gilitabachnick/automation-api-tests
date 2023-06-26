################################################################
#
# DOM = Document Object Mapping  
#
# This file contains all the objects mapping of REACH
#       used in the Manual test-set
#
#
# Author: Zeev Shulman
# Date: 01.11.2021
################################################################

''' =========================================
@ADMIN CONSOLE: REACH PARTNER CATALOG ITEMS
'''
REACH_PARTNER_CATALOG_ITEMS = "//*[text()='Partner Catalog Items']"
REACH_FILTER_BY_PID = "//input[@id='filter_input']"
REACH_SERVICE_FEATURE_DD = "//select[@id='filterServiceFeature']"
REACH_SERVICE_TYPE_DD = "//select[@id='filterServiceType']"
REACH_TURN_AROUND_DD = "//select[@id='filterTurnAroundTime']"
REACH_SERVICE_SOURCE_LANG_DD = "//select[@id='filterSourceLanguage']"
REACH_BULK_DELETE        = "//button[text()='Bulk Delete']"
REACH_CHECK_ITEM = "//input[@type='checkbox' and @value='TEXTTOREPLACE']"
REACH_CATALOG_ITEM_CONFIG  = "//button[@name='configureCatalogItemsButton']"

''' =========================================
@ADMIN CONSOLE: REACH PROFILE 
'''
REACH_PROFILE_TABLE_1_ID = '//*[@id="reach_profile_list_div"]/table/tbody/tr[1]/td[1]'
REACH_PROFILE_TABLE_1_NAME = '//*[@id="reach_profile_list_div"]/table/tbody/tr[1]/td[2]'
REACH_PROFILE_TABLE_1_DD  = '// *[ @ id = "reach_profile_list_div"] / table / tbody / tr[1] / td[10] / select'
REACH_PROFILE_CONFIG_CREDIT = '//*[@id="reachProfileCredit-credit"]'
REACH_PROFILE_CONFIG_TO_DATE = '//*[@id="reachProfileCredit-toDate"]'
REACH_PROFILE_ID_INPUT = '//input[@id="profileId"]'
REACH_CLONE_PROFILE_BTN = "//span[text()='Clone Profile']"

''' =========================================
@ADMIN CONSOLE: CONFIGURATION AUDIT
'''
ADMINCONSOLE_CONFIGURATION_TAB = ".//a[text()='Configuration']"
ADMINCONSOLE_AUDIT_TAB = ".//a[text()='Audit Trail']"
ADMINCONSOLE_AUDIT_TYPE = '//*[@id="filter_input"]'
ADMINCONSOLE_AUDIT_OBJECT_ID = '//*[@id="filter_object_id"]'
AUDIT_ROW1_DETAILS =  '//*[@id="audit_trail_list_div"]/table/tbody/tr[1]/td[9]'

''' =========================================
@ADMIN CONSOLE: REACH REQUESTS
'''
REACH_REQUESTS_TAB = ".//a[text()='Reach Requests']"
REACH_REQUESTS_FILTER = '//*[@id="filter_type"]'
REACH_EXPORT_CSV = "//span[text()='Export to CSV']"
REACH_EXPORT_LINK = '//a[contains(text(),"Download exported CSV")]'
REACH_REQUEST_ROW_1_FIELDS = '//*[@id="entry_vendor_task_list_div"]/table/tbody/tr[1]/td[TEXTTOREPLACE]'
REACH_STATUS_FILTER = "//select[@id='filter_status']"

''' =========================================
@ADMIN CONSOLE: CATALOG ITEMS 
'''
REACH_CATALOG_ITEMS_1_FIELDS = '//*[@id="catalog_item_list_div"]/table/tbody/tr[1]/td[TEXTTOREPLACE]'
REACH_IMPORT_CSV = '//*[@id="importCSV"]'
REACH_IMPORT_BTN = "//*[text()='Import']"
IMP_NUM = '//*[@id="catalog-item-import-dialog"]/p/var'
REACH_IMPORT_INPUT = '//*[@id="bulkUploadId"]'
REACH_IMPORT_RESULT = '//*[@id="getBulkUplodaResult"]/span'
REACH_CLOSE = "//*[text()='Close']"
REACH_IMPORT_LOG = '//*[@id="catalog-item-import-result-dialog"]/var[2]'
REACH_ITEMS_TABLE = '//*[@id="catalog_item_list_div"]/table/tbody/tr'
REACH_ITEM_ID = '//*[@id="catalog_item_list_div"]/table/tbody/tr[*]/td[14]/select'
REACH_ITEM_CONFIG_RESUBMISION = '//*[@id="allowResubmission"]'
REACH_ITEM_CONFIG_TYPE = '//*[@id="serviceType"]'
ITEM_UNIT_PRICE = '//*[@value="3"]'

''' ===============================================================
@ADMIN CONSOLE: BATCH PROCESS CONTROL - ENTRY INVESTIGATION
'''
BATCH_PROCESS_CONTROL_TAB = "//*[text()='Batch Process Control']"
ENTRY_ID_INPUT = '//input[@id="entryId"]'
ENTRY_ID_SEARCH = "//*[text()='Search']"
FIND_STRING_ANYWHERE = "//*[contains(text(),'TEXTTOREPLACE')]"

''' =========================================
@ADMIN CONSOLE: TEST ME
'''
TESTME_TAB = ".//a[text()='Developer']"
TESTME_KS_BOX = '//*[@id="chk-ks"]'
TESTME_KS = '//*[@id="request"]/div/div[6]/input[1]'
TESTME_SERVICE_REPORT = "//select[@name='service']/option[text()='report']"
TESTME_ACTION_GETTOTAL = "//select[@name='action']/option[text()='getTotal']"
TESTME_REPORT_TYPE_BOX = '//*[@id="dvService"]/div[4]/div[1]/input'
TESTME_REPORT_TYPE_USAGE = "//select[@name='reportType']/option[text()='REACH_USAGE']"
TESTME_EDIT = "//input[@class='edit-button button']"
TESTME_FILTER_FROMD_BOX = '//*[@id="dvService"]/div[5]/div/div/div[1]/input[2]'
TESTME_FILTER_FROMD = '//*[@id="dvService"]/div[5]/div/div/div[1]/input[1]'
TESTME_FILTER_TOD_BOX = '//*[@id="dvService"]/div[5]/div/div/div[2]/input[2]'
TESTME_FILTER_TOD = '//*[@id="dvService"]/div[5]/div/div/div[2]/input[1]'
TESTME_SEND = "//button[text()='Send']"
TESTME_REACH_USAGE_DATA = '//*[@id="editorDiv"]/div[2]/div/div[3]/div[5]/div/span[6]'

TESTME_SERVICE_ENTRYVVENDORTASK = "//select[@name='service']/option[text()='entryVendorTask']"
TESTME_ACTION_LIST = "//select[@name='action']/option[text()='list']"
TESTME_FILTER_ENTRY_BOX = '//*[@id="dvService"]/div[5]/div/div/div[16]/input[2]'
TESTME_FILTER_ENTRY = "//input[@name='filter:entryIdEqual']"

''' =========================================
@KMC: REACH PROFILE DICTIONARY
'''
REACH_PROFILE_DICTIONARY = "//*[text()='Dictionary']"
REACH_PROFILE_ADD_DICTIONARY = "//*[text()='Add Dictionary']"
REACH_PROFILE_DICTIONARY_FIELDS = '//input[@type="text"]'
REACH_PROFILE_DELETE_DICTIONARY = "//i[contains(@class,'kRemove')]"
REACH_PROFILE_CREDIT = "//*[text()='Credit']"
DICTIONARY_WORD_COUNTER = '//div[@class="kWordsFooter"]'
ENGLISH_LANGUAGE = "//*[text()='English']"
CHINESE_LANGUAGE = "//*[contains(text(),'Chinese')]"
SPANISH_LANGUAGE = "//*[contains(text(),'Spanish')]"

''' =========================================
@KMC: REACH CAPTIONS AND CAPTIONS EDITOR
'''
ENTRY_CAPTION           = "//div[text()='Captions']"
ADD_CAPTION             = "//span[contains(@class,'button')and text()='Add Caption']"
UPLOAD_SRT              = "//span[contains(@class,'button')and text()='Upload File']"
MORE_OPTIONS_DOTS       = "//span[contains(@class,'kIconmore')]"
CC_EDITOR               = "//span[text()='Closed Captions Editor']"

CAPTIONS_ROWS           = "//*[contains(@class,'text-area')]"
CAPTIONS_SAVE           = "//button[text()='Save']"
CAPTIONS_REVERT         = "//button[text()='Revert']"
CAPTIONS_YES            = "//button[text()='Yes']"
CAPTION_TIME            = '//input[@value="00:00:06,205"]'

CAPTION_SEARCH          = "//input[contains(@placeholder,'Search in Captions')]"
CAPTION_TO_REPLACE      = "//input[contains(@placeholder,'Replace with')]"
CAPTIONS_REPLACE        = "//button[text()='Replace']"
SPEAKER_BOXES           = "//input[contains(@class,'checkbox')]"
NEW_SPEAKER             = "//input[contains(@class,'add-speaker')]"
ADD_SPEAKER             = "//button[text()='Add']"
CLOSE_CAPTION_EDITOR    = "/html/body/kpopupwidget[1]/div/i"
ENTRY_RELATED_FILES = "//*[contains(text(),'Related Files')]"
TRANSCRIPT_TXT     = "//*[contains(text(),'transcript.txt')]"

''' =========================================
@KMC: SERVICES DASHBOARD - REACH
'''
SERVICES_DASHBOARD = "//*[contains(text(),'SERVICES DASHBOARD')]"
SERVICES_EMAIL_CSV = "//button[contains(@class,'download')]"
# SERVICES_MEDIA_NAME = "//button[contains(@class,'requests-table')]"
SERVICES_FIRST_COST =     '//*[@id="reach_allinone"]/div/div[2]/div/div/div[5]/div/div/div/div/div/div/div[1]/div[2]/div[1]/div/div[6]/div'
SERVICES_FIRST_COST_OLD = '//*[@id="reach_allinone"]/div/div[2]/div/div/div[5]/div/div/div/div/div/div[1]/div[2]/div[1]/div/div[5]/div'
SERVICES_REQUEST_NUM = "//span[contains(@class,'status-line')]"

SERVICES_UNIT = '//*[@id="reach_allinone"]/div/div[2]/div/div/div[2]/div/div/div/div/div/div[1]/div[1]'
SERVICES_ENTRY_BOX = '//*[@id="reach_allinone"]/div/div[2]/div/div/div[5]/div/div/div/div/div/div/div[1]/div[2]/div[TEXTTOREPLACE]/div/div[1]/div/input'
SERVICES_REJECT = "//button[text()='Reject']"
SERVICES_APPROVE = "//button[text()='Approve']"

SERVICES_DETAILS_BTN = "//button[contains(text(),'Show Details')]"
SERVICES_DETAILS_TOTAL = "//*[contains(@class,'total')]"
SERVICES_DETAILS_PARTIAL = "//*[contains(@class,'legend-value')]"

''' =========================================
@KMC: CAPTIONS_AND_ENRICH - REACH
'''
CAPTIONS_N_ENRICH = "//span[contains(@class,'button')and contains(text(),'Captions &')]"
FEATURE_SERVICE = '//*[@id="reach_allinone"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[1]/div/div/div/div/div[2]'
FEATURE_LANGUAGE = '//*[@id="reach_allinone"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]'
TARGET_TRANSLATION = '//*[@id="reach_allinone"]/div/div[2]/div/div[3]/div[2]/div[3]/div/div[1]/div[2]/div/div/div/div/div[1]'
UPLOAD_CAPTIONS_BTN = "//button[contains(text(),'Upload Captions')]"
UPLOAD_BROWSE_BTN = "//button[contains(text(),'Browse')]"
FEATURE_ALIGNMENT = '//*[@id="reach_allinone"]/div/div[2]/div/div[3]/div[2]/div[3]/div/div/div[1]/div/div/div/div/div[1]'
UPLOAD_TXT = "//button[contains(text(),'Upload txt')]"
SELECT_FILE_BTN = "//button[contains(text(),'Select File')]"
SUBMIT_BTN = "//*[contains(text(),'Submit')]"
# ENTRY_RELATED_FILES  = "//*[contains(text(),'Related Files')]"
RELATED_ASSET_ID = '//*[@id="appContainer"]/k-area-blocker/kkmcdashboard/div/kentries/kentry/k-area-blocker/div/div/div[2]/div[2]/kentryrelated/k-area-blocker/div/div/p-table/div/div/div/div[2]/table/tbody/tr/td[4]/div/span'

''' =========================================
@KMC: REACH ENTRY CAPTIONS TAB 
'''
CAPTION_QUALITY_SLIDER = '/html/body/kpopupwidget[18]/div/div/kentrycaptionsedit/div/form/div[2]/div[4]/div/kslider/div/span[2]'#'/html/body/kpopupwidget[17]/div/div/kentrycaptionsedit/div/form/div[2]/div[4]/div/kslider/div/span[2]'

YES_TEXT = "//*[contains(text(),'Yes')]"
CAPTION_LINES = '//*[@id="appContainer"]/k-area-blocker/kkmcdashboard/div/kentries/kentry/k-area-blocker/div/div/div[2]/div[2]/kentrycaptions/k-area-blocker/div/div/p-table/div/div/div/div[2]/table/tbody/tr'
CAPTION_SELECTED = '//*[@id="appContainer"]/k-area-blocker/kkmcdashboard/div/kentries/kentry/k-area-blocker/div/div/div[2]/div[2]/kentrycaptions/k-area-blocker/div/div/p-table/div/div/div/div[2]/table/tbody/tr[TEXTTOREPLACE]/td[6]'
CAPTION_ACCURACY = '//*[@id="appContainer"]/k-area-blocker/kkmcdashboard/div/kentries/kentry/k-area-blocker/div/div/div[2]/div[2]/kentrycaptions/k-area-blocker/div/div/p-table/div/div/div/div[2]/table/tbody/tr[TEXTTOREPLACE]/td[4]'

''' =========================================
@KMC: Administration USERS
'''
KMC_USERS = "//*[contains(@class,'kIconuser')]"
KMC_USERS_ADD = "//*[contains(text(),'Add User')]"
USERS_ADD_EMAIL = "/html/body/kpopupwidget[13]/div/div/kedituser/k-area-blocker/div/div[2]/form/div[2]/div[2]/input"
USERS_ADD_FIRSTN = "/html/body/kpopupwidget[13]/div/div/kedituser/k-area-blocker/div/div[2]/form/div[3]/div[2]/input"
USERS_ADD_LASTN = "/html/body/kpopupwidget[13]/div/div/kedituser/k-area-blocker/div/div[2]/form/div[4]/div[2]/input"
PUSER_ID = "/html/body/kpopupwidget[13]/div/div/kedituser/k-area-blocker/div/div[2]/form/div[6]/div/input"

''' =======================================================
@MALINATOR: DOWNLOAD KALTURA SCV & NOTIFICATION TESTS
'''
EMAIL_USER_BOX           = "//input[contains(@class,'input-text')]"
EMAIL_USER_GO           = "//button[@id='go-to-public']"
SERVICES_EMAIL_CAPTION = "//*[contains(text(),'Your CSV is ready for download')]"
JASON_TAB = '//*[@id="pills-json-tab"]'
EMAIL_MSG_JSON = '//*[@id="pills-json-content"]/pre'
KS_VIA_URL = "//*[contains(text(),'_')]"


