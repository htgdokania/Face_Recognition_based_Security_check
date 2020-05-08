import numpy as np
import cv2
import socket
import face_recognition
import os
from data_feed import send_image,authorize
import time

class SecurityCheck(object):

    def __init__(self, host, port):
        self.start=time.time()
        
        # Initialize some variables for face Recognition part
        self.process_this_frame=0
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        # Network streaming  part
        self.server_socket = socket.socket()
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)

        #Call the function to load known face data 
        self.load_known_faces()
        #start streaming
        self.streaming()

    def load_known_faces(self):
        ## Load the known_faces  images data from the folder
        folder="known_faces"
        self.known_face_names=[]
        self.known_face_encodings=[]

        for filename in os.listdir(folder):
            (file, ext) = os.path.splitext(filename)
            self.known_face_names.append(file)
            image=face_recognition.load_image_file(folder+'/'+filename)
            print(folder+'/'+filename)
            known_face_encoding= face_recognition.face_encodings(image)[0]
            self.known_face_encodings.append(known_face_encoding)

    def process_frame(self):
        speed=3 #processing speed for face Recognition to improve speed
        small_frame = cv2.resize(self.frame, (0, 0), fx=0.25, fy=0.25) # 1/4th frame
        rgb_small_frame = small_frame[:, :, ::-1] # convert to RGB

        if ((self.process_this_frame%speed)==0): 
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(self.known_face_encodings,face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(self.known_face_encodings,face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index] # if match found rename to the matched name
                self.face_names.append(name)

        if(self.process_this_frame==speed):
            self.process_this_frame=0
        else:
            self.process_this_frame+=1

    def send_adafruit(self,name):
        check=time.time()-self.start
        print("check=",check)
        if (check>5):                   # check if 5 secs went by , since last authentication was sent.
            if (name=='Unknown'):
                authorize(0)
                send_image(self.frame,name)
                cv2.imwrite('unknown_faces/unknown'+'{}.png'.format(int(time.time())),self.frame)
            else:
                authorize(1)
                send_image(self.frame,name)                
            self.start=time.time()  # Reset the start value.

    def display_frame(self):
        # Display the results
        for (top, right, bottom, left),name in zip(self.face_locations, self.face_names):
            #call function to send info on server
            self.send_adafruit(name)
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            # Draw a box around the face
            cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # Display the resulting image
        cv2.imshow('Video', self.frame)
        
    def streaming(self):
        try:
            print("Host: ", self.host_name + ' ' + self.host_ip)
            print("Connection from: ", self.client_address)
            print("Streaming...")
            print("Press 'q' to exit")
            
            # need bytes here
            stream_bytes = b' '
            while True:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    self.frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    self.frame=cv2.flip(self.frame,0) #To correct camera orientation.(in my case)
                    
                    #call function  to recognise face 
                    self.process_frame()            
                    #display
                    self.display_frame()

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break                    
        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    # host, port
    h, p = '', 8000 # '' represents listening to all devices
    SecurityCheck(h, p)

cv2.destroyAllWindows()



