from enum import Enum
from retrying import retry
import requests, json
from integrations import static_methods


class PractiTest:
    WAIT_EXPONENTIAL_MULTIPLIER = 10000
    WAIT_EXPONENTIAL_MAX = 60000

    def __init__(self, username,
                 token,
                 practitest_project_id,
                 project_name=None,
                 practitest_execute_at_night=None,
                 practitest_execute_automated=None,
                 practitest_automation_run_only=None,
                 additional_filter=None,
                 processed_field_id=None,
                 processed_field_value=None,
                 practitest_automation_trigger=None,
                 practitest_automation_trigger_value=None,
                 automation_env_field=None,
                 automation_platform_field=None,
                 is_srt=None,
                 execution_order=None,
                 automation_arguments=None,
                 test_automation_arguments=None
                 ):
        # PracitTest fields ID
        self.USER_NAME = username
        self.API_TOKEN = token
        self.PRACTITEST_PROJECT_ID = practitest_project_id
        self.PRACTITEST_PROJECT_NAME = project_name
        self.PRACTITEST_EXECUTE_AT_NIGHT = practitest_execute_at_night
        self.PRACTITEST_EXECUTE_AUTOMATED = practitest_execute_automated
        self.PRACTITEST_AUTOMATION_RUN_ONLY = practitest_automation_run_only
        self.ADDITIONAL_FILTER = additional_filter
        self.PROCESSED_FIELD_ID = processed_field_id
        self.PROCESSED_FIELD_VALUE = processed_field_value
        self.PRACTITEST_AUTOMATION_ENV_FIELD = automation_env_field
        self.PRACTITEST_AUTOMATION_PLATFORM_FIELD = automation_platform_field
        self.PRACTITEST_IS_SRT = is_srt
        self.PRACTITEST_EXECUTION_ORDER = execution_order
        self.PRACTITEST_AUTOMATION_ARGUMENTS = automation_arguments
        self.PRACTITEST_TEST_AUTOMATION_ARGUMENTS = test_automation_arguments

        # Trigger fields
        self.PRACTITEST_AUTOMATION_TRIGGER = practitest_automation_trigger
        self.PRACTITEST_AUTOMATION_TRIGGER_VALUE = practitest_automation_trigger_value

        ## Prepare test set for execution
        #self.TEST_SET_FIELDS_DICT = test_set_fields_dict

        self.BASE_URL = "https://api.practitest.com/api/v2/projects/" + self.PRACTITEST_PROJECT_ID
        self.RUNS_URI = f'{self.BASE_URL}/runs.json?developer_email={self.USER_NAME}&api_token={self.API_TOKEN}'
        self.INSTANCE_URI = f'{self.BASE_URL}/instances.json?developer_email={self.USER_NAME}&api_token={self.API_TOKEN}'
        self.SETS_URI = f'{self.BASE_URL}/sets.json?developer_email={self.USER_NAME}&api_token={self.API_TOKEN}'
        self.SPECIFIC_SET_URI = f'{self.BASE_URL}/sets/YOUR_SET_ID.json?developer_email={self.USER_NAME}&api_token={self.API_TOKEN}'
        self.CLONE_TEST_SET = f'{self.BASE_URL}/sets/YOUR_SET_ID/clone.json?developer_email={self.USER_NAME}&api_token={self.API_TOKEN}'
        self.HEADERS = {
            'Content-Type': 'application/json',
            'Connection': 'close'
        }

    class TestStatusEnum(Enum):
        def __str__(self):
            return str(self.value)

        PASSED = 'PASSED'
        FAILED = 'FAILED'
        BLOCKED = 'BLOCKED'
        NO_RUN = 'NO RUN'
        N_A = 'N/A'

    # return the oldest test set under specific filter id
    @retry(wait_exponential_multiplier=WAIT_EXPONENTIAL_MULTIPLIER, wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def get_oldest_test_set_under_specific_filter(self, filter_id, only_execute_at_night=False):
        """Get oldest TestSet under specific filter.
        :param filter_id: filter id
        :param only_execute_at_night: True for only execute at night
        :return: test set to process
        """
        test_sets_list = self.get_all_testsets_under_specific_filter_id(filter_id)
        if not test_sets_list:
            return
        test_set_to_process = []
        # Get any (first in the dict) test set from the dict
        if only_execute_at_night:
            # Search for the first test set which is onlyExecuteAtNight is TRUE
            for test_set in test_sets_list:
                # If testSet
                execute_at_night = test_set['attributes']['custom-fields'][self.PRACTITEST_EXECUTE_AT_NIGHT]
                if execute_at_night == 'yes' or execute_at_night == 'true':
                    test_set_to_process = test_set
                    break
        else:
            test_set_to_process = test_sets_list[0]
        # In case onlyExecuteAtNight=True and no test set found when the filed is checked in PractiTest
        if not test_set_to_process:
            print('No Test Set was found to execute, when "Execute at Night" checked in PractiTest')
            return

        for test_set in test_sets_list:
            # Get the oldest test set
            if static_methods.get_test_set_updated_time(test_set) < static_methods.get_test_set_updated_time(test_set_to_process):
                test_set_to_process = test_set

        print("TestSet name: " + str(test_set_to_process['attributes']['name']) + "; ID: " + str(test_set_to_process['attributes']['display-id']) +
                       " going to be processed")
        return test_set_to_process

    @retry(wait_exponential_multiplier=WAIT_EXPONENTIAL_MULTIPLIER, wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def send_request(self, method, url, headers, data=''):
        """Sends a GET/POST/PUT request.
        :param method: 'post' or 'get' or 'put' string
        :param url: URL as string
        :param headers: json as string
        :param data: data/json as string if sending 'post' or 'put' request
        :return: response
        """
        try:
            if str(method).lower() == 'get'.lower():
                r = requests.get(url, headers=headers, verify=False)
            elif str(method).lower() == 'post'.lower():
                r = requests.post(url, headers=headers, data=data, verify=False)
            elif str(method).lower() == 'put'.lower():
                r = requests.put(url, headers=headers, data=data, verify=False)
            else:
                print(f'Unknown request method: {method}')
                return
        except requests.exceptions.RequestException:
            raise Exception("WARNING: Failed to send request, going to retry")
        return r

    @retry(wait_exponential_multiplier=WAIT_EXPONENTIAL_MULTIPLIER, wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def wait_for_request_200(self, method, url, headers, msg_on_retry, data=''):
        """Sends a GET/POST/PUT request and verify code 200, else retry.
        :param method: 'post' or 'get' or 'put' string
        :param url: URL as string
        :param headers: json as string
        :param msg_on_retry: msg printed upon fail
        :param data: data/json as string if sending 'post' or 'put' request
        :return: response
        """
        r = self.send_request(method, url, headers, data)
        if r.status_code == 200:
            return r
        else:
            raise Exception('WARNING: ' + str(msg_on_retry) + f'; status code: {r.status_code}')

    def get_testset_with_specific_id(self, test_set_id):
        """Sends a GET request and verify code 200, else retry.
        :param test_set_id: test set id
        :return: dict data
        """
        url = self.SPECIFIC_SET_URI.replace('YOUR_SET_ID', str(test_set_id))
        response = self.wait_for_request_200('get', url, self.HEADERS,
                                             f'Bad response for get_testset_with_specific_id; Going to retry')
        return static_methods.get_dict_data_if_not_empty(json.loads(response.text))

    def clone_testset(self, original_testset_id, new_testset_name='Cloned Test Set'):
        """Clone test set by id.
        :param original_testset_id: test set id as int or string
        :param new_testset_name: new name of the clone test set name. Do not use, PractiTest has an issue this
        :return: cloned test set ID as string
        """
        # data = '{"data": { "type": "sets", "attributes": {"name": "' + newTestSetName + '"}}}' #TODO check if PT issue was resolved
        # data = '{"data": { "type": "sets", "attributes": {"name": "my new cloned TestSet", "planned-execution":"2022-03-01T12:43:31Z", "priority": "highest"}}}'
        data = '{"data": { "type": "sets"} }'
        url = self.CLONE_TEST_SET.replace('YOUR_SET_ID', str(original_testset_id))
        response = self.wait_for_request_200('post', url, self.HEADERS,
                                             'Bad response for clone test set instances; Going to retry',
                                             data=json.dumps(data))
        print('Test set was cloned from ID: ' + str(original_testset_id))
        return str(json.loads(response.text)['data']['id'])

    def clone_test_set_and_rename(self, test_set_id_to_clone, cloned_test_set_name):
        """Clone test set by id and rename it.
        :param test_set_id_to_clone:
        :param cloned_test_set_name:
        :return: cloned test set ID as string, else return -1
        """
        # Clone a test set from a template test set
        cloned_test_set_id = self.clone_testset(test_set_id_to_clone, cloned_test_set_name)
        if cloned_test_set_id == -1:
            print('FAILED to clone template test set ID: ' + str(test_set_id_to_clone))
        data = '{"data": { "type": "sets", "attributes": {"name": "' + cloned_test_set_name + '"}}}'
        if not self.update_test_set(cloned_test_set_id, data=data):
            print('FAILED to rename cloned test set : ' + str(test_set_id_to_clone))
            return -1
        return cloned_test_set_id

    def get_all_testsets_under_specific_filter_id(self, filter_id):
        """Return all test sets under specific filter id
        :param filter_id: filter id as int ot string
        :return: dictionary
        """
        url = self.SETS_URI + "&filter-id=" + str(filter_id)
        response = self.wait_for_request_200('get', url, self.HEADERS,
                                             f'Bad response for get_all_testsets_under_specific_filter_id; Going to retry')
        return static_methods.get_dict_data_if_not_empty(json.loads(response.text))

    def get_list_of_tests_by_status(self, test_set, status):
        """Return all test sets under specific filter id
        :param test_set: test set object
        :param status: TestStatusEnum: PASSED, FAILED, BLOCKED, NO_RUN, N_A, ALL
        :return: dictionary
        """
        tests_to_execute = []
        page = 1
        while True:
            url = self.INSTANCE_URI + "&set-ids=" + str(test_set['id']) + "&page[number]=" + str(page)
            # For next iteration
            page = page + 1
            response = self.wait_for_request_200('get', url, self.HEADERS,
                                                 f'Bad response for get_list_of_tests_by_status; Going to retry')
            dct_sets = json.loads(response.text)
            if len(dct_sets["data"]) > 0:
                for test_instance in dct_sets["data"]:
                    test_instance_atrr = test_instance['attributes']
                    # If status is 'ALL', will add the test with any status
                    if status.lower() == 'all':
                        tests_to_execute.append(test_instance)
                    # Get only if the test matches to given status
                    elif test_instance_atrr['run-status'].lower() == status.lower():
                        tests_to_execute.append(test_instance)
            else:
                if page > 2:
                    print(
                        "Finished getting tests from test set: '" + test_set['attributes']['name'] + "' ID: " + str(
                            test_set['attributes']['display-id']))
                else:
                    print("No instances in set. " + response.text)
                break
        return tests_to_execute

    def filter_tests_by_custom_fields(self, list_of_tests_to_filter):
        """Filter tests by custom fields. You need to set the self.ADDITIONAL_FILTER dict with the expected fields values
        :param list_of_tests_to_filter: list of tests object
        :return: list of tests object after filter
        """
        if not self.ADDITIONAL_FILTER:
            return list_of_tests_to_filter
        tests_to_execute = []
        for test in list_of_tests_to_filter:
            add_test = False
            for field_id in self.ADDITIONAL_FILTER:
                try:
                    if not test['attributes']['custom-fields'][field_id].lower() == self.ADDITIONAL_FILTER[field_id]:
                        add_test = False
                        break
                    add_test = True
                except Exception:
                    break
            if add_test:
                tests_to_execute.append(test)
        return tests_to_execute

    def update_test_set(self, instanceId, custom_fields_dict='', data=''):
        """Update the test set custom field.
        customFiledId example: "---f-38302"
        :param instanceId: test set instance id as int or string
        :param custom_fields_dict: dict of all custom fields to update
        :param data: data/json as string
        :return: True or False boolean
        """
        url = self.SETS_URI.replace('/sets', '/sets/' + str(instanceId))
        if not data:
            generated_data = static_methods.create_data_for_test_set_multiple_custom_fields(custom_fields_dict)
            # Convert data string to variable
            generated_data = eval(generated_data)
            generated_data = json.dumps(generated_data)
        else:
            generated_data = data
        try:
            self.wait_for_request_200('put', url, self.HEADERS, 'Bad response for update_test_set; Going to retry',
                                      data=generated_data)
            return True
        except:
            return False

