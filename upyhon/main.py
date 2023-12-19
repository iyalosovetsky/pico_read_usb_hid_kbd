from machine import UART, Pin
import array, time

# Example using PIO to drive a set of WS2812 LEDs.


import rp2


from grblstate import GrblState


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

HID_KEYCODE_TO_ASCII =[
    [b'\x00', b'\x00'], # 0x00 
    [b'\x00', b'\x00'], # 0x01  
    [b'\x00', b'\x00'], # 0x02  
    [b'g'   , b'G'    ], # 0x03  
    [b'a'   , b'A'    ], # 0x04 
    [b'b'   , b'B'    ], # 0x05 
    [b'c'   , b'C'    ], # 0x06 
    [b'd'   , b'D'    ], # 0x07 
    [b'e'   , b'E'    ], # 0x08 
    [b'f'   , b'F'    ], # 0x09 
    [b'g'   , b'G'    ], # 0x0a 
    [b'h'   , b'H'    ], # 0x0b 
    [b'i'   , b'I'    ], # 0x0c 
    [b'j'   , b'J'    ], # 0x0d 
    [b'k'   , b'K'    ], # 0x0e 
    [b'l'   , b'L'    ], # 0x0f 
    [b'm'   , b'M'    ], # 0x10 
    [b'n'   , b'N'    ], # 0x11 
    [b'o'   , b'O'    ], # 0x12 
    [b'p'   , b'P'    ], # 0x13 
    [b'q'   , b'Q'    ], # 0x14 
    [b'r'   , b'R'    ], # 0x15 
    [b's'   , b'S'    ], # 0x16 
    [b't'   , b'T'    ], # 0x17 
    [b'u'   , b'U'    ], # 0x18 
    [b'v'   , b'V'    ], # 0x19 
    [b'w'   , b'W'    ], # 0x1a 
    [b'x'   , b'X'    ], # 0x1b 
    [b'y'   , b'Y'    ], # 0x1c 
    [b'z'   , b'Z'    ], # 0x1d 
    [b'1'   , b'!'    ], # 0x1e 
    [b'2'   , b'@'    ], # 0x1f 
    [b'3'   , b'#'    ], # 0x20 
    [b'4'   , b'$'    ], # 0x21 
    [b'5'   , b'%'    ], # 0x22 
    [b'6'   , b'^'    ], # 0x23 
    [b'7'   , b'&'    ], # 0x24 
    [b'8'   , b'*'    ], # 0x25 
    [b'9'   , b'('    ], # 0x26 
    [b'0'   , b')'    ], # 0x27 
    [b'\r'  , b'\r'   ], # 0x28 
    [b'esc', b'esc' ], # 0x29 esc
    [b'backspace'  , b'shift backspace'   ], # 0x2a 
    [b'\t'  , b'\t'   ], # 0x2b 
    [b'space'   , b'shift space'    ], # 0x2c 
    [b'-'   , b'_'    ], # 0x2d 
    [b'='   , b'+'    ], # 0x2e 
    [b'['   , b'{'    ], # 0x2f 
    [b']'   , b'}'    ], # 0x30 
    [b'\\'  , b'|'    ], # 0x31 
    [b'#'   , b'~'    ], # 0x32 
    [b';'   , b':'    ], # 0x33 
    [b"'"   , b'"'    ], # 0x34 
    [b'`'   , b'~'    ], # 0x35 
    [b','   , b'<'    ], # 0x36 
    [b'.'   , b'>'    ], # 0x37 
    [b'/'   , b'?'    ], # 0x38 
    [b'\x00', b'\x00'], # 0x39 
    [b'f1', b'f1'], # 0x3a 
    [b'f2', b'f2'], # 0x3b 
    [b'f3', b'f3'], # 0x3c 
    [b'f4', b'f4'], # 0x3d 
    [b'f5', b'f5'], # 0x3e 
    [b'f6', b'f6'], # 0x3f 
    [b'f7', b'f7'], # 0x40 
    [b'f8', b'f8'], # 0x41 
    [b'f9', b'f9'], # 0x42 
    [b'f10', b'f10'], # 0x43 
    [b'f11', b'f11'], # 0x44 
    [b'f12', b'f12'], # 0x45 
    [b'prtScr', b'prtScr'], # 0x46 
    [b'scrollLock', b'scrollLock'], # 0x47 
    [b'pause', b'pause'], # 0x48 
    [b'insert', b'shift insert'], # 0x49 
    [b'home', b'shift home'], # 0x4a 
    [b'pageUp', b'pageUp'], # 0x4b [b'pageUp', b'shift pageUp'], # 0x4b 
    [b'del', b'shift del'], # 0x4c 
    [b'end', b'shift end'], # 0x4d 
    [b'pageDown', b'pageDown'], # 0x4e #[b'pageDown', b'shift pageDown'], # 0x4e 
    [b'\x00', b'\x00'], # 0x4f 
    [b'\x00', b'\x00'], # 0x50 
    [b'\x00', b'\x00'], # 0x51 
    [b'\x00', b'\x00'], # 0x52 
    [b'\x00', b'\x00'], # 0x53 
    [b'/'   , b'/'    ], # 0x54 
    [b'*'   , b'*'    ], # 0x55 
    [b'-'   , b'-'    ], # 0x56 
    [b'+'   , b'+'    ], # 0x57 
    [b'\r'  , b'\r'   ], # 0x58 
    [b'1'   , b'!'], # 0x59 
    [b'2'   , b'@'], # 0x5a 
    [b'3'   , b'#'], # 0x5b 
    [b'4'   , b'$'], # 0x5c 
    [b'5'   , b'%'], # 0x5d 
    [b'6'   , b'^'], # 0x5e 
    [b'7'   , b'&'], # 0x5f 
    [b'8'   , b'*'], # 0x60 
    [b'9'   , b'('], # 0x61 
    [b'0'   , b')'], # 0x62 
    [b'.'   , b'%'], # 0x63 
    [b'\x00', b'\x00'], # 0x64 
    [b'\x00', b'\x00'], # 0x65 
    [b'\x00', b'\x00'], # 0x66 
    [b'='   , b'='   ] # 0x67  
]






 
time.sleep(1)

