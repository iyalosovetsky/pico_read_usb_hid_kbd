import microcontroller
#microcontroller.cpu.frequency = 120000000
print(microcontroller.cpu.frequency)

import board
import usb_host
import usb
import sys
import supervisor
import time
import adafruit_usb_host_descriptors 
from adafruit_sdcard import SDCard
from  fourwire import FourWire
import os







import digitalio
from digitalio import DigitalInOut, Direction, Pull
import busio
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_st7789 import ST7789
import storage

bl_pin = digitalio.DigitalInOut(board.GP13)
bl_pin.direction=digitalio.Direction.OUTPUT
bl_pin.value=1

 

displayio.release_displays()

#spi = board.SPI()
if 'spi' in dir():
    try:
        spi.deinit()
    except:
        print('cannot deinit spi')
        
spi = busio.SPI(board.GP10, board.GP11, board.GP12) #busio.SPI(clock, MOSI, MISO)
sd_cs = digitalio.DigitalInOut(board.GP22)
sd_cs.direction = digitalio.Direction.OUTPUT
sd_cs.value = True



tft_cs = board.GP9
tft_dc = board.GP8
tft_reset=board.GP15



#sdcard = SDCard(spi, sd_cs)
#sdcard = SDCard(spi, sd_cs,500000)
sdcard = SDCard(spi, sd_cs,1000000)


vfs = storage.VfsFat(sdcard)

storage.mount(vfs, "/sd")

for ff in os.listdir('/sd'):
    if ff.startswith("test") and ff.endswith(".txt"):
        try:
            os.unlink('/sd/'+ff)
            print('deleted ','"/sd/'+ff+'"')
        except Exception as e:
            print('cannot delete ','"/sd/'+ff+'"', e)


with open("/sd/test1.txt", "w") as f:
    f.write("Hello world!\r\n")
    
    

#with open('purple.bmp','rb') as f1:
#    with open('/sd/purple.bmp','wb') as f2:
#       while True:
#          b=f1.read(1024)
#          if b: 
#             # process b if this is your intent   
#             n=f2.write(b)
#          else: break

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
 


display = ST7789(display_bus, width=320, height=240, rotation=270)
display.auto_refresh = True
print("Hello World!")
print(os.listdir('/sd'))
with open("/sd/test2.txt", "w") as f:
    f.write("Hello world!\r\n")
    f.write("This is a test\r\n")




 
# Open the file we just created and read from it
print('cat /sd/test2.txt')
with open("/sd/test2.txt", "r") as file:
    data = file.read()
    print('    ',data)
print(os.listdir('/sd'))

import board
import array

#------------------------------------
import sys
import supervisor
import time
import adafruit_usb_host_descriptors 

import usb.core
import usb_host    

pp=usb_host.Port(board.GP26, board.GP27)
if supervisor.runtime.usb_connected:
  print("USB<host>!")
else:
  print("!USB<host>")
  
  
ff=None
ff2=None
ii=0
while ii<100 and (ff is None or ff2 is None):
    time.sleep(0.5)
    ff2=usb.core.find(find_all=True)
    ff=usb.core.find()
    ii+=1
print(ii,ff,ff2)
if ff is None and ff2 is not None:
    print('point3')
    for k in ff2:
        print('point3',k)
        if k is not None:
            ff= k
            break
print('point2',ii,ff,ff2)        
print("Keyboard Reading ff...")
ff.set_configuration(1)
if ff.is_kernel_driver_active(0):
    print('is_kernel_driver_active')
    try:
        ff.detach_kernel_driver(0)
    except:
        print('can not detach_kernel_driver')
        

ar=array.array('I', [0 for i in range(10)])
ii=0

try:
    ff.read(0x81, ar)
    print('ar',ii,ar)
except Exception as e:
    print('except read', e)
    


while True:
   print(sys.stdin.read(1))

  
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