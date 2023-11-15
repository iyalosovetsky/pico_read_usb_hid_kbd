'''
 ##@name：		RS485_send.py
 ##@auther:		waveshare team
 ##@info:		This code has configured a serial port of Pico to connect to our PICO-2CH-RS485, 			which will continuously emit an incremental data.	
    originally found on cnczone.nl, posted by Rikkepic:
    http://cnczone.nl/viewtopic.php?f=35&t=11605

    Parameters

    PD001   2   RS485 Control of run commands
    PD002   2   RS485 Control of operating frequency
    PD023   1   Reverse run enabled
    PD163   1   RS485 Address: 1
    PD164   1   RS485 Baud rate: 9600
    PD165   3   RS485 Mode: RTU, 8N1

    == Function Read ==

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x01    0x03    0xA5    0x00 0x00   0x2C 0x6D       Read PD165 (165=0xA5)

    == Function Write ==

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x02    0x03    0x03    0x09 0xC4   0x8F 0x8D       Write PD003 (0x9C4 = 2500 = 25.00Hz)

    == Control Write ==

    ADDR    CMD     LEN     DATA    CRC
    0x01    0x03    0x01    0x01    0x31 0x88                   Start spindle clockwise

    ADDR    CMD     LEN     DATA    CRC
    0x01    0x03    0x01    0x08    0xF1 0x8E                   Stop spindle

    ADDR    CMD     LEN     DATA    CRC
    0x01    0x03    0x01    0x11    0x30 0x44                   Start spindle counter-clockwise

    == Control Read ==

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x04    0x03    0x00    0x00 0x00   0xF0 0x4E       Read Frequency

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x04    0x03    0x02    0x00 0x00   0x51 0x8E       Read Output Current

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x04    0x03    0x03    0x00 0x00   0x00 0x4E       Read Rotation

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x04    0x03    0x04    0x00 0x00   0xB1 0x8F       Read DC Volatge

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x04    0x03    0x05    0x00 0x00   0xE0 0x4F       Read AC Voltage

    ADDR    CMD     LEN     PAR     DATA        CRC
    0x01    0x04    0x03    0x07    0x00 0x00   0x41 0x8F       Read Temperature

    == Control Read ==

    ADDR    CMD     LEN     DATA        CRC
    0x01    0x05    0x02    0x09 0xC4   0xBF 0x0F               Write Frequency (0x9C4 = 2500 = 25.00HZ)

'''



from machine import UART, Pin
import time

#uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))


def modbusCrc(msg:str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


#uart0 = UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
a=0
txData = b'RS485 send test...\r\n'
#uart0.write(txData)
print('RS485 send test...')
time.sleep(0.1)
START_SPINDLE=bytearray([0x01,0x03,0x01,0x01,0x31,0x88])
STOP_SPINDLE=bytearray( [0x01,0x03,0x01,0x08,0xF1,0x8E])
#RPM_SPINDLE1=bytearray(  [0x01,0x05,0x02,0x09,0xC4,0xBF,0x0F]) # Write Frequency (0x9C4 = 2500 = 25.00HZ)
#RPM_SPINDLE2=bytearray(  [0x01,0x05,0x02,0x09,0xC4,0xBF,0x0F]) # Write Frequency (0x9C4 = 2500 = 25.00HZ)
#RPM_SPINDLE3=bytearray(  [0x01,0x05,0x02,0x09,0xC4,0xBF,0x0F]) # Write Frequency (0x9C4 = 2500 = 25.00HZ)
RPM_SPINDLE=bytearray(  [0x01,0x05,0x02,0x09,0xC4,0xBF,0x0F]) # Write Frequency (0x9C4 = 2500 = 25.00HZ)
GET_SPINDLE=bytearray(  [ 0x01, 0x04, 0x03, 0x00, 0x00, 0x00 ]) #01 04 03 00 CRC
#                  gets -> 0x1   0x3   0x1   0x9  0x30  0x4e   0x1  0x3 0x1 0x0 0xf0 0x48
#                              0   1     2    3     x      x          
FREQS =[6000,7000,8000,9000,12000]
#100 6000
#200 12000

commands=[STOP_SPINDLE,START_SPINDLE,RPM_SPINDLE,GET_SPINDLE]
commands_desc=['STOP_SPINDLE','START_SPINDLE','RPM_SPINDLE','GET_SPINDLE']
time.sleep(2)
# while True:
#     offset=a%4
#     #rpm=6000+(offset-2)*4000
#     print("\n",a)
#     cmd=commands[offset]
#     crc = modbusCrc(cmd[0:len(cmd)-2])
#     cmd[len(cmd)-2]=crc%256
#     cmd[len(cmd)-1]=crc//256
#     time.sleep(0.05) #50ms
#     while uart1.any() > 0:
#                 rxData = uart1.read()
#                 print("gets11 ->"," ".join(hex(n) for n in rxData))
#     print(commands_desc[offset]," ".join(hex(n) for n in cmd))
#     if offset==2 : # for set rpm
#         for hz in FREQS:
#             #hz = rpm / 60 * 100;
#             rpm =int(hz /60)*100;
#             cmd[3]=rpm//256
#             cmd[4]=rpm%256
#             print("rpm=",rpm,hz)
#             crc = modbusCrc(cmd[0:len(cmd)-2])
#             cmd[len(cmd)-2]=crc%256
#             cmd[len(cmd)-1]=crc//256
#             print("0x%04X"%(crc))
#             print("rpm ->",commands_desc[offset]," ".join(hex(n) for n in cmd))
#             #uart0.write(cmd)
#             uart1.write(cmd)
#             time.sleep(0.05) #50ms
#             while uart1.any() > 0:
#                 rxData = uart1.read()
#                 print("gets00 ->"," ".join(hex(n) for n in rxData))
#             time.sleep(10)
#     elif offset==3: # for get rpm
#         print("get ->",commands_desc[offset]," ".join(hex(n) for n in cmd))
#         uart1.write(cmd)
#         time.sleep(0.05) #50ms
#         while uart1.any() > 0:
#             rxData = uart1.read()
#             print("gets ->"," ".join(hex(n) for n in rxData))
            
        
#     else:        
#         print("0x%04X"%(crc))
#         print("->",commands_desc[offset]," ".join(hex(n) for n in cmd))
#         #uart0.write(cmd)
#         uart1.write(cmd)
#     #uart0.write("{}\r\n".format(a))
#     a=a+1
#     time.sleep(20)
#     #time.sleep(0.5)

start_time=time.time()-1000
ii=0

while True:
        time.sleep(0.05) #50ms
        if time.time()-start_time>120:
            ii +=1
            start_time = time.time()
            print("point1",ii,start_time)
        while uart1.any() > 0:
            rxData = uart1.read()
            print("gets ->"," ".join(hex(n) for n in rxData))
            print("gets[string ->",rxData)
            print()

