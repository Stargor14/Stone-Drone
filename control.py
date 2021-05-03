#!/usr/bin/env python
import serial
from msp import MultiWii
from util import push16
import time
import random
import thrust
from matplotlib import pyplot as plt
#raspi password is: drone
ser = 0
board = 0
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

def take_sensory():
    #take sensory data from ultrasonics
    #also take the current picth yaw etc, ordered 2 gyros for a reason (not rlly this is lucky af)
    sensory=[]
    #create serial string output format for arduino, ex. : "ultra1,ultra2,ultra3,ultra4,ultraup,ultradown,(all gyros)"
    #gonna have to trial and error the gyro to process raw data
    return sensory

def converthover(strength):
    return [0,0,strength,0]

def convert(code,strength=100):
    #move like an 8 way stick for "simplicity"
    R = 0
    P = 0
    T = 0
    Y = 0 #used for other functions, mainly for allignemnt using trigonometry  (gps and sesnors indoors)

    '''
        0      1      2
         \    / \    /
          \    |    /
    3<-- Drone(birds eye) -->4   UP: 100,101,102, etc.
           /    |    \           DOWN: -100,-101,-102, etc.
         /     \ /    \          NETRAL: 000,001,002, etc.
        5       6      7

    -1 = left/back 0 = neutral (throttle 0 is hover (estimate), this has to be calculated thru trail and error) 1 = right/forward
    000: R: -0.5 P:  0.5 T: 0.0 (essenitally hover throttle)
    001: R:  0.0 P:  0.5 T: 0.0
    002: R:  0.5 P:  0.5 T: 0.0
    003: R: -1.0 P:  0.0 T: 0.0
    004: R:  1.0 P:  0.0 T: 0.0
    005: R: -0.5 P: -0.5 T: 0.0
    006: R:  0.0 P: -0.5 T: 0.0
    007: R:  0.5 P: -0.5 T: 0.0

    108: R:  0.0 P:  0.0 T: 0.0

    100: R: -0.5 P:  0.5 T: 1.0 (or speed multiplier?)
    101: R:  0.0 P:  0.5 T: 1.0
    102: R:  0.5 P:  0.5 T: 1.0
    103: R: -1.0 P:  0.0 T: 1.0
    104: R:  1.0 P:  0.0 T: 1.0
    105: R: -0.5 P: -0.5 T: 1.0
    106: R:  0.0 P: -0.5 T: 1.0
    107: R:  0.5 P: -0.5 T: 1.0

    108: R:  0.0 P:  0.0 T: 1.0

   -100: R: -0.5 P:  0.5 T: -0.2 (lower than upward for soft landing purposes)
   -101: R:  0.0 P:  0.5 T: -0.2
   -102: R:  0.5 P:  0.5 T: -0.2
   -103: R: -1.0 P:  0.0 T: -0.2
   -104: R:  1.0 P:  0.0 T: -0.2
   -105: R: -0.5 P: -0.5 T: -0.2
   -106: R:  0.0 P: -0.5 T: -0.2
   -107: R:  0.5 P: -0.5 T: -0.2

   -108: R:  0.0 P:  0.0 T: -0.2
    '''
    code = str(code)#making sure code is string
    #elevation
    try:
        if code[0:2] == '00':
            T = 0
        elif code[0:2] == '10':
            T = strength #upward speed
        elif code[0:2] == '-1':
            T = -strength#descent speed
        else:
            print('invalid code')
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
    #move servos
    '''
    y(low PWM <- middlePWM -> high PWM of y motor)
    |
    |    . <-- starts at middle and can go in every direction
    |
    |_________ x(low PWM <- middlePWM -> high PWM of x motor)
    '''

def sensorservos(x,y):
    #moves sensor servos? maybe gyroscopes it
    # might end up deprecating if i dont gimbal the ultrasonics
    return
#calcualte Throttle and rudder/yaw
#throttle and rotation, yaw can be used as LIDAR type beat, can scan using all sensors and map surroundings, plot itslef within the space
#give direction/speed
#defaults:
#rudder: 0 (no spin)
#throttle: -1 (no throttle)
#aileron: 0 (no left/ right movement)
#elevator: 0 (no up/downward pitch)
def getsend():
    #called when client asks for server(drone) info
    return
hoverp = thrust.predict(895)[0]
def pushdata(data):
    buf = []
    #A = roll 0
    #E = pitch 1
    #T = throttle 2
    #R = yaw/spin 3
    print(int(data[2] * (1800-((1000*(hoverp/100))+1000)) + 1000+(1000*((hoverp)/100))))
    push16(buf, int(data[0] * 500 + 1500)) #test each individual axis
    push16(buf, int(data[1] * 500 + 1500))
    if int(data[2])<0:
        push16(buf, int(data[2] * (1000*(hoverp/100)) + 1000 + (1000*((hoverp)/100))))
    else:
        push16(buf, int(data[2] * (1800-((1000*(hoverp/100))+1000)) + 1000+(1000*((hoverp)/100)))) #1000-2000, y intercept is the hover%, calcuklated as 1000+(1000*(%)/100)
    push16(buf, int(data[3] * 500 + 1500))
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

def hovercalc(dheight=2):
    sensors = getsensory()
    strength = 0.1
    liftoffindoor(1)
    strt = time.perf_counter()
    while time.perf_counter()-strt<5:
        if sensors['height'] < dheight:
            strength
            pushdata(convert("",))

def liftoffindoor(dheight=2):
    strt = time.perf_counter()
    while True:
        if time.perf_counter()-strt<2:
            pushdata(convert('108',0.5))
        else:
            break

def hovertest():
    liftoff = True
    hover = False
    land = False
    A = 0
    x = 0
    y = 0
    path=[]
    strt = time.perf_counter()
    print('Started Liftoff sequence!')
    while True:
        if liftoff:
            code = '108'
            if time.perf_counter() - strt >= 5:
                hover = True

                print('Hovering!')
                strt = time.perf_counter()
                liftoff = False
            data = convert(code,0.5)
        if hover:
            code = '008'
            if time.perf_counter() - strt >= 5:
                land = True
                print("Landing!")
                strt = time.perf_counter()
                hover = False
            data = convert(code,0)
        if land:
            code = '-108'
            if time.perf_counter() - strt >= 5:
                print('Sequence over!')
                land = False    
                break
            data = convert(code,0.25)
        A += data[2]#replace with real location data
        y+= data[1]
        x+= data[0]
        plt.plot(path,color='green')
        plt.pause(0.05)
        path.append([A,y,x])
        pushdata(data)

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

reverselist=["",
'']

hovertest()
plt.show()
