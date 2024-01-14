import displayio
from adafruit_display_text import label
import terminalio
from waveST7789 import WaveST7789
import time

neo = WaveST7789()

messages = [
    "HELLO FROM ADAFRUIT INDUSTRIES",
    "12345678910 -$!+='()/:;?",
    "WOULD YOU LIKE TO PLAY A GAME?",
    "WELCOME TO JOHN PARK'S WORKSHOP",
]

screen = displayio.Group()

VFD_PURPLE = 0x00FFD2
VFD_GREEN = 0x00FF00
VFD_RED = 0xFF0000
VFD_BLUE = 0x0000FF
VFD_WHITE = 0xFFFFFF
VFD_BG = 0x000505

color_bitmap = displayio.Bitmap(neo.width,neo.height,  1)
color_palette = displayio.Palette(1)
color_palette[0] = VFD_BG
bg_sprite = displayio.TileGrid(color_bitmap, x=0, y=0, pixel_shader=color_palette)
screen.append(bg_sprite)

title_label = label.Label(
    terminalio.FONT, text="TTY CLUE", scale=4, color=VFD_PURPLE
)

title_label.x = 20
title_label.y = 16
screen.append(title_label)

footer_label = label.Label(
    terminalio.FONT, text="<PICK         SEND>", scale=2, color=VFD_PURPLE
)
footer_label.x = 4
footer_label.y = 220
screen.append(footer_label)
messages_config = [
    (0, messages[0], VFD_PURPLE, 2, 60),
    (1, messages[1], VFD_PURPLE, 2, 90),
    (2, messages[2], VFD_PURPLE, 2, 120),
    (3, messages[3], VFD_PURPLE, 2, 150),
]

messages_labels = {}  # dictionary of configured messages_labels

message_group = displayio.Group(scale=1)

for message_config in messages_config:
    (name, textline, color, x, y) = message_config  # unpack tuple into five var names
    message_label = label.Label(terminalio.FONT, text=textline, color=color)
    message_label.x = x
    message_label.y = y
    messages_labels[name] = message_label
    message_group.append(message_label)
screen.append(message_group)

neo.display.root_group=screen
time.sleep(1)



import vectorio
def _make_palette( color):
        palette = displayio.Palette(1)
        palette[0] = color
        return palette

def _remove_shapes():
        while len(neo.display.root_group) > 1:
            neo.display.root_group.pop()


