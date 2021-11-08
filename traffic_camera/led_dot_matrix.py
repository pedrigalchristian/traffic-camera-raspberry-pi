# File name: led_dot_matrix.py
# Author: Christian Pedrigal (pedrigalchristian@gmail.com)
# Date created: 10/25/2021
# Date last modified: 10/25/2021
# Python Version: 1.1

from time import sleep

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT


# Initializations
serial = spi(port=0, device=0, gpio=noop())
led = max7219(serial, width=8, height=8, block_orientation= 90)
led.contrast(100)
virtual = viewport(led, width=32, height=8)


def display_text(text_1, time_on = 0):
    """ Displays 'text_1' onto the LED MAX7219 for 'time_on' seconds.

        If time_on is '0', the text will be displayed indefinitely. """

    with canvas(virtual) as draw:
        led.show()
        text(draw, xy = (0,1), txt = text_1, fill = "white",
                                        font=proportional(TINY_FONT))
        if time_on != 0:
            sleep(time_on)
            led.hide()


def flash_text(text_1, time_on, flashes):
    """ Flashes 'text_1' for a number 'flashes' of flashes
        with a delay of 'time_on' seconds."""

    for i in range(flashes):
        with canvas(virtual) as draw:
            led.show()
            text(draw, xy = (0,1), txt = text_1, fill = "white",
                                         font=proportional(TINY_FONT))
            sleep(time_on)
            led.hide()
            sleep(time_on)
                     
if __name__ == "__main__":           
    display_text("hi", 0)