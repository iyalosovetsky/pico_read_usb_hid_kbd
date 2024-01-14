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

DEBUG= False

VFD_PURPLE = 0x00FFD2
VFD_GREEN = 0x00FF00
VFD_RED = 0xFF0000
VFD_YELLOW = 0xFFFF00


VFD_BLUE = 0x0000FF
VFD_WHITE = 0xFFFFFF

VFD_ARROW_X = VFD_RED
VFD_ARROW_Y = VFD_GREEN
VFD_ARROW_Z = VFD_BLUE


VFD_BG = 0x000505


import   time
from adafruit_display_text import label
import terminalio
import microcontroller

class GrblState(object):
    def __init__(self,kbd,uart_grbl_mpg,neo,
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
        self.__version__ = '0.1'
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
        self._execProgress = 'ok'
        self.kbd = kbd
        self.uart_grbl_mpg = uart_grbl_mpg
        self.neo = neo
        self.neo.setStateBottomRight([0,0,0]) # state on RB of display
        self._jog_arrow = ''
        self.idleCounter = 0
        self.editCmd = ''
        self.statetext = ''
        self.prev_statetext  = ''
        self.grblCmd2send=[]
        self._state_time_change = time.time()
        self._msg_conf = [
            ('x', '     ', VFD_GREEN, 190, 15, 3),
            ('y', '     ', VFD_RED, 190, 55, 3),
            ('z', '     ', VFD_BLUE, 190, 95, 3),
            ('cmd', '     ', VFD_WHITE, 0, 170, 2),
            ('state', '     ', VFD_WHITE, 190, 130, 2),
            ('icon', 'grbl', VFD_PURPLE, 20, 20, 4),
            ('info', '    ', VFD_WHITE, 0, 200, 1)
        ]
        self.labels = {}  # dictionary of configured messages_labels
        self.help = [
           'ctrl-r\nreboot',
           'ctrl-c\ncancel',
           '^\nMPG',
           '$\nunlock',
           'esc\ncancel',
           '!\nhold\\nresume',
           '?\nquery'
        ]
        self.helpIdx=-1



        for c1 in self._msg_conf:
            (name, textline, color, x, y, scale) = c1  # unpack tuple into five var names
            l_label = label.Label(terminalio.FONT, text=textline, color=color, scale=scale)
            l_label.x = x
            l_label.y = y
            self.labels[name] = l_label
            self.neo.display.root_group.append(l_label)


        self.hello()
        




    def neoSplitLine(self,text):
      textF=''
      len1 =0
      for cc in text.split('|'):
        if textF=='':
            textF +=cc
            len1 += len(cc)
            continue
        if textF.startswith('Bf'):
            continue
        if textF.startswith('MPos'):
            continue
        if textF.startswith('WCO'):
            continue    
        else:
            if len1+len(cc)>50:
                textF +='\n'
                len1 =0
            len1 += len(cc)+1
            textF +='|'+cc
      return textF
            
        
          

    def neoLabel(self,text,id='info',color=None):
        if color is not None and isinstance(color,str):
           if color.lower() == 'red':
              color = VFD_RED
           elif color.lower() == 'green':   
              color = VFD_GREEN
           elif color.lower() == 'blue':   
              color = VFD_BLUE
           elif color.lower() == 'purple':   
              color = VFD_PURPLE      
           elif color.lower() == 'yellow':   
              color = VFD_YELLOW      
           elif color.lower() == 'white':   
              color = VFD_WHITE      

        if id=='x':
          self.labels[id].text = '{0:.1f}'.format(self._mX)
          self.labels[id].color=VFD_ARROW_X
        elif id=='y':
          self.labels[id].text = '{0:.1f}'.format(self._mY)  
          self.labels[id].color=VFD_ARROW_Y
        elif id=='z':
          self.labels[id].text = '{0:.1f}'.format(self._mZ)  
          self.labels[id].color=VFD_ARROW_Z
        elif id=='cmd':
          self.labels[id].text = text
          if color is None:
             self.labels[id].color=VFD_PURPLE
        elif id=='state':
          self.labels[id].text = text
          if color is None and text.lower().startswith('alarm'):
             self.labels[id].color=VFD_RED
          elif color is None and (text.lower().startswith('run') or text.lower().startswith('jog')):
             self.labels[id].color=VFD_WHITE
          elif color is None:
             self.labels[id].color=VFD_GREEN
          else:   
             self.labels[id].color=color
        elif id=='icon':
          self.labels[id].text = text
          if color is None:
             self.labels[id].color=VFD_GREEN
          else:   
             self.labels[id].color=color
        elif id=='info':
          self.labels[id].text = self.neoSplitLine(text)
          if color is None:
             self.labels[id].color=VFD_GREEN if self._mpg else VFD_WHITE
          else:   
             self.labels[id].color=color

             
    def hello(self):
       self.neoLabel('GrblHAL v'+self.__version__,id='cmd',color=VFD_YELLOW)
       time.sleep(0.5)
       #self.neoLabel('       ',id='cmd',color=VFD_YELLOW)

    def getHelp(self):
       self.helpIdx+=1
       self.helpIdx=self.helpIdx%len(self.help)
       return self.help[self.helpIdx]
       

    def neoIcon(self,text,color=None) :     
        self.neoLabel(text,id='icon',color=VFD_YELLOW if color is None else  color)


       
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
      if DEBUG or (command is not None and command!='' and not command.startswith('?')) :
        print("mpgCommand:",command)
      if not( command.startswith('?') or command.startswith('!') or command.startswith('$') or command.startswith('$')):
        self._execProgress='do'  
      self.uart_grbl_mpg.write(command.encode())

    #jog $J=G91 X0 Y-5 F600
    #$J=G91 X1 F100000

    def grblJog(self, x:float=0.0, y: float=0.0, z:float=0.0):
      f=self.feedrate
      cmd=''
      if x is not None and x!=0.0:
        self.set_jog_arrow(('+' if x>0 else '-')+'x')
        cmd=f'$J=G91 G21 X{x} F{f}'
        #MPG -> <Idle|MPos:30.000,0.000,0.000|Bf:35,1023|FS:0,0,0|Pn:HS|WCO:0.000,0.000,0.000|WCS:G54|A:|Sc:|MPG:1|H:0|T:0|TLR:0|Sl:0.0|FW:grblHAL>
      elif y is not None and y!=0.0:
        self.set_jog_arrow(('+' if y>0 else '-')+'y')
        cmd=f'$J=G91 G21 Y{y} F{f}'
      elif z is not None and z!=0.0:
        self.set_jog_arrow(('+' if z>0 else '-')+'z')
        cmd=f'$J=G91 G21 Z{z} F{f}'
      if cmd !='':
          self.neoLabel(cmd,id='cmd')  
          self.mpgCommand(cmd+'\r\n')
          self.neoDisplayJog() 



    def send2grblOne(self,command:str):
      if DEBUG or (command is not None and command!='' and not command.startswith('?')) :
        print('send2grblOne:',command,len(command))
      if command in ('~','!','?'):
        #self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
        self.mpgCommand(command)
        if command !='?':
          self.neoLabel(command,id='cmd')
        else:  
           self.neoLabel(self.editCmd if self.editCmd!='' else '       ',id='cmd')
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
          self.neoIcon('feed {0:.0f}'.format(self._feedrate))
      elif command=='+feed':
          self.inc_feedrate()
          self.neoIcon('feed {0:.0f}'.format(self._feedrate))
      elif command=='-stepXY' :    
          self.dec_stepXY()
          if self._dXY<1:
            self.neoIcon('dX {0:.1f}'.format(self._dXY).replace('.',','))
          else:  
             self.neoIcon('dX {0:.0f}'.format(self._dXY))
      elif command=='+stepXY' :    
          self.inc_stepXY()
          if self._dXY<1:
            self.neoIcon('dX {0:.1f}'.format(self._dXY).replace('.',','))
          else:  
             self.neoIcon('dX {0:.0f}'.format(self._dXY))
      elif command=='-stepZ' :    
          self.dec_stepZ()
          if self._dZ<1:
            self.neoIcon('dZ {0:.1f}'.format(self._dZ).replace('.',','))
          else:  
             self.neoIcon('dZ {0:.0f}'.format(self._dZ))
      elif command=='+stepZ' :    
          self.inc_stepZ()
          if self._dZ<1:
            self.neoIcon('dZ {0:.1f}'.format(self._dZ).replace('.',','))
          else:  
             self.neoIcon('dZ {0:.0f}'.format(self._dZ))
      elif command in ('#'):  
        #self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) ##2 - leds ???       # 2 - macro1 10/2 blink
        self.neoLabel(command,id='cmd')
        self.uart_grbl_mpg.write(bytearray(b'\x8b\r\n'))
      elif command in ('cancel'):  
        # if self.state == 'run' or self.state == 'jog':
          #self.flashKbdLEDs(LED_SCROLLLOCK , BLINK_5) ##2 - leds ???       # 2 - macro1 10/2 blink
          self.uart_grbl_mpg.write(bytearray(b'\x85\r\n')) #Jog Cancel
          self.uart_grbl_mpg.write(bytearray(b'\x18\r\n')) # cancel ascii ctrl-x
          self.neoLabel(command,id='cmd')
          time.sleep(1)
          self.uart_grbl_mpg.write(bytearray(b'?\r\n')) # 
        # else:
          #self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
          # pass 
      elif command in ('reset'):  
          self.uart_grbl_mpg.write(bytearray(b'\x85\r\n')) #Jog Cancel
          self.uart_grbl_mpg.write(bytearray(b'\x18\r\n')) # cancel ascii ctrl-x
          self.neoLabel(command,id='cmd')
          time.sleep(1)
          self.uart_grbl_mpg.write(bytearray(b'?\r\n')) # 
          time.sleep(1)
          microcontroller.reset()
      elif command in ('help'):  
          self.neoIcon(self.getHelp())
      elif command in ('^'):  
        #self.flashKbdLEDs(LED_ALL , BLINK_2) ##7 - 3 leds       # 1 - macro1
        self.neoLabel('$X',id='cmd')
        self.uart_grbl_mpg.write('$X'.encode()+b'\r\n')
      else:
        if command.strip()!='':
          # self.neoInfo(command[:10],virtual_width = 128)
          self.neoLabel(command,id='cmd')
          self.uart_grbl_mpg.write(command.encode()+b'\r\n')
          if not(command.startswith('?') or command.startswith('!') or command.startswith('$') or command.startswith('$')):
            self._execProgress='do'

    def send2grbl(self,command:str):        
      if DEBUG or (command is not None and command!='' and not command.startswith('?')) :
        self.grblCmd2send.append(command)
        print('send2grbl:',command,' queueLen=',len(self.grblCmd2send), self._execProgress)
        if self._execProgress!='do':
          self.popCmd2grbl()

    def popCmd2grbl(self):
      if len(self.grblCmd2send)>0:
        l_cmd=self.grblCmd2send[0]
        if self._execProgress == 'do' and (
          l_cmd=='-y' or l_cmd=='+y' or 
          l_cmd=='-x' or l_cmd=='+x' or 
          l_cmd=='-z' or l_cmd=='+z' ):
          print('popCmd2grbl: busy', self._execProgress, l_cmd )
          return
        else:
          l_cmd=self.grblCmd2send.pop(0)
          self.send2grblOne(l_cmd)
            

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
        if len(grblState)>5:
          i=5
          while i>0 and grblState.endswith('ok'):
            i-=1
            grblState=grblState[:-2].strip()

        if not ((grblState.startswith('<') and grblState.endswith('>'))  or grblState.startswith('error:')  or grblState=='ok'):
          return         
        if grblState.startswith('error:'):
          self._execProgress='error'
          self._state=grblState
          self._state_is_changed = (self._state_prev is None or  self._state_prev != self._state)
          self._state_prev = self._state
          self._state_time_change = time.time()
          return
        elif grblState=='ok':
          self._execProgress='ok'
          self._state='ok'
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
              if self._execProgress=='do' and (self._state.startswith('idle') or self._state.startswith('alarm')) :
                 self._execProgress='done'
              self._state_time_change = time.time()
              
            else:
                elem = token.split(':')
                if len(elem)>1 and elem[0]=='mpg' and elem[1] is not None and (elem[1]=='1' or elem[1]=='0'):
                    
                    self._mpg_prev=self._mpg
                    self._mpg=(elem[1]=='1')
                    self.labels['info'].color=VFD_GREEN if self._mpg  else VFD_WHITE
                elif  len(elem)>1 and elem[0]=='mpos' and elem[1] is not None:       
                    xyz = elem[1].split(',')
                    if len(xyz)==3:
                      self._mX, self._mY,self._mZ = [ float(xx) for xx in xyz ]


    def displayState(self,grblState:str):     
      self.parseState(grblState.strip())
      # print("MPG ->",grblState,' \n - >> prev ',self.state_prev, self.mpg_prev,' now=>',self.state, self.mpg)
      self.neoLabel(self.grbl_state,id='info')
      self.neoLabel('',id='x')
      self.neoLabel('',id='y')
      self.neoLabel('',id='z')
      
      
      if self.mpg is not None and (self.mpg_prev is None or self.mpg !=self.mpg_prev):
          self._mpg_prev=self._mpg
      if self.state_is_changed() or self.state == 'idle' or self.state.startswith('hold') :  
              if self.state.startswith('alarm'):
                  self._jog_arrow = ''
                  self.neoDisplayJog()
                  self.neoIcon('^\nshft+6')
                  self.neoLabel(self.state,id='state')
              elif self.state == 'run':    
                  self.neoLabel(self.state,id='state')
              elif self.state == 'jog':    
                  self.neoLabel(self.state,id='state')
                  self.neoDisplayJog()
              elif self.state=='hold:1':
                  self.neoLabel(self.state,id='state')
              elif self.state=='hold:0':
                  #self.flashKbdLEDs(LED_NUMLOCK , BLINK_5)
                  # self.neoInfo(self.state)  
                  self.neoLabel(self.state,id='state')
              elif self.state.startswith('error'): 
                  self._jog_arrow = '' 
                  # self.neoError('err')  
                  #self.flashKbdLEDs(LED_CAPSLOCK , BLINK_5) 
                  self.neoLabel(self.state,id='state')
              elif self.state == 'idle' :
                  self._jog_arrow = ''    
                  #self.flashKbdLEDs(LED_ALL , NOBLINK) 
                  # self.neoIdle()
                  self.neoLabel(self.state,id='state')
    


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
            cl.append(cl0[cli])
         else:
            cl[cli] = cl0[cli] 

         
            
            
      self.prev_statetext = self.statetext
      self.statetext = text
      self.neo.clear()
      self.neo.text(text, 0, 0,cl,no_clear_wnd_pos=(self.prev_statetext == self.statetext) )
      #self.neo.animate(p_type=animate, p_delay=0.3)
      arrState=self.neo.rbState
      if self._mpg:
         arrState[0]='GREEN'
      else:
         arrState[0]='PURPLE'
      if  self.state.startswith('alarm'):
         arrState[2]='RED'
      elif self.state.startswith('hold'):
         arrState[2]='YELLOW'   
      else:
         arrState[2]='BLACK'   
      self.neo.setStateBottomRight(arrState)

         
       

    # def neoError(self,text:str, color:str = 'red', animate:str = 'window-left-right' ) :     
    #     self.neoText(text=text, color=color, animate = animate )     

    def neoDisplayJog(self) :     
        color=X_ARROW_COLOR
        if self._jog_arrow[-1:]=='y':
           color=Y_ARROW_COLOR
        elif self._jog_arrow[-1:]=='z':  
           color=Z_ARROW_COLOR

        # self.neoText(text=text, color=color, animate = animate, virtual_width = 16 )  
        if self._jog_arrow=='':
           self.neoIcon(text='   ')   
        else:
          self.neoIcon(text='>>>' if self._jog_arrow.startswith('+') else '<<<',color=color)   


    # def neoInfo(self,text:str, color:str = 'purple', animate:str = 'window-left-right', virtual_width = 64 ) :     
    #     self.neoText(text=text, color=color, animate = animate, virtual_width = virtual_width )  

    def setEdit(self, text):
       self.editCmd=text

    def neoShowEdit(self):
      self.idleCounter = 0
      # self.neoIdle()
      self.neoLabel(text=self.editCmd,id='cmd')
                                

    # def neoIdle(self, virtual_width = 64 ) :     
    #     color = 'purple'
    #     text = self.state
    #     animate = 'window-left-right'
    #     if self.kbd.get()!='':
    #       if self.idleCounter>10 and self.idleCounter%10<=7:  
    #         color = [X_ARROW_COLOR, Y_ARROW_COLOR , Z_ARROW_COLOR]
    #         text = '{0:.1f} {1:.1f} {2:.1f}'.format(self._mX, self._mY, self._mZ).replace('.',',')
    #         animate = 'window-left-right'
    #       else:  
    #        color = 'purple'
    #        animate = 'edit'
    #        text = self.kbd.get()

    #     else:   
    #       if self.idleCounter%4==0:
    #         color = 'purple'
    #         text = self.state
    #       elif self.idleCounter%4==1:  
    #         color = X_ARROW_COLOR   
    #         text = '{0:.1f}'.format(self._mX).replace('.',',')
    #       elif self.idleCounter%4==2:  
    #         color = Y_ARROW_COLOR   
    #         text = '{0:.1f}'.format(self._mY).replace('.',',')
    #       elif self.idleCounter%4==3:  
    #         color = Z_ARROW_COLOR   
    #         text = '{0:.1f}'.format(self._mZ).replace('.',',')
    #     self.idleCounter +=1
    #     self.neoText(text=text, color=color, animate = animate, virtual_width = virtual_width )                               

#todo new area Gcode line . Display there command and result, clear when new state parsed and state not in run and jog

#and it for  manual comands      
# hard beats every send ? or state changes        
        