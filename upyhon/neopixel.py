# Example using PIO to drive a set of WS2812 LEDs.
import array, time
from machine import Pin
import rp2

import font

MESSAGE        = 'MicroPython rocks!'
DISPLAY_WIDTH  = 16    # Display width in pixels.
DISPLAY_HEIGHT = 10     # Display height in pixels.
INTENSITY      = 50   # Message pixel brightness (0-255).
SPEED          = 25.0  # Scroll speed in pixels per second.

# Configure the number of WS2812 LEDs.
NUM_LEDS = 160
#PIN_NUM = 6
PIN_NUM = 22

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
        
class NeoPixel(object):
    def __init__(self,pin=PIN_NUM,num=NUM_LEDS,brightness=0.2):
        self.pin=pin
        self.num=num
        self.fr=font.FontRenderer(width=DISPLAY_WIDTH+1,height=DISPLAY_HEIGHT ,pixel=self.pixels_set2)
        self.fr.init()
        self.brightness = brightness
        self.animateType = 'No'
        self.animateDelay= 0.5
        self.ltick =  time.time()
        
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.num)])
        
        self.BLACK = (0, 0, 0)
        self.RED = (0, 15, 0)
        self.YELLOW = (15, 15, 0)
        self.GREEN = (15, 0, 0)
        self.CYAN = (0, 15, 15)
        self.BLUE = (0, 0, 15)
        self.PURPLE = (15, 0, 15)
        self.WHITE = (15, 15, 15)
        self.COLORS = [self.RED, self.YELLOW, self.GREEN, self.CYAN, self.BLUE, self.PURPLE, self.WHITE,self.BLACK ]
        self.lattice = [self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.RED, self.RED, self.RED, self.CYAN, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.CYAN, self.RED, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN, self.RED, self.RED, self.RED, self.RED, self.RED, self.RED, self.CYAN, self.CYAN, self.RED, self.RED, self.CYAN,
                        self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN,
                        self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN, self.CYAN]
        
    ##########################################################################
    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness) 
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)

    def pixels_set(self, i, color):
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

    def pixels_set2(self, x, y, color):
        i=y*16+x
        if y<DISPLAY_HEIGHT and x<DISPLAY_WIDTH:
            old=self.ar[i]
            self.ar[i] = old|(color[1]<<16) + (color[0]<<8) + color[2]


    def pixels_fill(self, color):
        for i in range(len(self.ar)):
            self.pixels_set(i, color)

    def color_chase(self, color, length):
        #for i in range(self.num):
        self.pixels_set(length, color)
            #time.sleep(wait)
#         self.pixels_show()
#         time.sleep(0.2)
     
    def wheel(self, pos):
        # Input a value 0 to 31 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 31:
            return (0, 0, 0)
        if pos < 10:
            return (31 - pos * 3, pos * 3, 0)
        if pos < 15:
            pos -= 10
            return (0, 31 - pos * 3,pos * 3)
        pos -= 15
        return (pos * 3, 0, 31 - pos * 3)
     
     
    def rainbow_cycle(self, wait):
        for j in range(256):
            for i in range(self.num):
                rc_index = (i * 256 // self.num) + j
                self.pixels_set(i, self.wheel(rc_index & 31))
            self.pixels_show()
            time.sleep(wait)
            
    def roll_right(self, cycle=False):
        l_pix=self.ar[NUM_LEDS-1]
        self.ar=array.array("I", [0 for _ in range(1)])+self.ar[0:NUM_LEDS-1]
        for r in range(DISPLAY_HEIGHT): ##10
            if cycle:
                if r<DISPLAY_HEIGHT-1:
                    self.ar[r*DISPLAY_WIDTH]=self.ar[(r+1)*DISPLAY_WIDTH]   #16  [0] stay [15+1(shift above)], 16 ->
                else:
                    self.ar[r*DISPLAY_WIDTH]=l_pix
            else:
                self.ar[r*DISPLAY_WIDTH]=0   #16
        self.pixels_show()

    def roll_left(self, cycle=False):
        l_pix=self.ar[0]
        self.ar=self.ar[1:NUM_LEDS]+array.array("I", [0 for _ in range(1)])
        for r in reversed(range(DISPLAY_HEIGHT)): ##10  0..9 9-r -> 9..0
            if cycle:
                if r==0:
                    self.ar[(r+1)*DISPLAY_WIDTH-1]=l_pix
                else:
                    self.ar[(r+1)*DISPLAY_WIDTH-1]=self.ar[r*DISPLAY_WIDTH-1]
                       
            else:
                self.ar[(r+1)*DISPLAY_WIDTH-1]=0   #16 0+1*16
        self.pixels_show()
        
    def text(self, text, x, y, color):
        self.animateType='No'
        self.fr.text(text, x, y, color)
        
    def animate(self, p_type=None, p_delay=0.3):
        if p_type is not None:
            self.animateType=p_type
            self.ltick =  time.time()
        if p_delay is not None:
            self.animateDelay=p_delay

            
        if self.ltick +self.animateDelay <  time.time():
            return
        
        
            
        if self.animateType == 'left-cycle':
            self.roll_left(cycle=True)
        elif self.animateType == 'right-cycle':
            self.roll_right(cycle=True)
        elif self.animateType == 'left':
            self.roll_left(cycle=False)
        elif self.animateType == 'right':
            self.roll_right(cycle=False)    
            
            
        


        

