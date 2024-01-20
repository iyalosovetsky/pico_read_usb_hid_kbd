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

from grblstate import GrblState, SmartKbd
from waveST7789 import WaveST7789
neo = WaveST7789()


sd_cs = digitalio.DigitalInOut(board.GP22)
sd_cs.direction = digitalio.Direction.OUTPUT
sd_cs.value = True

 
sdcard = SDCard(neo.spi, sd_cs,1000000)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")



pp=usb_host.Port(board.GP26, board.GP27)

#uartMPG = busio.UART(board.GP0, board.GP1, baudrate=115200)
UART_BUF_SIZE=1960
uartMPG = busio.UART(board.GP0, board.GP1, baudrate=115200, receiver_buffer_size=UART_BUF_SIZE)

#usbDescDemo()








  
  




kbd=SmartKbd()
st = GrblState(kbd=kbd, uart_grbl_mpg = uartMPG,neo=neo )
kbd.objGrblStateSetter(st)



start_time_cmd = time.time() 

DEBUG = False

while True:
  try:  
    st.query4MPG()
    if st.need_query:
        st.send2grblOne('?') # get status from grbl cnc machine
    mpgConsole=''
    ii_mpgCons=0     
    while ii_mpgCons<20:
        mpgConsolePart=uartMPG.read(UART_BUF_SIZE)
        ii_mpgCons +=1
        if mpgConsolePart is not None:
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
        try:
            proceedCh += sys.stdin.read(1)
        except:
            pass    
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
