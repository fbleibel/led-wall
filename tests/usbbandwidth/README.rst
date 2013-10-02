This executable measures the bandwidth available at the USB connection. The teensy boards should be set to continually get as much data as possible.
To run, first download sketch/UsbBandwidth.ino into your teensy(s). Or just read as much data as possible from the serial port! Then in this folder run::

    cmake .
    make

To compile, and then run it with::

  ./usbbandwidth /dev/ttyACM0

* From the Raspberry Pi, the bandwidth maxes out at 262 kB/s for each Teensy - adding more Teensy doesn't change their individual transfer rates.
* From my laptop, I get about 990kB/s for all Teensys together which is reasonably close to the USB1 standard speed. Connecting two Teensys on the same USB port divides the transfer rate by half, but that doesn't happen if you connect them to different ports.
