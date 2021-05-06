import cv2
import numpy as np
import time
import pandas as pd
import random
thres = 0.5 # Threshold to detect object

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
cap.set(10,70)

classNames= []
classFile = 'coco.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

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
#buf = video('soccer.mp4')
#for img in buf:
frametimes = []
def getimg():
    success,img = cap.read()
    return img
color = [[random.randint(100,255) for x in range(3)] for x in range(30)]
def scan(img):
    ft = pd.Series(frametimes).mean()
    strt = time.perf_counter()
    people = 0
    boxs = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    classIds, confs, bbox = net.detect(img,confThreshold=thres)
    if len(frametimes)>1:
        cv2.putText(img,f'{round(1/ft)} FPS',(10,40),font,1,color[10],2)
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            i = classNames[classId-1]
            if i == 'person' or i == 'cat' or i == 'car':
                cv2.rectangle(img,box,color=color[len(boxs)-1],thickness=2)
                cv2.line(img,(320,240),(round(box[0]+box[2]/2),round(box[1]+box[3]/2)),color[len(boxs)-1],2)
                cv2.line(img,(0,round(box[1]+box[3]/2)),(620,round(box[1]+box[3]/2)),color[len(boxs)-1],2)
                cv2.line(img,(round(box[0]+box[2]/2),0),(round(box[0]+box[2]/2),480),color[len(boxs)-1],2)
                cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),font,1,color[len(boxs)-1],2)
                cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),font,1,color[len(boxs)-1],2)
                boxs.append(box)
    frametimes.append(time.perf_counter()-strt)
    cv2.imshow("Drone Vision",img)
    cv2.waitKey(1)
    return boxs
