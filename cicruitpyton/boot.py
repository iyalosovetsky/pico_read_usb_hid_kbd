import board
import digitalio
import storage
import os
import usb_midi
import usb_cdc
import usb_hid

usb_midi.disable()
usb_cdc.enable(console=True, data=True)
usb_hid.enable(
    (usb_hid.Device.KEYBOARD,
     usb_hid.Device.MOUSE,
     usb_hid.Device.CONSUMER_CONTROL)
)
 
#storage.remount("/", readonly=False)

