#!/usr/bin/env python3

import re
import time
from hid.ctf_keyboard import Keyboard

keyboard = Keyboard()

with open('URGGGGGG.pcapng', 'rb') as f:
    raw = f.read()

time.sleep(5)
packets = [p[-8:] for p in re.findall(b'\x1b\x00.{33}', raw)]
for packet in packets:
    time.sleep(0.012)
    keyboard.send_report(packet)
