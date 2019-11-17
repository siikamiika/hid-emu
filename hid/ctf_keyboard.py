from .usb_hid import usb_hid

class Keyboard:
    def __init__(self):
        self.hid_keyboard = None
        for device in usb_hid.devices:
            if device.usage_page == 0x01 and device.usage == 0x06:
                self.hid_keyboard = device
                break
        if not self.hid_keyboard:
            raise IOError("Could not find an HID keyboard device.")

        # Reuse this bytearray to send keyboard reports.
        self.report = bytearray(8)

        # report[0] modifiers
        # report[1] unused
        # report[2:8] regular key presses

        # View onto byte 0 in report.
        self.report_modifier = memoryview(self.report)[0:1]

        # List of regular keys currently pressed.
        # View onto bytes 2-7 in report.
        self.report_keys = memoryview(self.report)[2:]

    def send_report(self, report):
        self.hid_keyboard.send_report(report)
