import serial
import pickle
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600)# serial port for sensory arduino
    ser.flush()
except Exception as e:
    ser = serial.Serial('/dev/ttyUSB1', 9600)
    ser.flush()
while True:
    by = ser.readline()
    if len(by)>10:
        try:
            print(by.decode())
        except:
            pass