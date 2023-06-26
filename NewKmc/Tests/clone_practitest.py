import os
import sys
import json

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)
import Practitest
import Config

print('Initializing and loading constants...')

# KmcVersion = 'v7.5.1'
# Analytics_Version = 'v3.0.0'
# BeVersion = '18.7.0'
# ReachBuild = '5.107.80'
# Environment = 'testing'

KmcVersion = os.getenv('kmc')
Analytics_Version = os.getenv('analytics')
BeVersion = os.getenv('be')
ReachBuild = os.getenv('reach')
Environment = os.getenv('env')

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
inifile = Config.ConfigFile(os.path.join(pth, 'PtParams.ini'))
if Environment == 'testing':
    section = 'Regression'
else:
    section = 'Post-Production'

ComposedMessage = ["Good morning! Here are links for today's " + section + ":", "Auto:"]

KmcTestNames = ['API tests - Automation ' + section + ' - ' + KmcVersion + ' + ' + BeVersion,
                'Remote PC1 - Automation ' + section + '- ' + KmcVersion + ' + BE ' + BeVersion,
                'Remote PC2 - Automation ' + section + ' - ' + KmcVersion + ' + BE ' + BeVersion,
                'Remote PC3 - Automation ' + section + ' - ' + KmcVersion + ' + BE ' + BeVersion,
                'Analytics ' + Analytics_Version + ' + BE ' + BeVersion + ' - ' + section]
KmcTestsToClone = inifile.RetIniVal(section, 'KMC_TESTS_TO_CLONE').split(',')

ManualTestNames = ['Manual ' + section + ' - ' + BeVersion,
                   'eSearch Automated ' + section + ' - ' + BeVersion]
ManualTestsToClone = inifile.RetIniVal(section, 'MANUAL_TESTS_TO_CLONE').split(',')

ReachTestName = 'Automation - Reach ' + section + ' version ' + ReachBuild + ' |API ' + BeVersion
ReachTest = inifile.RetIniVal(section, 'REACH_TEST_TO_CLONE')

AnalyticsField = inifile.RetIniVal('CustomFields', 'ANALYTICS_CUSTOM_FIELD')
AnalyticsFieldId = inifile.RetIniVal('CustomFields', 'ANALYTICS_FIELD_ID')
BeVersionField = inifile.RetIniVal('CustomFields', 'BE_CUSTOM_FIELD')
BeVersionFieldId = inifile.RetIniVal('CustomFields', 'BE_VERSION_FIELD_ID')
ManualKmcField = inifile.RetIniVal('CustomFields', 'MANUAL_KMC_CUSTOM_FIELD')
ManualKmcFieldId = inifile.RetIniVal('CustomFields', 'MANUAL_KMC_FIELD_VERSION_ID')
ReachBeField = inifile.RetIniVal('CustomFields', 'REACH_BE_CUSTOM_FIELD')
ReachBeFieldId = inifile.RetIniVal('CustomFields', 'REACH_BE_CUSTOM_FIELD_ID')

KmcPtProject = inifile.RetIniVal('Projects', 'KMC_PT_PROJECT')
KmcPt = Practitest.practitest(KmcPtProject)
ReachPtProject = inifile.RetIniVal('Projects', 'REACH_PT_PROJECT')
ReachPt = Practitest.practitest(ReachPtProject)
ManualPtProject = inifile.RetIniVal('Projects', 'MANUAL_PT_PROJECT')
ManualPt = Practitest.practitest(ManualPtProject)

