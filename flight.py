import cv2 as cv
import serial
from msp import MultiWii
from util import push16
import time
import random
import thrust
import socket as so
import numpy as np
#raspi password is: drone
ser = 0
board = 0
s = so.socket()
port = 42069
s.bind(('', port))
s.listen(5)

def initialize():
    global ser
    global board
    ser = serial.Serial('COM4', 9600)# serial port for sensory arduino
    board = MultiWii("/dev/ttyACM0") #__init__ takes the serial port, get from arduino IDE
    print("Flight Controller connected!")
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
    print(data[3])
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

class Close(Exception):
    pass
def flightloop():
    while True:
        sensory = [1]
        try:
            data = c.recv(1024)
            n = np.random.bytes(408960)
            c.send(n)
            #might add second send call for sensory data
            if not data:
                raise Close
            #print(data)
            data = data.decode().split()
            if data[0] != 'no':
                idd = int(data[1])
                strength = idd*0.25
                pushdata(convert(data[0],strength))
            else:
                print('doing automated stuff')
            #print(data)
        except Close:
            print(f'closed connection')
            c.close()
            break
        except Exception as e:
            print(e)

while True:
    c, addr = s.accept()
    #initialize()
    print(f'connected from {addr}, ready to fly')
    flightloop()
