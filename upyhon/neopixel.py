# Example using PIO to drive a set of WS2812 LEDs.
import array, time
from machine import Pin
import rp2

import font

MESSAGE        = 'MicroPython rocks!'
DISPLAY_WIDTH  = 16    # Display width in pixels.
DISPLAY_VIRTUAL_WIDTH = DISPLAY_WIDTH+4*16    # Display width in pixels.
DISPLAY_HEIGHT = 10     # Display height in pixels.
INTENSITY      = 50   # Message pixel brightness (0-255).
SPEED          = 25.0  # Scroll speed in pixels per second.
COUNT_PAUSE_LR_TICKS = 10 # pause tick for display left/right max pos window 

# Configure the number of WS2812 LEDs.
# NUM_LEDS = DISPLAY_VIRTUAL_WIDTH * DISPLAY_HEIGHT

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
    def __init__(self,pin=PIN_NUM,
                      width:int=DISPLAY_WIDTH,
                      width_virtual:int=DISPLAY_VIRTUAL_WIDTH,
                      height:int=DISPLAY_HEIGHT,
                      brightness:float=0.2):
        self.pin=pin
        self.width_virtual = width_virtual
        self.width = width
        self.height = height
        self.num = self.width * self.height
        self.num_virtual = self.width_virtual * self.height
        self.x_window_pos = 0
        self.fr=font.FontRenderer(width=self.width_virtual, height=self.height, pixel=self.pixels_set2)
        self.fr.init()
        self.brightness = brightness
        self.animateType = 'No'
        self.animateDelay= 0.5
        self.animate_dx= 1
        self.animate_lr_pause_ticks= 0
        #self.animate_lr_pause_ticks= COUNT_PAUSE_LR_TICKS
        self.ltick =  time.time()
        self.cursor_pos=0
        
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.num_virtual)])
        
        self.BLACK = (0, 0, 0)
        self.RED = (0, 15, 0)
        self.YELLOW = (15, 15, 0)
        self.GREEN = (15, 0, 0)
        self.CYAN = (0, 15, 15)
        self.BLUE = (0, 0, 15)
        self.PURPLE = (15, 0, 15)
        self.WHITE = (15, 15, 15)
        
    ##########################################################################
    def pixels_show0(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness) 
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)

    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num)]) # 160 phis LEDs
        for col in range(self.width): # cols
            col_virt=col+self.x_window_pos # offset in virtual window
            for row in range(self.height):
                if col_virt>=self.width_virtual or  col_virt<0: #overdraw right or left -> black
                    c2 = 0
                else:
                    c = self.ar[row*self.width_virtual+col_virt]    
                    r = int(((c >> 8) & 0xFF) * self.brightness)
                    g = int(((c >> 16) & 0xFF) * self.brightness)
                    b = int((c & 0xFF) * self.brightness)
                    c2 = (g<<16) + (r<<8) + b
                dimmer_ar[row*self.width+col] = c2
        self.sm.put(dimmer_ar, 8)




    def pixels_set(self, i, color):
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

    def pixels_set2(self, x, y, color):
        i=y*self.width_virtual+x
        if y<self.height and x<self.width_virtual:
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
     
     
    def roll_window_pointer(self, dx:int, overdraw:str='no'):
        if dx is not None and dx<=self.width and dx>=-self.width and dx!=0:
            self.animate_dx=dx
        if dx is not None and dx<-self.width_virtual*10: #initial to 0
            self.x_window_pos = 0
            return
        self.x_window_pos += self.animate_dx #   
        overdraw_val = self.width if overdraw=='yes' else 0 #over draw on virtual window
        
        if overdraw=='lr':
            if self.cursor_pos>0 and self.cursor_pos>self.width:
                max_window_pos=self.cursor_pos-self.width
            else:
                max_window_pos=self.width_virtual-self.width-1
            if self.x_window_pos>=max_window_pos: #  
                self.x_window_pos = max_window_pos # max val is 47 (draws only 1 vertical bar right)
                self.animate_lr_pause_ticks -=1 
                if self.animate_lr_pause_ticks>0:
                    return
                else:
                    self.animate_lr_pause_ticks=COUNT_PAUSE_LR_TICKS
                self.animate_dx = - abs(self.animate_dx)
            elif self.x_window_pos < 0: # min val is -16
                self.x_window_pos = 0
                self.animate_lr_pause_ticks -=1 
                if self.animate_lr_pause_ticks>0:
                    return
                else:
                    self.animate_lr_pause_ticks=COUNT_PAUSE_LR_TICKS
                self.animate_dx = abs(self.animate_dx)
        else:    
            if self.x_window_pos+self.width>=self.width_virtual+overdraw_val: # >=48
                self.x_window_pos = self.width_virtual+overdraw_val-self.width-1 # max val is 47 (draws only 1 vertical bar right)
            elif self.x_window_pos < -overdraw_val: # min val is -16
                self.x_window_pos = -overdraw_val

    def roll_window(self, dx:int , overdraw:str='no'):
        self.roll_window_pointer(dx=dx, overdraw=overdraw)
        self.pixels_show()
            
    def mdroll_right(self, cycle=False):
        l_pix=self.ar[self.num_virtual-1]
        self.ar=array.array("I", [0 for _ in range(1)])+self.ar[0:self.num_virtual-1]
        for r in range(self.height): ##10
            if cycle:
                if r<self.height-1:
                    self.ar[r*self.width_virtual]=self.ar[(r+1)*self.width_virtual]   #16  [0] stay [15+1(shift above)], 16 ->
                else:
                    self.ar[r*self.width_virtual]=l_pix
            else:
                self.ar[r*self.width_virtual]=0   #16
        self.pixels_show()

    def roll_right(self, cycle=False):
        l_pix=self.ar[self.num-1]
        if self.num_virtual-self.num>0:
            self.ar=array.array("I", [0 for _ in range(1)])+self.ar[0:self.num-1]+array.array("I", [0 for _ in range(self.num_virtual-self.num)])
        else:
            self.ar=array.array("I", [0 for _ in range(1)])+self.ar[0:self.num-1]                
        for r in range(self.height): ##10
            if cycle:
                if r<self.height-1:
                    self.ar[r*self.width]=self.ar[(r+1)*self.width]   #16  [0] stay [15+1(shift above)], 16 ->
                else:
                    self.ar[r*self.width]=l_pix
            else:
                self.ar[r*self.width]=0   #16
        self.pixels_show()

    def mdroll_left(self, cycle=False):
        l_pix=self.ar[0]
        self.ar=self.ar[1:self.num_virtual]+array.array("I", [0 for _ in range(1)])
        for r in reversed(range(self.height)): ##10  0..9 9-r -> 9..0
            if cycle:
                if r==0:
                    self.ar[(r+1)*self.width_virtual-1]=l_pix
                else:
                    self.ar[(r+1)*self.width_virtual-1]=self.ar[r*self.width_virtual-1]
                       
            else:
                self.ar[(r+1)*self.width_virtual-1]=0   #16 0+1*16
        self.pixels_show()

    def roll_left(self, cycle=False):
        l_pix=self.ar[0]
        if self.num_virtual-self.num>0:
            self.ar=self.ar[1:self.num]+array.array("I", [0 for _ in range(self.num_virtual-self.num+1)])
        else:    
            self.ar=self.ar[1:self.num]+array.array("I", [0 for _ in range(1)])
        for r in reversed(range(self.height)): ##10  0..9 9-r -> 9..0
            if cycle:
                if r==0:
                    self.ar[(r+1)*self.width-1]=l_pix
                else:
                    self.ar[(r+1)*self.width-1]=self.ar[r*self.width-1]
                       
            else:
                self.ar[(r+1)*self.width-1]=0   #16 0+1*16
        self.pixels_show()

    def text(self, text, x, y, color):
        self.animateType='No'
        self.fr.text(text, x, y, color)
        self.cursor_pos=self.fr._cursor_pos
        self.animate_lr_pause_ticks=COUNT_PAUSE_LR_TICKS
        self.x_window_pos = 0
        self.animate_dx= 1
        if self.cursor_pos<self.width:
            self.animate_dx= 0
        print('cursor pos is ',self.cursor_pos)
        
    def animate(self, p_type=None, p_delay=0.3):
        if p_type is not None:
            self.animateType=p_type
            self.ltick =  time.time()
            self.x_window_pos = 0
            self.animate_dx= 1

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
        elif self.animateType == 'window-right':
            self.roll_window(overdraw='no', dx=1)    
        elif self.animateType == 'window-over-right':
            self.roll_window(overdraw='yes', dx=1)    
        elif self.animateType == 'window-left':
            self.roll_window(overdraw='no', dx=-1)    
        elif self.animateType == 'window-left-right':
            self.roll_window(overdraw='lr', dx=None)    
            
            
        


# from neopixel import NeoPixel        
# import time
# neo = NeoPixel()
# cl = neo.PURPLE
# neo.pixels_fill(neo.BLACK)
# neo.pixels_show()
# neo.text('hello world!', 0, 0,cl )
# neo.pixels_show()
# for i in range(480):
#    time.sleep(0.1)
#    neo.animate(p_type='window-left-right')

