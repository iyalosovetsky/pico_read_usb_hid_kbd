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
BLACK = (0, 0, 0)

BLACK = (0, 0, 0)
RED = (0, 15, 0)
YELLOW = (15, 15, 0)
GREEN = (15, 0, 0)
CYAN = (0, 15, 15)
BLUE = (0, 0, 15)
PURPLE = (15, 0, 15)
WHITE = (15, 15, 15)

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
        self.ar = array.array("I", [0 for _ in range(self.num_virtual)])
        self.cursor_pos=0
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
        self._stateBottomRight = [] # state on right bottom corner
        
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        


    def setStateBottomRight(self,arrState):
       if arrState is None or len(arrState)>self.width:
           print ('setRBState: error arr size!!',len(arrState) )
       self._stateBottomRight =arrState
    #    for  ii in range(len(self._stateBottomRight)):
    #       c = self._stateBottomRight[ii]
    #       r = int(((c >> 8) & 0xFF) * self.brightness)
    #       g = int(((c >> 16) & 0xFF) * self.brightness)
    #       b = int((c & 0xFF) * self.brightness)
    #       c2 = (g<<16) + (r<<8) + b
    #       if c2!=c:
    #           self._stateBottomRight[ii]=c2
              
    @property
    def rbState(self):
            return self._stateBottomRight     

        
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
                c2 = 0
                if len(self._stateBottomRight)>0 and row==self.height-1 and col>= self.width-len(self._stateBottomRight) : # for example 3 status on bottom light corner 13,14,15 led 16-3
                    c2 = self._stateBottomRight[len(self._stateBottomRight)-(self.width-col)] # 3 -[16-13]=0, 3 -[16-14]=1    , 3 -[16-15]=2
                else:
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

    def clear(self):
        self.pixels_fill(BLACK)

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
        
        if dx is not None and dx<=self.width and dx>=-self.width :
            self.animate_dx=dx
        if dx is not None and dx< -self.width_virtual*10: #initial to 0
            self.x_window_pos = 0
            return
        if self.animate_dx==0:
            self.x_window_pos = 0
            return 
        else:
            self.x_window_pos += self.animate_dx
        overdraw_val = self.width if overdraw=='yes' else 0 #over draw on virtual window
        
        if overdraw=='lr':
            if self.cursor_pos>self.width:
                max_window_pos=self.cursor_pos-self.width+1
            else:
                max_window_pos=self.width_virtual-self.width-1
            if self.x_window_pos > max_window_pos: #  
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
    
    def clear(self, virtual_width:int = DISPLAY_VIRTUAL_WIDTH):
        self.x_window_pos = 0
        self.cursor_pos=0
        if virtual_width!= self.width_virtual:
            self.width_virtual = virtual_width
            self.num = self.width * self.height
            self.num_virtual = self.width_virtual * self.height
            self.ar = array.array("I", [0 for _ in range(self.num_virtual)])
        else:    
            self.pixels_fill((0,0,0))
        
        
        
    
    def text(self, text, x, y, color, no_clear_wnd_pos=False):
        self.animateType='No'
        self.fr.text(text, x, y, color)
        if self.fr._cursor_pos>0:
            self.cursor_pos=self.fr._cursor_pos-1
        else:
            self.cursor_pos=0
        if not no_clear_wnd_pos:    
            self.animate_lr_pause_ticks=COUNT_PAUSE_LR_TICKS
            self.x_window_pos = 0
            self.animate_dx= -1
            if self.cursor_pos<=self.width:
                self.animate_dx= 0
        #print('cursor pos is ',self.cursor_pos,'animateDX=',self.animate_dx, self.animateType)
        
    def animate(self, p_type=None, p_delay=0.3):
        if p_type is not None and (self.animateType!=p_type or p_type=='edit'):
            self.animateType=p_type
            self.ltick =  time.time()
            if p_type=='edit' and self.cursor_pos<=self.width:
                self.x_window_pos = 0
                self.animate_dx= 0
            elif p_type=='edit' and self.cursor_pos>self.width:    
                self.x_window_pos = self.cursor_pos - self.width + 1
                self.animate_dx= 0
            else:
                self.x_window_pos = 0    
            
            

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
            
    @staticmethod
    def color2rgb(color:str = 'PURPLE'):
      if color.upper()=='PURPLE':
         return PURPLE
      elif color.upper()=='RED':
         return RED
      elif color.upper()=='GREEN':
         return GREEN
      elif color.upper()=='BLUE':
         return BLUE
      elif color.upper()=='BLACK':
         return BLACK
      elif color.upper()=='CYAN':
         return CYAN
      elif color.upper()=='WHITE':
         return WHITE
      elif color.upper()=='YELLOW':
         return YELLOW
      else:
         return WHITE

    @staticmethod
    def color2rgbInt(color:str = 'PURPLE', brightness:float =0.1 ):
      cl=NeoPixel.color2rgb(color)
      br = 15.99* (0.99 if brightness>1.0 else brightness)
      #47 b
      #47*256 g
      #47*256*256 r
      b = int(br *cl[2])
      r = int(br *cl[1])
      g = int(br *cl[0])
      return (r<<16) + (g<<8) + b           
        


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