start_time=time.time()-1000
ii=0

#


def getKeyName(kbdData):
    l_char=''
    l_shift=0
    l_ctrl=0
    l_caps=0
    if not(kbdData[0]==1 and len(kbdData)%8==0 and len(kbdData)>=8 and kbdData[7]==2):
       return l_char, l_shift,-1,-1
    if not(kbdData[1]|kbdData[4]==255 and kbdData[2]|kbdData[5]==255 and kbdData[3]|kbdData[6]==255):    
       return l_char, l_shift,-1,-2
    l_ctrl=kbdData[2]
    l_caps=kbdData[1]
    l_scan=kbdData[3]
    l_numlockOff = (l_caps & 1 == 0)
    if (l_scan==0x50 or (l_scan==0x5c and l_numlockOff)): #left 
        l_char='left'     
    elif (l_scan==0x4f or (l_scan==0x5e and l_numlockOff)): #right
        l_char='right'     
    elif (l_scan==0x52 or (l_scan==0x60 and l_numlockOff)): #up
        l_char='up'     
    elif ((l_scan==0x61 and l_numlockOff)): #pageUp
        l_char='pageUp'     
    elif ((l_scan==0x5b and l_numlockOff)): #pageDown
        l_char='pageDown'     
    elif ((l_scan==0x5f and l_numlockOff)): #home
        l_char='home'     
    elif ((l_scan==0x59 and l_numlockOff)): #end
        l_char='end'     
    elif ((l_scan==0x62 and l_numlockOff)): #end
        l_char='insert'     
    elif ((l_scan==0x63 and l_numlockOff)): #del
        l_char='del'     
    elif (l_scan==0x51 or (l_scan==0x5a and l_numlockOff)): #down
        l_char='down'     
    elif (l_scan==0x28 or (l_scan==0x58 and l_numlockOff)): #enter
        l_char='enter'     
    else: 
        if (l_ctrl & 0xdd)==0: ## no shift noalt 
            if not(l_scan>=0x59 and l_scan<=0x63):
                l_shift= 1 if ((l_ctrl & 0x22)>0) else 0
                if (l_caps & 0x02):
                    l_shift ^=1 
            l_char=HID_KEYCODE_TO_ASCII[l_scan][l_shift].decode()        
        else:    
            l_char +=('r' if (l_ctrl & 0x40) else '')+('alt-' if (l_ctrl & 0x44) else '')
            l_char +=('r' if (l_ctrl & 0x10) else '')+('ctrl-' if (l_ctrl & 0x11) else '')
            l_char +=('r' if (l_ctrl & 0x20) else '')+('shift-' if (l_ctrl & 0x22) else '')
            l_char +=('r' if (l_ctrl & 0x80) else '')+('opt-' if (l_ctrl & 0x88) else '')
            l_char +=HID_KEYCODE_TO_ASCII[l_scan][0].decode() 
    return l_char, l_shift, l_ctrl, l_caps

def flashKbdLeds(p_leds_mask: int , p_macro_n: int):
    # kk=0x17     #7 - 3 leds       # 1 - macro1
    #print ("flashKbdLeds:", p_leds_mask , p_macro_n)
    kk=(p_macro_n&15)*16 | (p_leds_mask&15)
    cmd[1]=kk
    cmd[2]=255-kk
    uartKBD.write(cmd)
    # print("sended 0 ->"," ".join(hex(n) for n in cmd))


