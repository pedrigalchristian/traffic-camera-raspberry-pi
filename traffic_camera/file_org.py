# File name: file_org.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

import os
import shutil
from datetime import datetime
import xlwt


current_date = datetime.now()


def create_main_folder(main_folder, parent_directory):
    """ Creates a main directory for the the photo storage."""

    sub_directory = os.path.join(parent_directory, main_folder)
    os.chdir(parent_directory)
    
    if not os.path.exists(sub_directory):
        os.mkdir(main_folder)
        print("Created new daily folder!")
    
    os.chdir(sub_directory)
    return sub_directory


def create_daily_folder(current_date, sub_directory):
    """ Creates a child directory for every new day the program is run.""" 
    
    date = datetime.now()
    
    if current_date == date:
        return curent_date
    else:
        
        # Creation of daily folder filename.
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        folder_name = "{}{}{}".format(year,month,day)
        
        # Creation of full path to daily folder.
        full_path = os.path.join(sub_directory, folder_name) 
        os.chdir(sub_directory)
        
        # Creates new daily folder if doesn't exist already.
        if not os.path.exists(full_path):
            os.mkdir(folder_name)
            
        os.chdir(full_path)
        return (full_path, date)
    
    
def create_timestamp_folder(path):
    """ Creates a child directory named after the current time HH.MM. """

    # Creation of timestamp folder filename.
    date = datetime.now()
    hour = date.strftime("%H")
    minute = date.strftime("%M")
    second = date.strftime("%S")
    folder_name = '{}.{}.{}'.format(hour,minute,second)
    
    # Creation of full path to timestamp folder.
    subfolder = os.path.join(path,folder_name)
    os.chdir(path)
    
    # Creates new daily folder if doesn't exist already.
    if not os.path.exists(subfolder):
        os.mkdir(folder_name)
        
    os.chdir(subfolder)
    return subfolder


def move_files_to_path(queue_0, old_path, desired_path, queue_1, e1):
    """ Appends filenames to desired path, and places into queue."""
    
    # Receives filenames from queue from camera_capture_process
    file_list = []
    while not queue_0.empty():
        file_list = queue_0.get()
        # print(file_list)
    
    # Appends filenames to desired directory path
    new_file_list = [os.path.join(desired_path, file) for file in file_list]
    # _append_to_excel(new_file_list)
    
    # Moves file to desired directory
    for file in file_list:
            shutil.move(os.path.join(old_path, file),
                        os.path.join(desired_path, file))
    
    # Sends full file names to queue for LPR process
    queue_1.put(new_file_list)
    e1.set()
 
 
def remove_empty_dir(folder_path):
    """ Deletes all empty folders and subfolders of given folder_path."""

    walk = list(os.walk(folder_path))
    for path, _, _ in walk[::-1]:
        if path != folder_path and len(os.listdir(path)) == 0:
                os.rmdir(path)
                print("Empty folders deleted!")


def _append_to_excel(array):
    """ Creates an Excel sheet for filenames."""
    wb = xlwt.Workbook()
    sheet1 = wb.add_sheet("Sheet 1")
    style = xlwt.easyxf("alignment: wrap on")
    col = 0
    for i in range(len(array)):
        sheet1.write(i, col, array[i], style)
    wb.save("Camera_Pics.xls")