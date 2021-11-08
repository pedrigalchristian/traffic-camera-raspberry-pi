""" Testing Serial Read for OPS with OY feature."""

import serial_interface

serial_interface.connect_USB()

if __name__ == "__main__":
    
    while True:
        serial_interface._serial_read_json()
    