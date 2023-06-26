import os
import traceback, re

import Config

def before_run(cls):
    testId = get_current_test_id()
    kill_browsers()
    update_global_variables(cls, testId)
    set_env_ini(cls, cls.isProd, cls.ConfigId)

# Extracts the current test id from the test file name
def get_current_test_id():
    stack_trace = traceback.extract_stack()
    for frame in stack_trace:
        # use regular expressions to extract the number
        match = re.search("_\d+\d+_", frame.filename)
        if match:
            return match.group().strip('_')

def kill_browsers():
    os.system("taskkill /IM chromedriver.exe /F")
    os.system("taskkill /IM chrome.exe /F")

def update_global_variables(cls, testId):
    #Set Jenkins parameters
    cls.Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
    cls.isProd = os.getenv('isProd')
    if str(cls.isProd) == 'true':
        cls.isProd = True
    else:
        cls.isProd = False

    cls.IsSRT = os.getenv('IsSRT')
    if str(cls.IsSRT) == 'true':
        cls.IsSRT = True
    else:
        cls.IsSRT = False
    # Only if this is remote execution - if the second line is populated
    automationArguments = get_csv_value_by_test_id(testId, 15) # 15 = Automation Arguments
    if automationArguments:
        os.environ['ServerURL'] = automationArguments.split(';')[0]
        os.environ['PartnerID'] = automationArguments.split(';')[1].strip('\n')
        try:
            os.environ['ConfigId'] = automationArguments.split(';')[2].strip('\n')
        except:
            pass
    cls.PartnerID = os.getenv('PartnerID')
    cls.ServerURL = os.getenv('ServerURL')
    cls.ConfigId = os.getenv('ConfigId')

# Get CSV value by the column index, when 0 is the first column.
def get_csv_value_by_test_id(testId, columnIndex):
    try:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tests_to_execute.csv'))
        with open(csv_path) as f:
            lines = f.readlines()
        if not lines:
            print("The CSV is empty")
            return
        if len(lines) < 2:
            print("No tests in the CSV")
            return
        for line in lines:
            splitted_line = line.split(',')
            # execution_order,automation_env_field,test_display_id,automation_platform_field,automation_run_only,execute_at_night,session_id,test_set_id,test_set_name,test_instance_id,case_name,assigned_to,project_name,project_id,is_srt,automation_arguments
            if testId == splitted_line[2]:
                return splitted_line[columnIndex]
        print("No test found in the CSV")
        return
    except:
        print("FAILED to get_csv_value_by_test_id")
        return

# Moran.Cohen
# This function set ini file according to env Prod/Testing + Dynamic ini by configId
def set_env_ini(cls, isProd, configId=None):
    pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
    if configId == None:
        cls.ConfigId = ""
        if isProd:# Regular config - Testing/Prod options
            cls.section = "Production"
            cls.inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            cls.env = 'prod'
            print('PRODUCTION ENVIRONMENT')
        else:
            cls.section = "Testing"
            cls.inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            cls.env = 'testing'
            print('TESTING ENVIRONMENT')
    else: # configId with dynamic ini file
        if isProd:
            cls.section = "Production"
            cls.inifile = Config.ConfigFile(os.path.join(pth, configId + '.ini'))
            cls.env = 'prod'
            print(configId + ' ENVIRONMENT')
        else:
            cls.section = "Testing"
            #cls.inifile = Config.ConfigFile(os.path.join(pth, configId + '.ini'))
            cls.inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            cls.env = 'testing'
            print(configId + ' ENVIRONMENT')