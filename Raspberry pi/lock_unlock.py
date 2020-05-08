import time
import base64
import os
from Adafruit_IO import Client, Feed, RequestError
import RPi.GPIO as GPIO

ADAFRUIT_IO_KEY = 'YOUR_AIO_KEY'
ADAFRUIT_IO_USERNAME = 'USERNAME'

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED_Green=26
LED_Red=19
GPIO.setup(LED_Green,GPIO.OUT)
GPIO.setup(LED_Red,GPIO.OUT)
lock_feed=aio.feeds('lock')

while 1:
    data=aio.data('lock')
    try:
        print('processing..')
        for d in data:
            status=d.value
        print(status)
        if (status=='1'):
            GPIO.output(LED_Green,GPIO.HIGH)
            GPIO.output(LED_Red,GPIO.LOW)
            time.sleep(10)
            #auto lock if unlocked after 10 sec
            aio.send(lock_feed.key,0)
        else:
            GPIO.output(LED_Green,GPIO.LOW)
            GPIO.output(LED_Red,GPIO.HIGH)
        
            
    except:
        print(' Failed...')
    
    time.sleep(4)

