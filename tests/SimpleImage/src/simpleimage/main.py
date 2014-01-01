import os
import re
import sys
import time
from argparse import ArgumentParser
from PyQt4 import QtCore, QtGui
from simpleimage.data import OctoWS281XImageData, DisplayTrigger

# Pixels per row
NUM_PIXELS_H = 72
# Pixels per column
NUM_PIXELS_V = 36
# Teensy boards controlling tiles
NUM_TEENSY = 3
# Number of rows (2 * number of strips)
ROWS_PER_TEENSY = NUM_PIXELS_V / NUM_TEENSY

TEENSY_DATA_PATTERN = ("^LED_WIDTH=(\d+),LED_HEIGHT=(\d+),"
                       "LED_OFFSET_X=(\d+),LED_OFFSET_Y=(\d+),"
                       "LED_LAYOUT=(\d+),NUM_PORTS_USED=(\d+)$")

def process(path, device_names):
    """
    Process the image and send it to a teensy board.
    """
    print "Reading {0}".format(path)
    image = QtGui.QImage(path)
    if image.isNull():
        print "Error opening {0}!".format(path)
        return 1
    if image.width() != NUM_PIXELS_H or image.height() != NUM_PIXELS_V:
        print "Resizing to {0}x{1} (original size: {2}x{3})".format(
            NUM_PIXELS_H, NUM_PIXELS_V, image.width(), image.height())
        image = image.scaled(NUM_PIXELS_H, NUM_PIXELS_V)
    
    
    for device_index, device_name in enumerate(device_names):
        # Must open two files, one for reading and one for writing.
        # Use universal newline support - arduino's serial ends lines with \r\n. 
        serial_in = open(device_name, "rU")
        serial_out = open(device_name, "w", buffering=0)
        
        # Rows wrap once for each strip.
        with serial_in, serial_out:
            print "Asking {0} for information...".format(device_name)
            serial_out.write("?")
            serial_out.flush()

            line = ''
            while not line:            
                line = serial_in.readline()
                if not line:
                    continue
                match = re.match(TEENSY_DATA_PATTERN, line)
                if match:
                    led_width = int(match.group(1))
                    led_height = int(match.group(2))
                    led_offset_x = int(match.group(3))
                    led_offset_y = int(match.group(4))
                    layout = int(match.group(5))
                    num_ports_used = int(match.group(6))
                    print "\tTeensy says: {0}".format(match.group(0))
            
            image_data = OctoWS281XImageData(
                led_width, led_height, layout, led_offset_x, led_offset_y,
                num_ports_used)
            print "\tSending frame"
            start = time.time()
            data = image_data.toByteArray(image)
            print "\tComputed image data in {0:.1f}ms".format(
                1000 * (time.time() - start))
            start = time.time()
            # The first teensy board will send the frame sync signal.
            #if device_index == 0:
            trigger = DisplayTrigger.AfterFirstByteWithDelay
#             else:
#                 trigger = DisplayTrigger.OnFrameSync
            # Wait 10ms before frame sync
            image_data.send(data, serial_out, 0, trigger)
            serial_out.flush()
            print "\tFrame sent in {0:.1f}ms\n".format(
                1000 * (time.time() - start))
    print "Shutting down."
    return 0
    
def main():
    """
    """
    parser = ArgumentParser()
    parser.add_argument("path", help="Path to the image to send")
    parser.add_argument("devices",
                        help="Name of the serial port(s) corresponding to "
                        "the teensy boards to send the image to. Max {0}. If "
                        "nothing is provided, will be automatically determined."
                        .format(NUM_TEENSY),
                        nargs="*")

    args = parser.parse_args()    
    if args.devices:
        devices = args.devices
    else:
        devices = []
        for i in xrange(256):
            device_name = "/dev/ttyACM{0}".format(i)
            if os.path.exists(device_name):
                devices.append(device_name)
        print "Found {0} terminal devices to connect to.".format(len(devices))
    if len(devices) == 0:
        print "Dry run..."
    return process(args.path, devices)
    
if __name__ == "__main__":
    sys.exit(main())\

