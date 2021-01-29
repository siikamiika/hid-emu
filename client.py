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
        for dev in self.devices:
            dev.grab()
        self.devices_by_fd = {dev.fd: dev for dev in self.devices}
        self.rel_events = {
            INPUT_CODE_MOVE: [],
            INPUT_CODE_WHEEL: [],
        }

    def stream_events(self):
        while True:
            readable_fds, _, _ = select(self.devices_by_fd, [], [])
            for readable_fd in readable_fds:
                for event in self.devices_by_fd[readable_fd].read():
                    result = self.handle_event(event) # pylint: disable=assignment-from-no-return
                    if result is not None:
                        yield result.hid_encode()

            # send a single mouse event consisting of multiple smaller ones
            for hid_encoded_event in self.combine_rel_events():
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
        hid_code = event.get_hid_code()
        if hid_code in self.rel_events:
            self.rel_events[hid_code].append(event)

    def combine_rel_events(self):
        for hid_code, evdev_code_x, evdev_code_y in (
            (INPUT_CODE_MOVE,  REL_X,      REL_Y),
            (INPUT_CODE_WHEEL, REL_HWHEEL, REL_WHEEL),
        ):
            move = {evdev_code_x: 0, evdev_code_y: 0}
            for event in self.rel_events[hid_code]:
                move[event.code] += event.value
            self.rel_events[hid_code] = []
            while move[evdev_code_x] or move[evdev_code_y]:
                x_part = min(127, max(-127, move[evdev_code_x]))
                y_part = min(127, max(-127, move[evdev_code_y]))
                move[evdev_code_x] -= x_part
                move[evdev_code_y] -= y_part
                yield struct.pack('BBbb', INPUT_TYPE_REL, hid_code, x_part, y_part)


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
        if hid_type in [INPUT_TYPE_KEY, INPUT_TYPE_BTN]:
            return struct.pack('BBB', hid_type, hid_code, self.value)
        elif hid_type == INPUT_TYPE_REL:
            val_x = 0
            val_y = 0
            if self.code in [REL_X, REL_HWHEEL]:
                val_x = self.value
            elif self.code in [REL_Y, REL_WHEEL]:
                val_y = self.value
            return struct.pack('BBbb', hid_type, hid_code, val_x, val_y)
        return None

    def get_hid_type(self):
        if (self.type == EV_KEY and
                self.code in EvdevToHidEvent.evdev_mouse_buttons and
                self.value in [0, 1]):
            return INPUT_TYPE_BTN
        elif self.type == EV_KEY and self.value in [0, 1]:
            return INPUT_TYPE_KEY
        elif self.type == EV_REL:
            return INPUT_TYPE_REL
        return None

    def get_hid_code(self):
        if self.type == EV_KEY:
            if self.code == KEY_HENKAN:
                return EVDEV_KEY_TO_HID_CODE.get(KEY_RIGHTALT)
            if self.code == KEY_KATAKANAHIRAGANA:
                return EVDEV_KEY_TO_HID_CODE.get(KEY_BACKSPACE)
            return EVDEV_KEY_TO_HID_CODE.get(self.code)
        elif self.type == EV_REL:
            return EVDEV_REL_TO_HID_CODE.get(self.code)


def main():
    input_source = InputSource(
        # we must go deeper
        '/dev/input/by-id/windows-virt-kbd',
        '/dev/input/by-id/windows-virt-mouse',
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        for hid_encoded_event in input_source.stream_events():
            if hid_encoded_event:
                print(hid_encoded_event)
                send(s, hid_encoded_event)

if __name__ == '__main__':
    main()
