#!/usr/bin/env python
import serial
from msp import MultiWii
from util import push16
import time

ser = serial.Serial('COM4', 9600)# serial port for sensory arduino
board = MultiWii("/dev/ttyACM0") #__init__ takes the serial port, get from arduino IDE
print("Flight Controller connected!")
#GPS Waypoint Navigation, Live Stream Video, Altitude Hold, Position Hold, Return to Home, random patrol, follow (some bright color) ball
#Telemetry via Bluetooth

time.sleep(1.0)

board.enable_arm()
board.arm()

#need function or taking in sensory data and processing
#need diff modes for flying, set path, gps to gps, follow the dots (using camera), random patrol (indoor using sensors), hover at ALTITUDE, etc etc

def take_sensory():
    #take sensory data from ultrasonics
    #also take the current picth yaw etc, ordered 2 gyros for a reason (not rlly this is lucky af)
    sensory=[]
    return sensory

def camservos(x,y):
    #will move camera servos to desired position to x,y
    '''
    y(low PWM <- middlePWM -> high PWM of y motor)
    |
    |    . <-- starts at middle and can go in every direction
    |
    |_________ x(low PWM <- middlePWM -> high PWM of x motor)
    '''
    return

def sensorservos(x,y):
    #moves sensor servos? maybe gyroscopes it
    # might end up deprecating if i dont gimbal the ultrasonics
    return

def calcTRAE():
    #calcualte Throttle and rudder/yaw
    #throttle and rotation, yaw can be used as LIDAR type beat, can scan using all sensors and map surroundings, plot itslef within the space
    #give direction/speed
    #defaults:
    #rudder: 0 (no spin)
    #throttle: -1 (no throttle)
    #aileron: 0 (no left/ right movement)
    #elevator: 0 (no up/downward pitch)

    return 0,-1,0,0

def run():
    while True:
        # This is raw control function, logic can be handled in a diff function

        # calculate roll, pitch, yaw and throttle from dpad positions
        # 0 being centre, -1 being far left and 1 being far right.
        # 0 being centre, -1 being at the bottom and 1 being at the top.
        x1, y1 , x2, y2 = calcTRAE()
        rudder = x1 #yaw
        throttle = (y1 + 1.0) / 2.0 #throttle
        aileron = x2 #roll
        elevator = y2 #pitch

        # roll, pitch, yaw, throttle, aux1, aux2, aux3, aux4
        # each modulate from 1000 to 2000
        buf = []
        push16(buf, int(aileron * 500 + 1500)) #test each individual axis
        push16(buf, int(elevator * 500 + 1500))
        push16(buf, int(throttle * 1000 + 1000))
        push16(buf, int(rudder * 500 + 1500))
        push16(buf, 1500)
        push16(buf, 1000) #these will end up being servo, might have to make gyro function by myself
        push16(buf, 1000)
        push16(buf, 1000) #buf is just a serialized string of all the inforamtiuon being sent, check out util.py to verify

        # send rc command
        board.sendCMD(MultiWii.SET_RAW_RC, buf)
        time.sleep(0.025)

        # print board attitude
        board.getData(MultiWii.ATTITUDE)
        print(board.attitude)
        time.sleep(0.025)
