"""
See http://www.pjrc.com/teensy/td_libs_OctoWS2811.html for an introduction.

Part of this code was taken from:

OctoWS2811 movie2serial.pde - Transmit video data to 1 or more
Teensy 3.0 boards running OctoWS2811 VideoDisplay.ino
http://www.pjrc.com/teensy/td_libs_OctoWS2811.html
Copyright (c) 2013 Paul Stoffregen, PJRC.COM, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import struct

class OctoWS281XImageDataError(Exception):
    """Base class for exceptions raised in this module.
    """
    

class LedLayout(object):
    """Used when converting an image rectangle to individual LED data for each
    strip. Used if LED rows wrap on the same strip, e.g. led_height > 8.
    
    Constants used in OctoWS281XImageData
    """
    # Rows wrap from left to right
    LeftToRight = 0
    # Rows wrap from right to left
    RightToLeft = 1
    

class DisplayTrigger(object):
    """ Configuration options to control the start of the frame transmission
    from the teensy board. Explanations copied from the OctoWS2811 arduino code.
    
    Constants used in OctoWS281XImageData.
    """
    # Frame sync pulse to be sent a specified number of microseconds after
    # reception of the first byte (typically at 75% of the frame time, to allow
    # other boards to fully receive their data). Normally '*' is used when the
    # sender controls the pace of playback by transmitting each frame as it
    # should appear.
    AfterFirstByteWithDelay = "*"
    
    # Frame sync pulse to be sent  a specified number of microseconds after the
    # previous frame sync. Normally this is used when the sender  transmits
    # each frame as quickly as possible, and we control the pacing of video
    # playback by updating the LEDs based on time elapsed from the previous
    # frame.
    AfterPreviousFrameSyncWithDelay = "$"
    
    # Frame to be displayed when a frame sync pulse is received from another
    # board. In a multi-board system, the sender would normally transmit one '*'
    # or '$' message and '%' messages to all other boards, so every Teensy 3.0
    # updates at the exact same moment.
    OnFrameSync = "%"


class OctoWS281XImageData(object):
    """This class is a transcription of the processing "movie2serial" example
    in OctoWS2811. See license notice above. Named this way as the same signals
    work for both OctoWS2811 and OctoWS2812.
    
    This class can send data to a connected teensy device via a serial port;
    in that case, the program "OctoWS2811VideoDisplay" must be set on the
    board.
    """
    def __init__(self,
                 led_width,
                 led_height,
                 layout=LedLayout.LeftToRight,
                 led_offset_x=0,
                 led_offset_y=0,
                 num_ports_used=8):
        """
        :Args:
            led_width:
                number of pixels per row, same as LED_WIDTH in the
                OctoWS2811 arduino sketch.
            led_height:
                Must be a multiple of 8. See original explanation for LED_HEIGHT
                in the OctoWS2811 arduino sketch.
            layout:
                Strip layout. One of the public members of `LedLayout`.
            led_offset_x, led_offset_y:
                Horizontal and vertical offsets: identifies the top-left corner
                of the image to read, in the source image.
            num_ports_used:
                How many ports are actually connected on the teensy. Defaults to
                8 (all available ports are used). It is assumed that 'LED' ports
                (strips) 1 through num_ports_used are connected, and higher
                indices are not. Image lines corresponding to unused ports will
                not be read. 
        Note: led_width and led_height *must* match what is set on the teensy
        board, or no data will be displayed.
        """
        if led_height % 8 != 0:
            raise OctoWS281XImageDataError("Bad LED height specified! Expecting"
                                           " a multiple of 8.")
        self._led_width = led_width
        self._led_height = led_height
        self._layout = layout
        self._led_offset_x = led_offset_x
        self._led_offset_y = led_offset_y
        self._num_ports_used = num_ports_used
        
    def toByteArray(self, image):
        """
        converts an image to OctoWS2811's raw data format.
        The number of vertical pixels in the image must be a multiple of 8.
        
        :Args:
            image: 
                any object with a pixel(x, y) method that returns a (integral)
                RGB value. x values range from 0 to led_width - 1, y values from
                0 to led_height - 1.
        
        Note: this function is quite slow (takes 10-20ms for a small image for
        me). Use C?
        """
        data = bytearray()
        rowsPerPin = self._led_height / 8
        # Byte values per pixel
        pixel = [0] * 8
        
        for y in xrange(rowsPerPin):
            if (y & 1) == self._layout:
                # even numbered rows are left to right
                xbegin = 0
                xend = self._led_width
                xinc = 1
            else:
                # odd numbered rows are right to left
                xbegin = self._led_width - 1
                xend = -1
                xinc = -1
              
            for x in xrange(xbegin, xend, xinc):
                for i in xrange(8):
                    if i >= self._num_ports_used:
                        # There is no strip connected. But we still have to
                        # provide data for it.
                        pixel[i] = 0x000000
                    else:
                        # fetch 8 pixels from the image, 1 for each pin
                        image_x = x + self._led_offset_x
                        image_y = y + self._led_offset_y + rowsPerPin * i
                        rgb = image.pixel(image_x, image_y)
                        pixel[i] = self._colorWiring(rgb)
                # convert 8 pixels to 24 bytes
                for bit_index in xrange(23, -1, -1):
                    mask = 1 << bit_index
                    b = 0
                    for i in xrange(8):
                        if pixel[i] & mask:
                            b |= (1 << i)
                    data.append(b)
        return data
    
    def send(self,
             data,
             destination,
             delay_us=0,
             trigger=DisplayTrigger.AfterFirstByteWithDelay):
        """
        Convenience function to send image data to an opened file or device.
        
        :Args:
            data:
                Data returned by self.toByteArray().
            destination:
                An opened file or device, i.e. any object with a write()
                method.
            delay_us:
                Number of microseconds to wait after frame sync trigger, as an
                `int`. Maximum value of 65535 (~65ms). Ignored if trigger is
                set to "OnFrameSync".s
            trigger:
                One character, either "*", "$" or "%". Pass in one of the
                public members of the `DisplayTrigger` enumeration. Controls
                the timing of the frame sending.
        """
        # Little-endian, short.
        delay_us_bytes = struct.pack("<h", delay_us)
        destination.write(trigger)
        destination.write(delay_us_bytes)
        destination.write(data)
        destination.flush()
        
    def _colorWiring(self, c):
        """Translate the 24 bit color from RGB to the actual
        order used by the LED wiring.  GRB is the most common."""
        # GRB - most common wiring
        return (((c & 0xFF0000) >> 8) |
                 ((c & 0x00FF00) << 8) |
                 (c & 0x0000FF))
