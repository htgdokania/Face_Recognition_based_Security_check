import numpy as np
import cv2
import socket
import face_recognition
import os
from data_feed import send_image,authorize
import time

class VideoStreamingTest(object):
    def __init__(self, host, port):
        self.server_socket = socket.socket()
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.streaming()

    def streaming(self):
        speed=3 #processing speed for face Recognition .

        ## Load the known_faces  images data from the folder
        folder="known_faces"
        known_face_names=[]
        known_face_encodings=[]

        for filename in os.listdir(folder):
            (file, ext) = os.path.splitext(filename)
            known_face_names.append(file)
            image=face_recognition.load_image_file(folder+'/'+filename)
            print(folder+'/'+filename)
            known_face_encoding= face_recognition.face_encodings(image)[0]
            known_face_encodings.append(known_face_encoding)

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame=0


        try:
            print("Host: ", self.host_name + ' ' + self.host_ip)
            print("Connection from: ", self.client_address)
            print("Streaming...")
            print("Press 'q' to exit")

            # need bytes here
            stream_bytes = b' '
            start=time.time()
            while True:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    frame=cv2.flip(frame,0)
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25) # 1/4th frame
                    rgb_small_frame = small_frame[:, :, ::-1] # convert to RGB

                    if ((process_this_frame%speed)==0):
                        # Find all the faces and face encodings in the current frame of video
                        face_locations = face_recognition.face_locations(rgb_small_frame)
                        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                        face_names = []
                        for face_encoding in face_encodings:
                            # See if the face is a match for the known face(s)
                            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                            name = "Unknown"
                            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = known_face_names[best_match_index] # if match found rename to the matched name
                            face_names.append(name)

                    if(process_this_frame==speed+1):
                        process_this_frame=0
                    else:
                        process_this_frame+=1

                    # Display the results
                    for (top, right, bottom, left), name in zip(face_locations, face_names):

                        check=time.time()-start
                        print("check=",check)
                        
                        if (check>30):# check if 30 secs gone since last authentication was sent.
                            if (name=='Unknown'):
                                authorize(0)
                                send_image(frame,name)
                            else:
                                authorize(1)
                                send_image(frame,name)
                                
                            start=time.time()# Reset the start to send another authorization only after 30 secs delay.
                                        
                        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                        # Draw a label with a name below the face
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                 
                    # Display the resulting image
                    cv2.imshow('Video', frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    
        finally:
            self.connection.close()
            self.server_socket.close()


if __name__ == '__main__':
    # host, port
    h, p = '', 8000  # '' means only for 
    VideoStreamingTest(h, p)

cv2.destroyAllWindows()



