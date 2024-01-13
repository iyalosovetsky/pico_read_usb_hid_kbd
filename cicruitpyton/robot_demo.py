import displayio
from adafruit_display_text import label
import terminalio
from neopixel import NeoPixel
import time

neo = NeoPixel()

messages = [
    "HELLO FROM ADAFRUIT INDUSTRIES",
    "12345678910 -$!+='()/:;?",
    "WOULD YOU LIKE TO PLAY A GAME?",
    "WELCOME TO JOHN PARK'S WORKSHOP",
]

screen = displayio.Group()

VFD_GREEN = 0x00FFD2
VFD_BG = 0x000505

color_bitmap = displayio.Bitmap(240, 320, 1)
color_palette = displayio.Palette(1)
color_palette[0] = VFD_BG
bg_sprite = displayio.TileGrid(color_bitmap, x=0, y=0, pixel_shader=color_palette)
screen.append(bg_sprite)

title_label = label.Label(
    terminalio.FONT, text="TTY CLUE", scale=4, color=VFD_GREEN
)

title_label.x = 20
title_label.y = 16
screen.append(title_label)

footer_label = label.Label(
    terminalio.FONT, text="<PICK         SEND>", scale=2, color=VFD_GREEN
)
footer_label.x = 4
footer_label.y = 220
screen.append(footer_label)
messages_config = [
    (0, messages[0], VFD_GREEN, 2, 60),
    (1, messages[1], VFD_GREEN, 2, 90),
    (2, messages[2], VFD_GREEN, 2, 120),
    (3, messages[3], VFD_GREEN, 2, 150),
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
time.sleep(5)



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
            y=(neo.display.height // 2 - height // 2) + y_offset - 1
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
    text_area = Label(
        terminalio.FONT,
        text="Waiting for\nconnection",
        color=0,
        scale=3,
        anchor_point=(0.5, 0.5),
        anchored_position=(neo.width // 2, neo.height // 2)
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
            x=0, y=0,
            width=neo.width,
            height=neo.height)
neo.display.root_group.append(rect)


