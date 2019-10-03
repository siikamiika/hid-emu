#!/usr/bin/env python3

import struct
import time
import socketserver
import threading
import base64

from hid.keyboard import Keyboard
from hid.mouse import Mouse


INPUT_TYPE_KEY = 0
INPUT_TYPE_BTN = 1
INPUT_TYPE_REL = 2

INPUT_CODE_MOVE = 0
INPUT_CODE_WHEEL = 1


class InputRouter:
    def __init__(self, keyboard=None, mouse=None, gamepad=None):
        self.keyboard = keyboard
        self.mouse = mouse
        self.gamepad = gamepad

    def route_input(self, payload):
        input_type, payload = payload[0], payload[1:]
        if input_type == INPUT_TYPE_KEY:
            self._handle_key(payload)
        elif input_type == INPUT_TYPE_BTN:
            self._handle_btn(payload)
        elif input_type == INPUT_TYPE_REL:
            self._handle_rel(payload)

    def _handle_key(self, payload):
        code, value = payload
        if value == 1:
            self.keyboard.press(code)
        elif value == 0:
            self.keyboard.release(code)

    def _handle_btn(self, payload):
        code, value = payload
        if value == 1:
            self.mouse.press(code)
        elif value == 0:
            self.mouse.release(code)

    def _handle_rel(self, payload):
        code, rel_x, rel_y = struct.unpack('Bbb', payload)
        if code == INPUT_CODE_MOVE:
            self.mouse.move(x=rel_x, y=rel_y)
        elif code == INPUT_CODE_WHEEL:
            self.mouse.move(wheel=rel_y, hwheel=rel_x)


def test_input_router():
    input_router = InputRouter(
        keyboard=Keyboard(),
        mouse=Mouse(),
    )
    input_router.route_input(b'\x00\x04\x01') # press A
    input_router.route_input(b'\x00\x04\x00') # release A
    input_router.route_input(b'\x01\x01\x01') # press left mouse button
    time.sleep(0.1)
    input_router.route_input(b'\x02\x00\x7f\x7f') # move mouse 127 pixels down and right
    time.sleep(0.1)
    input_router.route_input(b'\x01\x01\x00') # release left mouse button


class InputServerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = base64.b64decode(self.rfile.readline())
        while data:
            self.server.input_router.route_input(data)
            data = base64.b64decode(self.rfile.readline())


class InputServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    def __init__(self, *args, **kwargs):
        self.input_router = kwargs.pop('input_router')
        super(InputServer, self).__init__(*args, **kwargs)


def test():
    test_input_router()


def main():
    input_router = InputRouter(
        keyboard=Keyboard(),
        mouse=Mouse(),
    )
    input_server = InputServer(('', 9888), InputServerHandler, input_router=input_router)
    input_server.serve_forever()

if __name__ == "__main__":
    main()
