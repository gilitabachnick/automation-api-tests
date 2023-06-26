import csv
import json
import os, sys
import shutil
from datetime import datetime

DEFAULT_APP = 'APITests'

def json_find_item(obj, key):
    try:
        if key in obj: return obj[key]
        for k, v in obj.items():
            if isinstance(v, dict):
                item = json_find_item(v, key)
                if item is not None:
                    return str(item)
    except Exception:
        print(f'WARNING: Key {str(key)} not found in json file')  # TODO maybe need to remove this print
        return None

def load_json_config(json_path):
    try:
        with open(json_path) as f:
            return json.load(f)
    except Exception:
        print(f'Failed to read json from {json_path}')
        return False

def get_dict_data_if_not_empty(dictionary):
    if len(dictionary["data"]) != 0:
        return dictionary["data"]
    else:
        return

def create_data_for_test_set_multiple_custom_fields(custom_fields_dict):
    """Creates generic data for updating multiple custom fields in test set by sending one request
    :param custom_fields_dict:
    :return: data as json string
    """
    template_suffix = '}}}}'
    data = '{"data": { "type": "sets", "attributes": {"custom-fields": {'

    for custom_field in custom_fields_dict:
        if type(custom_fields_dict[custom_field]) is list:
            data = data + '"' + str(custom_field) + '": ' + str(custom_fields_dict[custom_field])
        else:
            data = data + '"' + str(custom_field) + '": "' + str(custom_fields_dict[custom_field]) + '"'
        # if not last, add ',' at the end
        if custom_field != list(custom_fields_dict.keys())[-1]:
            data = data + ','
    data = data + template_suffix
    return data

def get_test_set_updated_time(test_set):
    try:
        date_time_str = test_set['attributes']['updated-at'][:19]
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
    except:
        raise Exception("FAILED to parse Test set Updated Time: '" + str(test_set['attributes']['updated-at']) + "'")
    return date_time_obj

def print_dict(dictionary):
    for key in dictionary:
        print(key + ": " + str(dictionary[key]))

def get_practitest_URL_to_tests(_pt_project_id, _test_set_id):
    return f'https://prod.practitest.com/p/{str(_pt_project_id)}/sets/{str(_test_set_id)}/edit'

def print_practitest_URL_to_tests(_pt_project_id, _test_set_id):
    test_set_url = get_practitest_URL_to_tests(_pt_project_id, _test_set_id)
    print("Full report: " + test_set_url)

def try_to_get_dict_value(str_to_eval, test=None, test_set=None, default_return='None'):
    value = default_return
    try:
        value = eval(str_to_eval)
    except:
        pass
    return value

# Try to get first the Test (instance) value, otherwise, get the Test Set value
def try_to_get_first_test_value(test_str_to_eval, test_set_str_to_eval, test=None, test_set=None, default_return='None'):
    value = default_return
    try:
        value = eval(test_str_to_eval)
    except:
        try:
            value = eval(test_set_str_to_eval)
        except:
            pass
    return value

# Creates csv or appends if exists
def create_test_csv(list_of_test_dict, csv_file_path_output):
    # Create CSV file
    if list_of_test_dict:
        try:
            if os.path.isfile(csv_file_path_output):
                writeMode = 'a'
            else:
                writeMode = 'w'
            # Create CSV headers by testsCsvDict keys
            field_names = []
            for key in list_of_test_dict[0]:
                field_names.append(key)
            if os.path.isfile(csv_file_path_output):
                # Open file in append mode
                with open(csv_file_path_output, 'a+', newline='', encoding='utf-8') as write_obj:
                    # Create a writer object from csv module
                    dict_writer = csv.DictWriter(write_obj, fieldnames=field_names)
                    # Add dictionary as wor in the csv
                    for test_dict in list_of_test_dict:
                        dict_writer.writerow(test_dict)
            else:
                with open(csv_file_path_output, mode=writeMode, newline='', encoding='utf-8') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=field_names)
                    writer.writeheader()
                    for test_dict in list_of_test_dict:
                        writer.writerow(test_dict)
        except Exception as ex:
            print('FAILED to create ' + str(csv_file_path_output) + ' file: ' + str(ex))
            return
    else:
        print('FAILED to create ' + str(csv_file_path_output) + ' file')
        return

    print('"' + str(csv_file_path_output) + '" created with ' + str(len(list_of_test_dict)) + " test rows:")
    for test_dict in list_of_test_dict:
        print(test_dict)
    return list_of_test_dict

# In case the test and the test set has same field, should take first the test field value if exists
# IMPORTANT: we are using eval inside the function, DO NOT remove the 'test_set, test,' parameters from the signature
def choose_value_test_or_test_set(test_set, test, field_id_get_from_dict_str, default_return='None'):
    value = default_return
    try:
        value = eval('test_set' + field_id_get_from_dict_str)
    except:
        pass
    try:
        value = eval('test' + field_id_get_from_dict_str)
    except:
        pass
    return value

def read_test_names_from_csv(execution_order=False):
    tests_to_run= []
    csv_path =  os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'tests_to_execute.csv'))
    with open(csv_path, 'r') as csv_mat:
        test_rows = csv.DictReader(csv_mat)
        for row in test_rows:
            if execution_order:
                tests_to_run.append([row['test_display_id'], row['execution_order']])
            else:
                tests_to_run.append(row['test_display_id'])
    return tests_to_run

