from KalturaClient import *
import time
import DOM
import pywinauto
import zipfile
import os

class reportFuncs:
    def openSession(self, url, secret, user, type, partner, privilige):
        try:
            config = KalturaConfiguration(partner)
            config.serviceUrl = url
            client = KalturaClient(config)
            ks = client.generateSession(secret, user, type, partner, privileges=privilige)
            client.setKs(ks)
        except Exception as Exp:
            print(Exp)
            return Exp
        return client, ks.decode()

    def listEntries(self, client, pager, filter):
        try:
            EntryList = client.liveStream.list(filter, pager)
        except Exception as Exp:
            print(Exp)
            return Exp
        return EntryList
    def loginKmcWithKs(self, wdobj, webdriver, url, kmcFuncs):
        try:
            webdriver.get(url)
            time.sleep(10)
            rc = kmcFuncs.selectOneOfInvisibleSameObjects(webdriver, DOM.MSG_CLOSE)  # Close welcome screen
            rc.click()
        except Exception as Exp:
            print(Exp)
            return Exp
        if wdobj.Sync(webdriver, DOM.ENTRIES_TAB):
            return True
        else:
            return False

    def backToEntries(self, webdrive):
        webdrive.find_element_by_xpath("//button[@icon='kIconarrow_backward']").click()  # Back to entry
        time.sleep(1)
        webdrive.find_element_by_xpath(DOM.ENTRIES_TAB).click()  # Back to entries list

    def downloadPdf(self, webdrive, kmcfuncs, entryId, filePath):
        try:
            Entry = kmcfuncs.selectEntryfromtbl(webdrive, entryId)
            webdrive.find_element_by_xpath("//span[text()='View Analytics']").click()
            time.sleep(10)
            iframe = webdrive.find_element_by_xpath("//iframe")
            webdrive.switch_to.frame(iframe)
            try:
                webdrive.find_element_by_xpath("//span[text()='Download Report']").click()
            except Exception as Exp:
                print(' Entry does not have Analytics, proceeding to the next one...')
                self.backToEntries(webdrive)
                return
            time.sleep(10)
            app = pywinauto.application.Application()  # Open application handler
            app = app.connect(title=u'Save As', class_name='#32770')  # Focus on window with title "Save As"
            time.sleep(1)
            app[' Save As ']['Edit1'].set_edit_text(filePath)  # Send file path
            time.sleep(1)
            app[' Save As ']['Button1'].click_input()  # Click "Save" button
            time.sleep(1)
            print(' Done!')
            self.backToEntries(webdrive)
        except Exception as Exp:
            print(Exp)
            return False
        return True

    def createZip(self, zip, folder):
        try:
            zf = zipfile.ZipFile(zip, "w")
            for dirname, subdirs, files in os.walk(folder):
                zf.write(dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename))
        except Exception as Exp:
            print(Exp)
            return False
        return True
