import cv2
import socket as so
import numpy as np
import pickle
import pandas as pd
from picamera.array import PiRGBArray
from picamera import PiCamera
s = so.socket()
port = 42069
s.bind(('', port))
s.listen(5)
s.setsockopt(so.IPPROTO_TCP, so.TCP_NODELAY, 1)
c, addr = s.accept()
print(f'connected from {addr}, ready to fly')
tick = 0
notdata = 0
class Close(Exception):
    pass
camera = PiCamera()
camera.resolution = (320*1,240*1)
camera.framerate = 20
#raw_capture = PiRGBArray(camera, size=(640, 480))
#imga = PiRGBArray(camera, size=(640, 480))
#img = np.empty(((240*2) * (320*2) * 3), dtype=np.uint8)
while True:
    try:
        data = c.recv(10000)
        img = np.empty(((240*1) * (320*1) * 3), dtype=np.uint8)
        camera.capture(img, 'bgr', use_video_port=True)
        #camera.capture(img, 'bgr')
        img = img.reshape((240,320, 3))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
        img = cv2.imencode('.jpg', img, encode_param)[1] #compression for wifi transfer
        img = pickle.dumps(img)
        print(len(img))
        c.send(img)
        if tick == 0:
            data = pickle.loads(data)
            if type(data) is str:
                print(data)
                data = data.split()
                command = data[0]
                idd = int(data[1])
                strength = idd*0.25
                notdata = 0
        elif tick == 1:
            boxs = pickle.loads(data)
            if len(boxs) == 2:
                #print(f'FPS: {boxs[1]}')
                boxs = [list(x) for x in boxs[0]]
                print(boxs)
                notdata = 0
        if not data:
            notdata+=1
        if notdata >= 100:
            raise Close

        #flightlogic
        if command != 'no': #essentially if manual control is on
            pushdata(convert(command,strength))
        else: #if in automation mode
            if tick == 1:
                #print(followbox(boxs))
                pass

        #end of loop actions
        if tick == 0:
            tick = 1
        elif tick == 1:
            tick = 0
    except Close:
        print(f'closed connection')
        c.close()
        break
    except Exception as e:
        print(e)
