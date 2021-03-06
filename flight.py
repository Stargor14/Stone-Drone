import cv2
import serial
import time
import random
import thrust
import socket as so
import numpy as np
import pickle
import pandas as pd
from picamera.array import PiRGBArray
from picamera import PiCamera
#raspi password is: eryk2005
#change arduino code in protocol.cpp and multiwii.cpp
ser = 0
s = so.socket()
port = 42069
s.bind(('', port))
s.listen(5)
s.setsockopt(so.IPPROTO_TCP, so.TCP_NODELAY, 1)
camera = PiCamera()
camera.resolution = (320*1,240*1)
camera.framerate = 20
servox = 90
servoy = 90

def initialize():
    global ser
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600,timeout=0)# serial port for sensory arduino
        ser.flush()
    except Exception as e:
        ser = serial.Serial('/dev/ttyUSB1', 9600,timeout=0)
        ser.flush()
    #set servos to 90
    #arm the motors

#GPS Waypoint Navigation, Live Stream Video, Altitude Hold, Position Hold, Return to Home, random patrol, follow (some bright color) ball, bluetooth control
#Telemetry via Bluetooth
#need function or taking in sensory data and processing
#need diff modes for flying, set path, gps to gps, follow the dots (using camera), random patrol (indoor using sensors), hover at ALTITUDE, etc etc

def convert(code,strength=0.5):
    #move like an 8 way stick for "simplicity"
    R = 0
    P = 0
    T = 0
    Y = 0
    code = str(code)
    #elevation
    try:
        if code[0:2] == '00':
            T = 0
        elif code[0:2] == '10':
            T = strength #upward speed
        elif code[0:2] == '-1':
            T = -strength#descent speed
        #direction
        if code[-1] == '0':
            R = -strength
            P = strength
        elif code[-1] == '1':
            R = 0
            P = strength
        elif code[-1] == '2':
            R = strength
            P = strength
        elif code[-1] == '3':
            R = -strength
            P = 0
        elif code[-1] == '4':
            R = strength
            P = 0
        elif code[-1] == '5':
            R = -strength
            P = -strength
        elif code[-1] == '6':
            R = 0
            P = -strength
        elif code[-1] == '7':
            R = strength
            P = -strength
        elif code[-1] == '8':
            R = 0
            P = 0
        elif code == '999':
            R = 0
            P = 0
            T = 0
            Y = strength
        else:
            print('invalid code')
    except Exception as e:
        print(e)
        print('invalid code')
    return [R,P,T,Y]

def camservos(x,y,z):
    #will move camera servos to desired position to x,y
    #pass as 0-180 for every servo
    #send serial data to arduino
    print((x,y,z))
    return

#throttle and rotation, yaw can be used as LIDAR type beat, can scan using all sensors and map surroundings, plot itslef within the space
#give direction/speed

#off defaults:
#rudder: 0 (no spin)
#throttle: -1 (no throttle)
#aileron: 0 (no left/ right movement)
#elevator: 0 (no up/downward pitch)

#hoverp = thrust.predict(895)[0]
codelist=[
 "000", "100", "-100"
,"001", "101", "-101"
,"002", "102", "-102"
,"003", "103", "-103"
,"004", "104", "-104"
,"005", "105", "-105"
,"006", "106", "-106"
,"007", "107", "-107"
,"008", "108", "-108"]
def video(path):
    cap = cv2.VideoCapture(f'{path}')
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    buf = np.empty((frameCount, frameHeight, frameWidth, 3), np.dtype('uint8'))

    fc = 0
    ret = True
    strt = time.perf_counter()
    while (fc < frameCount  and ret):
        ret, buf[fc] = cap.read()
        if fc%100 == 0:
            rem = (frameCount-fc)/100
            eta = rem*(time.perf_counter()-strt)
            print(f"{fc}/{frameCount} ETA: {eta}s")
            strt = time.perf_counter()
        fc += 1

    cap.release()
    return buf
def centreobject(box):
    middlex = (box[2]/2)+box[0]
    middley = (box[3]/2)+box[1]
    middle = (middlex,middley)
    return middle
