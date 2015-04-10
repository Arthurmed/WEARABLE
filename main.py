import ble
import matlab
from multiprocessing import Queue, Process
import socket
import threading
import time
import datetime


#communication with matlab
monitor = matlab.MONITOR()

def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')


def generate_event():

    monitor.send_data('EVENT')


def main():
    #connect with wearable
    a = ble.BLE('COM11', 9600)
    devices = a.get_devices()
    if a._CONNECTED == False:
        a.connect_device(devices)
    t1 = threading.Thread(target=generate_event)


    for i in range(10000):

        data = a.read_data()  # read data from BLE object
        frame = ';'.join([timestamp(), data])
        print frame
        monitor.send_data(frame)
        time.sleep(0.1)
    a.disconnect()

main()