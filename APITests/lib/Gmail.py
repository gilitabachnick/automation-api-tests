import email
import poplib
import Config
import os
import yagmail

class gmail():
    
    def __init__(self):
        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
        inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        self.mailbox = poplib.POP3_SSL('pop.gmail.com')
        self.Emailuser = inifile.RetIniVal('Email', 'USER')
        self.mailbox.user(self.Emailuser)
        APPPass = inifile.RetIniVal('Email', 'APPPass')
        self.mailbox.pass_(APPPass)
        self.pwd = inifile.RetIniVal('Email', 'PWD')




        
    # return the first mail 
    def retTopemail(self):
        try:
            emailCont = ''
            for i in self.mailbox.retr(1)[1]:
                msg = email.message_from_string(str(i))
                emailCont = emailCont + str(msg.get_payload())
            result = emailCont
        except:
            result= False
            
        return result

    
    # return all mailbox content    
    def retMailboxContent(self):
        numMessages = len(self.mailbox.list()[1])
        
        if numMessages != 0:
            try:
                for i in range(numMessages):
                    result = ''
                    for j in self.mailbox.retr(i+1)[1]:
                        msg = email.message_from_string(str(j))
                        result = result + str(msg.get_payload())
                           
            except Exception as exp:
                print(('exception is: ' + str(exp)))
                result= False    
        else:
            result = False
            
        return result
    
    #inds send x-y example:  deleteEmail(1-3)   
    def deleteEmail(self,inds=None):
        numMessages = len(self.mailbox.list()[1])
        if inds != None:
            for i in range(inds.split('-')[0],inds.split('-')[1]):
                self.mailbox.dele(i+1)
        else:
            for i in range(numMessages):
                self.mailbox.dele(i+1)
        self.mailbox.quit()
    # Ilia Vitlin
    # This function fetches first message using IMAP from Gmail inbox with hardcoded credentials and
    # returns its decoded body
    def fetchTopEmailBody(self):
        import imaplib
        username = self.Emailuser
        password = self.pwd
        try:
            # create an IMAP4 class with SSL
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            # authenticate
            imap.login(username, password)

            status, messages = imap.select("INBOX")
            res, msg = imap.fetch(str(1), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
            imap.close()
            imap.logout()
            if not isinstance(msg, list):
                body = msg.get_payload(decode=True).decode()
            else:
                return False
        except Exception as EXP:
            print(EXP)
            return False
        else:
            return body
    # Ilia Vitlin
    # This function looks for a string in message body and if found, returns URL in message, if not found - return False
    def searchUrlInMessage(self, msgEmail , searchString):
        # findall() has been used
        # with valid conditions for urls in string
        import re
        if msgEmail.find(searchString):
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            url = re.findall(regex, msgEmail)
            return [x[0] for x in url]
        else:
            return False
