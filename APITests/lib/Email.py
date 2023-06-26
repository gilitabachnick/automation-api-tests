import smtplib
import os
import Config
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
#from email.utils import COMMASPACE, formatdate

import yagmail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

USER = inifile.RetIniVal('Email', 'USER')
PWD = inifile.RetIniVal('Email', 'PWD')
APPPass = inifile.RetIniVal('Email', 'APPPass')



class email():
    def __init__(self, logfile, iniSecSendTo,  logMessages=None):
        self.logfile = logfile
        self.logMessages = logMessages
        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
        inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        try:
            if iniSecSendTo.find(";") > 0:
                self.sendto = iniSecSendTo
            else:
                self.sendto = inifile.RetIniVal(iniSecSendTo, 'sendto')
        except:
            self.sendto = None

        self.smtpserver = 'smtp.gmail.com'
        if self.sendto[-1]==";":
            self.sendto = self.sendto[:-1]






    def sendEmailFailtest(self, testname):

        sender = 'autokalt@gmail.com'
        subject = 'Test- ' + testname + ' FAIL'

        # msg = MIMEMultipart()
        # msg['Subject'] = subject
        # msg['From'] = sender
        # msg['To'] = self.sendto
        # body = self.logMessages
        #
        # msg.attach(MIMEText(body, 'plain'))
        # filename = str(self.logfile.name).split("\\")[-1]
        attachment = open(self.logfile.name, "rb")

        content = ['mail body content', 'pytest.ini', 'test.png']

        with yagmail.SMTP(USER, APPPass) as yag:
            try:
                yag.send(to=self.sendto, subject=subject, contents=self.logMessages, attachments=attachment)
            except Exception as Exp:
                print(Exp)
            print('Sent email successfully')


    def sendEmailAddStitching(self, text, files):

        msg = MIMEMultipart()
        msg['From'] = 'kaltura.gen@kaltura.com'
        msg['To'] = 'adi.miller@kaltura.com;limor.bercovici@kaltura.com'

        # msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Problem in test'

        msg.attach(MIMEText(text))
        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                msg.attach(part)
        conn = smtplib.SMTP(self.smtpserver, 587)
        conn.starttls()
        user, password = (USER, PWD)
        conn.login(user, password)

        try:
            conn.sendmail(msg['From'], ['adi.miller@kaltura.com', 'moran.cohen@kaltura.com'], msg.as_string())
        finally:
            conn.quit()

            # mailing list should be sent with ; between each recipient

    # startStop - send 'start' or 'finish'
    def sendEmailStartFinTest(self, testName, startFinish, mailinglist, text=None):

        smtp = smtplib.SMTP(self.smtpserver, 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo
        smtp.login(USER, PWD)
        sender = 'kaltura.gen@kaltura.com'
        subject = 'Test- ' + testName + ' ' + startFinish

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        # msg['To'] = COMMASPACE.join(mailinglist)
        msg['Content-Type'] = 'text/plain'
        msg.attach(MIMEText(text))

        try:
            smtp.sendmail(sender, mailinglist, msg.as_string())
        except:
            print('Mail was not sent check the smtp password correctness')

        smtp.close()