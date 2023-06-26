import os, sys
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'APITests', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.insert(1,pth)
import time
import Config
from integrations.PractiTest.practitest import *
from integrations.static_methods import *


# Generate list of dictionaries of field name and value for each test
def prepare_list_of_test_fields_dict(practitest_instance, test_set, tests_to_execute):
    list_of_test_dict = []
    # To identify same test set execution
    test_set_session_id = str(time.time()).replace(".", "")
    # Create dictionary with CSV headers and values for each test
    for test in tests_to_execute:
        tests_csv_dict = {'execution_order': try_to_get_dict_value(
                            f"str(test['attributes']['custom-fields']['{practitest_instance.PRACTITEST_EXECUTION_ORDER}'])",
                            test=test),
                        'automation_env_field': str(choose_value_test_or_test_set(test_set, test,
                                                                         f"['attributes']['custom-fields']['{practitest_instance.PRACTITEST_AUTOMATION_ENV_FIELD}']")),
                        'test_display_id': str(test['attributes']['test-display-id']),
                        'automation_platform_field': str(choose_value_test_or_test_set(test_set, test,
                                                                     f"['attributes']['custom-fields']['{practitest_instance.PRACTITEST_AUTOMATION_PLATFORM_FIELD}']")),
                        'automation_run_only': try_to_get_dict_value(
                            f"str(test_set['attributes']['custom-fields']['{practitest_instance.PRACTITEST_AUTOMATION_RUN_ONLY}'])",
                            test_set=test_set, default_return='NO RUN'),
                        'execute_at_night': try_to_get_dict_value(
                            f"str(test_set['attributes']['custom-fields']['{practitest_instance.PRACTITEST_EXECUTE_AT_NIGHT}'])",
                            test_set=test_set, default_return='no'),
                        'session_id': test_set_session_id,
                        'test_set_id': str(test_set['attributes']['display-id']),
                        'test_set_name': str(test_set['attributes']['name']),
                        'test_instance_id': str(test['id']),
                        'case_name': str(test['attributes']['name']).replace("'", "").replace('"', '').replace(',', '')
                            .replace('(', '').replace(')', '').replace('<', '').replace('>', '').replace('!', '')
                            .replace('@', '').replace('#', '').replace('*', ''),
                        'assigned_to': try_to_get_dict_value("str(test_set['attributes']['assigned-to-id'])",
                                                             test_set=test_set, default_return='None'),
                        'project_name': str(practitest_instance.PRACTITEST_PROJECT_NAME),
                        'project_id': str(practitest.PRACTITEST_PROJECT_ID),
                        'is_srt': try_to_get_dict_value(f"str(test_set['attributes']['custom-fields']['{practitest_instance.PRACTITEST_IS_SRT}'])",
                              test_set=test_set, default_return='no'),
                        'automation_arguments': try_to_get_first_test_value(f"str(test['attributes']['custom-fields']['{practitest_instance.PRACTITEST_TEST_AUTOMATION_ARGUMENTS}'])",
                                                                            f"str(test_set['attributes']['custom-fields']['{practitest_instance.PRACTITEST_AUTOMATION_ARGUMENTS}'])", test=test, test_set=test_set)
                    }

        list_of_test_dict.append(tests_csv_dict)
    if list_of_test_dict:
        return list_of_test_dict
    else:
        return

