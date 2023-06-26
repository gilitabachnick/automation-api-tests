import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#import BrowserProxy
import QrcodeReader


isProd = os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False
    
Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
    
class TestClass:
    
    def test_1(self):
        QrCode = QrcodeReader.QrCodeReader(lib='liveQrCodes')
        rc = QrCode.retQrVal('/home/ubuntu/build/workspace/Live_test_1/APITests/Tests/liveQrCodes/ScreenShot_15112016_041102.png')
        print((str(rc)))
        
        
      #=========================================================================
      #   #Val = QrCode.retQrVal('/home/ubuntu/build/workspace/Live_test_1/APITests/Tests/liveQrCodes/ScreenShot_15112016_121650.png')
        print(' after val = ')
        print((type(rc)))
      #    
      
        rc = rc[28:32]
      #   except Exception as exp:
      #       print exp
        print(' after rc[28:32]')
        print(rc)
        rc = rc.replace(':','')
        print('after replace')
        print(rc)
      #   Val = int(Val)
      #   self.prevVal = Val
      # 
      #=========================================================================
        