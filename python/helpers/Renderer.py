import Collections
import IO

from dotmap import DotMap
from lib import epd2in13b 

from PIL import Image
        
def draw_logo(global_settings, frame_black, frame_red):      
    IO.log(global_settings, 'Rendering logo')
    
    pihole_logo_top    = Image.open('img/pihole-bw-80-top.bmp')
    pihole_logo_bottom = Image.open('img/pihole-bw-80-bottom.bmp')
    frame_black.paste(pihole_logo_top, (-12, 2))
    frame_red.paste(pihole_logo_bottom, (-12, 2))

def frame(epd, black, red):
    epd.display_frame(epd.get_frame_buffer(black), epd.get_frame_buffer(red))

def new():
    return Image.new('1', (epd2in13b.EPD_HEIGHT, epd2in13b.EPD_WIDTH), 255)

def draw_chart(color, data, factor):
    chart_bottom = epd2in13b.EPD_WIDTH - 22
    columns = Collections.div_array(data, factor)
    for i, val in enumerate(columns):
        color.rectangle((i * 3 + 2, chart_bottom - val, i * 3 + 3, chart_bottom), outline = 0, fill = 1)

def draw_charts(global_settings, (bottom_color, bottom_chart), (top_color, top_chart)):
    IO.log(global_settings, 'Rendering charts')
    
    factor = max(bottom_chart) / global_settings.cfg.chart.height

    draw_chart(bottom_color, bottom_chart, factor)
    draw_chart(top_color, top_chart, factor)