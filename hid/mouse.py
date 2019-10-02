# The MIT License (MIT)
#
# Copyright (c) 2017 Dan Halbert
# Copyright (c) 2019 siikamiika
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from .usb_hid import usb_hid

class Mouse:

    LEFT_BUTTON   = 0b1
    RIGHT_BUTTON  = 0b10
    MIDDLE_BUTTON = 0b100
    BUTTON_4      = 0b1000
    BUTTON_5      = 0b10000
    BUTTON_6      = 0b100000

    def __init__(self):
        self.hid_mouse = None
        for device in usb_hid.devices:
            if device.usage_page == 0x01 and device.usage == 0x02:
                self.hid_mouse = device
                break
        if not self.hid_mouse:
            raise IOError("Could not find an HID mouse device.")

        # Reuse this bytearray to send mouse reports.
        # report[0] buttons pressed (LEFT, MIDDLE, RIGHT)
        # report[1] x movement
        # report[2] y movement
        # report[3] wheel movement
        # report[4] horizontal wheel movement
        self.report = bytearray(5)

    def press(self, buttons):
        self.report[0] |= buttons
        self._send_no_move()

    def release(self, buttons):
        self.report[0] &= ~buttons
        self._send_no_move()

    def release_all(self):
        self.report[0] = 0
        self._send_no_move()

    def click(self, buttons):
        self.press(buttons)
        self.release(buttons)

    def move(self, x=0, y=0, wheel=0, hwheel=0):
        # Send multiple reports if necessary to move or scroll requested amounts.
        while x != 0 or y != 0 or wheel != 0 or hwheel != 0:
            partial_x = self._limit(x)
            partial_y = self._limit(y)
            partial_wheel = self._limit(wheel)
            partial_hwheel = self._limit(hwheel)
            self.report[1] = partial_x & 0xff
            self.report[2] = partial_y & 0xff
            self.report[3] = partial_wheel & 0xff
            self.report[4] = partial_hwheel & 0xff
            self.hid_mouse.send_report(self.report)
            x -= partial_x
            y -= partial_y
            wheel -= partial_wheel
            hwheel -= partial_hwheel

    def _send_no_move(self):
        """Send a button-only report."""
        self.report[1] = 0
        self.report[2] = 0
        self.report[3] = 0
        self.report[4] = 0
        self.hid_mouse.send_report(self.report)

    @staticmethod
    def _limit(dist):
        return min(127, max(-127, dist))
