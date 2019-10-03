#!/usr/bin/env python3

import sys
import socket
import base64
import time
import evdev
import struct
from select import select

from data.constants import *
from data.evdev_to_hid import *


HOST = 'raspberrypi'
PORT = 9888


def send(s, data):
    s.sendall(base64.b64encode(data) + b'\n')


class InputSource:
    def __init__(self, *device_paths):
        self.devices = [evdev.InputDevice(p) for p in device_paths]
        self.devices_by_fd = {dev.fd: dev for dev in self.devices}
        self.rel_events = dict(
            move=[],
            wheel=[],
        )

    def stream_events(self):
        while True:
            readable_fds, _, _ = select(self.devices_by_fd, [], [])
            for readable_fd in readable_fds:
                for event in self.devices_by_fd[readable_fd].read():
                    result = self.handle_event(event) # pylint: disable=assignment-from-no-return
                    if result is not None:
                        yield result.hid_encode()

            # send a single mouse event consisting of multiple smaller ones
            for hid_encoded_event in  self.combine_rel_events():
                yield hid_encoded_event

            # fixes some race condition or something
            time.sleep(0.005)

    def handle_event(self, event):
        event = EvdevToHidEvent.from_evdev_event(event)
        if event.get_hid_type() == INPUT_TYPE_REL:
            self.handle_rel(event)
            return None
        return event

    def handle_rel(self, event):
        if event.get_hid_code() == INPUT_CODE_MOVE:
            self.rel_events['move'].append(event)
        elif event.get_hid_code() == INPUT_CODE_WHEEL:
            self.rel_events['wheel'].append(event)

    def combine_rel_events(self):
        move_x = 0
        move_y = 0
        for event in self.rel_events['move']:
            if event.code == REL_X:
                move_x += event.value
            elif event.code == REL_Y:
                move_y += event.value
        self.rel_events['move'] = []
        if move_x or move_y:
            yield struct.pack('BBbb', INPUT_TYPE_REL, INPUT_CODE_MOVE, move_x, move_y)

        hwheel = 0
        wheel = 0
        for event in self.rel_events['wheel']:
            if event.code == REL_HWHEEL:
                hwheel += event.value
            elif event.code == REL_WHEEL:
                wheel += event.value
        self.rel_events['wheel'] = []
        if hwheel or wheel:
            yield struct.pack('BBbb', INPUT_TYPE_REL, INPUT_CODE_WHEEL, hwheel, wheel)



class EvdevToHidEvent:
    evdev_mouse_buttons = [
        BTN_LEFT,
        BTN_MIDDLE,
        BTN_RIGHT,
        BTN_SIDE,
        BTN_EXTRA,
    ]

    def __init__(self, code, type, value):
        self.code = code
        self.type = type
        self.value = value

    @staticmethod
    def from_evdev_event(event):
        return EvdevToHidEvent(event.code, event.type, event.value)

    def hid_encode(self):
        hid_type = self.get_hid_type()
        hid_code = self.get_hid_code()
        if hid_type == INPUT_TYPE_REL:
            val_x = 0
            val_y = 0
            if self.code in [REL_X, REL_HWHEEL]:
                val_x = self.value
            elif self.code in [REL_Y, REL_WHEEL]:
                val_y = self.value
            return struct.pack('BBbb', hid_type, hid_code, val_x, val_y)
        return None

    def get_hid_type(self):
        if (self.code in EvdevToHidEvent.evdev_mouse_buttons and
                self.type == EV_KEY and
                self.value in [0, 1]):
            return INPUT_TYPE_BTN
        elif self.type == EV_KEY and self.value in [0, 1]:
            return INPUT_TYPE_KEY
        elif self.type == EV_REL:
            return INPUT_TYPE_REL
        return None

    def get_hid_code(self):
        return EVDEV_TO_HID_CODE.get(self.code)


def main():
    input_source = InputSource(
        # we must go deeper
        '/dev/input/by-id/linux-virt-kbd',
        '/dev/input/by-id/linux-virt-mouse',
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for hid_encoded_event in input_source.stream_events():
            if hid_encoded_event:
                print(hid_encoded_event)
                send(s, hid_encoded_event)

if __name__ == '__main__':
    main()
