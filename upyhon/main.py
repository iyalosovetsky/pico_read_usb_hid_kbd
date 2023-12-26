from machine import UART, Pin
import   time

# Example using PIO to drive a set of WS2812 LEDs.


import rp2


from grblstate import GrblState
from smartKbd import SmartKbd


# for communicate with usb keyboard module
# keyboard module set keycode like this:
#  0x1 byte1 byte2 byte3 !byte1 !byte2 !byte3 0x2
#  for example 
#  0x1 0x1 0x0 0xa 0xfe 0xff 0xf5 0x2
#  where 
#    byte1 is ctrl 
#    byte2 is alt(0x04),ralt(0x40),ctrl(0x01),rctrl(0x10),shit(0x02),rctrl(0x20) , opt(0x08) , ropt(0x80) 
#    byte3 keycode - 'g' button

DEBUG = False

uartKBD = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
uartMPG = UART(0, baudrate=115200, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1))
txData = b'RS485 send test...\r\n'
print('RS485 send test...')

start_time=time.time()-1000

kbd=SmartKbd(uart_kbd=uartKBD)
st = GrblState(kbd=kbd, uart_grbl_mpg = uartMPG )
kbd.objGrblStateSetter(st)

start_time_q = time.time()



while True:
        st.neo.animate()
    #try:
        time.sleep(0.05) #50ms
        if time.time()-start_time_q>3:
            st.sent2grbl('?') # get status from grbl cnc machine
            start_time_q = time.time()

        while uartMPG.any() > 0:
            rxMPG = uartMPG.read()
            st.displayState(rxMPG.decode())
            
        while uartKBD.any() > 0:
            kbd.proceedChars(uartKBD.read(), DEBUG) 
                 
                    
            

                #rxdata = uart1.read()

#except Exception as e1:
    #    print("rt error",e1)


