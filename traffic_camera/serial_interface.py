# File name: serial_interface.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

import serial.tools.list_ports
import re
from time import monotonic
import json


# Initializations
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()



def connect_USB():
    """ Establishes a connection to a peripheral (radar)
    via serial interface."""

    portList = [str(onePort) for onePort in ports]
    print(portList)
    
    portVar = portList[0][0:12]
    print("Connected to USB Port: " + portVar + "!")
    
    if "ACM" not in portVar: # Connects OPS243 to ttyACM0 port
        raise Exception("Radar Sensor not detected!")
      
    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()


def _serial_read_json():
    """ Reads data into JSON format."""
    if serialInst.in_waiting:
        packet = serialInst.readline()
        data = packet.decode('utf').rstrip('\n')
        data = json.loads(data)
        
        print(abs(float(data["speed"]))) # reads speed key from OPS243
    

def _data_array(array_length, queue3):
    """ Store the bytes into a list of fixed size 'array_length'.
        
        This function is blocking, and will run until the list is full.
        
        Parameters:
        - array_length: integer that determines max size of list
        - queue3: queue that the data is put into. """
    if serialInst.in_waiting:
        print("Data is received!")
        speed_data_list = []
        for i in range(array_length):
                packet = serialInst.readline()
                data = float(packet.decode('utf').rstrip('\n'))      
                maxVal = max(abs(speed_data_list))
        queue3.put(maxVal)
        return (speed_data_list, maxVal) # Returns Tuple of entire array and max val
    else:
        return (None, None)


def data_array_any_amount(speed_limit, queue3, e):
    """ Store the bytes into a list of variable size 'array_length'.

        With a timeout, the function will run until there is a timeout.
        
        Parameters:
        - speed_limit: float variable that puts data exceeding this value
                       into queue3.
        - queue3: Queue object that receives speed data.
        - e: Event object that triggers on and off the camera_capture process.
    """
# This private function is a working improvement of data_array(),
# which aims to return arrays of variable array sizes.
    serialInst.timeout = 0.3
    
    if serialInst.in_waiting:
        
        print("Data is received!")
        speed_data_list = []
        
        sw = 0
        while sw == 0: # Begin reading from serial interface.
            packet = serialInst.readline()
            data = packet.decode('utf').rstrip('\r\n')
            
            if data != '': # If data is not empty string.
                
                data = json.loads(data)
                data = abs(float(data["speed"])) # Read value of key 'speed'.
                speed_data_list.append(data) # Append speed to list.
                
                maxVal = max(speed_data_list)
                
                if maxVal > speed_limit:
                    e.set() # Set Event object on, triggering camera_capture.
                    queue3.put(maxVal)
            else:
                sw = 1 # End data reading from serial interface.
                e.clear() # Set Event object off, ending camera_capture.
                
        return (speed_data_list, maxVal)
    else:
        return (None, None)




    
