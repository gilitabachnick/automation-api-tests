from retrying import retry
import requests
import sys, os
import pytest

print("***************** 1 ************")
headers = {
    'Content-Type': 'application/json',
}

params = (
    ('filter-id', '1820582'),
)

os.environ['FILTER_ID'] = "1820582"
os.environ['PYTHONUNBUFFERED'] = "1"


def main():
    print("***************** 2 ************")
    pt_result = pt_test_set_api()
    isprod = set_env_type(pt_result['data'])

    if 'display-id' in pt_result['data'][0]['attributes']:
        print("***************** 3 ************")
        os.environ.setdefault("Practi_TestSet_ID", str(pt_result['data'][0]['attributes']['display-id']))
        displayId = str(pt_result['data'][0]['attributes']['display-id'])
        host = str(pt_result["data"][0]["attributes"]["custom-fields"]["---f-108627"])
        print(" --------- DISPLAY ID= " + displayId)
        print(" --------- ISPROD = " + isprod)
        print("***************** 4 ************")

    theFile = r'C:\jenkins\workspace\Host5.txt'

    if os.path.exists(theFile):
        os.remove(theFile)

    try:
        f = open(theFile, "w")
        f.write("[env]\nPracti_TestSet_ID:" + displayId + "\nisProd:" + isprod)
        f.close()

        print("***************** 5 ************")

        print("******************* DONE WITH CREATING THE ENV INI FILE  to: " + str(theFile) + " *************")
        sys.exit(0)
    except Exception as Exp:
        print("could not create the host file Host5.txt due to the exception: " + str(Exp))
        sys.exit(1)


@retry(wait_exponential_multiplier=10000, wait_exponential_max=60000)
def pt_test_set_api():
    print('Going to send GET request')
    response = requests.get('https://api.practitest.com/api/v2/projects/20271/sets.json', headers=headers,
                            params=params,
                            auth=('adi.miller@kaltura.com', 'deee12e1d8746561e1815d0430814c82c9dbb57d'))
    print('Got GET response')
    pt_res = response.json()
    response.close()
    return pt_res


def set_env_type(pt_result):
    pt_env = pt_result[0]['attributes']['custom-fields']['---f-105927']

    if pt_env == "Testing":
        isProd = 'false'
        print('testing')
    else:
        isProd = True
        isProd = 'true'
        print(str(pt_env))
        print('production')

    return isProd


main()