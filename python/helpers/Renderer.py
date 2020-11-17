from PIL import Image

import Collections, IO

from lib import epd2in13b as Display

# Public methods
def frame(display, black, red):
    display.display_frame(display.get_frame_buffer(black), display.get_frame_buffer(red))

def new():
    return Image.new('1', (Display.EPD_HEIGHT, Display.EPD_WIDTH), 255)

def draw_logo(cfg, frame_black, frame_red):
    IO.log(cfg, 'Rendering logo')

    pihole_logo_top    = Image.open('img/pihole-bw-80-top.bmp')
    pihole_logo_bottom = Image.open('img/pihole-bw-80-bottom.bmp')
    frame_black.paste(pihole_logo_top, (-12, 2))
    frame_red.paste(pihole_logo_bottom, (-12, 2))

def draw_charts(cfg, (bottom_color, bottom_chart), (top_color, top_chart)):
    IO.log(cfg, 'Rendering charts')

    factor = max(bottom_chart) / cfg.chart.height

    __draw_chart(bottom_color, bottom_chart, factor)
    __draw_chart(top_color, top_chart, factor)

# Private methods
def __draw_chart(color, data, factor):
    chart_bottom = Display.EPD_WIDTH - 22
    columns = Collections.div_array(data, factor)
    for i, val in enumerate(columns):
        color.rectangle((i * 3 + 2, chart_bottom - val, i * 3 + 3, chart_bottom), outline = 0, fill = 1)