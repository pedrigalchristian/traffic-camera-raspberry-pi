# File name: camera_config.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

from picamera import PiCamera
import time


def capture_num_frames(send_queue, e1, receive_queue):
    """ Create camera object and start background process for camera capture

    Parameters:
    - send_queue: puts pictures into queue for future access with Queue.get()
    - e1: an event that triggers the continuous camera capture, which runs
          indefinitely until e1 is cleared using the Event.clear()
          in data_array_any_amount() function.
    - receive_queue: receives max_speed data and parses value
                     into picture filename
    """

    # Camera Initializations
    camera = PiCamera()
    camera.zoom = (0.35, 0.35, 0.30, 0.30)
    # camera.color_effects = (128,128) # black and white
    camera.contrast = 13
    #camera.shutter_speed = 8000
    camera.exposure_mode = 'sports'
    # camera.iso = 400
    
    
    # Runs background process
    while True:

        if e1.is_set():
            
            pic_array = []
            max_speed = receive_queue.get()

            for i, filename in enumerate(camera.capture_continuous(
                                    'image{counter:02d}_max_speed%02d.mph.jpg'
                                                                % max_speed)):
               pic_array.append(filename)
               print(f"{filename} created!")
               if not e1.is_set():
                   break # Ends camera capture process
                
            send_queue.put(pic_array) # Puts array of images into queue
        else: pass


