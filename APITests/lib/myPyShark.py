import datetime
import os
import os.path

import pyshark


class mypyshark():
    
    # timetolisten - the time need to listen (seconds)
    def listen(self,timetolisten,outputFile=os.path.join(os.path.dirname(__file__),'test.pcapng')):
        print(('Start SNIFF ' + str(datetime.datetime.now().time())))
        if os.path.exists(outputFile):
            os.remove(outputFile)
        capture = pyshark.LiveCapture(interface='Ethernet',output_file=outputFile) #bpf_filter='http.request.uri contains playManifest'
        capture.sniff(timeout=timetolisten) 
        capture.close()
        print(('STOP SNIFF ' + str(datetime.datetime.now().time())))
        return capture 
    # display filer example - 'http contains \"manifest\"' 
    def retFromCaptureFile(self, filePth,displayFilter):
        try:
            capFile = pyshark.FileCapture(filePth,display_filter=displayFilter)
            return capFile[0]
        except:
            return 0
        