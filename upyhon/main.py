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








 
time.sleep(1)

start_time=time.time()-1000
ii=0

#


 

 









kbd=SmartKbd(uart_kbd=uartKBD)
st = GrblState(kbd=kbd, uart_grbl_mpg = uartMPG )


st.neo.clear()
st.neoText('GrblHAL', color = 'YELLOW', animate = 'window-left-right') 

 


start_time_q = time.time()



while True:
        st.neo.animate()
    #try:
        time.sleep(0.05) #50ms
        if time.time()-start_time_q>3:
            #uartMPG.write(('\r\n' if st.state == 'run' else '?').encode()  )
            #if time.time()-st._state_time_change>10:
            #    st.sent2grbl('')
            #    time.sleep(0.05) #50ms
            st.sent2grbl('?')
            # st.sent2grbl(KBD2GRBL.get('?' if st.state == 'jog' else '?','?'))
            start_time_q = time.time()

        while uartMPG.any() > 0:
            rxMPG = uartMPG.read()
            st.displayState(rxMPG.decode())
            
            
            
        while uartKBD.any() > 0:
            rxdata = uartKBD.read()
            # print("gets[string0 ->"," ".join(hex(n) for n in rxdata))
            for i in range(0, len(rxdata), 8):
                line1 = rxdata[i:i + 8] 
                l_char, l_shift, l_ctrl, l_caps = kbd.getKeyName(line1)
                # print("gets[string0/1 char ->",l_char,"error ->",l_ctrl,l_caps," ".join(hex(n) for n in line1))
                if l_char =='esc' or l_char =='pause' or l_char =='@' or l_char =='^' or \
                    l_char =='~' or l_char =='#' or l_char =='?' or l_char =='!' or \
                    l_char =='left' or l_char =='right' or l_char =='pageUp' or l_char =='pageDown' or \
                    l_char =='up' or l_char =='down' or \
                    l_char =='f1' or l_char =='f2' or l_char =='f3' or l_char =='f4' or \
                    l_char =='f5' or l_char =='f6' or l_char =='enter' or \
                    (l_char.startswith('ctrl-f') and len(l_char)>6) or (l_char.startswith('alt-f') and len(l_char)>5):
                    if l_char in ('~','!','?','#','^','@') or \
                        l_char =='left' or l_char =='right' or l_char =='pageUp' or l_char =='pageDown' or \
                        l_char =='up' or l_char =='down' or \
                        l_char =='f1' or l_char =='f2' or l_char =='f3' or l_char =='f4' or \
                        l_char =='f5' or l_char =='f6' or l_char =='esc' or l_char =='pause':
                        st.sent2grbl(kbd.chars2Grbl(l_char))
                        kbd.clear()
                        
                    elif l_char in ('enter'):
                        st.sent2grbl(kbd.getc())
                    elif l_char.startswith('ctrl-f') and len(l_char)>6:
                        st.sent2grbl(kbd.get_macro(l_char[5:]))
                        kbd.clear()
                    elif l_char.startswith('alt-f') and len(l_char)>5:
                        kbd.set_macro(l_char[4:])
                        st.neoShowEdit()
                elif l_char == 'space' or l_char =='shift space':
                    kbd.put_char(' ')
                    st.neoShowEdit()
                elif l_char == 'backspace' or l_char =='shift backspace':
                    kbd.backspace()
                    st.neoShowEdit()

                    
                    
                elif not(l_char.startswith('alt-') or l_char.startswith('shift-') or l_char.startswith('ctrl-') or l_char.startswith('opt-')
                          or l_char.startswith('ralt-') or l_char.startswith('rshift-') or l_char.startswith('rctrl-') or l_char.startswith('ropt-')):    
                    kbd.put_char(l_char) 
                    st.neoShowEdit()
                    
                    
                    
                    
            
            if DEBUG:
                try:
                    print("end of get ->",kbd.grblCommand, l_shift,hex(rxdata[1]),rxdata[2],rxdata[3],l_char)
                except Exception as e1:
                    print("rt error",e1)
                    
                print()
                #rxdata = uart1.read()

#except Exception as e1:
    #    print("rt error",e1)


