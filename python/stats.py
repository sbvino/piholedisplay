#!/usr/bin/env python
# encoding: utf-8

 #  @filename   :   main.cpp
 #  @brief      :   2.13inch e-paper display demo
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     September 9 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 ##
from __future__ import unicode_literals

import configparser
import json
import pprint
import random
import re
import requests
import subprocess

from dotmap import DotMap
from lib import epd2in13b 

import time
from time import localtime, strftime

import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

globals = DotMap(dict(    
    width = epd2in13b.EPD_HEIGHT,
    height = epd2in13b.EPD_WIDTH,
    current_row = 0
))

class Stats:
    @staticmethod
    def render(epd):        
        while True:
            IO.read_cfg();        
            cfg = globals.cfg
            IO.log_obj('Configuration:', cfg.toDict(), 3)
            
            IO.log('Rendering status')
        
            frame_black = Renderer.new()
            frame_red   = Renderer.new()

            black = ImageDraw.Draw(frame_black)
            red   = ImageDraw.Draw(frame_red)

            black.rectangle((0, 0, globals.width, globals.height), outline = 0, fill = None)

            ip              = IO.shell('hostname -I | cut -d" " -f1')
            host            = IO.shell('hostname').lower() + '.local'
            mem, mem_part   = IO.shell('free -m | awk \'NR==2{printf "%s/%s MB#%.2f%%", $3,$2,$3*100/$2 }\'').split('#', 1)
            disk, disk_part = IO.shell('df -h | awk \'$NF=="/"{printf "%d/%d GB#%s", $3,$2,$5}\'').split('#', 1)        
            
            IO.log(
    '''IP:           {0}
    Host:         {1}
    Memory usage: {2} {3}
    Disk:         {4} {5}'''.format(ip, host, mem, mem_part, disk, disk_part))
            
            try:
                data = IO.get_json(cfg.pihole.api_url)
                
                clients        = data['unique_clients']
                ads_blocked    = data['ads_blocked_today']
                ads_percentage = data['ads_percentage_today']
                dns_queries    = data['dns_queries_today']
                
                IO.log_obj('API response:', data)
            except KeyError:
                time.sleep(1)
                continue

            try:
                data = IO.get_json(cfg.pihole.api_url + '?overTimeData10mins')

                domains = Collections.dict_to_columns(data['domains_over_time'])
                ads     = Collections.dict_to_columns(data['ads_over_time'])
            except KeyError:
                time.sleep(1)
                continue

            ads_blocked_label = random.choice(cfg.labels_ads)
               
            if cfg.screen.draw_logo:
                Renderer.draw_logo(frame_black, frame_red)
            else:
                Renderer.draw_charts((black, domains), (red, ads))

            globals.current_row = 0
            
            Text.row(black, cfg.chart.x_stat, 'HOST:', host)
            Text.row(black, cfg.chart.x_stat, 'IP:',   ip)
            Text.row(black, cfg.chart.x_stat, 'Mem:',  mem)
            Text.row(black, cfg.chart.x_stat, 'Disk:', disk)
            
            Text.line(red, 2, 31, mem_part, align = 'right')
            Text.line(red, 2, 46, disk_part, align = 'right')

            Text.row(black, cfg.chart.x_result, 'Clients:', clients)
            Text.row(black, cfg.chart.x_result, ads_blocked_label + ':', ads_blocked)
            Text.row(black, cfg.chart.x_result, 'DNS Queries:', dns_queries)
            
            Text.line(red, 2, 76, '{0:.2f}%'.format(ads_percentage), align = 'right')

            Text.line(red, 7,  globals.height - 24, 'Pi', size = 11)
            Text.line(red, 20, globals.height - 24, '-hole', True)

            Text.line(black, 13, globals.height - 14, u'↻:')
            Text.line(black, 23, globals.height - 12, strftime('%H:%M', localtime()), size = 8)

            rotation = (PIL.Image.ROTATE_90, PIL.Image.ROTATE_270)[cfg.screen.draw_inverted]
            Renderer.frame(epd, frame_black.transpose(rotation), frame_red.transpose(rotation))
            
            IO.log('Rendering completed', 
                'Sleeping for {0} min at {1}'.format(cfg.pihole.interval_minutes, strftime('%H:%M:%S', localtime())))
            epd.sleep()
            epd.delay_ms(cfg.pihole.interval_minutes * 60 * 1000)

            # awakening the display
            epd.init()

