'''
Created on Jan 02, 2019

@author: adi.millman
'''

import time

import DOM
import KmcBasicFuncs


class adminFuncs:
    

    def __init__(self, webdrvr, logi):
        
        self.Wd = webdrvr
        self.logi = logi
        self.basicFuncs = KmcBasicFuncs.basicFuncs()

    ###        
    # Function 'addUser'  - This function will add a *new KMC user* via Administration section.
    # For test that adds a user that already exists in Kaltura system - use  isRegistered=True
    ###
    
    def addUser (self,userEmail,firstName,lastName,userID,currentUsersNum,isRegistered=False):
                
        
        self.logi.appendMsg("INFO - Starting Add User function. Current Users Number is: "+ currentUsersNum)
        self.logi.appendMsg("INFO - Going to click 'Add User'")
        time.sleep(2)
        
        self.logi.appendMsg("INFO - Going to fill in User's eMail, first and last names")
        self.inputUserDetails(userEmail, firstName, lastName, userID)

        time.sleep(5)
            
        self.logi.appendMsg("INFO - Going to click 'Save' button")
        self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()
        time.sleep(10)

        if isRegistered == True:
            self.logi.appendMsg("INFO - Going to approve the 'User Already Exists' alert dialog")
            userExistsAlert = self.Wd.find_element_by_xpath(DOM.ADD_EXISTING_USER_ALERT_TITLE)
            if userExistsAlert.text == 'User already exists': 
                self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_YES).click()
                self.logi.appendMsg("PASS - 'User Already Exists' alert was approved")
            else:
                self.logi.appendMsg("FAIL - expected alert did not pop for approval, or the given login Email address is already listed in this account and cannot be added")
                return False
        time.sleep(5)

        # Verifying the new user has been added

        self.logi.appendMsg("INFO - Going to verify the users' count in the top banner increased after adding a new user, Current Users Number was: "+ currentUsersNum + " and after addition it should be: "+ str(int(currentUsersNum)+1))
        availableUsersMsg = self.Wd.find_element_by_xpath(DOM.ADMIN_MORE_USERS_MSG).text
        time.sleep(3)
        newCurrentUsersNum = (availableUsersMsg.split("\n")[1].split(" "))[0]
        self.logi.appendMsg("INFO - New Current Users Number is: "+ newCurrentUsersNum)
        
        if (int(newCurrentUsersNum) == (int(currentUsersNum) + 1)):
            self.logi.appendMsg("PASS - The number of users increased as Expected")
            
            self.logi.appendMsg("INFO - Going to verify the test user " +firstName +" "+ lastName+" is in the Users list")
            usersRows = len(self.Wd.find_elements_by_xpath(DOM.ADMIN_USERS_ROW_NAME))
           
            
            # identify the test user in the Users list
           
            for u in range(usersRows):
                userInRow = self.basicFuncs.retTblRowName(self.Wd, u+1, tableItem="user")
                if userInRow.find(firstName)>=0 and userInRow.find(lastName)>=0:
                    self.logi.appendMsg("PASS - Test user " + firstName + " " + lastName + " was added to Users list")
                    return True
                else:
                    continue
                
           
            self.logi.appendMsg("FAIL - Test user details were not found in Users list")
            return False

        else:
            self.logi.appendMsg("FAIL - current users count did not increase after trying to add user")
            return False
        

    ###
    # Function 'deleteUser'  - This function will delete a KMC user from the Users List. Identifying the row in which the given full name is listed and deleting this row    
    ###
    
    def deleteUser (self,userEmail,firstName,lastName):
        
        self.Wd.find_element_by_xpath(DOM.ADMIN_MAIN).click()
        time.sleep(2)
        
        # identify the test user in the Users list
        usersNamesRowsNum = len(self.Wd.find_elements_by_xpath(DOM.ADMIN_USERS_ROW_NAME))
       
        for i in range(usersNamesRowsNum):
            userNameInRow = self.basicFuncs.retTblRowName(self.Wd, i+1, "user")
            if userNameInRow.find(firstName)>=0 and userNameInRow.find(lastName)>=0:
                # delete user
                try:
                    rc = self.basicFuncs.tblSelectAction(self.Wd, i+1, "Delete","user")
                    time.sleep(2)
                    if not rc:
                        self.logi.appendMsg("FAIL - Could not select delete action for the item in Users list")         
                        return False
                    
                    self.Wd.find_element_by_xpath(DOM.GLOBAL_YES_BUTTON).click()
                    time.sleep(3)
                    self.logi.appendMsg("PASS - Test user was deleted successfully")                                 
                    return True
                
                except:
                    self.logi.appendMsg("FAIL - Failed to delete Test User")
                    return False  
            else:                
                continue
        
            self.logi.appendMsg("INFO - The test user is not listed as an item in Users list")
            return False

    # verify if the user id appears on the user table list
    def verify_user_id(self, user_id):
        try:
            info_table = self.Wd.find_elements_by_xpath(DOM.ADMIN_USER_INFO.replace('TEXTTOREPLACE',user_id))
        except:
            self.logi.appendMsg("FAIL - Failed to find user id")
            return False

        if len(info_table) == 2:
            self.logi.appendMsg("INFO - The test user id is the same as the email address")
            return True
        else:
            self.logi.appendMsg("INFO - The test user id is not the same as the email address")
            return False

    # Function to edit the user id field
    # user_to_edit = the User Name of the user you want to edit first+last name
    # user_id_text_input = the text to add or replace on the user id 
    # append = to add the text to the end of the string or not
    def edit_user_id(self, user_to_edit, user_id_text_input, append=False, save_changes=True):
        try:
            kUser_action_table = self.Wd.find_elements_by_xpath(DOM.USERS_ROW_ACTIONS)
            kUser_id_table = self.Wd.find_elements_by_xpath(DOM.ADMIN_USERS_ROW_NAME)
            for webElement in range(len(kUser_id_table)):
                webElementText = kUser_id_table[webElement].text
                # check if the given profile name exists in the user profiles list
                if user_to_edit in webElementText:
                    kUser_action_table[webElement].click()
                    time.sleep(1)
                    self.Wd.find_element_by_xpath(DOM.USERS_ROW_ACTION_EDIT).click()


            test_status = False

            time.sleep(5)

            if append:
                self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[3].send_keys(user_id_text_input)
                test_status = True
            else:
                self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[3].clear()
                self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[3].send_keys(user_id_text_input)
                test_status = True

            if save_changes:
                self.Wd.find_element_by_xpath(DOM.GLOBAL_SAVE).click()
                self.Wd.find_element_by_xpath(DOM.POPUP_MESSAGE_OK).click()
                test_status = True
            else:
                self.Wd.find_elements_by_xpath(DOM.UPLOAD_SETTINGS_CLOSE)[-1].click()
                test_status = True

            return test_status
        except:
            self.logi.appendMsg("FAIL - edit user failed")
            return False

    # Function to input user details in add user forum
    def inputUserDetails(self, userEmail='', firstName='', lastName='', userID=''):
        try:
            # Navigate to Administration > Users
            self.logi.appendMsg("INFO - Going to navigate to Administration > Users")
            self.Wd.find_element_by_xpath(DOM.ADMIN_MAIN).click()

            time.sleep(5)

            self.logi.appendMsg("INFO - Going to click 'Add User'")
            try:
                add_user_button = self.Wd.find_element_by_xpath(DOM.USERS_ADD_USER)
                if add_user_button.is_displayed():
                    add_user_button.click()
            except Exception as e:
                print(e)
                self.logi.appendMsg("FAIL - FAILED to click on add user button")
                return False

            self.logi.appendMsg("INFO - going to verify user input fields")
            rows = self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_ROW)

            for row in rows:
                labelDetail = row.find_element_by_xpath(DOM.ADD_USER_MODAL_LABEL)
                if labelDetail.text == 'Login Email address':
                    try:
                        self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[0].send_keys(userEmail)
                    except:
                        raise NameError('FAIL - Insert input Login Email address failed')
                elif labelDetail.text == 'First Name':
                    try:
                        self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[1].send_keys(firstName)
                    except:
                        raise NameError('FAIL - Insert input First Name failed')
                elif labelDetail.text == 'Last Name':
                    try:
                        self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[2].send_keys(lastName)
                    except:
                        raise NameError('FAIL - Insert input Last Name failed')
                elif labelDetail.text == 'Publisher User ID':
                    try:
                        self.Wd.find_elements_by_xpath(DOM.ADD_USER_MODAL_INPUT)[3].send_keys(userID)
                    except:
                        raise NameError('FAIL - Insert input Publisher User ID failed')
                else:
                    continue
        except Exception as e:
            self.logi.appendMsg(str(e))
            self.logi.appendMsg("FAIL - Failed to input user's details")
            return False

    # Checks the number of input errors in the add user forum
    # num_of_errors = the number of expected errors to be checked
    def verify_valid_user_info_input(self, input_error_list, num_of_errors=0):
        error_num = 0

        # Loops over the errors in the user input, if xpath is not found moves to the next xpath
        # If found error counter is raised by 1
        for xpath_error in input_error_list:
            try:
                xpath = self.Wd.find_element_by_xpath(xpath_error)

                if xpath is not None:
                    error_num += 1
            except:
                continue

        try:
            if num_of_errors == error_num:
                self.logi.appendMsg("INFO - Number of input errors match")
                closeButton = self.basicFuncs.selectOneOfInvisibleSameObjects(self.Wd, DOM.UPLOAD_SETTINGS_CLOSE)
                closeButton.click()
                return True
        except:
            self.logi.appendMsg("INFO - Number of errors dose not match")
            return False

    ###
    # changeAccount  - This function will get to the Change Account dialog using the logged-in-user name
    # and will switch to a selected account (targetAccountName) (AKA - "Name of Publisher/Company")
    ###
    def change_account (self, target_account):
        self.logi.appendMsg("INFO - Going to switch to "+ target_account + "'s account")
        self.Wd.find_element_by_xpath(DOM.ACCOUNT_USERNAME).click()
        self.Wd.find_element_by_xpath(DOM.CHANGE_ACCOUNT_BUTTON).click()
        self.Wd.find_element_by_xpath(DOM.CHANGE_ACCOUNT_DIALOG_LABEL.replace("TEXTTOREPLACE", target_account)).click()
        time.sleep(1)
        self.logi.appendMsg( "INFO - Click 'Continue' if enabled, or close if target account is already selected ")
        continue_button = self.Wd.find_element_by_xpath(DOM.CHANGE_ACCOUNT_DIALOG_CONTINUE)
        try:
            if continue_button.is_enabled():
                continue_button.click()
                time.sleep(5)
                self.logi.appendMsg("INFO - Request switch to " + target_account + " passed successfully")
            else:
                continue_button = self.basicFuncs.selectOneOfInvisibleSameObjects(self.Wd, DOM.UPLOAD_SETTINGS_CLOSE)
                continue_button.click()
                self.logi.appendMsg("INFO - User already logged in account " + target_account + ". No need to switch")
        except:
            self.logi.appendMsg("INFO - User already logged in account " + target_account + ". No need to switch")
            return False


        ##########################################################################
        #########  add verification to the new account is loged in ################
        ##########################################################################