#todo when send g0 x200 grbl set mpg=0 and so many bugs there
#https://github.com/gnea/grbl/blob/master/doc/markdown/commands.md
# 0x85 : Jog Cancel

# Immediately cancels the current jog state by a feed hold and automatically flushing any remaining jog commands in the buffer.
# Command is ignored, if not in a JOG state or if jog cancel is already invoked and in-process.
# Grbl will return to the IDLE state or the DOOR state, if the safety door was detected as ajar during the cancel.
# Feed Overrides

# Immediately alters the feed override value. An active feed motion is altered within tens of milliseconds.
# Does not alter rapid rates, which include G0, G28, and G30, or jog motions.
# Feed override value can not be 10% or greater than 200%.
# If feed override value does not change, the command is ignored.
# Feed override range and increments may be changed in config.h.
# The commands are:
# 0x90 : Set 100% of programmed rate.
# 0x91 : Increase 10%
# 0x92 : Decrease 10%
# 0x93 : Increase 1%
# 0x94 : Decrease 1%
# Rapid Overrides

# Immediately alters the rapid override value. An active rapid motion is altered within tens of milliseconds.
# Only effects rapid motions, which include G0, G28, and G30.
# If rapid override value does not change, the command is ignored.
# Rapid override set values may be changed in config.h.
# The commands are:
# 0x95 : Set to 100% full rapid rate.
# 0x96 : Set to 50% of rapid rate.
# 0x97 : Set to 25% of rapid rate.
# Spindle Speed Overrides

# Immediately alters the spindle speed override value. An active spindle speed is altered within tens of milliseconds.
# Override values may be changed at any time, regardless of if the spindle is enabled or disabled.
# Spindle override value can not be 10% or greater than 200%
# If spindle override value does not change, the command is ignored.
# Spindle override range and increments may be altered in config.h.
# The commands are:
# 0x99 : Set 100% of programmed spindle speed
# 0x9A : Increase 10%
# 0x9B : Decrease 10%
# 0x9C : Increase 1%
# 0x9D : Decrease 1%
# 0x9E : Toggle Spindle Stop

# Toggles spindle enable or disable state immediately, but only while in the HOLD state.
# The command is otherwise ignored, especially while in motion. This prevents accidental disabling during a job that can either destroy the part/machine or cause personal injury. Industrial machines handle the spindle stop override similarly.
# When motion restarts via cycle start, the last spindle state will be restored and wait 4.0 seconds (configurable) before resuming the tool path. This ensures the user doesn't forget to turn it back on.
# While disabled, spindle speed override values may still be altered and will be in effect once the spindle is re-enabled.
# If a safety door is opened, the DOOR state will supersede the spindle stop override, where it will manage the spindle re-energizing itself upon closing the door and resuming. The prior spindle stop override state is cleared and reset.
# 0xA0 : Toggle Flood Coolant

# Toggles flood coolant state and output pin until the next toggle or g-code command alters it.
# May be commanded at any time while in IDLE, RUN, or HOLD states. It is otherwise ignored.
# This override directly changes the coolant modal state in the g-code parser. Grbl will continue to operate normally like it received and executed an M8 or M9 g-code command.
# When $G g-code parser state is queried, the toggle override change will be reflected by an M8 enabled or disabled with an M9 or not appearing when M7 is present.
# 0xA1 : Toggle Mist Coolant

# Enabled by ENABLE_M7 compile-time option. Default is disabled.
# Toggles mist coolant state and output pin until the next toggle or g-code command alters it.
# May be commanded at any time while in IDLE, RUN, or HOLD states. It is otherwise ignored.
# This override directly changes the coolant modal state in the g-code parser. Grbl will continue to operate normally like it received and executed an M7 or M9 g-code command.
# When $G g-code parser state is queried, the toggle override change will be reflected by an M7 enabled or disabled with an M9 or not appearing when M8 is present.
C_STEP_MAX = 100.0
C_STEP_MIN = 0.1

