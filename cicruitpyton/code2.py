import microcontroller
#microcontroller.cpu.frequency = 120000000
print(microcontroller.cpu.frequency)

import board
import array
import usb.core
import usb_host

import sys
import supervisor
import time
import adafruit_usb_host_descriptors 
from adafruit_sdcard import SDCard
import os

import digitalio
import busio
import storage

from grblstate import GrblState
from smartKbd import SmartKbd
from waveST7789 import WaveST7789
neo = WaveST7789()


sd_cs = digitalio.DigitalInOut(board.GP22)
sd_cs.direction = digitalio.Direction.OUTPUT
sd_cs.value = True

 
sdcard = SDCard(neo.spi, sd_cs,1000000)


vfs = storage.VfsFat(sdcard)

storage.mount(vfs, "/sd")


def sdDemo():
    for ff in os.listdir('/sd'):
        if True or ff.startswith("test") and ff.endswith(".txt"):
            try:
                os.unlink('/sd/'+ff)
                print('deleted ','"/sd/'+ff+'"')
            except Exception as e:
                print('cannot delete ','"/sd/'+ff+'"', e)
    with open("/sd/test1.txt", "w") as f:
        f.write("Hello world!\r\n")

    with open("/sd/test2.txt", "w") as f:
        f.write("Hello world!\r\n")
        f.write("This is a test\r\n")

    # Open the file we just created and read from it
    print('cat /sd/test2.txt')
    with open("/sd/test2.txt", "r") as file:
        data = file.read()
        print('    ',data)
    print(os.listdir('/sd'))

def usbDescDemo():
    if supervisor.runtime.usb_connected:
        print("USB<host>!")
    else:
        print("!USB<host>")

    device=None
    ff2=None
    ii=0
    while ii<100 and (device is None or ff2 is None):
        time.sleep(0.5)
        ff2=usb.core.find(find_all=True)
        device=usb.core.find()
        ii+=1
    print(ii,device,ff2)
    if device is None and ff2 is not None:
        print('point3')
        for k in ff2:
            print('point3',k)
            if k is not None:
                device= k
                break
    print('point2',ii,device,ff2)
    print("device------------")
    print("pid", hex(device.idProduct))
    print("vid", hex(device.idVendor))
    print("man", device.manufacturer)
    print("product", device.product)
    print("serial", device.serial_number)
    print("config[0]:")
    config_descriptor = adafruit_usb_host_descriptors.get_configuration_descriptor(
        device, 0
    )
    i = 0
    while i < len(config_descriptor):
        descriptor_len = config_descriptor[i]
        descriptor_type = config_descriptor[i + 1]
        if descriptor_type == adafruit_usb_host_descriptors.DESC_CONFIGURATION:
            config_value = config_descriptor[i + 5]
            print(f" value {config_value:d}")
        elif descriptor_type == adafruit_usb_host_descriptors.DESC_INTERFACE:
            interface_number = config_descriptor[i + 2]
            interface_class = config_descriptor[i + 5]
            interface_subclass = config_descriptor[i + 6]
            print(f" interface[{interface_number:d}]")
            print(
                f"  class {interface_class:02x} subclass {interface_subclass:02x}"
            )
        elif descriptor_type == adafruit_usb_host_descriptors.DESC_ENDPOINT:
            endpoint_address = config_descriptor[i + 2]
            if endpoint_address & 128:
                print(f"  IN {endpoint_address:02x}")
            else:
                print(f"  OUT {endpoint_address:02x}")
        i += descriptor_len
    print()

    print("Keyboard Reading device...")
    device.set_configuration(1)
    if device.is_kernel_driver_active(0):
        print('is_kernel_driver_active')
    #    try:
    #        ff.detach_kernel_driver(0)
    #    except:
    #        print('can not detach_kernel_driver')
            

    ar=array.array('I', [0 for i in range(10)])
    ii=0
    try:
        device.read(0x81, ar)
        print('ar',ar)
    except Exception as e:
        print('except read', e)
        
    for kk in range(256):
        try:
            device.read(ii, ar)
            print('ar',ii,ar)
        except Exception as e:
            #print('except read', e)
            pass
        





#------------------------------------
sdDemo()

pp=usb_host.Port(board.GP26, board.GP27)

uartMPG = busio.UART(board.GP0, board.GP1, baudrate=115200)

#usbDescDemo()








  
  




kbd=SmartKbd()
st = GrblState(kbd=kbd, uart_grbl_mpg = uartMPG,neo=neo )
kbd.objGrblStateSetter(st)


start_time_q =time.time()
start_time_cmd = time.time() 
uartMPG.write(bytearray(b'\x8b\r\n'))
DEBUG = True

while True:
  try:  
    if time.time()-start_time_q>3:
        #st.send2grbl('?') # get status from grbl cnc machine
        st.send2grblOne('?') # get status from grbl cnc machine
        start_time_q = time.time()
    mpgConsole=''
    ii_mpgCons=0     
    while ii_mpgCons<20:
        mpgConsolePart=uartMPG.read(100)
        ii_mpgCons +=1
        if mpgConsolePart is not None:
          start_time_q = time.time()
          mpgConsole+=mpgConsolePart.decode()
          #print(mpgCons)
        else:
          break
        time.sleep(0.1) 
    if mpgConsole is not None and mpgConsole!='': 
        if DEBUG:
            print('mpgConsole:',mpgConsole)
        st.displayState(mpgConsole)
    proceedCh=''    
    while supervisor.runtime.serial_bytes_available:
        start_time_q = time.time()
        proceedCh += sys.stdin.read(1)
    if proceedCh!='':
        if DEBUG:
            print('proceedCh:',proceedCh,[ord(res) for res in proceedCh])
        kbd.proceedChars(proceedCh, DEBUG)
    if time.time()-start_time_cmd>1:
        st.popCmd2grbl()
        start_time_cmd = time.time()    
    time.sleep(0.1)
  except KeyboardInterrupt:
        print('main: will cancel')
        st.send2grblOne('cancel')
       
        
            

  
#-----------------------------------------------

print("boot end.")
time.sleep(5)
splash = displayio.Group()
display.root_group = splash
odb = displayio.OnDiskBitmap('/purple.bmp')
face = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
splash.append(face)
display.refresh()
# Draw a label
#text_group = displayio.Group(scale=2, x=57, y=120)
#text = "Hello World!"
#text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
#text_group.append(text_area)  # Subgroup for text scaling
#splash.append(text_group)

 
while True:
    pass




display.refresh()
