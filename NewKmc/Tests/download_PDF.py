import os
import sys
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import reportFuncs
import MySelenium
import KmcBasicFuncs
import time
from KalturaClient.Plugins.Core import *

dcUrl = os.environ['dcUrl']
partner = os.environ['partner']
secret = os.environ['secret']
user = os.environ['user']


# dcUrl = 'https://www.kaltura.com/'
# partner = '4352233'
# secret = 'fbf80440d364abbdd844e71412d320f0'
# user = 'tom.cohen@kaltura.com'
downloadPath = "c:\\temp\\PDF\\"
zip = "c:\\temp\\" + partner + '.zip'

funcs = reportFuncs.reportFuncs()
kmcFuncs = KmcBasicFuncs.basicFuncs()

MyClient = funcs.openSession(dcUrl, secret, user, 2, partner, 'disableentitlement')  # Two variables returned, client and KS

if isinstance(MyClient, tuple):
    print('Got valid KS... ')
else:
    print("FAIL - Couldn't get valid KS, exiting")
    exit(1)
MyFilter = KalturaLiveEntryFilter()
MyFilter.orderBy = KalturaMediaEntryOrderBy.PLAYS_DESC

MyPager = KalturaFilterPager()
MyPager.pageSize = 500
MyPager.pageIndex = 1

EntryList = funcs.listEntries(MyClient[0], MyPager, MyFilter)
listLen = str(len(EntryList.objects))
if isinstance(EntryList.objects, list):
    print('Got valid list of ' + listLen + ' entries... ')
else:
    print('FAIL - No list of entries, exiting...')
    exit(1)
entriesIds = []
for obj in EntryList.objects:
    entriesIds.append(obj.id)  # Create list of entryIds in


# Log in to KMC with KS
Wdobj = MySelenium.seleniumWebDrive()
Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")
URL = 'https://kmc.kaltura.com/index.php/kmcng/actions/login-by-ks/' + MyClient[1]

mainPage = funcs.loginKmcWithKs(Wdobj, Wd, URL, kmcFuncs)
if not mainPage:
    print("FAIL - Couldn't login, exiting!")
    exit(1)
else:
    print('Logged in successfully!')

time.sleep(5)

entryIndex = 1
for entry in entriesIds:
    print('Downloading entry ' + entry + ', ' + str(entryIndex) + ' of ' + listLen + ' ...', end="")
    pathPrefix = downloadPath + entry + '.pdf'
    rc = funcs.downloadPdf(Wd, kmcFuncs, entry, pathPrefix)
    entryIndex = entryIndex + 1

Wd.quit()
print('All reports downloaded!')
print('Compressing all documents to single zip file ' + zip + '...', end="")
Zip = funcs.createZip(zip, downloadPath)
if Zip:
    print(' Done!')
else:
    print('FAIL - Could not compress')
print('Bye!')

