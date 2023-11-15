Read input from a USB keyboard connected to the Raspberry Pi Pico Micro-USB port, via an OTG cable

Based on code from https://github.com/raspberrypi/pico-examples/tree/master/usb/host/host_cdc_msc_hid and https://github.com/No0ne/ps2pico

and 
based on code from https://github.com/vruivo/pico_read_usb_keyboard

1. Added NumLock CapsLock ScrollLock, Leds  

2. Hidden debug output

3. Fixed 0xa ("g" symbol)

4. The data in raw

5. Micropython code for catch keycodes.

<img src="/pico_read_usb_otg.png" width=65%>


