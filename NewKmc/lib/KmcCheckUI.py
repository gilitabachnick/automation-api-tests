'''
@author: Erez Bouskila
'''



import time
# TODO: check if builtins is in use


import DOM
import KmcBasicFuncs


class CheckUI:

    def __init__(self, Wd, logi):
        self.Wd = Wd
        self.logi = logi
        self.BasicFuncs = KmcBasicFuncs.basicFuncs()

    # Function that checks the number of pages
    # number_of_pages (int) - the number of expected pages shown in the list
    def verify_pagination_buttons(self, number_of_pages):
        list_of_buttons = [DOM.FIRST_PAGE, DOM.PREV_PAGE, DOM.PAGE_NUMBER, DOM.NEXT_PAGE, DOM.LAST_PAGE, DOM.ROWS_MENU]

        for elem in list_of_buttons:
            try:
                if elem == DOM.PAGE_NUMBER:
                    verify_buttons = self.Wd.find_elements_by_xpath(elem)
                    if len(verify_buttons) == number_of_pages:
                        self.logi.appendMsg("PASS - Number of expected pages found")
                        continue
                else:
                    verify_button = self.Wd.find_element_by_xpath(elem)
                    if verify_button.is_displayed() == True:
                        self.logi.appendMsg("PASS - pagination button is displaying")
                        continue
                    else:
                        self.logi.appendMsg("FAIL - pagination button is NOT displaying")
                        return False
            except:
                self.logi.appendMsg("FAIL - could not find pagination button")

        return True

    # Checks the row menu list items: 25, 50, 100, 250
    def verify_show_rows_menu_items(self):
        try:
            menu_row_button = self.Wd.find_element_by_xpath(DOM.ROWS_MENU)

            try:
                if menu_row_button.is_displayed() == True:
                    menu_row_button.click()
            except:
                self.logi.appendMsg("FAIL - menu row did not open")
                return False

            row_menu_items = self.Wd.find_elements_by_xpath(DOM.MENU_ROW_OPTION)
            if len(row_menu_items) == 4:
                self.logi.appendMsg("PASS - Show row menu has all 4 items")
                return True

        except:
            self.logi.appendMsg("FAIL - menu row did not open / counld not verify menu items")
            return False

    # checks that the navigation buttons are disabled when on first page and last page
    def verify_disabled_page_navigation_buttons(self):
        forward_buttons = [DOM.DISABLED_NEXT_PAGE, DOM.DISABLED_LAST_PAGE]
        backwards_buttons = [DOM.DISABLED_FIRST_PAGE, DOM.DISABLED_PREV_PAGE]

        try:
            # always navigate to entries menu
            self.Wd.find_element_by_xpath(DOM.CONTENT_TAB).click()
            time.sleep(3)

            for backwards_button in backwards_buttons:
                try:
                    button = self.Wd.find_element_by_xpath(backwards_button)
                except:
                    raise NameError('FAIL - backward button not found')
                if button.is_displayed() == True:
                    self.logi.appendMsg("PASS - disabled backwards navigation button is showing")
                    continue
                else:
                    self.logi.appendMsg("FAIL - disabled backwards navigation button is NOT showing")
                    return False

            time.sleep(1)

            self.Wd.find_element_by_xpath(DOM.LAST_PAGE).click()

            time.sleep(1)

            for forward_button in forward_buttons:
                try:
                    button = self.Wd.find_element_by_xpath(forward_button)
                except:
                    raise NameError('FAIL - forward button not found')
                if button.is_displayed() == True:
                    self.logi.appendMsg("PASS - disabled forward navigation button is showing")
                    continue
                else:
                    self.logi.appendMsg("FAIL - disabled forward navigation button is NOT showing")
                    return False
        except Exception as e:
            print(e)
            self.logi.appendMsg("FAIL - disabled navigation button is NOT showing")
            return False

        return True

