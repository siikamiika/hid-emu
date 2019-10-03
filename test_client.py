#!/usr/bin/env python3

import socket
import base64
import time

HOST = 'raspberrypi'
PORT = 9888

def send(s, data):
    s.sendall(base64.b64encode(data) + b'\n')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    send(s, b'\x00\x04\x01') # press A
    send(s, b'\x00\x04\x00') # release A
    send(s, b'\x01\x01\x01') # press left mouse button
    time.sleep(0.1)
    send(s, b'\x02\x00\x7f\x7f') # move mouse 127 pixels down and right
    time.sleep(0.1)
    send(s, b'\x01\x01\x00') # release left mouse button
