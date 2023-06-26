import requests
import sys, os
import pytest

print("***************** 1 ************")

filterId = "1789485"
hostField = "---f-58877"
pthToChangeSetStatus = "C:\\Jenkins\\workspace\\BE-ReachTests\\NewKmc\\Practitest\\test_change_Practitest_set_Status_Reach.py"
projectId = '1328'
envField = "---f-30761"

headers = {
    'Content-Type': 'application/json',
}

params = (
    ('filter-id', filterId),
)

os.environ['FILTER_ID'] = filterId


def main():
    print("***************** 2 ************")
    pt_result = pt_test_set_api()
    isprod = set_env_type(pt_result['data'])

    if 'display-id' in pt_result['data'][0]['attributes']:
        print("***************** 3 ************")
        os.environ.setdefault("Practi_TestSet_ID", str(pt_result['data'][0]['attributes']['display-id']))
        displayId = str(pt_result['data'][0]['attributes']['display-id'])
        host = str(pt_result["data"][0]["attributes"]["custom-fields"][hostField])

        print("***************** 4 ************")

    theFile = r'C:\jenkins\workspace\Host.txt'
    if os.path.exists(theFile):
        os.remove(theFile)

    f = open(theFile, "w")
    f.write("[env]\nPracti_TestSet_ID:" + displayId + "\nisProd:" + isprod)
    f.close()

    print("***************** 5 ************")

    print("******************* DONE WITH CREATING THE ENV INI FILE  to: " + str(theFile) + " *************")
    try:
        pytest.main(
            [pthToChangeSetStatus, '-s'])

        sys.exit(0)
    except Exception as Exp:
        print(Exp)
        return

def pt_test_set_api():
    response = requests.get('https://api.practitest.com/api/v2/projects/' + projectId + '/sets.json', headers=headers,
                            params=params,
                            auth=('adi.miller@kaltura.com', 'deee12e1d8746561e1815d0430814c82c9dbb57d'))
    pt_res = response.json()
    return pt_res


def set_env_type(pt_result):
    pt_env = pt_result[0]['attributes']['custom-fields'][envField]

    if pt_env.find("Testing") >= 0:
        isProd = 'false'
        print('testing')
    else:
        isProd = True
        isProd = 'true'
        print(str(pt_env))
        print('production')

    return isProd

main()