def copy_tests(folder_project_name, execution_order=False):
    app = folder_project_name
    PROJECT_ROOT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', app))
    # Will contain test files (test_*.py) to execute
    TEMP_TEST_DIR_PATH = os.path.abspath(os.path.join(PROJECT_ROOT_DIR_PATH, 'TestsToExecute'))
    # Delete folder if exists and create empty folder
    if not delete_folder_and_create(TEMP_TEST_DIR_PATH):
        return False
    # Exclude testsToExecute folder because we're copying tests to this folder
    EXCLUDE_DIRECTORIES = {'TestsToExecute'}
    # Get a list of all tests to execute from testSetAuto.csv
    tests_to_run = read_test_names_from_csv(execution_order)
    try:
    # Go over all tests in tree under root folder, if test appears in the list above, then copy to temp folder
        for test in tests_to_run:
            for dirpath, dirs, files in os.walk(PROJECT_ROOT_DIR_PATH):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRECTORIES]  # exclude directory if in exclude list
                for filename in files:
                    fname = os.path.join(dirpath, filename)
                    if execution_order:
                        if fname.endswith('.py') and ('_' + str(test[0]) in fname):
                            file_name = fname.split('\\')[-1]
                            if test[1] != 'None':
                                # '5' - represents the index of the file name string, after "test_"
                                new_file_name = file_name[:5] + str(test[1]) + '_' + file_name[5:]
                                dst = os.path.abspath(os.path.join(TEMP_TEST_DIR_PATH, new_file_name))
                            else:
                                dst = os.path.abspath(os.path.join(TEMP_TEST_DIR_PATH, fname.split('\\')[-1]))
                            shutil.copyfile(fname, dst)
                            print(f'Test {fname} copied to TestToExecute folder')
                    else:
                        if fname.endswith('.py') and ('_' + str(test) in fname):
                            print(fname)
                            # src = os.path.abspath(os.path.join(p, file))
                            dst = os.path.abspath(os.path.join(TEMP_TEST_DIR_PATH, fname.split('\\')[-1]))
                            shutil.copyfile(fname, dst)
                            print(f'Test {fname} copied to TestToExecute folder')
    except:
        print("FAILED to copy temp folder for tests to execute: '" + str(TEMP_TEST_DIR_PATH) + "'")
        return False
    return True

def delete_folder_and_create(folder_path):
    # Check Folder is exists or Not
    if os.path.exists(folder_path):
        try:
            # Delete Folder code
            shutil.rmtree(folder_path)
            print("The folder has been deleted successfully!")
        except Exception:
            print("Failed to delete folder:" +str(folder_path))
            return False
    print("Going to create:" + str(folder_path))
    try:
        os.makedirs(folder_path)
    except Exception:
        print("Failed to create folder:" + str(folder_path))
        return False
    return True

def delete_file_is_exists(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        print("Failed to delete file:" + str(file_path))
        return False
    return True

def get_test_instance_from_test_set_file(test_display_id):
    instance = ""
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests_to_execute.csv'))
    try:
        with open(csv_path, 'r') as csv_mat:
            test_line = csv.DictReader(csv_mat)
            for row in test_line:
                if row['test_display_id'] == test_display_id:
                    instance = row['test_instance_id']
                    break
            return instance
    except Exception:
        print("Failed to get test line from " + str(csv_path))
        return
    return

def handle_global_variables():
    """Update .env file with global variables that needed: isProd, IsSRT, PartnerID, ServerURL
    :return: True
    """
    try:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests_to_execute.csv'))
        dot_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'jenkins', '.env'))
        # Get the second line in csv
        with open(csv_path) as f:
            line = f.readlines()[1]
        if not line:
            return
        splitted_line = line.split(',')
        ### splitted_line[1] = automation_env_field  ###
        ### splitted_line[14] = is_srt               ###
        ### splitted_line[15] = automation_arguments ###
        is_prod= True if splitted_line[1].lower()=='prod' else False
        is_srt = True if splitted_line[14].replace(f'\n', '')=='yes' or splitted_line[14].replace(f'\n', '')=='true' else False
        with open(dot_env_path, 'r') as file:
            lines = file.readlines()
        with open(dot_env_path, 'w') as file:
            for line in lines:
                if 'isProd' in line:
                    line = 'isProd=true\n' if is_prod else 'isProd=false\n'
                    file.write(line)
                if 'IsSRT' in line:
                    line = 'IsSRT=true\n' if is_srt else 'IsSRT=false\n'
                    file.write(line)
        ### splitted_line[15] = automation_arguments ###
        with open(dot_env_path, 'a') as file:
            if splitted_line[15].rstrip('\n') != 'None':
                file.write('ServerURL=' + splitted_line[15].split(';')[0] + '\n')
                file.write('PartnerID=' + splitted_line[15].split(';')[1] + '\n')
        file.close()
    except Exception as exp:
        print("Failed to handle is srt and is prod variables: " + str(exp))
        return
    return True

def delete_file_if_exists_and_create_new_one(file_path):
    # Delete file if exists
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except OSError as e:
        # If it fails, inform the user.
        print("Error: %s - %s." % (e.filename, e.strerror))
        return False
    # Create new file
    try:
        with open(file_path, 'w'): pass
    except Exception:
        print("Error: Failed to create new file:" + str(file_path))
        return False
    return True

