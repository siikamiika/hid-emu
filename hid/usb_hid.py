# The MIT License (MIT)
#
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

HID_KEYBOARD_DEVICE = '/dev/hidg0'
HID_MOUSE_DEVICE = '/dev/hidg1'

class HidKeyboard:
    report_id = 0x01
    usage_page = 0x01
    usage = 0x06

    @classmethod
    def send_report(cls, report):
        with open(HID_KEYBOARD_DEVICE, 'wb') as f:
            f.write(bytes([cls.report_id]) + report)


class HidMouse:
    report_id = 0x02
    usage_page = 0x01
    usage = 0x02

    @classmethod
    def send_report(cls, report):
        with open(HID_MOUSE_DEVICE, 'wb') as f:
            f.write(bytes([cls.report_id]) + report)


class usb_hid:
    devices = [
        HidKeyboard,
        HidMouse,
    ]