if __name__ == '__main__':
    pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'APITests', 'ini'))
    inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
    PRACTITEST_API_TOKEN = inifile.RetIniVal('Practitest', 'PRACTITEST_API_TOKEN')
    PRACTITEST_EMAIL = inifile.RetIniVal('Practitest', 'PRACTITEST_EMAIL')
    if len(sys.argv) < 2:
        print(
            'Please provide two arguments: json_file_name filterId')
        exit(1)
    _json_file_name = str(sys.argv[1])
    filter_id = sys.argv[2]
    # Read from json file
    d = load_json_config(_json_file_name)
    # Create PractiTest class instance
    pt_username = PRACTITEST_EMAIL
    pt_token = PRACTITEST_API_TOKEN
    csv_file_path_output = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'tests_to_execute.csv'))
    practitest = PractiTest(pt_username, pt_token,
                            practitest_project_id=json_find_item(d, 'project_id'),
                            project_name=json_find_item(d, 'project_name'),
                            practitest_execute_at_night=json_find_item(d, 'execute_at_night'),
                            practitest_execute_automated=json_find_item(d, 'execute_automated'),
                            practitest_automation_run_only=json_find_item(d, 'automation_run_only'),
                            additional_filter={
                                json_find_item(d, 'execute_automated'): json_find_item(d, 'execute_automated_value')},
                            processed_field_id=json_find_item(d, 'processed_field_id'),
                            processed_field_value=json_find_item(d, 'processed_field_value'),
                            practitest_automation_trigger=json_find_item(d, 'automation_status'),
                            practitest_automation_trigger_value=json_find_item(d, 'trigger_field_value'),
                            automation_env_field=json_find_item(d, 'automation_env_field'),
                            automation_platform_field = json_find_item(d, 'automation_platform_field'),
                            is_srt = json_find_item(d, 'is_srt'),
                            execution_order = json_find_item(d, 'execution_order'),
                            automation_arguments = json_find_item(d, 'automation_arguments'),
                            test_automation_arguments = json_find_item(d, 'test_automation_arguments'))
                            # ,test_set_fields_dict=json.loads(
                            #     json_find_item(d, 'prepare_test_set_for_execution').replace("'", "\"")))
    # Get the oldest test set (last updated)
    test_set = practitest.get_oldest_test_set_under_specific_filter(filter_id)
    if not test_set:
        print("No Test Sets found to execute under filter: '" + str(filter_id) + "'")
        exit(1)

    # Mark test set as processed
    data = '{"data": {"type": "sets","attributes": {"custom-fields": {"' + practitest.PROCESSED_FIELD_ID + '": "' + practitest.PROCESSED_FIELD_VALUE + '"}}}}'
    if not practitest.update_test_set(test_set['id'], data=data):
        print("Unable to set Test Set as processed")
        exit(1)
    test_set_display_id = test_set['attributes']['display-id']
    print(f'Test Set ID {test_set_display_id} was updated as processed')

    # Prepare List of tests to execute
    tests_to_execute = practitest.get_list_of_tests_by_status(test_set, test_set['attributes']['custom-fields'][practitest.PRACTITEST_AUTOMATION_RUN_ONLY])
    if not tests_to_execute:
        print("No tests found with matching criteria")
        exit(1)

    # Additional filter by any custom filed of tests to execute
    # Need set ADDITIONAL_FILTER
    # For example:
    # ADDITIONAL_FILTER = {PRACTITEST_EXECUTE_AUTOMATED:'yes'}
    tests_to_execute = practitest.filter_tests_by_custom_fields(tests_to_execute)
    if not tests_to_execute:
        print("No tests left after additional filter")
        exit(1)

    # Generate list of dictionaries of field name and value for each test
    list_of_test_dict = prepare_list_of_test_fields_dict(practitest, test_set, tests_to_execute)
    if not list_of_test_dict:
        print("FAILED to generate list of dictionaries of field name and value for each test")
        exit(1)

    # Delete existing CSV file
    if not delete_file_is_exists(csv_file_path_output):
        print("FAILED to delete CSV file")
        exit(1)

    # Create CSV file with test rows
    if not create_test_csv(list_of_test_dict, csv_file_path_output):
        print("FAILED to create CSV file")
        exit(1)

    # Copy tests files to folder TestsToExecute (only tests from tests_to_execute.csv)
    if not copy_tests('APITests', execution_order=True):
        print("FAILED to copy tests files")
        exit(1)

    # Pick to first raw in the csv file, to check isProd, IsSRT, PartnerID, ServerURL
    # Update .env file which used when executing tests from TestToExecute folder,
    # py.test -s --envfile .\\jenkins\\.env APITests\\TestsToExecute
    if not handle_global_variables():
        exit(1)
    exit(0)