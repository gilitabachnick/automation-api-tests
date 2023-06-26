import os
import sys
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
import pytest
import Practitest
import Config
import reporter
import external_funcs

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
deployment_instructions_page_id = os.getenv('page_id')
testStatus = True


#===========================================================================
# Description :   Verify BE components version 
#
# Test scenario:  Get updated versions from current deployment instructions Confluence page, 
# then components versions from server and server_saas_config git repos
#                          
# Verifications:  Compare versions
#
#===========================================================================

class TestClass:    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        global testStatus
        try:
            self.practitest = Practitest.practitest('4586')
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            
            self.logi = reporter.Reporter()
            self.logi.initMsg('Verify BE components version')          

            
            GitToken = inifile.RetIniVal('Environment', 'iliaGitToken')
            JiraToken = inifile.RetIniVal('Environment', 'iliaJiraToken')

            #Get Git config files
            self.logi.appendMsg('Getting config files from Git...')            
            mygit=external_funcs.external_funcs()
            saas = mygit.get_git_file_contents(GitToken, 'server-saas-config', 'configurations/local.ini')
            base = mygit.get_git_file_contents(GitToken, 'server', 'configurations/base.ini')            
            self.config = saas + base
            #Get Confluence page
            self.logi.appendMsg('Getting Deployment instructions page...')
            myconfluence = external_funcs.external_funcs()
            soup = myconfluence.get_confluence_page(deployment_instructions_page_id, 'ilia.vitlin@kaltura.com', JiraToken)
            #soup = myconfluence.get_confluence_page('1238368575', 'ilia.vitlin@kaltura.com', JiraToken)
            table = soup.find("table")
            rows = table.findAll('tr')
            self.product_arr = []
            self.git_prod_arr = []
            self.versions_arr = []
            
            #Dictionary to convert between Git and Deployment instructions product names 
            conversion = {
               'Reach Components' : 'kmcng_reach_version',
               'KEA' : 'kmcng_kea_version',
               'KMC NG' : 'kmcng_version',
               'New Analytics' : 'kmc_analytics_version',
               'Player v2' : 'html5_version',
               'Live dashboard in KMC' : 'live_dashboard_version'          
            }
            #Find all updated components versions in Confluence and fill them into array
            self.logi.appendMsg('Filling versions into array...')
            for tr in rows:
                product = tr.findAll('th')
                cols = tr.findAll('td')
                for td in cols:
                    if td.find(text='Yes'):              
                        if (len(product) > 1):
                            if product[1].text in conversion:
                                self.product_arr.append(product[1].text)
                                self.git_prod_arr.append(conversion[product[1].text])
                                self.versions_arr.append(cols[0].text)
                        else:
                            if product[0].text in conversion:
                                self.product_arr.append(product[0].text)                    
                                self.git_prod_arr.append(conversion[product[0].text])
                                self.versions_arr.append(cols[0].text) 
                        break
        except:
            pass        
    #===========================================================================
    # test Verify BE components version 
    #===========================================================================    
    def test_1540_Verify_BE_components(self):
        global testStatus       
        try:
            #Compare versions
            self.logi.appendMsg('Comparing versions...')
            for line in self.config.splitlines():
                for i in range(len(self.git_prod_arr)):
                    if self.git_prod_arr[i] in line:
                        self.actual_version = line.split(' = ')
                        if self.actual_version[1] ==  self.versions_arr[i]:
                            print((self.product_arr[i] + ' deployment instructions version ' + self.versions_arr[i] + ' matches Git version ' + self.actual_version[1]))
                        else:
                            print((self.product_arr[i] + ' deployment instructions version ' + self.versions_arr[i] + ' >>>DOES NOT<<< match Git version ' + self.actual_version[1] + '!'))
                            testStatus=False
                        break
        except:
            testStatus=False
            self.logi.appendMsg('General error, test failed!')
            pass
            
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    def teardown_class(self):
        global testStatus
        
        print('#########')
        print('tear down')
        print('#########')
  
        if testStatus == False:
            #self.logi.reportTest('fail')
            self.logi.appendMsg('Found versions mismatch, test failed!')
            self.practitest.post(Practi_TestSet_ID, '1540','1') 
            assert False
        else:
            #self.logi.reportTest('pass')
            self.logi.appendMsg('All versions match, test pass!')
            self.practitest.post(Practi_TestSet_ID, '1540','0') 
            assert True       
              
    pytest.main(args=['test_1540_Verify_BE_components.py','-s'])
