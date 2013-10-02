This exexcutable measures the bandwidth available at the USB connection, from your computer or a raspberry Pi, say. The teensy boards should be set to continually get as much data as possible.
To run, first download sketch/UsbBandwidth.ino into your teensy(s). Or just read as much data as possible from the serial port! Then in this folder run::

    cmake .
    make

To compile, and then run it with::

  ./usbbandwidth /dev/ttyACM0

From the raspberry pi I have seen 262 kB/s for each teensy even when multiple ones are connected via a hub - not sure what to make of it as surely the total usb bandwidth should be limited?
From my computer, I get about 990kB/s for all teensys together. Connecting two teensys divides the transfer rate by half.
