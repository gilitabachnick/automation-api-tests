import os
import sys
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#import random
import Config
import external_funcs
from atlassian import Confluence
from jira import JIRA
from datetime import datetime


# Read configuration
assignee = 'Renan.Bresler, iliav, ellal, moran.cohen,60291f87c5a0430067b966db,61fb372e9c1d520069294f71,62675230d364ae006808d48a'
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
JiraToken = inifile.RetIniVal('Environment', 'iliaJiraToken')
deployment_instructions_page_id = os.getenv('page_id')
product_arr = []
versions_arr = []


###########################################################################
#       Get list of updated components from deployment instructions       #
###########################################################################

# Get Confluence page
print('Pulling deployment instructions page...')
try:
    myconfluence = external_funcs.external_funcs()
    soup = myconfluence.get_confluence_page(deployment_instructions_page_id, 'ilia.vitlin@kaltura.com', JiraToken)
    time = soup.find("time")
    date_time = datetime.strptime(time.attrs['datetime'], '\\"%Y-%m-%d\\"')
    stripped_date = date_time.strftime('%Y-%m-%d')
    macro_date = date_time.strftime('%d %b %Y')
    title_date = date_time.strftime('%B %d, %Y')
    table = soup.find("table")
    rows = table.findAll('tr')

# Find all updated components versions in Confluence and fill them into arrays
    for tr in rows:
        product = tr.findAll('th')
        cols = tr.findAll('td')
        for td in cols:
            if td.find(text='Yes'):              
                if (len(product) > 1):
                         product_arr.append(product[1].text)
                         versions_arr.append(cols[0].text)
                else:
                         product_arr.append(product[0].text)                    
                         versions_arr.append(cols[0].text) 
                break
            
    #Creating versions table
    versions_table = '<table><tr><th>Date</th><td><time datetime="'+str(stripped_date)+'" class="date-past">'+str(macro_date)+'</time></td></tr>'
    #Fill versions_table
    for x in range(len(product_arr)):
        versions_table=versions_table+'<tr><th>'+product_arr[x]+'</th><td>'+versions_arr[x]+'</td></tr>'
          
    versions_table=versions_table+'</table>'
    
except Exception as Exp:
    print(Exp)
    exit(1)
print('Built new components table, proceeding to search Jira for last sprint tickets...')
###########################################################################
#       Get list of Jira tickets for current sprint                       #
###########################################################################
try:
#Connect to JIRA
    jira = JIRA(basic_auth=('ilia.vitlin@kaltura.com', JiraToken), options={'server': 'https://kaltura.atlassian.net'})
    
    
    SUP = jira.search_issues('assignee in ('+assignee+') AND project = Support AND status in\
     ("Ready for QA", "Ready for Deployment") ORDER BY assignee DESC', 0, 100,True,'components,assignee',None)
    Story = jira.search_issues('assignee in ('+assignee+') AND type = Story AND status in\
     ("Ready for QA", "Ready for Deployment") ORDER BY assignee DESC', 0, 100,True,'components,assignee',None)
    Misc = jira.search_issues('assignee in ('+assignee+') AND type != Story AND project != Support \
    AND status in ("Ready for QA", "Ready for Deployment") ORDER BY assignee DESC', 0, 100,True,'components,assignee',None)
    
except Exception as Exp:
    print(Exp)
    exit(1)
print('Found tickets, building tickets tables...')
table_header = '<table><tr><th>Product</th><th>JIRA Item</th><th>Executed By</th><th>Test Status</th><th>Comments</th></tr>'
try:
    sup_table = table_header
    for sup in SUP:
        if len(sup.fields.components)!=0:
            component = sup.fields.components[0].name
        else:
            component = 'Other'
        sup_table = sup_table + '<tr><td>'+component+'</td><td><ac:structured-macro ac:name="jira"><ac:parameter ac:name="columns">\
        key,summary,type,created,updated,due,assignee,reporter,priority,status,resolution</ac:parameter><ac:parameter ac:name="key">'+sup.key+'</ac:parameter>\
        </ac:structured-macro></td><td><ac:link><ri:user ri:account-id="'+sup.fields.assignee.accountId+'"/></ac:link></td><td></td><td></td></tr>'
    sup_table = sup_table + '</table>'
    
    story_table = table_header
    for story in Story:
        if len(story.fields.components)!=0:
            component = story.fields.components[0].name
        else:
            component = 'Other'    
        story_table = story_table + '<tr><td>'+component+'</td><td><ac:structured-macro ac:name="jira"><ac:parameter ac:name="columns">\
        key,summary,type,created,updated,due,assignee,reporter,priority,status,resolution</ac:parameter><ac:parameter ac:name="key">'+story.key+'</ac:parameter>\
         </ac:structured-macro></td><td><ac:link><ri:user ri:account-id="'+story.fields.assignee.accountId+'"/></ac:link></td><td></td><td></td></tr>'
    story_table = story_table + '</table>'
    
    misc_table = table_header
    for misc in Misc:
        if len(misc.fields.components)!=0:
            component = misc.fields.components[0].name
        else:
            component = 'Other'
        misc_table = misc_table + '<tr><td>'+component+'</td><td><ac:structured-macro ac:name="jira"><ac:parameter ac:name="columns">\
        key,summary,type,created,updated,due,assignee,reporter,priority,status,resolution</ac:parameter><ac:parameter ac:name="key">'+misc.key+'</ac:parameter>\
        </ac:structured-macro></td><td><ac:link><ri:user ri:account-id="'+misc.fields.assignee.accountId+'"/></ac:link></td><td></td><td></td></tr>'
    misc_table = misc_table + '</table>'   
except Exception as Exp:
    print(Exp)
    exit(1)
print('Composed tables, building final Confluence payload...')
#Assemble full HTML body
try:
    main_body = versions_table
    main_body = main_body + '<h1>1&nbsp;&nbsp; Document purpose:</h1><ul><li>Short review on the release content</li><li>Review the checklist bellow and verify all done</li>\
        <li>Describe in high level which tests have been performed</li><li>Described the bugs\Problems that were found, referring to their priority and severity&nbsp;</li>\
        <li>For each problem, a decision should be taken whether it can be released as known bug</li></ul><br></br><h1>2 &nbsp; New features / Changes in existing functionality:</h1><br></br>'
    main_body = main_body + story_table
    main_body = main_body + '<h1>3&nbsp;&nbsp; Production support tickets verification:</h1>'
    main_body = main_body + sup_table
    main_body = main_body + '<h1>4&nbsp;&nbsp; Other Resolved Issues verification</h1>'
    main_body = main_body + misc_table
except Exception as Exp:
    print(Exp)
    exit(1)
print('Composed payload, creating Confluence page...')
###########################################################################
#                      Create Report in Confluence                        #
###########################################################################
try:
    confluence = Confluence(
        url='https://kaltura.atlassian.net/wiki/',
        username='ilia.vitlin@kaltura.com',
        password=JiraToken)
       
    status = confluence.create_page(
        space='QAC',
        parent_id='16875543',
        title='QA.Core SaaS Deployment Report: '+title_date,
        body=main_body)
       
    new_page_link = status['_links']['base']+status['_links']['webui']
    print('Confluence page created successfully, the link is:')
    print(new_page_link)
except Exception as Exp:
    print(Exp)