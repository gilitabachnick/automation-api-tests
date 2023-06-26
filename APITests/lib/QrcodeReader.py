##########################################################################
# this class meant to create screen shots of video's/ pictures
# contain QR code, read them and compare to expected return 
# value of this QR code
# capture2text: Download should https://sourceforge.net/projects/capture2text/
# path=r'C:\Program Files (x86)\Kaltura\QRCodeDetector\Capture2Text\Capture2Text.exe
###########################################################################

import os
import platform
import time

from pyzbar.pyzbar import decode

try:
    from PIL import Image
    import zbarlight
    
except:
    pass

from PIL import Image, ImageDraw

import subprocess
import datetime
#import imagehash


class QrCodeReader():
    
    def __init__(self,lib=os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','QRtemp')),wbDriver=None, logobj=None):
        self.lib = lib
        self.wbDriver = wbDriver
        self.ImageEditorPath=r'C:\WINDOWS\system32\mspaint.exe'
        self.prevQr = None
        self.currQr = None
        self.prevVal = None
        self.currVal = None
        self.logobj = logobj
        self.VideoStopPlayTime = 0
        self.initVals()
        
    def initVals(self):
        self.prevQr = None
        self.currQr = None
        self.prevVal = None
        self.currVal = None

    def saveScreenShot(self):
        #=======================================================================
        # try:
        #     img = ImageGrab.grab()
        # except Exception as Exp:
        #     print 'THIS IS THE EXCEPTION FPR IMAGE.GRAB- ' + str(Exp)
        # nowtime = datetime.datetime.now()
        # saveas = os.path.join(self.lib,'ScreenShot_' + nowtime.strftime('%d%m%Y_%I%M%S')+'.png')
        # print saveas
        # img.save(saveas)
        #=======================================================================
        
        nowtime = datetime.datetime.now()
        
        saveas = os.path.abspath(os.path.join(self.lib,'ScreenShot_' + str(nowtime.strftime('%d%m%Y_%I%M%S'))+'.png'))
        try:
            self.wbDriver.get_screenshot_as_file(saveas)
            
        except Exception as Exp:
            print(('THIS IS THE EXCEPTION FPR IMAGE.GRAB- ' + str(Exp)))
            
        return saveas
        
    def QrCodeCompare(self,imgPath,expectedVal,QrReader=r'C:\Program Files (x86)\Kaltura\QRCodeDetector\QRCodeDetector.exe'):
        rc = self.retQrVal(imgPath, QrReader)
        if rc == expectedVal:
            return True
        else:
            return False
        
    # def retQrVal(self,imgPath,QrReader=r'C:\Program Files (x86)\Kaltura\QRCodeDetector\QRCodeDetector.exe'):
    #     if platform.system() == 'Windows':
    #         try:
    #
    #             proc = subprocess.Popen(QrReader + ' ' + imgPath, stdout=subprocess.PIPE)
    #             output = proc.stdout.read()
    #             rcArr = output.split('"')
    #         except Exception as exp:
    #             print(exp)
    #
    #         try:
    #             rc = rcArr[1]
    #             return rc
    #         except:
    #             return False
    #
    #
    #     elif platform.system() == 'Linux':
    #         with open(imgPath, 'rb') as image_file:
    #             image = Image.open(image_file)
    #             image.load()
    #             codes = zbarlight.scan_codes('qrcode', image)
    #
    #             try:
    #                 return codes[0]
    #             except:
    #                 return False




##############################################################################################################


    # Resolve and return a list with decoded QR codes (can handle multiple QR coded on image)
    # Return None if no QR code were detected
    # Draw a red rectangle around the codes
    def retQrVal(self, filePath, expectedMultiple=False):
        # Init QR results list
        qrListResults = []
        try:
            image = Image.open(filePath).convert('RGB')
            draw = ImageDraw.Draw(image)
            for barcode in decode(image):
                rect = barcode.rect
                # qrListResults.append(str(barcode[0]))
                qrListResults.append(barcode[0].decode("utf-8"))
                draw.rectangle(
                    (
                        (rect.left, rect.top),
                        (rect.left + rect.width, rect.top + rect.height)
                    ),
                    width=10,
                    outline='#ff0000'
                )

                draw.polygon(barcode.polygon, outline='#ff0000')

            image.save(filePath)
        except Exception as exp:
            return None
        if expectedMultiple:
            return qrListResults
        else:
            # return the first and only one as expected
            if not qrListResults:
                return None
            else:
                return qrListResults[0]

    ##############################################################################################################


                
                       
    def placeCurrPrevScr(self):
        try:
            Qr = self.saveScreenShot()
            ''' first time this method called'''
            if self.prevQr == None:
                self.prevQr = Qr
                
            else:  # shift prev to curr and set curr with the new value 
                self.currQr = Qr 
                        
            return self.placeCurrPrevVal()
        except Exception as exp:
            print(exp)
            return False
           
    
    def placeCurrPrevVal(self):
        ''' first time this method called'''
        if self.prevVal == None:
            try:
                rc = self.retQrVal(self.prevQr)
                rc1 = rc[24:32]
                t = datetime.datetime.strptime(rc1,'%H:%M:%S')
                self.prevVal = t
                return True
            except:
                self.prevQr = None
                return False
        # shift prev to curr and set curr with the new value                 
        else: 
            QRNotfound = False
            cnt =0  
            while not QRNotfound:
                try:
                    rc = self.retQrVal(self.currQr)
                    rc1 = rc[24:32]
                    t = datetime.datetime.strptime(rc1,'%H:%M:%S')
                    self.currVal = t
                    QRNotfound = True
                except:
                    rc= None
                    time.sleep(1)
                    self.currQr = self.saveScreenShot()
                    self.logobj.appendMsg('the following screen shot did not had QR code' + str(self.currQr))
                    cnt = cnt + 1
                    if cnt == 2:
                        QRNotfound = True
        if rc == None:
            return False
        else:    
            return True    
         
    def checkProgress(self,interval, isAppend=False):
        gapInterval = interval+3
        
        if self.currVal == None and self.prevVal == None:
            print(' NO QR ')
            return False
        
        elif self.currVal!=None and self.prevVal!=None:
            
            self.currVal = time.strptime(str(self.currVal),'%Y-%m-%d %H:%M:%S')
            self.currVal = datetime.datetime(self.currVal.tm_year,self.currVal.tm_mon,self.currVal.tm_mday,self.currVal.tm_hour,self.currVal.tm_min,self.currVal.tm_sec)
            self.prevVal = time.strptime(str(self.prevVal) ,'%Y-%m-%d %H:%M:%S')
            self.prevVal = datetime.datetime(self.prevVal.tm_year,self.prevVal.tm_mon,self.prevVal.tm_mday,self.prevVal.tm_hour,self.prevVal.tm_min,self.prevVal.tm_sec)
            
                
            mintime =  datetime.timedelta(seconds=interval) 
            maxtime =  datetime.timedelta(seconds=gapInterval)
            
            '''if the video played ok delete the previous QR code file and just save the current takken  
            time gap duration of one second for cases the number of milliseconds create virtual gap of one second more due to other code line running''' 
            if self.currVal >= self.prevVal+mintime and self.currVal <= self.prevVal+maxtime:
                #print 'going to delete QR file -' + str(self.prevQr)
                os.remove(self.prevQr)
                self.prevQr = self.currQr
                self.prevVal = self.currVal
                self.VideoStopPlayTime = 0
                return True
            elif isAppend and self.currVal < self.prevVal:
                self.logobj.appendMsg('PASS - last qr value was- ' + str(self.prevVal) + ' the current is- ' + str(self.currVal))
                return "append"
            else:
                self.VideoStopPlayTime = self.VideoStopPlayTime+1
                self.logobj.appendMsg('!!! WARNING !!!!')
                self.logobj.appendMsg('Video is not played correctly - at least one of the QR code images trying to take on video play was not displayed')
                self.logobj.appendMsg('last qr value was- ' + str(self.prevVal) + ' the current should have been- a second to 4 seconds more and the actual is- ' + str(self.currVal))
                self.logobj.appendMsg('the following screen shot did not progress in the QR code' + str(self.currQr))
                self.logobj.appendMsg('!!!!!!!!!!!!!!!!')
                self.initVals()
                if self.VideoStopPlayTime ==2:       # only if it happens 3 times the test fail         
                    return False
                else:
                    return True
        else:
            return True      
        
        
        
    def QrCodeCompareToLastRead(self, imgPath, interval):
        
        Qr = self.placeCurrPrevScr()
        rc = self.retQrVal(Qr)
        # no QRcode in the screen shot - initialize the curr and prev and send the screen shot
        if isinstance(rc,bool):
            self.prevQr = None
            self.currQr = None 
            return Qr
        
        # otherwise check the QR increments  
        bCheckProgress = self.placeCurrPrevVal(Qr)
        if bCheckProgress:
            okForNow = self.checkProgress(interval)
        
        # if there was no progress in the video return the file path
        if not okForNow:
            return Qr
        else:
            return True   
               
    # Moran.cohen    
    # This function saves screen shot of the entry
    def placeCurrPrevScr_OnlyPlayback(self):
        Qr = self.saveScreenShot()
        ''' first time this method called'''
        if self.prevQr == None:
            self.prevQr = Qr
            
        else:  # shift prev to curr and set curr with the new value 
            self.currQr = Qr 
                    
        return self.placeCurrPrevVal_OnlyPlayback()
           
    # Moran.cohen    
    # This function set the previous/current value of the video screen
    def placeCurrPrevVal_OnlyPlayback(self):
        ''' first time this method called'''
        if self.prevVal == None:
            try:
                rc,output = self.retVal_OnlyPlayback_ByCapture2Text(self.prevQr)
                self.prevVal = output
                return True
            except:
                self.prevQr = None
                return False
        # shift prev to curr and set curr with the new value                 
        else: 
            QRNotfound = False
            cnt =0  
            while not QRNotfound:
                try:
                    rc, output = self.retVal_OnlyPlayback_ByCapture2Text(self.currQr)
                    self.currVal = output
                    QRNotfound = True
                except:
                    rc= None
                    time.sleep(1)
                    self.currQr = self.saveScreenShot()
                    self.logobj.appendMsg('the following screen shot did not had QR code' + str(self.currQr))
                    cnt = cnt + 1
                    if cnt == 2:
                        QRNotfound = True
        if rc == None:
            return False
        else:    
            return True       
            
    
    # Moran.cohen    
    # This function return value of the capture2Text of the screen shot
    def retVal_OnlyPlayback_ByCapture2Text(self,imgPath,QrReader=r'C:\Program Files (x86)\Kaltura\QRCodeDetector\Capture2Text\Capture2Text.exe'):
        if platform.system() == 'Windows':
            try: 
                proc = subprocess.Popen(QrReader + ' -i ' + imgPath, stdout=subprocess.PIPE)      
                output = proc.stdout.read()
                if str(output).find("Something went wrong") > -1:
                    print((str(output)))
                    return False,output
                #elif str(output).find("<Error>") > -1:
                elif str(output).find("b'\\xc2\\xa35") > -1: #if black screen
                    print("BLACK SCREEN" + (str(output)))
                    return False, output
                else:
                    rc = output
                    return True,rc
                    
            except Exception as exp:
                print(exp)
                return False,str(exp)
                          
        #=======================================================================
        # elif platform.system() == 'Linux':
        #     with open(imgPath, 'rb') as image_file:
        #         image = Image.open(image_file)
        #         image.load()
        #         codes = zbarlight.scan_codes('qrcode', image)
        #         
        #         try:
        #             return codes[0]
        #         except:
        #             return False
        #=======================================================================
               
    # Moran.cohen    
    # This function compares between the current to previous screen shots.            
    def checkProgress_OnlyPlayback(self,interval,AudioOnly=False):
        gapInterval = interval+3
        
        if self.currVal == None and self.prevVal == None:
            print(' NO Capture2Text from Images')
            return False
        elif AudioOnly == True:
            #if (str(self.currVal).find("<Error>") > -1 or str(self.currVal).find("b'\\xc2\\xa35") > -1) and self.currVal == self.prevVal:
            #if str(self.currVal).find("b'\\xc2\\xa35") > -1 and self.currVal == self.prevVal: # if black screen is playing -->It is ok for audio only
            if self.currVal == self.prevVal:  # if black screen is playing -->It is ok for audio only
                print('PASS -  NO Capture2Text from Images - Return BLACK SCREEN" - Ok Playback for Audio only case.self.currVal= ' + str(self.currVal) + ", prevVal=" + str(self.prevVal))
                return True
            else:
                print('FAIL - NOT expected playback behavior for Audio only case.currVal= ' + str(self.currVal) + ", prevVal=" + str(self.prevVal))
                return False
        elif self.currVal!=None and self.prevVal!=None:
            
            #===================================================================
            # if self.currVal == self.prevVal:
            #     print "Entry doesn't play"
            #     self.VideoStopPlayTime = 1
            #===================================================================            
            '''if the video played ok delete the previous Capture2Text and just save the current taken  
            time gap duration of one second for cases the number of milliseconds create virtual gap of one second more due to other code line running''' 
            if self.currVal != self.prevVal:
                os.remove(self.prevQr)
                self.prevQr = self.currQr
                self.prevVal = self.currVal
                self.VideoStopPlayTime = 0
                return True
            else:
                print("Entry doesn't play")
                self.VideoStopPlayTime = self.VideoStopPlayTime+1
                self.logobj.appendMsg('!!! WARNING !!!!')
                self.logobj.appendMsg('Video is not played correctly - at least one of the images trying to take on video play was not displayed')
                self.logobj.appendMsg('last value was- ' + str(self.prevVal) + ' the current should have been- a second to 4 seconds more and the actual is- ' + str(self.currVal))
                self.logobj.appendMsg('the following screen shot did not progress' + str(self.currQr))
                self.logobj.appendMsg('!!!!!!!!!!!!!!!!')
                self.initVals()
                if self.VideoStopPlayTime ==1:                
                    return False
                else:
                    return True
        else:
            return True

        # this function verify qr code is progressing till some point it start from a lower value (the appended recording)
        # Written by Adi Miller
        # timeToTrackQR - send the number of Seconds to verify the QR's

        def verifyAppendEntryProgress(timeToTrackQR):
            timeisfinish = False
            startTime = time.time()
            self.initVals()
            tempStatus = False

            # while not time is up (timeToTrackQR) continue to check the Qr codes on the stream
            while not timeisfinish:
                rc = self.placeCurrPrevScr()
                if rc:
                    rc = self.checkProgress(1,isAppend=True)
                    if rc=="append":
                        self.logobj.appendMsg("PASS - the QR code started again after: " + str(time.time() - startTime) + "of playing the entry")
                        self.status = True
                        timeisfinish = True
                if time.time() - startTime > timeToTrackQR:
                    timeisfinish = True