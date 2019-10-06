#!/usr/bin/env python3
import re

ROW_VALID_PART_PATT = re.compile(r'[0-9a-f, ]{2,}')
HEX_PATT = re.compile(r'[0-9a-z]{2}')

with open('descriptors.txt') as f:
    blocks = f.read().split('\n\n')


cmd = "python -c \"with open('functions/hid.usb0/report_desc', 'wb') as f: f.write(b'{}')\""
buff = ""

for block in blocks:
    for line in block.splitlines():
        if line.strip()[0] == '#':
            continue
        clean_line = ROW_VALID_PART_PATT.match(line)
        if clean_line is None:
            continue
        for char in HEX_PATT.findall(clean_line.group(0)):
            buff += f'\\x{char}'

print(cmd.format(buff))
