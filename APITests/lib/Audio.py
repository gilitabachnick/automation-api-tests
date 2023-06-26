#import pyaudio
import datetime
import math
import struct
import subprocess
import wave
import time
import os
import wave

# import required libraries
from datetime import date

import pyautogui
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import MySelenium
import reporter2

Threshold = 10

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
#FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2

TIMEOUT_LENGTH = 5

f_name_directory = r'C:\temp'

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self,Wd, logi):
        self.Wd = Wd
        self.logi = logi

    # this function record sound input till TIMEOUT_LENGTH ends (pyaudio)
    def record(self):
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    # this function write the input from sound devices and write it to wave file
    # def write(self, recording):
    #     n_files = len(os.listdir(f_name_directory))
    #
    #     filename = os.path.join(f_name_directory, '{}.wav'.format(n_files))
    #
    #     wf = wave.open(filename, 'wb')
    #     wf.setnchannels(CHANNELS)
    #     wf.setsampwidth(self.p.get_sample_size(FORMAT))
    #     wf.setframerate(RATE)
    #     wf.writeframes(recording)
    #     wf.close()
    #     print('Written to file: {}'.format(filename))
    #     print('Returning to listening')


    # this function listen to sound input device and detect noise that is byond threashold
    # def listen(self):
    #     print('Listening beginning')
    #     bStartRecord = False
    #     while not bStartRecord:
    #         input = self.stream.read(chunk)
    #         rms_val = self.rms(input)
    #         if rms_val > Threshold:
    #             bStartRecord = True
    #             self.newRecord()

    # this function compare between 2 wave files frames and return true if both are eqaul and false if not
    # send the long wav file to serach in, in parameter fpth1
    # send the sub wav file to search for in fpth2
    def CompareWavFiles(self, fpth1, fpth2, numOfFramesToEqualize):
    #     # Loading audio files
        try:
            f1= wave.open(fpth1,'rb')
            f2 = wave.open(fpth2,'rb')
        except Exception as Exp:
            print ("the following exception occured while trying to open the wave file: " + Exp)

        frf1 = f1.readframes(f1.getnframes())
        frf2 = f2.readframes(f2.getnframes())

        try:
            frf1.index(frf2,0)
            return True
        except:
            return False

    def newListen(self):
        # Sampling frequency
        frequency = 44400

        # Recording duration in seconds
        duration = 20
        recording = sd.rec(int(duration * frequency),
                           samplerate=frequency, channels=2, dtype='int16')
        while recording.sum()/88800<0.1:
            print("not yet " + str(recording.sum()))
        # while recording[recording.__len__()-1][0]<=0 and recording[recording.__len__()-1][1]<=0:
        #     continue

        print("start input play")
        sd.stop()
        self.newRecord()



    # sounddevice
    def Record2(self):
        # Sampling frequency
        frequency = 44400

        # Recording duration in seconds
        duration = 20
        soundDetected = False
        # rawoutputStream = sd.RawOutputStream()
        # dd= rawoutputStream.
        # while not soundDetected:
        #     try:
        #         sd.get_stream()
        #
        #         print("sound detected")
        #         soundDetected = True
        #     except:
        #         print("No sound yet")

        # to record audio from
        # sound-device into a Numpy
        recording = sd.rec(int(duration * frequency),
                           samplerate=frequency, channels=2)

        # Wait for the audio to complete
        sd.wait()

        # using scipy to save the recording in .wav format
        # This will convert the NumPy array
        # to an audio file with the given sampling frequency
        write(r'c:\temp\recording0.wav', frequency, recording)

        # using wavio to save the recording in .wav format
        # This will convert the NumPy array to an audio
        # file with the given sampling frequency
        wv.write(r'c:\temp\recording0.wav', recording, frequency, sampwidth=2)


    # this function record only chrome, using chrome addin "Chrome Audio Capture", the webdriver need to ne already initialize with this addin
    # secsToRecord - number of seconds to record
    # runRemote - send false if this run localy
    # saveToPth - send the path and file name, where to save the recorded wav file
    def Record3(self, secsToRecord, saveToPth=r'c:\temp'):

        try:
            primTab = self.Wd.window_handles[0]
            fname = str(datetime.datetime.now()).split(".")[0].replace("-","_").replace(" ","_").replace(":","") + "_recorded.wav"

            # start recod by sending the ctrl+shift+s
            # stop recording by sending ctrl+shift+x
            action = ActionChains(self.Wd)
            action.send_keys(Keys.CONTROL+Keys.SHIFT+"s")
            action.perform()
            time.sleep(secsToRecord)
            action.send_keys(Keys.CONTROL+Keys.SHIFT+"x")
            action.perform()

            audioCaptureTab = self.Wd.window_handles[1]
            self.Wd.switch_to.window(audioCaptureTab)
            self.Wd.find_element_by_id("saveCapture").click()

            pyautogui.FAILSAFE = False
            theFilePth = str(os.path.abspath(os.path.join(saveToPth, fname)))
            pyautogui.typewrite(theFilePth)
            pyautogui.press('enter')
            self.Wd.close()

            self.Wd.switch_to.window(primTab)

            return theFilePth

        except Exception as Exp:
            print (str(Exp))
            return False

logi = reporter2.Reporter2('test_audio')
Wdobj = MySelenium.seleniumWebDrive()
Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")
action = ActionChains(Wd)
action.send_keys(Keys.CONTROL+Keys.SHIFT+"s")
action.perform()
time.sleep(5)
a = Recorder(Wd,logi)
a.Record3(10)

#a.listen()
#
a.CompareWavFiles(r'c:\temp\recording0.wav',r'c:\temp\recording1.wav',100)