C_STEP_Z_MAX = 20.0
C_STEP_Z_MIN = 0.1

C_FEED_MAX = 2000.0
C_FEED_MIN = 200.0


LED_SCROLLLOCK =  0x04
LED_CAPSLOCK = 0x02
LED_NUMLOCK = 0x01
LED_ALL = LED_SCROLLLOCK + LED_CAPSLOCK + LED_NUMLOCK

BLINK_2 = 1
BLINK_5 = 2
BLINK_INFINITE = 3
NOBLINK = 4

X_ARROW_COLOR = 'red'
Y_ARROW_COLOR = 'green'
Z_ARROW_COLOR = 'blue'

BLACK = (0, 0, 0)
RED = (0, 15, 0)
YELLOW = (15, 15, 0)
GREEN = (15, 0, 0)
CYAN = (0, 15, 15)
BLUE = (0, 0, 15)
PURPLE = (15, 0, 15)
WHITE = (15, 15, 15)


from neopixel import NeoPixel
import   time

class GrblState(object):
    def __init__(self,kbd,uart_grbl_mpg,
                  state:str = '', 
                  mpg:bool = None,
                  mX:float = 0.0,
                  mY:float = 0.0,
                  mZ:float = 0.0,
                  wX:float = 0.0,
                  wY:float = 0.0,
                  wZ:float = 0.0,
                  dXY:float = 10.0,
                  dZ:float = 1.0,
                  feedrate =  1000.0
                  ) :
        self._state = state
        self._state_prev = ''
        self._error = ''
        self._alarm = ''
        self._mpg = mpg
        self._mpg_prev = ''
        self._mX = mX
        self._mY = mY
        self._mZ = mZ
        self._wX = wX
        self._wY = wY
        self._wZ = wZ
        self._dXY = dXY
        self._dZ = dZ
        self._feedrate = feedrate
        self._state_is_changed = False
        self.grbl_state = ''
        self.kbd = kbd
        self.flashKbdLEDs = kbd.flashKbdLeds
        self.uart_grbl_mpg = uart_grbl_mpg
        self.neo = NeoPixel()
        self._jog_arrow = ''
        self.idleCounter = 0
        self.statetext = ''
        self.prev_statetext  = ''
        self._state_time_change = time.time()


    def inc_feedrate(self):
      if self._feedrate+100.0 > C_FEED_MAX:
           self._feedrate = C_FEED_MAX
      else:    
           self._feedrate +=100.0
      self._state_prev='feed'
      print('g_feedrate now',self._feedrate)  


    def dec_feedrate(self):
      if self._feedrate-100.0 < C_FEED_MIN:
           self._feedrate = C_FEED_MIN
      else:    
           self._feedrate -=100.0
      self._state_prev='feed'     
      print('g_feedrate now',self._feedrate)  

    def inc_stepXY(self):
      if self._dXY*10.0>C_STEP_MAX:
           self._dXY =C_STEP_MAX
      else:   
           self._dXY *=10.0
      self._state_prev='stepX'     
      print('g_step+ now',self._dXY)         

    def dec_stepXY(self):
      if self._dXY*0.1<C_STEP_MIN:
           self._dXY =C_STEP_MIN
      else:   
           self._dXY *=0.1
      self._state_prev='stepX'          
      print('g_step- now',self._dXY)         

    def inc_stepZ(self):
      if self._dXY*10.0>C_STEP_Z_MAX:
           self._dZ =C_STEP_Z_MAX
      else:   
           self._dZ *=10.0
      self._state_prev='stepZ'          
      print('g_step_z now',self._dZ)         

    def dec_stepZ(self):
      if self._dZ*0.1<C_STEP_Z_MIN:
           self._dZ =C_STEP_Z_MIN
      else:   
           self._dZ *=0.1
      self._state_prev='stepZ'          
      print('g_step_z now',self._dZ)  

    def set_jog_arrow(self, arrow:str):
      #print('new set_jog_arrow ',arrow)
      self._jog_arrow = arrow
      


    def mpgCommand(self, command:str):
      print("mpgCommand:",command)
      self.uart_grbl_mpg.write(command.encode())

    #jog $J=G91 X0 Y-5 F600
    #$J=G91 X1 F100000

    def grblJog(self, x:float=0.0, y: float=0.0, z:float=0.0):
      f=self.feedrate
      if x is not None and x!=0.0:
        self.set_jog_arrow(('+' if x>0 else '-')+'x')
        self.mpgCommand(f'$J=G91 G21 X{x} F{f}\r\n')
        #MPG -> <Idle|MPos:30.000,0.000,0.000|Bf:35,1023|FS:0,0,0|Pn:HS|WCO:0.000,0.000,0.000|WCS:G54|A:|Sc:|MPG:1|H:0|T:0|TLR:0|Sl:0.0|FW:grblHAL>
        self.parseState('<Jog|FW:grblHAL>') 
      elif y is not None and y!=0.0:
        self.set_jog_arrow(('+' if y>0 else '-')+'y')
        self.mpgCommand(f'$J=G91 G21 Y{y} F{f}\r\n')    
        self.parseState('<Jog|FW:grblHAL>') 
      elif z is not None and z!=0.0:
        self.set_jog_arrow(('+' if z>0 else '-')+'z')
        self.mpgCommand(f'$J=G91 G21 Z{z} F{f}\r\n')    
        self.parseState('<Jog|FW:grblHAL>') 



    def sent2grbl(self,command:str):
      print('sent2grbl:',command,len(command))
      if command in ('~','!','?'):
        self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
        self.mpgCommand(command)
      elif command=='-y':
          if self.state=='idle':
            self.grblJog(y=-self.step)
      elif  command=='+y':
          if self.state=='idle':
            self.grblJog(y=self.step)
      elif command=='-x':
          if self.state=='idle':
            self.grblJog(x=-self.step)
      elif  command=='+x':
          if self.state=='idle':
            self.grblJog(x=self.step)
      elif command=='-z':
          if self.state=='idle':
            self.grblJog(z=-self.step)
      elif  command=='+z':
          if self.state=='idle':
            self.grblJog(z=self.step)
      elif command=='-feed' : 
          self.dec_feedrate()
          self.neoInfo('feed {0:.0f}'.format(self._feedrate))
      elif command=='+feed':
          self.inc_feedrate()
          self.neoInfo('feed {0:.0f}'.format(self._feedrate))
      elif command=='-stepXY' :    
          self.dec_stepXY()
          if self._dXY<1:
            self.neoInfo('dX {0:.1f}'.format(self._dXY).replace('.',','))
          else:  
             self.neoInfo('dX {0:.0f}'.format(self._dXY))
      elif command=='+stepXY' :    
          self.inc_stepXY()
          if self._dXY<1:
            self.neoInfo('dX {0:.1f}'.format(self._dXY).replace('.',','))
          else:  
             self.neoInfo('dX {0:.0f}'.format(self._dXY))
      elif command=='-stepZ' :    
          self.dec_stepZ()
          if self._dZ<1:
            self.neoInfo('dZ {0:.1f}'.format(self._dZ).replace('.',','))
          else:  
             self.neoInfo('dZ {0:.0f}'.format(self._dZ))
      elif command=='+stepZ' :    
          self.inc_stepZ()
          if self._dZ<1:
            self.neoInfo('dZ {0:.1f}'.format(self._dZ).replace('.',','))
          else:  
             self.neoInfo('dZ {0:.0f}'.format(self._dZ))
      elif command in ('#'):  
        self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) ##2 - leds ???       # 2 - macro1 10/2 blink
        self.uart_grbl_mpg.write(bytearray(b'\x8b\r\n'))
      elif command in ('cancel'):  
        if self.state == 'run' or self.state == 'jog':
          self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) ##2 - leds ???       # 2 - macro1 10/2 blink
          self.uart_grbl_mpg.write(bytearray(b'\x85\r\n')) #Jog Cancel
          self.uart_grbl_mpg.write(bytearray(b'\x18\r\n')) # cancel ascii ctrl-x
          time.sleep(1)
          self.uart_grbl_mpg.write(bytearray(b'?\r\n')) # 
        else:
          self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
              
      elif command in ('^'):  
        self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
        self.uart_grbl_mpg.write('$X'.encode()+b'\r\n')
      else:
        if command.strip()!='':
          self.neoInfo(command[:10],virtual_width = 128)
        self.uart_grbl_mpg.write(command.encode()+b'\r\n')


    @property
    def feedrate(self):
        return self._feedrate  

    @property
    def step(self):
        return self._dXY          

    @property
    def mpg(self):
        return self._mpg    
    @property
    def mpg_prev(self):
        return self._mpg_prev
    
    @property
    def state(self):
        return self._state  
    
    @property
    def state_prev(self):
        return self._state_prev     
    
    def state_is_changed(self):
        l_changed = self._state_is_changed
        self._state_is_changed = False
        return l_changed
        
            
    #MPG -> <Idle|MPos:30.000,0.000,0.000|Bf:35,1023|FS:0,0,0|Pn:HS|WCO:0.000,0.000,0.000|WCS:G54|A:|Sc:|MPG:1|H:0|T:0|TLR:0|Sl:0.0|FW:grblHAL>
    def parseState(self,grblState:str):
        if grblState is None:
          return 
        
        i=5
        while i>0 and grblState.endswith('ok'):
          i-=1
          grblState=grblState[:-2].strip()

        if not (grblState.startswith('<') and grblState.endswith('>')):
          return         
        if grblState.startswith('error:'):
          self._state='error'
          self._state_is_changed = (self._state_prev is None or  self._state_prev != self._state)
          self._state_prev = self._state
          self._state_time_change = time.time()
          return 
        
        self.grbl_state = grblState


                
        for ii,token in enumerate(self.grbl_state.replace('<','').replace('>','').lower().split('|')):
            if ii==0 :
              prv = self._state_prev
              self._state_prev = self._state
              self._state = token
              self._state_is_changed = (prv is None or  prv != self._state)
              self._state_time_change = time.time()
              
            else:
                elem = token.split(':')
                if len(elem)>1 and elem[0]=='mpg' and elem[1] is not None and (elem[1]=='1' or elem[1]=='0'):
                    self._mpg_prev=self._mpg
                    self._mpg=(elem[1]=='1')
                elif  len(elem)>1 and elem[0]=='mpos' and elem[1] is not None:       
                    xyz = elem[1].split(',')
                    if len(xyz)==3:
                      self._mX, self._mY,self._mZ = [ float(xx) for xx in xyz ]


    def displayState(self,grblState:str):     
      self.parseState(grblState.strip())
      print("MPG ->",grblState,' \n - >> prev ',self.state_prev, self.mpg_prev,' now=>',self.state, self.mpg)
      if self.mpg is not None and (self.mpg_prev is None or self.mpg !=self.mpg_prev):
          self._mpg_prev=self._mpg
          self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5 if self.mpg else BLINK_2) 
          if self.mpg:
            self.neoInfo('MPG:1',color='green')
          else:
             self.neoInfo('MPG:0',color='purple')  
      if self.state_is_changed() or self.state == 'idle' or self.state.startswith('hold') :  
              if self.state == 'alarm':
                  self._jog_arrow = ''
                  self.flashKbdLEDs(LED_ALL , BLINK_INFINITE)
                  self.neoError('alrm')
              elif self.state == 'run':    
                  self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) 
                  self.neoInfo(self.state)  
              elif self.state == 'jog':    
                  self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) 
                  self.neoDisplayJog()
              elif self.state=='hold:1':
                  self.flashKbdLEDs(LED_NUMLOCK , BLINK_INFINITE)
                  self.neoError(self.state)  
              elif self.state=='hold:0':
                  self.flashKbdLEDs(LED_NUMLOCK , BLINK_5)
                  self.neoInfo(self.state)  
              elif self.state == 'error': 
                  self._jog_arrow = '' 
                  self.neoError('err')  
                  self.flashKbdLEDs(LED_CAPSLOCK , BLINK_5) 
              elif self.state == 'idle' :
                  self._jog_arrow = ''    
                  self.flashKbdLEDs(LED_ALL , NOBLINK) 
                  self.neoIdle()
    
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

       

    def neoText(self,text:str, color = 'PURPLE', animate:str = 'None', virtual_width:int = 64  ) :     

      cl0 = ['PURPLE']
      cl =[]

      if type(color) is str:
         cl0 = [color]
      elif type(color) in (tuple, list):
         cl0 = color   
      else:
         cl0 = ['PURPLE']
      for cli  in range(len(cl0)):
         if len(cl)<cli+1:
            cl.append(self.color2rgb(cl0[cli]))
         else:
            cl[cli] = self.color2rgb(cl0[cli]) 

         
            
            
      self.prev_statetext = self.statetext
      self.statetext = text
      self.neo.clear(virtual_width=virtual_width)
      self.neo.text(text, 0, 0,cl,no_clear_wnd_pos=(self.prev_statetext == self.statetext) )
      self.neo.animate(p_type=animate, p_delay=0.3)
      self.neo.pixels_show()

    def neoError(self,text:str, color:str = 'red', animate:str = 'window-left-right' ) :     
        self.neoText(text=text, color=color, animate = animate )     

    def neoDisplayJog(self, animate:str = 'right-cycle' ) :     
        color=X_ARROW_COLOR
        if self._jog_arrow[-1:]=='y':
           color=Y_ARROW_COLOR
        elif self._jog_arrow[-1:]=='z':  
           color=Z_ARROW_COLOR

        text='>>>' if self._jog_arrow.startswith('+') else '<<<' 
        print('    _jog_arrow=',self._jog_arrow)  
        self.neoText(text=text, color=color, animate = animate, virtual_width = 16 )     


    def neoInfo(self,text:str, color:str = 'purple', animate:str = 'window-left-right', virtual_width = 64 ) :     
        self.neoText(text=text, color=color, animate = animate, virtual_width = virtual_width )  

    def neoShowEdit(self):
      self.idleCounter = 0
      self.neo.animate()
      self.neoIdle()
                                

    def neoIdle(self, virtual_width = 64 ) :     
        color = 'purple'
        text = self.state
        animate = 'window-left-right'
        if self.kbd.get()!='':
          if self.idleCounter>10 and self.idleCounter%10<=7:  
            color = [X_ARROW_COLOR, Y_ARROW_COLOR , Z_ARROW_COLOR]
            text = '{0:.1f} {1:.1f} {2:.1f}'.format(self._mX, self._mY, self._mZ).replace('.',',')
            animate = 'window-left-right'
          else:  
           color = 'purple'
           animate = 'edit'
           text = self.kbd.get()

        else:   
          if self.idleCounter%4==0:
            color = 'purple'
            text = self.state
          elif self.idleCounter%4==1:  
            color = X_ARROW_COLOR   
            text = '{0:.1f}'.format(self._mX).replace('.',',')
          elif self.idleCounter%4==2:  
            color = Y_ARROW_COLOR   
            text = '{0:.1f}'.format(self._mY).replace('.',',')
          elif self.idleCounter%4==3:  
            color = Z_ARROW_COLOR   
            text = '{0:.1f}'.format(self._mZ).replace('.',',')
        self.idleCounter +=1
        self.neoText(text=text, color=color, animate = animate, virtual_width = virtual_width )                               