def _add_centered_rect(width, height, x_offset=0, y_offset=0, color=None):
        if color is None:
            color = 0
        rectangle = vectorio.Rectangle(
            pixel_shader=_make_palette(color),
            width=width,
            height=height,
            x=(neo.width//2 - width//2) + x_offset - 1,
            y=(neo.height//2 - height//2) + y_offset - 1
        )
        neo.display.root_group.append(rectangle)

def _add_centered_polygon(points, x_offset=0, y_offset=0, color=None):
        if color is None:
            color = 0
        # Figure out the shape dimensions by using min and max
        width = max(points, key=lambda item:item[0])[0] - min(points, key=lambda item:item[0])[0]
        height = max(points, key=lambda item:item[1])[1] - min(points, key=lambda item:item[1])[1]
        polygon = vectorio.Polygon(
            pixel_shader=_make_palette(color),
            points=points,
            x=(neo.width // 2 - width // 2) + x_offset - 1,
            y=(neo.height // 2 - height // 2) + y_offset - 1
        )
        neo.display.root_group.append(polygon)

def _add_centered_circle( radius, x_offset=0, y_offset=0, color=None):
        if color is None:
            color = 0
        circle = vectorio.Circle(
            pixel_shader=_make_palette(color),
            radius=radius,
            x=(neo.width // 2) + x_offset - 1,
            y=(neo.height // 2) + y_offset - 1
        )
        neo.display.root_group.append(circle)


def _set_status_waiting():
    _remove_shapes()
    text_area = label.Label(
        terminalio.FONT,
        text="Waiting for\nconnection",
        color=VFD_PURPLE,
        scale=3,
        anchor_point=(0.1, 0.1),
        anchored_position=(neo.width // 4, neo.height // 4)
    )
    neo.display.root_group.append(text_area)


def _set_status_reverse():
        _remove_shapes()
        _add_centered_polygon([(40, 0), (60, 0), (100, 100), (0, 100)], 0, 0)
        _add_centered_polygon([(0, 40), (100, 40), (50, 0)], 0, -40)


def _set_status_forward():
        _remove_shapes()
        _add_centered_polygon([(20, 0), (60, 0), (80, 100), (0, 100)])
        _add_centered_polygon([(0, 0), (150, 0), (75, 50)], 0, 50)



def _set_status_rotate_ccw():
    _remove_shapes()
    _add_centered_circle(80)
    _add_centered_circle(50, 0, 0, 0xFFFF00)
    _add_centered_rect(160, 60, 0, 0, 0xFFFF00)
    _add_centered_polygon([(40, 0), (80, 40), (0, 40)], 60, 10)
    _add_centered_polygon([(40, 40), (80, 0), (0, 0)], -60, -10)

def _set_status_left():
    _remove_shapes()
    _add_centered_rect(100, 40)
    _add_centered_polygon([(0, 0), (0, 100), (50, 50)], 50)

def _set_status_rotate_cw():
    _remove_shapes()
    _add_centered_circle(80)
    _add_centered_circle(50, 0, 0, 0xFFFF00)
    _add_centered_rect(160, 60, 0, 0, 0xFFFF00)
    _add_centered_polygon([(40, 0), (80, 40), (0, 40)], -60, 10)
    _add_centered_polygon([(40, 40), (80, 0), (0, 0)], 60, -10)

def _set_status_stop():
    _remove_shapes()
    _add_centered_rect(100, 100)



_remove_shapes()
rect = vectorio.Rectangle(
            pixel_shader=_make_palette(0xFFFF00),
            x=10, y=10,
            width=50,
            height=26)
neo.display.root_group.append(rect)
time.sleep(.5)
_set_status_waiting()
time.sleep(.5)
_remove_shapes()
now = time.localtime()


msg_conf = [
            ('x', '     ', VFD_GREEN, 190, 15, 3),
            ('y', '     ', VFD_RED, 190, 55, 3),
            ('z', '     ', VFD_BLUE, 190, 95, 3),
            ('cmd', '     ', VFD_WHITE, 0, 170, 2),
            ('state', '     ', VFD_WHITE, 190, 130, 2),
            ('icon', '    ', VFD_PURPLE, 60, 60, 4),
            ('info', '    ', VFD_WHITE, 0, 200, 1)
        ]

labels = {}  # dictionary of configured messages_labels

message_group = displayio.Group(scale=1)

for c1 in msg_conf:
    (name, textline, color, x, y, scale) = c1  # unpack tuple into five var names
    l_label = label.Label(terminalio.FONT, text=textline, color=color, scale=scale)
    l_label.x = x
    l_label.y = y
    labels[name] = l_label
    neo.display.root_group.append(l_label)
 


 


# Main loop
i=0
# text='<Idle|MPos:0.000,0.000,0.000|Bf:35,1023|FS:0,0,0|MPG:0>'.split('|')
# text='Idle|FS:0,0,0|MPG:0'
textF=''
state=''
state='<Jog|MPos:0.000,0.000,0.000|Bf:35,1023|FS:0,0,0|WCO:0.000,0.000,0.000|WCS:G54|A:|Sc:|MPG:1|H:0|T:0|TLR:0>'
command='$J=G91 G21 Y10.0 F1000.0'
len1=0
for cc in state.split('|'):
    if textF=='':
        textF +=cc
        len1 += len(cc)
        state = cc[1:]
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
        


text2='0.000\n0.000\n0.000'
while True: 
    try: 
        # update text property to change the text showing on the display
        now = time.localtime()
        i+=1
        if i%7==0:
            labels['x'].text = '10.02'
        elif i%7==1:
            labels['y'].text = '-520.12'
        elif i%7==2:
            labels['z'].text = '-27.39'
        elif i%7==3:
            labels['info'].text = textF
        elif i%7==4:
            labels['icon'].text = '>>>'
        elif i%7==5:
            labels['cmd'].text = command
        else:
            labels['state'].text = state
            if state.startswith('Alarm'):
                labels['state'].color=VFD_RED
            elif state.startswith('Jog') or state.startswith('Run'):
                labels['state'].color=VFD_GREEN
            else:
                labels['state'].color=VFD_WHITE
                
                
            
            
        print(i)   

        time.sleep(1)
    except KeyboardInterrupt:
        break