LED_SCROLLLOCK =  0x04
LED_CAPSLOCK = 0x02
LED_NUMLOCK = 0x01
LED_ALL = LED_SCROLLLOCK + LED_CAPSLOCK + LED_NUMLOCK

BLINK_2 = 1
BLINK_5 = 2
BLINK_INFINITE = 3
NOBLINK = 4








#jog $J=G91 X0 Y-5 F600
#$J=G91 X1 F100000


st = GrblState(cb_flashKbdLEDs=flashKbdLeds, uart_grbl_mpg = uartMPG )

st.neo.pixels_fill(st.neo.BLACK)
st.neo.animate(p_type='left-cycle', p_delay=0.3)
st.neo.pixels_show()
st.neo.text('GrblHAL', 0, 0, st.neo.YELLOW)
st.neo.pixels_show()
st.neo.animate(p_type='window-left-right')



            






            

    
    






COMMAND=''
MACROS={}
KBD2GRBL ={
    'left':'-y',
    'right':'+y',
    'pageUp':'-z',
    'pageDown': '+z',
    'up':'+x', 
    'down':'-x', 
    'f1': '-stepXY',
    'f2': '+stepXY', 
    'f3': '-stepZ',
    'f4': '+stepZ',
    'f5': '-feed',
    'f6': '+feed',
    'esc': 'cancel',
    '~':'~',
    '!':'!',
    '?':'?',
    '#':'#',
    '$':'$',
    '@':'@'

}

cmd=bytearray(  [0x01,0x01,0xFE,0x02])
start_time_q = time.time()



while True:
        st.neo.animate()
    #try:
        time.sleep(0.05) #50ms
        if time.time()-start_time_q>3:
            uartMPG.write(('?' if st.state == 'jog' else '?').encode()  )
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
                l_char, l_shift, l_ctrl, l_caps = getKeyName(line1)
                # print("gets[string0/1 char ->",l_char,"error ->",l_ctrl,l_caps," ".join(hex(n) for n in line1))
                if l_char =='esc' or l_char =='@' or l_char =='$' or \
                    l_char =='~' or l_char =='#' or l_char =='?' or l_char =='!' or \
                    l_char =='left' or l_char =='right' or l_char =='pageUp' or l_char =='pageDown' or \
                    l_char =='up' or l_char =='down' or \
                    l_char =='f1' or l_char =='f2' or l_char =='f3' or l_char =='f4' or \
                    l_char =='f5' or l_char =='f6' or l_char =='enter' or \
                    (l_char.startswith('ctrl-f') and len(l_char)>6) or (l_char.startswith('alt-f') and len(l_char)>5):
                    if l_char in ('~','!','?','#','$','@') or \
                        l_char =='left' or l_char =='right' or l_char =='pageUp' or l_char =='pageDown' or \
                        l_char =='up' or l_char =='down' or \
                        l_char =='f1' or l_char =='f2' or l_char =='f3' or l_char =='f4' or \
                        l_char =='f5' or l_char =='f6' or l_char =='esc':
                        st.sent2grbl(KBD2GRBL.get(l_char,l_char))
                        COMMAND=''                        
                        
                    elif l_char in ('enter'):
                        st.sent2grbl(COMMAND)
                        COMMAND=''
                        
                    elif l_char in ('backspace'):
                        COMMAND =COMMAND[0:-1]

                    elif l_char.startswith('ctrl-f') and len(l_char)>6:
                        COMMAND=MACROS.get(l_char[5:],'')
                        print('command/restore F macro->',l_char[5:],'<-',COMMAND)
                        COMMAND=''
                    elif l_char.startswith('alt-f') and len(l_char)>5:
                        print('command/set F macro->',l_char[4:],'=',COMMAND)
                        MACROS[l_char[4:]]=COMMAND
                        COMMAND=''
                elif l_char in ('space'):
                    COMMAND +=' '
                    
                elif not(l_char.startswith('alt-') or l_char.startswith('shift-') or l_char.startswith('ctrl-') or l_char.startswith('opt-')
                          or l_char.startswith('ralt-') or l_char.startswith('rshift-') or l_char.startswith('rctrl-') or l_char.startswith('ropt-')):    
                    COMMAND +=l_char
                    
                    
                    
            
            if DEBUG:
                try:
                    print("end of get ->",COMMAND, l_shift,hex(rxdata[1]),rxdata[2],rxdata[3],l_char)
                except Exception as e1:
                    print("rt error",e1)
                    
                print()
                #rxdata = uart1.read()

#except Exception as e1:
    #    print("rt error",e1)


