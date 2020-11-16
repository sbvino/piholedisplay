#!/usr/bin/env python
# encoding: utf-8

#  @filename   :   stats.py
#  @brief      :   Render Pi-Hole stats to 2.13inch e-paper.
#  @author     :   @Cerbrus on GitHub
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

import random

from helpers import Collections
from helpers import IO
from helpers import Renderer
from helpers import Text

from dotmap import DotMap
from lib import epd2in13b

import time
from time import localtime, strftime

from PIL import Image
from PIL import ImageDraw

global_settings = DotMap(dict(
    width = epd2in13b.EPD_HEIGHT,
    height = epd2in13b.EPD_WIDTH,
    current_row = 0
))

class Stats:
    def __init__(self, epd, global_settings):
        while True:
            success = self.render(epd, global_settings)
            if success == False:
                continue
    
    def render(self, epd, g):
        IO.read_cfg(g);
        cfg = g.cfg
        IO.log_obj(g, 'Configuration:', cfg.toDict(), 3)

        IO.log(g, 'Rendering status')

        frame_black = Renderer.new()
        frame_red   = Renderer.new()

        black = ImageDraw.Draw(frame_black)
        red   = ImageDraw.Draw(frame_red)

        black.rectangle((0, 0, g.width, g.height), outline = 0, fill = None)

        ip              = IO.shell('hostname -I | cut -d" " -f1')
        host            = IO.shell('hostname').lower() + '.local'
        mem, mem_part   = IO.shell('free -m | awk \'NR==2{printf "%s/%s MB#%.2f%%", $3,$2,$3*100/$2 }\'').split('#', 1)
        disk, disk_part = IO.shell('df -h | awk \'$NF=="/"{printf "%d/%d GB#%s", $3,$2,$5}\'').split('#', 1)

        IO.log(g,
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

            IO.log_obj(g, 'API response:', data)
        except KeyError:
            time.sleep(1)
            return False

        try:
            data = IO.get_json(cfg.pihole.api_url + '?overTimeData10mins')

            domains = Collections.dict_to_columns(data['domains_over_time'])
            ads     = Collections.dict_to_columns(data['ads_over_time'])
        except KeyError:
            time.sleep(1)
            return False

        ads_blocked_label = random.choice(cfg.labels_ads)

        if cfg.screen.draw_logo:
            Renderer.draw_logo(frame_black, frame_red)
        else:
            Renderer.draw_charts(g, (black, domains), (red, ads))

        g.current_row = 0

        Text.row(g, black, cfg.chart.x_stat, 'HOST:', host)
        Text.row(g, black, cfg.chart.x_stat, 'IP:',   ip)
        Text.row(g, black, cfg.chart.x_stat, 'Mem:',  mem)
        Text.row(g, black, cfg.chart.x_stat, 'Disk:', disk)

        Text.line(g, red, 2, 31, mem_part, align = 'right')
        Text.line(g, red, 2, 46, disk_part, align = 'right')

        Text.row(g, black, cfg.chart.x_result, 'Clients:', clients)
        Text.row(g, black, cfg.chart.x_result, ads_blocked_label + ':', ads_blocked)
        Text.row(g, black, cfg.chart.x_result, 'DNS Queries:', dns_queries)

        Text.line(g, red, 2, 76, '{0:.2f}%'.format(ads_percentage), align = 'right')

        Text.line(g, red, 7,  g.height - 24, 'Pi', size = 11)
        Text.line(g, red, 20, g.height - 24, '-hole', True)

        Text.line(g, black, 13, g.height - 14, u'↻:')
        Text.line(g, black, 23, g.height - 12, strftime('%H:%M', localtime()), size = 8)

        rotation = (Image.ROTATE_90, Image.ROTATE_270)[cfg.screen.draw_inverted]
        Renderer.frame(epd, frame_black.transpose(rotation), frame_red.transpose(rotation))

        IO.log(g, 'Rendering completed',
            'Sleeping for {0} min at {1}'.format(cfg.pihole.interval_minutes, strftime('%H:%M:%S', localtime())))
        epd.sleep()
        epd.delay_ms(cfg.pihole.interval_minutes * 60 * 1000)

        # Awakening the display
        epd.init()
        
        # Rendering was successful.
        return True

def main():
    IO.read_cfg(global_settings);
    IO.log(global_settings, 'Initiating screen...')
    epd = epd2in13b.EPD()
    epd.init()

    try:
        Stats(epd, global_settings)
    finally:
        IO.log(global_settings, 'Sleeping epd before leaving')
        epd.sleep()

if __name__ == '__main__':
    main()