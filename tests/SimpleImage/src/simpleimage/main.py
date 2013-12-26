import os
from argparse import ArgumentParser
from PyQt4 import QtCore, QtGui

# Pixels per row
NUM_PIXELS_H = 72
# Pixels per column
NUM_PIXELS_V = 36
# Teensy boards controlling tiles
NUM_TEENSY = 3
# Number of rows (2 * number of strips)
ROWS_PER_TEENSY = NUM_PIXELS_V / NUM_TEENSY



def process(path, device_names):
    print "Reading {0}".format(path)
    image = QtGui.QImage(path)
    if image.width() != NUM_PIXELS_H or image.height() != NUM_PIXELS_V:
        print "Resizing to {0}x{1} (original size: {2}x{3})".format(
            NUM_PIXELS_H, NUM_PIXELS_V, image.width(), image.height())
        image = image.scaled(NUM_PIXELS_H, NUM_PIXELS_V)
    for device_name in device_names:
        with open(device_name, "w") as device:
            device.write("*")
            # Wait 10ms before frame sync
            us = 10 * 1000
            device.write(us & 0xFF00 >> 8)
            device.write(us & 0xFF)
            device.write(data)
    
def main():
    """
    """
    app = QtCore.QCoreApplication([])
    parser = ArgumentParser()
    parser.add_argument("path", help="Path to the image to send")
    parser.add_argument("devices",
                        help="Name of the serial port(s) corresponding to "
                        "the teensy boards to send the image to. Max {0}"
                        .format(NUM_TEENSY),
                        nargs="+")
    args = parser.parse_args()
    process(args.path, args.devices)
    
if __name__ == "__main__":
    main()