class Close(Exception):
    pass
def getremdeg():
    xleft = servox
    xright = 360-servox
    yup = servoy
    ydown = 180-servoy
    return xleft,xright,yup,ydown
def followbox(boxs):
    centrex = xlen/2
    centrey = ylen/2
    xmod = xlen/180
    ymod = ylen/180
    servoloc = (90,90)
    remdegrees = getremdeg() #gets remainign degrees of freedom of servos, 0x+ 1x-, 2y+, 3y-
    padding = 50 #allows for margin of error, in pixels
    newx = 0
    newy = 0
    if len(boxs) == 1:
        objloc = centreobject(boxs[0])
    if len(boxs) > 1 and type(boxs) is list:
        boxspd = pd.DataFrame(boxs)
        avrgbox = []
        for i in boxspd:
            avrgbox.append(boxspd[i].mean())
        objloc = centreobject(avrgbox)
    if len(boxs) >=1 and type(boxs) is list:
        if objloc[0]/xmod>(centrex+padding)/xmod:# x not centred right
            newx = min((objloc[0]/xmod) - (centrex)/xmod,remdegrees[1])
        if objloc[0]/xmod<(centrex-padding)/xmod:
            newx = min((objloc[0]/xmod) - (centrex)/xmod,remdegrees[0])
        if objloc[1]/ymod>(centrey+padding)/ymod:# y not centred down
            newy = min((objloc[1]/ymod) - (centrey)/ymod,remdegrees[3])
        if objloc[1]/ymod<(centrey-padding)/ymod:
            newy = min((objloc[1]/ymod) - (centrey)/ymod,remdegrees[2])
        return (newx,newy,0)
    else:
        return (0,0,0)
def getgyro():
    ser.reset_input_buffer()#definetly a very messy solution, but it works 
    time.sleep(0.03)
    for _ in range(2):
        by = ser.readline()
    by = by.decode()
    print(by) #god knows wtf is even happening anymore, if I increase teh resolution the gyro doesnt read anymore.... they arent even part of the same system...
    for i in range(len(str(by))):
        print(by[i])
    return 0,0,0
def flightloop():
    command = '008'
    strength = 0.25
    tick = 0
    notdata = 0
    started = False
    time.sleep(2)
    while True:
        try:
            
            data = c.recv(10000)
            img = np.empty(((240*1) * (320*1) * 3), dtype=np.uint8)
            camera.capture(img, 'bgr', use_video_port=True)
            img = img.reshape((240,320, 3))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]
            result, img = cv2.imencode('.jpg', img, encode_param) #compression for wifi transfer
            c.send(pickle.dumps(img))
            if tick == 0:
                data = pickle.loads(data)
                if type(data) is str:
                    #print(data)
                    data = data.split()
                    command = data[0]
                    idd = int(data[1])
                    strength = idd*0.25
                    notdata = 0
            elif tick == 1:
                boxs = pickle.loads(data)
                boxs = [list(x) for x in boxs]
                try:
                    if boxs[0][0] == 'n': #fixes server client tick desync, command and strength would be read as boxs
                        continue
                except:
                    pass
                notdata = 0
            if not data:
                notdata+=1
            if notdata >= 100:
                raise Close

            #flightlogic
            #print((command,strength))
            getgyro()
            if command != 'no': #essentially if manual control is on
                pass
            else: #if in automation mode
                if tick == 1:
                    print(followbox(boxs))
                    pass

            #end of loop actions
            if tick == 0:
                tick = 1
            elif tick == 1:
                tick = 0         
        except Close: #error handling
            print(f'closed connection')
            c.close()
            break
        except Exception as e:
            print(e)
            pass
ylen = 240
xlen = 320
def autoloop():
    readings = []#measured per angle, therefore needs to be very precise
    #might have to use servos to scan

initialize()
while True: #backup loop, if connection is lost
    #WRITE FULL AUTO MODE, START WRITING CODE FOR LIDAR
    print('Ready to connect')
    c, addr = s.accept()
    #initialize()
    print(f'connected from {addr}, ready to fly')
    flightloop()


