# Server side
## main.py (This code should be run before client.py in raspberry pi)
This is the main code which acts as a server to receive and process images from picamera connected to the raspberry pi .
Also it looks for faces using Face_recognition library .  All we need is a single image of the person .

## data_feed.py
This code is called from within main.py , to send the data(Image and Authentication to lock/unlock any device)  to io.adafruit.com

## known_faces Folder
We need to add a single image of all the authorized person in this folder. File name should be the name of the person in the image. For example : Harsh.png 

# Raspberry Pi 

## client.py (This code should only after main.py is running on the server end)
This code captures an image from pi camera and Sends it to the server for further processing.

## lock_unlock.py
This code Reads the status of 'lock' feed  from io.adafruit.com and updates the status of the device accordingly.
I have used Green and Red LEDs to represent 'ON' and 'OFF' respectively.
Also if the device is 'ON'. This code makes sure to autolock the same after an interval of 10sec for added security. 
