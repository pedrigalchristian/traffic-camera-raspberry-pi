# File name: license_plate_recognition_API.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

import requests
import json
import re
import os
import time

from pprint import pprint

from .led_dot_matrix import display_text, flash_text, led


def LPR_to_file(queue, token, e):
    """ Reads data from queue, sends request to LPR, and writes to text file.

        Parameters:
        - queue: Queue object that receives data from move_files_to_path()
        - token: TOKEN from https://platerecognizer.com/
        - e: Event object that is set when move_files_to_path() is called """


    while True: # Runs daemon (background) process
        
        # Collect the data from the queue from move_files_to_path
        if not queue.empty() and e.is_set():
            new_file_list = queue.get()
            print(new_file_list)
            
            # Initializations
            carList = []
            filenames = []
            polling_time = 1
            count = 0
            missed = 0
            
            last_time = time.monotonic()
            path_ind = new_file_list[0].find("image")
            
            e.clear()
            
            # Runs the following block for each picture filename 
            while count < len(new_file_list):
                
                # Runs each code with a time delay of 'polling_time'
                # so that the HTTP request is not receiving too many
                # requests at one time.
                if time.monotonic() - last_time >= polling_time:
                    
                    # Context manager for sending requests
                    with open(new_file_list[count], 'rb') as fp:
                        
                        try: # Sends a HTTP POST request to the LPR url
                             # to analyze the pictures.
                            response = requests.post( 
                                'https://api.platerecognizer.com/' +
                                                'v1/plate-reader/',
                                files=dict(upload=fp), # data
                                headers={'Authorization': f'Token {token}'})
                        except:
                            print("No internet connection")
                            break
                    #pprint(response.json())
                    
                    # Raises exception if requests are sent too many at once.
                    if "status_code" in response.json():
                        raise Exception("Looking up too fast!")
                        time.sleep(2)
                        continue
                    else:
                        # If empty results are returned from LPR,
                        # add count to 'missed'.
                        if response.json()["results"] == []:
                            missed += 1
                            #os.remove(new_file_list[count])
                            # print(new_file_list[count], " deleted!")
                        
                        # If non-empty results are returned,
                        # add JSON response to carList list,
                        # and report the Processing Time.
                        elif response.json()["results"] != []:
                            filenames.append(new_file_list[count][path_ind::1])
                            carList.append(response.json())        
                        print("Processing Time for {}: ".format(
                                          new_file_list[count])
                                          + str(round((time.monotonic()
                                          - last_time),3))
                                          + " secs"
                                          )
                        last_time = time.monotonic()
                        count += 1
                        
            led.hide() # turn off LED
            pprint(carList)
            
            
            # Writes any successfully captured license plates to a textfile.
            results_count = range(len(carList))
            timestamps = [carList[x]["timestamp"] for x in results_count]
            plates = [carList[x]["results"][0]["plate"]
                                                  for x in results_count]
            dscores = [round(carList[x]["results"][0]["dscore"],4)
                                                  for x in results_count]
            xmins = [carList[x]["results"][0]["box"]["xmin"]
                                                  for x in results_count]
            xmaxs = [carList[x]["results"][0]["box"]["xmax"]
                                                  for x in results_count]
            xwidths = [(xmaxs[x] - xmins[x]) for x in range(len(xmins))]
            print(len(timestamps))

            if len(timestamps) != 0:
                path = new_file_list[0][0:path_ind]
                print(path)
                with open(path + 'LPR_Results.txt', 'w') as file:
                    print('Writing file...')
                    txt = "{5:>34}{1:^5}{0:>28}{1:^5}{2:>10}" + \
                                                "{1:^5}{3:<8}{1:^5}{4:>5}\n"
                    file.write(txt.format(
                        "Timestamps",
                        "|",
                        "Plates",
                        "D-Scores",
                        "X-Widths",
                        "Filename"
                            ))
                    for i in range(len(timestamps)):
                        file.write(txt.format(
                            timestamps[i], "|",
                            plates[i],
                            dscores[i],
                            xwidths[i],
                            filenames[i]))
                    file.write("%i / %i images analyzed" % (len(new_file_list)
                                                            - missed,
                                                            len(new_file_list)
                                                            )
                                                               )



