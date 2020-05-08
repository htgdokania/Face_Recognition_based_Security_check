import time
import base64
import os
import cv2
from Adafruit_IO import Client, Feed, RequestError

ADAFRUIT_IO_KEY = 'YOUR_AIO_KEY'
ADAFRUIT_IO_USERNAME = 'USERNAME'
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

def send_image(frame,name):
  frame=cv2.resize(frame,(300,300))
  cv2.imwrite(name+'.jpg',frame)
  print('Camera: SNAP!Sending photo....')
  cam_feed = aio.feeds('known')
  if (name=='Unknown'):
    cam_feed = aio.feeds('unknown')
                
  with open(name+'.jpg', "rb") as imageFile:
      image = base64.b64encode(imageFile.read()) # encode the b64 bytearray as a string for adafruit-io
      image_string = image.decode("utf-8")
      try:
        aio.send(cam_feed.key, image_string)
        print('Picture sent to Adafruit IO')
      except:
        print('Sending to Adafruit IO Failed...')
  time.sleep(2)# camera capture interval, in seconds

def authorize(status):
  print('Camera: SNAP!.Sending info...')
  lock_feed=aio.feeds('lock')
  try:
    aio.send(lock_feed.key, status)
    print('Authorization sent to Adafruit IO')
  except:
    print('Sending to Adafruit IO Failed...')
  time.sleep(2)# camera capture interval, in seconds


  
