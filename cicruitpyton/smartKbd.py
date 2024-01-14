



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
    'reset': 'reset',
    '~':'~', #Cycle Start/Resume from Feed Hold, Door or Program pause.
    '!':'!', #Feed Hold – Stop all motion.
    'pause':'!', 
    '?':'?',
    '#':'#',
    'scrollLock':'#', # to toggle mpg MPG mode
    '^':'^',
    'f12':'^', # sends $X to grbl to unlock CNC from alarm mode
    '@':'@'

}

class SmartKbd(object):
    def __init__(self):
        self.cmd=bytearray(  [0x01,0x01,0xFE,0x02])
        
        self.grblCommand=''
        
        self.grblPrevCommand = ''

        self.grblMacro={}
        self.grblStateObj=  None
        
        

    def objGrblStateSetter(self,grblStateObj):
        self.grblStateObj = grblStateObj
        self.grblStateObj.setEdit(self.grblCommand)

 
    @staticmethod
    def chars2Grbl(charIn:str): 
        return KBD2GRBL.get(charIn,charIn)
    
    def backspace(self):
        self.grblCommand =self.grblCommand[0:-1]
        self.grblStateObj.setEdit(self.grblCommand)

    
    def put_char(self, char):
        self.grblCommand +=char
        self.grblStateObj.setEdit(self.grblCommand)

    def space(self):
        self.put_char(' ')  
        self.grblStateObj.setEdit(self.grblCommand)


    def clear(self):
        self.grblPrevCommand=self.grblCommand
        self.grblCommand = ''
        self.grblStateObj.setEdit(self.grblCommand)  

    def set_macro(self, key:str):
        self.grblMacro[key]=self.grblCommand
        self.clear()

    def get_macro(self, key:str):
        self.clear()
        self.grblCommand=self.grblMacro[key]
        self.grblStateObj.setEdit(self.grblCommand)
        return self.grblCommand
        
    def get(self):
        return self.grblCommand 

    def getc(self):
        self.clear()
        return self.grblPrevCommand
    
    @staticmethod
    def splitEsc(rxdata:str):
        l_chars=[]
        i=20
        l_chars=[]
        while i>0 and len(rxdata)>0:
            i-=1
            if rxdata.startswith(chr(27)+chr(91)+chr(68)):
                l_char = 'left'
                l_chars.append(l_char)
                rxdata=rxdata[3:]
            elif rxdata.startswith(chr(27)+chr(91)+chr(67)):  
                l_char = 'right'
                l_chars.append(l_char)
                rxdata=rxdata[3:]
            elif rxdata.startswith(chr(27)+chr(91)+chr(65)):  
                l_char = 'up'    
                l_chars.append(l_char)
                rxdata=rxdata[3:]
            elif rxdata.startswith(chr(27)+chr(91)+chr(66)):  
                l_char = 'down'
                l_chars.append(l_char)        
                rxdata=rxdata[3:]
            elif rxdata.startswith(chr(27)+chr(91)):
                l_char = 'ukn'
                l_chars.append(l_char)        
                rxdata=rxdata[3:]
            elif rxdata.startswith(chr(27)):
                l_char = 'esc'
                l_chars.append(l_char)                
                rxdata=rxdata[1:]
            elif rxdata.startswith(chr(18)):
                l_char = 'reset'
                l_chars.append(l_char)                
                rxdata=rxdata[1:]



            elif ord(rxdata[:1])==10:
                l_char ='enter'
                l_chars.append(l_char)                
                rxdata=rxdata[1:]
            elif ord(rxdata[:1])==8:
                l_char ='backspace'
                l_chars.append(l_char)                
                rxdata=rxdata[1:]
            elif ord(rxdata[:1])==9:
                l_char ='tab'
                l_chars.append(l_char)                
                rxdata=rxdata[1:]
            else:
                l_char =rxdata[:1]
                l_chars.append(l_char)                
                rxdata=rxdata[1:]
        return l_chars
    

    def proceedOneChar(self,charIn:str): 
        if charIn =='enter' :
            self.grblStateObj.send2grbl(self.getc())
        elif charIn == ' ' or charIn == 'space' or charIn =='shift space' or charIn =='tab':
            self.put_char(' ')
            self.grblStateObj.neoShowEdit()
        elif charIn == 'backspace' or charIn =='shift backspace'  :
            self.backspace()
            self.grblStateObj.neoShowEdit()
        elif charIn in ('~','!','?','#','^','@') or \
                charIn =='left' or charIn =='right' or charIn =='pageUp' or charIn =='pageDown' or \
                charIn =='up' or charIn =='down' or \
                charIn =='f1' or charIn =='f2' or charIn =='f3' or charIn =='f4' or \
                charIn =='f5' or charIn =='f6' or charIn =='f7' or charIn =='f8' or \
                charIn =='f9' or charIn =='f10' or charIn =='f11' or charIn =='f12' or \
                charIn =='esc' or charIn =='pause'  or charIn =='scrollLock' or charIn =='reset': 
                self.grblStateObj.send2grbl(self.chars2Grbl(charIn))
                self.clear()
        elif charIn.startswith('ctrl-f') and len(charIn)>6:
            self.grblStateObj.send2grbl(self.get_macro(charIn[5:]))
            self.clear()
        elif charIn.startswith('alt-f') and len(charIn)>5:
            self.set_macro(charIn[4:])
            self.grblStateObj.neoShowEdit()

        elif not(charIn.startswith('alt-') or charIn.startswith('shift-') or charIn.startswith('ctrl-') or charIn.startswith('opt-')
                    or charIn.startswith('ralt-') or charIn.startswith('rshift-') or charIn.startswith('rctrl-') or charIn.startswith('ropt-')):    
            self.put_char(charIn) 
            self.grblStateObj.neoShowEdit()



    def proceedChars(self,rxdata:str, DEBUG:bool = False  ): 
        if DEBUG:
                print('proceedChars: rxdata=',rxdata)

        if self.grblStateObj is None:
            if DEBUG:
                print('proceedChars: No grblStateObj FOUND!!!')
            return
        
        l_chars=self.splitEsc(rxdata)
        for l_char in (l_chars):
            self.proceedOneChar(l_char)
