#!/usr/bin/python3
#
# File name: main.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

################################# Imports ####################################


# Standard library imports
from os import system
import multiprocessing as mp
import warnings

# Local application imports
from traffic_camera.serial_interface import connect_USB
from traffic_camera.serial_interface import data_array_any_amount
from traffic_camera.serial_interface import ports, serialInst

from traffic_camera.file_org import create_main_folder, current_date
from traffic_camera.file_org import create_timestamp_folder, remove_empty_dir
from traffic_camera.file_org import create_daily_folder, move_files_to_path

from traffic_camera.camera_config import capture_num_frames

from traffic_camera.led_dot_matrix import display_text, flash_text, led

import traffic_camera.license_plate_recognition_API as LPR

############################ Global Variables ################################

# User Arguments
# Please modify these arguments to your Traffic Speed Camera application.
# The `token` variable is from user account from: https://platerecognizer.com/
speed_limit = 10  # in mph
main_folder = "LPR Speed Photos"  # Name of your main directory
parent_directory = '/home/pi/Desktop/'  # Location of your main directory
token = 'b0d681034ef2a4b8d3db7e0813e440f4780e1519'

# Constants
DATA_BUFFER = 30  # size of speed_list
FLASH_TIME = 0.08
NUM_FLASH = 2
NUM_FLASH_LONG = 11
FLASH_PERSIST = 0
ERROR_STR = "ER"
############################## Initializations ###############################

# Clear all processes

# Establish serial interface with OPS243.
connect_USB() 

# Creation/Initialization of directories of traffic photos.
curr_directory = create_main_folder(main_folder, parent_directory)
daily_folder_path = ''
folder_path = ''

# Empty display of LED Matrix.
led.clear()

# Initialization of variables shared amongst processes.
speed_list = mp.Array('d', range(DATA_BUFFER))
max_speed_shared = mp.Value('d', 0.0)
max_speed = max_speed_shared.value

# Creation of multiprocessing queues.
queue_captured_pics = mp.JoinableQueue()
queue_pic_filenames = mp.JoinableQueue()
queue_captured_speed = mp.JoinableQueue()

# Creation/Initialization of muliprocessing events
event_radar_to_camera = mp.Event()
event_LPR_to_file_org = mp.Event()
event_radar_to_camera.clear()
event_LPR_to_file_org.set()

# Switch to run code snippet once.
sw = 0
################################# Main Program ###############################


if __name__ == "__main__":
    # Main program to run the traffic speed camera.
    
    while True:
        # Main loop for program.
        try:   
            
            # If this is the first time the program is being run for the day,
            # a new folder based on the current date will be created.
            (daily_folder_path, current_date) = create_daily_folder(
                                                            current_date,
                                                            curr_directory
                                                            )
            
            # Completes a process that removes all empty folders in daily folder
            remove_process = mp.Process(target = remove_empty_dir,
                                        args = (daily_folder_path,)
                                        )
            remove_process.start()
            remove_process.join()
 
            # This will return data only if data is received.
            # Otherwise, a a tuple of (None, None) is returned.
            (speed_list, max_speed) = data_array_any_amount(speed_limit,
                                                        queue_captured_speed,
                                                        event_radar_to_camera
                                                            )

            if sw == 0: # Runs following code snippet once:
                        # creation of daemon camera and LPR processes.
                
                # Create daemon process for LPR Recognition.
                LPR_process = mp.Process(target = LPR.LPR_to_file,
                                         args = (queue_pic_filenames,
                                                 token,
                                                 event_LPR_to_file_org
                                                 ),
                                         name = "LPR")
                LPR_process.daemon = True
                LPR_process.start()
                print("LPR Process started")
                
                # Create a daemon process of a camera capture.
                camera_process = mp.Process(target = capture_num_frames,
                                            args = (queue_captured_pics,
                                                    event_radar_to_camera,
                                                    queue_captured_speed
                                                    )
                                            )
                camera_process.daemon = True
                camera_process.start()
                print("Camera Process started")
                sw = 1
            
            # If there is data that is received...
            if (speed_list, max_speed) != (None, None):
                print(speed_list, max_speed)
                
                # And if the reported max speed is less than the speed limit...
                if max_speed <= speed_limit:
                    
                    # The LED Dot Matrix will flash several times.
                    flash_text(str(round(max_speed)), FLASH_TIME,
                                                               NUM_FLASH_LONG)
                    print("The captured speed %d mph was below speed limit."
                          % max_speed)
                    
                else:
                    
                    # The LED will flash and persist.
                    flash_text(str(round(max_speed)), FLASH_TIME, NUM_FLASH)
                    display_text(str(round(max_speed)), FLASH_PERSIST)
                    
                    # A timestamp is created for this camera capture.
                    folder_path = create_timestamp_folder(daily_folder_path)
                    print("Exceeded the {} mph speed limit at {} mph!" \
                                        .format(speed_limit, max_speed))
                    
                    # Transfer files from the daily folder  
                    # to the time stamp folder.  
                    move_files_to_path(queue_captured_pics,
                                       daily_folder_path,
                                       folder_path,
                                       queue_pic_filenames,
                                       event_LPR_to_file_org)
                    
        except KeyboardInterrupt:
            # Kill all daemon processes.
            system("sudo pkill python")
            warnings.warn("Killed all processes.")
            
        except:
            #warnings.warn("Keyboard interrupt was detected. Ending program now.")
            warnings.warn("Ending program now.")
            display_text(ERROR_STR)
            
            camera_process.join(1.0)
            LPR_process.join(3.0)
            warnings.warn("Terminated camera_process and LPR Process")
            sw = 0

        


    
        


                







        
