# hid-emu

A keyboard/mouse switch that works on a Raspberry Pi Zero over bridged ethernet or a Raspberry Pi Zero W over Wi-FI.

## Setting up

1. Flash Raspbian Lite on a Micro SD card
2. On the flashed card, edit
    - `/boot/config.txt` to have `dtoverlay=dwc2`
    - `/etc/modules` to have `dwc2` and `libcomposite`
    - `/etc/rc.local` to have ` /home/pi/hid-emu/usb_device_emu` before `exit 0`
    - `/etc/systemd/system/dhcpcd.service.d/wait.conf` to have `ExecStart=/usr/lib/dhcpcd5/dhcpcd -b -q %I` instead of the previous command. Speeds up boot by ~30 seconds when a DHCP server is not immediately available.
3. Boot the Pi with the card
4. If not using Wi-Fi, bridge the RNDIS interface with your ethernet interface to get LAN (and internet) access
5. Use your preferred method to secure the connection between `client.py` (ran on the device that has the keyboard) and `server.py` (ran on the Pi on boot). By default the connection is over plain TCP socket. Remember to edit `server.py` so that it doesn't listen to all interfaces.
6. Run client.py
