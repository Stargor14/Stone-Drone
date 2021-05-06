import cv2
import serial
from msp import MultiWii
from util import push16
import time
import random
import thrust
import socket as so
import numpy as np
import pickle
import pandas as pd
#raspi password is: eryk2005
ser = 0
board = 0
s = so.socket()
port = 42069
s.bind(('', port))
s.listen(5)
#s.setsockopt(so.IPPROTO_TCP, so.TCP_NODELAY, 1)
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
cap.set(10,70)
servox = 90
servoy = 90

def initialize():
    global ser
    global board
    ser = serial.Serial('COM4', 9600)# serial port for sensory arduino
    board = MultiWii("/dev/ttyACM0") #__init__ takes the serial port, get from arduino IDE
    print("Flight Controller connected!")
    #set servos to 90
    time.sleep(1.0)
    board.enable_arm()
    board.arm()

#GPS Waypoint Navigation, Live Stream Video, Altitude Hold, Position Hold, Return to Home, random patrol, follow (some bright color) ball, bluetooth control
#Telemetry via Bluetooth
#need function or taking in sensory data and processing
#need diff modes for flying, set path, gps to gps, follow the dots (using camera), random patrol (indoor using sensors), hover at ALTITUDE, etc etc

def converthover(strength):
    return [0,0,strength,0]

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

def camservos(x,y):
    #will move camera servos to desired position to x,y
    #min is 0 max is 180, middle is 90
    # +90 = 1
    # -90 = -1
    # f(x) = 90x+90
    xpos = (90*x)+90
    ypos = (90*y)+90

#throttle and rotation, yaw can be used as LIDAR type beat, can scan using all sensors and map surroundings, plot itslef within the space
#give direction/speed

#off defaults:
#rudder: 0 (no spin)
#throttle: -1 (no throttle)
#aileron: 0 (no left/ right movement)
#elevator: 0 (no up/downward pitch)

hoverp = thrust.predict(895)[0]
def pushdata(data):
    buf = []
    #A = roll 0
    #E = pitch 1
    #T = throttle 2
    #R = yaw/spin 3
    roll = 0
    pitch = 0
    throttle = 0
    spin = 0
    push16(buf, int(data[0] * 400 + 1500)) #test each individual axis
    roll = abs(data[0] * 100)
    push16(buf, int(data[1] * 400 + 1500))
    pitch = abs(data[1] * 100)
    if int(data[2])<0:
        push16(buf, int(data[2] * (1000*(hoverp/100)) + 1000 + (1000*((hoverp)/100))))
        throttle = int((hoverp)*data[2]+hoverp)
        #print(f'{(hoverp)*data[2]+hoverp}% throttle')
    else:
        push16(buf, int(data[2] * (1800-((1000*(hoverp/100))+1000)) + 1000+(1000*((hoverp)/100)))) #1000-2000, y intercept is the hover%, calcuklated as 1000+(1000*(%)/100)
        throttle = int((100-hoverp)*data[2]+hoverp)
        #print(f'{(100-hoverp)*data[2]+hoverp}% throttle')
    push16(buf, int(data[3] * 400 + 1500))
    spin = abs(data[3] * 100)
    print(f"Roll: {roll} Pitch: {pitch} Throttle: {throttle}% Spin: {spin}")
    #idek what the values of the serial are, but thankfully someone smarter than me atm made a solution for it, thank u Aldo Vargas
    push16(buf, 1500)# none of these will be used, I have seperate arduino for I/O
    push16(buf, 1000)
    push16(buf, 1000)
    push16(buf, 1000) #buf is just a serialized string/array? of all the informatiuon being sent, check out util.py to verify
    # send rc command
    #board.sendCMD(MultiWii.SET_RAW_RC, buf)
    #time.sleep(0.025)

    # print board attitude
    #board.getData(MultiWii.ATTITUDE)
    #print(board.attitude)
    #time.sleep(0.025)
    return buf

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
    xright = 180-servox
    yup = servoy
    ydown = 180-servoy
    return xleft,xright,yup,ydown
def getimg():
    success,img = cap.read()
    return img
def flightloop():
    frames = video('test.mp4')
    n=0
    command = '008'
    strength = 0.25
    tick = 0
    while True:
        try:
            data = c.recv(100000)
            #c.send(pickle.dumps(cap.read()))
            c.send(pickle.dumps(frames[n]))
            n+=1
            if tick == 0:
                data = pickle.loads(data)
                if type(data) is str:
                    #print(data)
                    data = data.split()
                    command = data[0]
                    idd = int(data[1])
                    strength = idd*0.25
            elif tick == 1:
                boxs = pickle.loads(data)
                if len(boxs) == 2:
                    print(f'FPS: {boxs[1]}')
                    boxs = [list(x) for x in boxs[0]]
                    print(boxs)
            if not data:
                raise Close

            #flightlogic
            if command != 'no': #essentially if manual control is on
                pushdata(convert(command,strength))
            else: #if in automation mode
                if tick == 1:
                    ylen = len(frames[10])
                    xlen = len(frames[10][10])
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
                    if len(boxs) > 2 and type(boxs) is list:
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
                        print((newx,newy))
            #end of loop actions
            if tick == 0:
                tick = 1
            elif tick == 1:
                tick = 0
        except Close:
            print(f'closed connection')
            c.close()
            break
        #except Exception as e:
        #    print(e)

while True:
    c, addr = s.accept()
    #initialize()
    print(f'connected from {addr}, ready to fly')
    flightloop()
