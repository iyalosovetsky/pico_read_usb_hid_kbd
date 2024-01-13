
import time






DISPLAY_WIDTH  = 320    # Display width in pixels.
DISPLAY_HEIGHT = 240     # Display height in pixels.
DISPLAY_ROTATION = 90



from adafruit_display_text import label
from adafruit_st7789 import ST7789
import displayio
from  fourwire import FourWire
import board
import digitalio
import busio
import vectorio

def portDeinit(port):
    try:
        p = digitalio.DigitalInOut(port)
        p.deinit()
    except:
            pass 
        

class WaveST7789(object):
    def __init__(self, width:int=DISPLAY_WIDTH,
                      height:int=DISPLAY_HEIGHT,
                      rotation:int=DISPLAY_ROTATION,
                      brightness:int=1):

        displayio.release_displays()

        portDeinit(board.GP8)
        portDeinit(board.GP9)
        portDeinit(board.GP10)
        portDeinit(board.GP11)
        portDeinit(board.GP12)
        portDeinit(board.GP13)
        portDeinit(board.GP15)


        bl_pin = digitalio.DigitalInOut(board.GP13)
        bl_pin.direction=digitalio.Direction.OUTPUT
        bl_pin.value=brightness 
        tft_cs = board.GP9
        tft_dc = board.GP8
        tft_reset=board.GP15
        
   

       


        self.spi = busio.SPI(board.GP10, board.GP11, board.GP12) 
        

        display_bus = FourWire(self.spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
 


        self.display = ST7789(display_bus, width=width, height=height, rotation=rotation)
        self.display.auto_refresh = True
        splash = displayio.Group()
        self.display.root_group = splash
        print("Hello World!")
        
        self.rotation=rotation
        # if (rotation%180):
        #     self.width = height
        #     self.height = width
        # else:
        self.width = width
        self.height = height
            

        self.brightness = brightness
        self.ltick =  time.time()
        self._stateBottomRight = [] # state on right bottom corner
        
  
         
    def setStateBottomRight(self,arrState):
       if arrState is None or len(arrState)>self.width:
           print ('setRBState: error arr size!!',len(arrState) )
       self._stateBottomRight =arrState
              
    @property
    def rbState(self):
            return self._stateBottomRight     

        
 

    

    def clear(self):
        pass

     
     
    
    def text(self, text, x, y, color, no_clear_wnd_pos=False):
         print(text)

    def pixels_show(self):
         pass     
        

    def _make_palette(self, color):
            palette = displayio.Palette(1)
            palette[0] = color
            return palette

    def _remove_shapes(self,):
            while len(self.display.root_group) > 1:
                self.display.root_group.pop()


    def _add_centered_rect(self,width, height, x_offset=0, y_offset=0, color=None):
            if color is None:
                color = 0
            rectangle = vectorio.Rectangle(
                pixel_shader=self._make_palette(color),
                width=width,
                height=height,
                x=(self.width//2 - width//2) + x_offset - 1,
                y=(self.height//2 - height//2) + y_offset - 1
            )
            self.display.root_group.append(rectangle)

    def _add_centered_polygon(self,points, x_offset=0, y_offset=0, color=None):
            if color is None:
                color = 0
            # Figure out the shape dimensions by using min and max
            width = max(points, key=lambda item:item[0])[0] - min(points, key=lambda item:item[0])[0]
            height = max(points, key=lambda item:item[1])[1] - min(points, key=lambda item:item[1])[1]
            polygon = vectorio.Polygon(
                pixel_shader=self._make_palette(color),
                points=points,
                x=(self.width // 2 - width // 2) + x_offset - 1,
                y=(self.height // 2 - height // 2) + y_offset - 1
            )
            self.display.root_group.append(polygon)

    def _add_centered_circle(self, radius, x_offset=0, y_offset=0, color=None):
            if color is None:
                color = 0
            circle = vectorio.Circle(
                pixel_shader=self._make_palette(color),
                radius=radius,
                x=(self.width // 2) + x_offset - 1,
                y=(self.height // 2) + y_offset - 1
            )
            self.display.root_group.append(circle)



    def _set_status_reverse(self):
            self._remove_shapes()
            self._add_centered_polygon([(40, 0), (60, 0), (100, 100), (0, 100)], 0, 0)
            self._add_centered_polygon([(0, 40), (100, 40), (50, 0)], 0, -40)


    def _set_status_forward(self):
            self._remove_shapes()
            self._add_centered_polygon([(20, 0), (60, 0), (80, 100), (0, 100)])
            self._add_centered_polygon([(0, 0), (150, 0), (75, 50)], 0, 50)



    def _set_status_rotate_ccw(self):
        self._remove_shapes()
        self._add_centered_circle(80)
        self._add_centered_circle(50, 0, 0, 0xFFFF00)
        self._add_centered_rect(160, 60, 0, 0, 0xFFFF00)
        self._add_centered_polygon([(40, 0), (80, 40), (0, 40)], 60, 10)
        self._add_centered_polygon([(40, 40), (80, 0), (0, 0)], -60, -10)

    def _set_status_left(self):
        self._remove_shapes()
        self._add_centered_rect(100, 40)
        self._add_centered_polygon([(0, 0), (0, 100), (50, 50)], 50)

    def _set_status_rotate_cw(self):
        self._remove_shapes()
        self._add_centered_circle(80)
        self._add_centered_circle(50, 0, 0, 0xFFFF00)
        self._add_centered_rect(160, 60, 0, 0, 0xFFFF00)
        self._add_centered_polygon([(40, 0), (80, 40), (0, 40)], -60, 10)
        self._add_centered_polygon([(40, 40), (80, 0), (0, 0)], 60, -10)

    def _set_status_stop(self):
        self._remove_shapes()
        self._add_centered_rect(100, 100)

