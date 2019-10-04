import sys
sys.path.append('..')

from data.constants import *
from hid.mouse import Mouse as HIDMouse

EVDEV_KEY_TO_HID_CODE = {
    BTN_LEFT:   HIDMouse.LEFT_BUTTON,
    BTN_MIDDLE: HIDMouse.MIDDLE_BUTTON,
    BTN_RIGHT:  HIDMouse.RIGHT_BUTTON,
    BTN_SIDE:   HIDMouse.BUTTON_5,
    BTN_EXTRA:  HIDMouse.BUTTON_6,
}

EVDEV_REL_TO_HID_CODE = {
    REL_X:      INPUT_CODE_MOVE,
    REL_Y:      INPUT_CODE_MOVE,
    REL_WHEEL:  INPUT_CODE_WHEEL,
    REL_HWHEEL: INPUT_CODE_WHEEL,
}