class Text:
    @staticmethod
    def line(draw, x, y, string, bold = False, size = 10, align = ''):
        top = 2

        font_name = ('DejaVuSansMono', 'DejaVuSansMono-Bold')[bold]
        font_size = (size, 11)[bold]
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + font_name + '.ttf', font_size)

        if 'right' in align or 'bottom' in align:
            w, h = draw.textsize(string, font = font)
            if 'right' in align:
                x = globals.width - (w + x)
            if 'bottom' in align:
                y = globals.height - (h + y)
        
        draw.text(
            (x, top + y),
            string,
            font = font,
            fill = 0)                    
    
    @staticmethod
    def replace(str, replacements):
        for old, new in replacements:
            str = re.sub(old, new, str)
        return str
    
    @classmethod
    def row(self, draw, x, label, value):
        y = globals.current_row * 15
        self.line(draw, x[0], y,     str(label), True)
        self.line(draw, x[1], y + 1, str(value), False)
        globals.current_row += 1
        
class Renderer:
    @staticmethod
    def draw_logo(frame_black, frame_red):      
        IO.log('Rendering logo')
        
        pihole_logo_top    = Image.open('img/pihole-bw-80-top.bmp')
        pihole_logo_bottom = Image.open('img/pihole-bw-80-bottom.bmp')
        frame_black.paste(pihole_logo_top, (-12, 2))
        frame_red.paste(pihole_logo_bottom, (-12, 2))

    @staticmethod
    def frame(epd, black, red):
        epd.display_frame(epd.get_frame_buffer(black), epd.get_frame_buffer(red))

    @staticmethod
    def new():
        return Image.new('1', (epd2in13b.EPD_HEIGHT, epd2in13b.EPD_WIDTH), 255)

    @staticmethod
    def draw_chart(color, data, factor):
        chart_bottom = epd2in13b.EPD_WIDTH - 22
        columns = Collections.div_array(data, factor)
        for i, val in enumerate(columns):
            color.rectangle((i * 3 + 2, chart_bottom - val, i * 3 + 3, chart_bottom), outline = 0, fill = 1)

    @classmethod
    def draw_charts(self, (bottom_color, bottom_chart), (top_color, top_chart)):
        IO.log('Rendering charts')
        
        factor = max(bottom_chart) / globals.cfg.chart.height

        self.draw_chart(bottom_color, bottom_chart, factor)
        self.draw_chart(top_color, top_chart, factor)

class IO:
    @staticmethod
    def shell(command):
        return subprocess.check_output(command, shell = True).strip()
    
    @staticmethod
    def get_json(url):
        r = requests.get(url)
        return json.loads(r.text)
    
    @staticmethod
    def log(*args):
        newline = globals.cfg.screen.newline
        print newline + newline.join(args)
                
    @classmethod
    def read_cfg(self):
        with open('config.json') as json_file:
            config = DotMap(json.load(json_file))
        globals.cfg = config
    
    @classmethod
    def log_obj(self, title, obj, depth = 1):
        newline = globals.cfg.screen.newline
        pp = pprint.PrettyPrinter(indent = 2, depth = depth)
        
        str = Text.replace(
            pp.pformat(obj),
            [
                ('u?\'', '\''),
                ('^{', '{' + newline + ' '),
                ('}$', newline + '}')
            ])
            
        self.log(title, str)
    
class Collections:
    @staticmethod
    def dict_to_columns(dict):
        col_count = 20
        dict_length = len(dict);
        if dict_length == 0:
            return []
        
        if dict_length <= col_count:
            entries_per_column = 1
            col_count = dict_length
        else:
            entries_per_column = dict_length / col_count

        colums = [0] * col_count
        index_dict = 0

        for key in dict:
            index = index_dict / entries_per_column;
            if index >= col_count:
                continue
            colums[index] += dict[key]
            index_dict += 1

        return colums

    @staticmethod
    def div_array(array, factor):
        return [int(i / factor) for i in array]

def deep_reset(epd):
    IO.read_cfg();
    IO.log('Resetting to white...')
    white_screen = Renderer.new()
    Renderer.frame(epd, white_screen, white_screen)
    epd.delay_ms(1000)
    
def main():
    IO.read_cfg();
    IO.log('Initiating screen...')
    epd = epd2in13b.EPD()
    epd.init()
    
    try:
        Stats.render(epd)
    finally:
        IO.log('Sleeping epd before leaving')
        epd.sleep()

if __name__ == '__main__':
    main()