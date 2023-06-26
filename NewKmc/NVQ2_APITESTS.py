import requests
import sys, os
import pytest

headers = {
    'Content-Type': 'application/json',
}

params = (
    ('filter-id', '2271913'),
)

os.environ['FILTER_ID'] = "2271913"


def main():
    pt_result = pt_test_set_api()
    isprod = set_env_type(pt_result['data'])

    if 'display-id' in pt_result['data'][0]['attributes']:

        displayId = str(pt_result['data'][0]['attributes']['display-id'])
        host = str(pt_result["data"][0]["attributes"]["custom-fields"]["---f-50309"])

        theFile = '/home/ubuntu/jenkins/workspace/Host.txt'
        if os.path.exists(theFile):
            os.remove(theFile)

        f = open(theFile, "w")
        f.write("[env]\nPracti_TestSet_ID:" + displayId + "\nisProd:" + isprod)
        f.close()

        print("******************* DONE WITH CREATING THE ENV INI FILE  to: " + str(theFile) + " *************")

        pytest.main(
            ['/home/ubuntu/jenkins/workspace/BE_APITESTS_NVQ2/NewKmc/Practitest/test_change_Practitest_set_Status_API.py', '-s'])

        sys.exit(0)
    else:
        sys.exit(1)


def pt_test_set_api():
    response = requests.get('https://api.practitest.com/api/v2/projects/4586/sets.json', headers=headers, params=params,
                            auth=('adi.miller@kaltura.com', 'deee12e1d8746561e1815d0430814c82c9dbb57d'))
    pt_res = response.json()
    return pt_res


def set_env_type(pt_result):
    pt_env = pt_result[0]['attributes']['custom-fields']['---f-43697']

    if pt_env == '["Testing"]':
        isProd = 'false'
        print('testing')
    else:
        isProd = True
        isProd = 'true'
        print('production')

    return isProd

main()