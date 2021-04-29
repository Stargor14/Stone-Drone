#!/usr/bin/env python

from msp import MultiWii
from util import push16
import time

board = MultiWii("/dev/ttyACM0") #__init__ takes teh serial port, get from arduino IDE
print("Flight Controller connected!")

time.sleep(1.0)

board.enable_arm()
board.arm()

#need function or taking in sensory data and processing
#need diff modes for flying, set path, gps to gps, follow the dots (using camera), random patrol (indoor using sensors), hover at ALTITUDE, etc etc

def calcTR():
    #calcualte Throttle and rudder/yaw
    return 0,-1

def calcAE():
    #calculate Aileron/roll and elevator/?
    return 0,0

def run():
    while True:
        # This is raw control function, logic can be handled in a diff function

        # calculate roll, pitch, yaw and throttle from dpad positions
        # 0 being centre, -1 being far left and 1 being far right.
        # 0 being centre, -1 being at the bottom and 1 being at the top.
        x, y = calcTR()
        throttle = (y + 1.0) / 2.0 #throttle
        rudder = x #yaw

        x, y = calcAE()
        aileron = x #roll
        elevator = y #? figure out

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