print('Checking if necessary custom fields values present, adding them if needed...')
try:
    BeValueUpdate = KmcPt.addCustomFieldValue(KmcPtProject, BeVersionField, BeVersion)
    if BeValueUpdate[1] == 'pass':
        print('BE Version "' + BeVersion + '" exists, no need to add')
    elif BeValueUpdate[1] == 'update':
        print('BE Version "' + BeVersion + '" added to custom field values')
    else:
        print('Failed to update BE versions!')

    AnalyticsValueUpdate = KmcPt.addCustomFieldValue(KmcPtProject, AnalyticsField, Analytics_Version)
    if AnalyticsValueUpdate[1] == 'pass':
        print('Analytics Version "' + Analytics_Version + '" exists, no need to add')
    elif AnalyticsValueUpdate[1] == 'update':
        print('Analytics Version "' + Analytics_Version + '" added to custom field values')
    else:
        print('Failed to update Analytics versions!')

    ReachBeValueUpdate = ReachPt.addCustomFieldValue(ReachPtProject, ReachBeField, BeVersion)
    if ReachBeValueUpdate[1] == 'pass':
        print('Reach BE Version "' + BeVersion + '" exists, no need to add')
    elif ReachBeValueUpdate[1] == 'update':
        print('Reach BE Version "' + BeVersion + '" added to custom field values')
    else:
        print('Failed to update Reach BE versions!')
except Exception as Exp:
    print('Error updating field:' + str(Exp))
    raise

print('Going to clone KMC and API tests for automated ' + section + '...')
for test, name in zip(KmcTestsToClone, KmcTestNames):
    url = "https://api.practitest.com/api/v2/projects/" + KmcPtProject + "/sets/" + test + "/clone.json"
    data = json.dumps({"data": {"type": "sets", "attributes": {
        "name": name, "version": KmcVersion,
        "custom-fields": {AnalyticsFieldId: Analytics_Version, BeVersionFieldId: BeVersion}}}})

    CloneResult = KmcPt.cloneAutomationTestSet(url, data)
    if str(CloneResult[0]) != '200':
        print("Error in test " + name + ": " + str(CloneResult))
    else:
        print('Success - cloned "' + name + '"')
        testUrl = "https://prod.practitest.com/p/" + KmcPtProject + "/sets/" + CloneResult[1] + "/edit"
        if "Analytics" in name:
            ComposedMessage.append('Analytics:')
        ComposedMessage.append(testUrl)

print('Going to clone Manual and eSearch tests for ' + section + '...')
ComposedMessage.append('Manual:')

for test, name in zip(ManualTestsToClone, ManualTestNames):
    url = "https://api.practitest.com/api/v2/projects/" + ManualPtProject + "/sets/" + test + "/clone.json"
    data = json.dumps({"data": {"type": "sets", "attributes": {
        "name": name, "version": BeVersion,
        "custom-fields": {ManualKmcFieldId: KmcVersion}}}})
    CloneResult = ManualPt.cloneAutomationTestSet(url, data)
    if str(CloneResult[0]) != '200':
        print("Error in test " + name + ": " + str(CloneResult))
    else:
        print('Success - cloned "' + name + '"')
        testUrl = "https://prod.practitest.com/p/" + ManualPtProject + "/sets/" + CloneResult[1] + "/edit"
        if "eSearch" in name:
            ComposedMessage.append('eSearch:')
        ComposedMessage.append(testUrl)

print('Going to clone Reach tests for ' + section + '...')
ComposedMessage.append('Reach:')

url = "https://api.practitest.com/api/v2/projects/" + ReachPtProject + "/sets/" + ReachTest + "/clone.json"
data = json.dumps({"data": {"type": "sets", "attributes": {
    "name": ReachTestName, "custom-fields": {ReachBeFieldId: ReachBuild}}}})
CloneResult = ReachPt.cloneAutomationTestSet(url, data)
if str(CloneResult[0]) != '200':
    print("Error in test " + ReachTestName + ": " + str(CloneResult))
else:
    print('Success - cloned "' + ReachTestName + '"')
    testUrl = "https://prod.practitest.com/p/" + ReachPtProject + "/sets/" + CloneResult[1] + "/edit"
    ComposedMessage.append(testUrl)

ComposedMessage.append(" ")
ComposedMessage.append("I'll update when to start")
print(*ComposedMessage, sep="\n")
