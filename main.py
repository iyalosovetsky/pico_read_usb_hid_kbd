from machine import UART, Pin
import time



uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
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
    [b'pageUp', b'shift pageUp'], # 0x4b 
    [b'del', b'shift del'], # 0x4c 
    [b'end', b'shift end'], # 0x4d 
    [b'pageDown', b'shift pageDown'], # 0x4e 
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

def getKeyName(rxData):
    l_char=''
    l_shift=0
    l_ctrl=0
    l_caps=0
    if not(rxData[0]==1 and len(rxData)%8==0 and len(rxData)>=8 and rxData[7]==2):
       return l_char, l_shift,-1,-1
    if not(rxData[1]|rxData[4]==255 and rxData[2]|rxData[5]==255 and rxData[3]|rxData[6]==255):    
       return l_char, l_shift,-1,-2
    l_ctrl=rxData[2]
    l_caps=rxData[1]
    if (rxData[3]==0x50 or (rxData[3]==0x5c and rxData[1] & 1 == 0)): #left 
        l_char='left'     
    elif (rxData[3]==0x4f or (rxData[3]==0x5e and rxData[1] & 1 == 0)): #rigth
        l_char='rigth'     
    elif (rxData[3]==0x52 or (rxData[3]==0x60 and rxData[1] & 1 == 0)): #up
        l_char='up'     
    elif ((rxData[3]==0x61 and rxData[1] & 1 == 0)): #pageUp
        l_char='pageUp'     
    elif ((rxData[3]==0x5b and rxData[1] & 1 == 0)): #pageDown
        l_char='pageDown'     
    elif ((rxData[3]==0x5f and rxData[1] & 1 == 0)): #home
        l_char='home'     
    elif ((rxData[3]==0x59 and rxData[1] & 1 == 0)): #end
        l_char='end'     
    elif ((rxData[3]==0x62 and rxData[1] & 1 == 0)): #end
        l_char='insert'     
    elif ((rxData[3]==0x63 and rxData[1] & 1 == 0)): #del
        l_char='del'     
    elif (rxData[3]==0x51 or (rxData[3]==0x5a and rxData[1] & 1 == 0)): #down
        l_char='down'     
    elif (rxData[3]==0x28 or (rxData[3]==0x58 and rxData[1] & 1 == 0)): #enter
        l_char='enter'     
    else: 
        if (rxData[2] & 0xdd)==0: ## no shift noalt 
            if not(rxData[3]>=0x59 and rxData[3]<=0x63):
                l_shift= 1 if ((rxData[2] & 0x22)>0) else 0
                if (rxData[1] & 0x02):
                    l_shift ^=1 
            l_char=HID_KEYCODE_TO_ASCII[rxData[3]][l_shift].decode()        
        else:    
            l_char +=('r' if (rxData[2] & 0x40) else '')+('alt-' if (rxData[2] & 0x44) else '')
            l_char +=('r' if (rxData[2] & 0x10) else '')+('ctrl-' if (rxData[2] & 0x11) else '')
            l_char +=('r' if (rxData[2] & 0x20) else '')+('shift-' if (rxData[2] & 0x22) else '')
            l_char +=('r' if (rxData[2] & 0x80) else '')+('opt-' if (rxData[2] & 0x88) else '')
            l_char +=HID_KEYCODE_TO_ASCII[rxData[3]][0].decode() 
    return l_char, l_shift, l_ctrl, l_caps


COMMAND=''
MACROS={}


while True:
        time.sleep(0.05) #50ms
        if time.time()-start_time>120:
            ii +=1
            start_time = time.time()
            print("point1",ii,start_time)
        while uart1.any() > 0:
            rxdata = uart1.read()
            print("gets[string0 ->"," ".join(hex(n) for n in rxdata))
            for i in range(0, len(rxdata), 8):
                line1 = rxdata[i:i + 8] 
                l_char, l_shift, l_ctrl, l_caps = getKeyName(line1)
                print("gets[string0/1 char ->",l_char,"error ->",l_ctrl,l_caps," ".join(hex(n) for n in line1))
                if l_char =='esc' or l_char =='~' or l_char =='!' or l_char =='enter' or (l_char.startswith('ctrl-f') and len(l_char)>6) or (l_char.startswith('alt-f') and len(l_char)>5):
                    if l_char in ('~','!'):
                        COMMAND=l_char
                        print('command/hold->',COMMAND)
                        COMMAND=''
                    elif l_char in ('esc'):
                        COMMAND=''  
                    elif l_char in ('enter'):
                        print('command->',COMMAND)
                        COMMAND=''
                    elif l_char in ('backspace'):
                        COMMAND =COMMAND[0:-1]
                    elif l_char.startswith('ctrl-f') and len(l_char)>6:
                        COMMAND=MACROS.get(l_char[5:],'')
                        print('command/restrore F macro->',l_char[5:],'<-',COMMAND)
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

            print("gets[string2 ->",COMMAND, l_shift,hex(rxdata[1]),rxdata[2],rxdata[3],l_char)
            print()
