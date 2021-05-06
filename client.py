import socket as so
import time
import pygame
import detect
import pickle
import cv2
pygame.init()

s = so.socket()
port = 42069
#192.168.0.24
s.connect(('192.168.0.18',port)) #chnage to raspi ipp
s.setsockopt(so.IPPROTO_TCP, so.TCP_NODELAY, 1)
pygame.joystick.init()
j = pygame.joystick.Joystick(0)
j.init()
reading = True
r = False
l = False
f = False
b = False
u = False
d = False
spin = False
controlling = False
strength = 1
bytesent = 0
rate = 1/10 #framerate
ticks = 0
tick = 0
imgs = 0
strt = time.perf_counter()
processing = False
while reading:
    code = 'no'
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            v = round(event.value)
            if event.axis == 1:
                if v == -1:
                    r = True
                if v == 1:
                    l = True
                if v == 0:
                    r = False
                    l = False
            else:
                if v == -1:
                    f = True
                if v == 1:
                    b = True
                if v == 0:
                    f = False
                    b = False
        if event.type == pygame.JOYBUTTONDOWN:
            bu = event.button
            if bu == 0:
                u = True
            if bu == 1:
                spin = True
            if bu == 2:
                d = True
            if bu == 3:
                if controlling:
                    controlling = False
                else:
                    controlling = True
            if bu == 5:
                if strength == 1:
                    strength = 2
                elif strength == 2:
                    strength = 3
                elif strength == 3:
                    strength = 4
                elif strength == 4:
                    strength = 1
            if bu == 4:
                if not processing:
                    processing = True
                else:
                    processing = False
        if event.type == pygame.JOYBUTTONUP:
            bu = event.button
            if bu == 0:
                u = False
            if bu == 1:
                spin = False
            if bu == 2:
                d = False
        if event.type == pygame.QUIT:
            reading = False
    if controlling:
        if r and not f and not b:
            if not u and not d:
                code = '004'
            if u:
                code = '104'
            if d:
                code = '-104'
        if l and not f and not b:
            if not u and not d:
                code = '003'
            if u:
                code = '103'
            if d:
                code = '-103'
        if f and not r and not l:
            if not u and not d:
                code = '001'
            if u:
                code = '101'
            if d:
                code = '-101'
        if b and not r and not l:
            if not u and not d:
                code = '006'
            if u:
                code = '106'
            if d:
                code = '-106'
        if f and r:
            if not u and not d:
                code = '002'
            if u:
                code = '102'
            if d:
                code = '-102'
        if f and l:
            if not u and not d:
                code = '000'
            if u:
                code = '100'
            if d:
                code = '-100'
        if b and r:
            if not u and not d:
                code = '007'
            if u:
                code = '107'
            if d:
                code = '-107'
        if b and l:
            if not u and not d:
                code = '005'
            if u:
                code = '105'
            if d:
                code = '-105'
        if not f and not r and not l and not b:
            if not u and not d:
                code = '008'
            if u:
                code = '108'
            if d:
                code = '-108'
        if spin:
            code = '999'
    boxs=[]
    if processing:
        try:
            data = pickle.loads(data)
            data = cv2.imdecode(data, 1)
            boxs = detect.scan(data)
            #print(boxs)
        except Exception as e:
            print(e)
            pass
    msg = f'{code} {strength}'
    #preprocessing to be sent as bytes
    boxs = pickle.dumps(boxs)
    msg = pickle.dumps(msg)
    #choosing what message to send
    if tick == 0:
        s.send(msg)
    if tick == 1:
        s.send(boxs)
    data = s.recv(1161600)
    #byterate testing
    bytesent += len(data)+len(msg)
    byterate = round(bytesent/(time.perf_counter()-strt))
    print(f'byterate: {byterate/1000000}Mb/s') #change from total averdge to recent averdge (10sec)
    ticks+=1
    if ticks == 300:
        strt = time.perf_counter()
        bytesent = 0
        ticks = 0

    #end of loop code
    if tick == 0:
        tick = 1
    elif tick == 1:
        tick = 0
    time.sleep(rate)
