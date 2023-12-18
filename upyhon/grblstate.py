C_STEP_MAX = 100.0
C_STEP_MIN = 0.1

C_STEP_Z_MAX = 20.0
C_STEP_Z_MIN = 0.1

C_FEED_MAX = 8000.0
C_FEED_MIN = 200.0


LED_SCROLLLOCK =  0x04
LED_CAPSLOCK = 0x02
LED_NUMLOCK = 0x01
LED_ALL = LED_SCROLLLOCK + LED_CAPSLOCK + LED_NUMLOCK

BLINK_2 = 1
BLINK_5 = 2
BLINK_INFINITE = 3
NOBLINK = 4


from neopixel import NeoPixel

class GrblState(object):
    def __init__(self,cb_flashKbdLEDs,uart_grbl_mpg,
                  state:str = None, 
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
        self.flashKbdLEDs = cb_flashKbdLEDs
        self.uart_grbl_mpg = uart_grbl_mpg
        self.neo = NeoPixel()
        self._jog_arrow = ''


    def inc_feedrate(self):
      if self._feedrate+100.0 > C_FEED_MAX:
           self._feedrate = C_FEED_MAX
      else:    
           self._feedrate +=100.0
      print('g_feedrate now',self._feedrate)  


    def dec_feedrate(self):
      if self._feedrate-100.0 < C_FEED_MIN:
           self._feedrate = C_FEED_MIN
      else:    
           self._feedrate -=100.0
      print('g_feedrate now',self._feedrate)  

    def inc_stepXY(self):
      if self._dXY*10.0>C_STEP_MAX:
           self._dXY =C_STEP_MAX
      else:   
           self._dXY *=10.0
      print('g_step+ now',self._dXY)         

    def dec_stepXY(self):
      if self._dXY*0.1<C_STEP_MIN:
           self._dXY =C_STEP_MIN
      else:   
           self._dXY *=0.1
      print('g_step- now',self._dXY)         

    def inc_stepZ(self):
      if self._dXY*10.0>C_STEP_Z_MAX:
           self._dZ =C_STEP_Z_MAX
      else:   
           self._dZ *=10.0
      print('g_step_z now',self._dZ)         

    def dec_stepZ(self):
      if self._dZ*0.1<C_STEP_Z_MIN:
           self._dZ =C_STEP_Z_MIN
      else:   
           self._dZ *=0.1
      print('g_step_z now',self._dZ)  

    def set_jog_arrow(self, arrow:str):
      self._jog_arrow = arrow


    def mpgCommand(self, command:str):
      print("mpgCommand:",command)
      self.uart_grbl_mpg.write(command.encode())

    def grblJog(self, x:float=0.0, y: float=0.0, z:float=0.0):
      f=self.feedrate
      if x is not None and x!=0.0:
        self.set_jog_arrow(('+' if x>0 else '-')+'x')
        self.mpgCommand(f'$J=G91 G21 X{x} F{f} \r\n') 
      elif y is not None and y!=0.0:
        self.set_jog_arrow(('+' if y>0 else '-')+'y')
        self.mpgCommand(f'$J=G91 G21 Y{y} F{f} \r\n')    
      elif z is not None and z!=0.0:
        self.set_jog_arrow(('+' if z>0 else '-')+'z')
        self.mpgCommand(f'$J=G91 G21 Z{z} F{f} \r\n')    



    def sent2grbl(self,command:str):
      print('sent2grbl:',command)
      if command in ('~','!','?'):
        self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
        self.mpgCommand(command)
      elif command=='-y':
          self.grblJog(y=-self.step)
      elif  command=='+y':
          self.grblJog(y=self.step)
      elif command=='-x':
          self.grblJog(x=-self.step)
      elif  command=='+x':
          self.grblJog(x=self.step)
      elif command=='-z':
          self.grblJog(z=-self.step)
      elif  command=='+z':
          self.grblJog(z=self.step)
      elif command=='-feed' : 
          self.dec_feedrate()
          self.neoInfo('f{0:.0f}'.format(self._feedrate/10))
      elif command=='+feed':
          self.inc_feedrate()
          self.neoInfo('f{0:.0f}'.format(self._feedrate/10))
      elif command=='-stepXY' :    
          self.dec_stepXY()
          if self._dXY<1:
            self.neoInfo('{0:.1f}'.format(self._dXY).replace('.',','))
          else:  
             self.neoInfo('{0:.0f}'.format(self._dXY))
      elif command=='+stepXY' :    
          self.inc_stepXY()
          if self._dXY<1:
            self.neoInfo('{0:.1f}'.format(self._dXY).replace('.',','))
          else:  
             self.neoInfo('{0:.0f}'.format(self._dXY))
      elif command=='-stepZ' :    
          self.dec_stepZ()
          if self._dZ<1:
            self.neoInfo('z{0:.1f}'.format(self._dZ).replace('.',','))
          else:  
             self.neoInfo('z{0:.0f}'.format(self._dZ))
      elif command=='+stepZ' :    
          self.inc_stepZ()
          if self._dZ<1:
            self.neoInfo('z{0:.1f}'.format(self._dZ).replace('.',','))
          else:  
             self.neoInfo('z{0:.0f}'.format(self._dZ))
      elif command in ('#'):  
        self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) ##2 - leds ???       # 2 - macro1 10/2 blink
        self.uart_grbl_mpg.write(bytearray(b'\x8b\r\n'))
      elif command in ('cancel'):  
        if self.state == 'run' or st.state == 'jog':
          self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) ##2 - leds ???       # 2 - macro1 10/2 blink
          self.uart_grbl_mpg.write(bytearray(b'\x85\r\n'))
          self.uart_grbl_mpg.write(bytearray(b'\x18\r\n')) # cancel ascii
        else:
          self.flashKbdLeds(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
              
      elif command in ('$'):  
        self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
        self.uart_grbl_mpg.write('$X'.encode()+b'\r\n')
      else:
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
        if not (grblState.startswith('<') and grblState.endswith('>')):
          return         
        if grblState.startswith('error:'):
          self._state='error'
          self._state_is_changed = (self._state_prev is None or  self._state_prev != self._state)
          self._state_prev = self._state
          return 
        
        self.grbl_state = grblState


                
        for ii,token in enumerate(self.grbl_state.replace('<','').replace('>','').lower().split('|')):
            if ii==0 :
              self._state = token
              self._state_is_changed = (self._state_prev is None or  self._state_prev != self._state)
              self._state_prev = self._state
            else:
                elem = token.split(':')
                if len(elem)>1 and elem[0]=='mpg' and elem[1] is not None:
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
          self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5 if self.mpg else BLINK_2) 
      if self.state_is_changed():  
              if self.state == 'alarm':
                  self._jog_arrow = ''
                  self.flashKbdLEDs(LED_ALL , BLINK_INFINITE)
                  self.neoError('alrm')

                  
              elif self.state == 'run':    
                  self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) 
              elif self.state == 'jog':    
                  self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) 
                  self.neo.pixels_fill(self.neo.BLACK)
                  if self._jog_arrow.startswith('+'):
                    self.neoJogInc('>>>')
                  else:  
                    self.neoJogDec('<<<')
              elif self.state == 'hold':    
                  self.flashKbdLEDs(LED_NUMLOCK , BLINK_INFINITE) 
              elif self.state == 'error': 
                  self._jog_arrow = '' 
                  self.neoError('err')  
                  self.flashKbdLEDs(LED_CAPSLOCK , BLINK_5) 
              elif self.state == 'idle' :
                  self._jog_arrow = ''    
                  self.flashKbdLEDs(LED_ALL , NOBLINK) 
                  self.neoInfo('Idle')

    def neoText(self,text:str, color:str = 'PURPLE', animate:str = 'None' ) :     
      self.neo.pixels_fill(self.neo.BLACK)
      cl = self.neo.PURPLE
      if color.upper()=='PURPLE':
         cl = self.neo.PURPLE
      elif color.upper()=='RED':
         cl = self.neo.RED
      elif color.upper()=='GREEN':
         cl = self.neo.GREEN
      elif color.upper()=='BLUE':
         cl = self.neo.BLUE
      elif color.upper()=='BLACK':
         cl = self.neo.BLACK
      elif color.upper()=='CYAN':
         cl = self.neo.CYAN
      elif color.upper()=='WHITE':
         cl = self.neo.WHITE
      elif color.upper()=='YELLOW':
         cl = self.neo.YELLOW
      else:
         cl = self.neo.WHITE
      self.neo.text(text, 0, 0,cl )
      self.neo.animate(p_type=animate, p_delay=0.3)
      self.neo.pixels_show()

    def neoError(self,text:str, color:str = 'red', animate:str = 'None' ) :     
        self.neoText(text=text, color=color, animate = animate )     

    def neoJogInc(self,text:str, color:str = 'green', animate:str = 'right-cycle' ) :     
        self.neoText(text=text, color=color, animate = animate )     

    def neoJogDec(self,text:str, color:str = 'red', animate:str = 'left-cycle' ) :     
        self.neoText(text=text, color=color, animate = animate )              

    def neoInfo(self,text:str, color:str = 'purple', animate:str = 'None' ) :     
        self.neoText(text=text, color=color, animate = animate )                       