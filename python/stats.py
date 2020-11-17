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

from helpers import IO
from helpers import Renderer
from helpers import Text

from dotmap import DotMap
from lib import epd2in13b as Display

import time
from time import localtime, strftime

from PIL import Image
from PIL import ImageDraw

global_settings = DotMap(dict(
    width = Display.EPD_HEIGHT,
    height = Display.EPD_WIDTH,
    current_row = 0
))

class Stats:
    def __init__(self, display, global_settings):
        while global_settings.cfg.options.interval_minutes > 0:
            success = self.render(display, global_settings)
            if success == False:
                continue
            IO.read_cfg(global_settings);

    def render(self, display, g):
        c = g.cfg
        IO.log_obj(c, 'Configuration:', c.toDict(), 3)

        IO.log(c, 'Rendering status')

        frame_black = Renderer.new()
        frame_red   = Renderer.new()

        black = ImageDraw.Draw(frame_black)
        red   = ImageDraw.Draw(frame_red)

        black.rectangle((0, 0, g.width, g.height), outline = 0, fill = None)

        ip              = IO.shell('hostname -I | cut -d" " -f1')
        host            = IO.shell('hostname').lower() + '.local'
        mem, mem_part   = IO.shell('free -m | awk \'NR==2{printf "%s/%s MB#%.2f%%", $3,$2,$3*100/$2 }\'').split('#', 1)
        disk, disk_part = IO.shell('df -h | awk \'$NF=="/"{printf "%d/%d GB#%s", $3,$2,$5}\'').split('#', 1)

        IO.log(c,
'''IP:           {0}
Host:         {1}
Memory usage: {2} {3}
Disk:         {4} {5}'''.format(ip, host, mem, mem_part, disk, disk_part))

        try:
            clients, ads_blocked, ads_percentage, dns_queries = IO.get_stats_pihole(c)
            domains, ads = IO.get_stats_pihole_history(c)
        except KeyError:
            time.sleep(1)
            return False

        IO.log(c,
'''Clients:     {0}
Ads blocked: {1} {2:.2f}%
DNS Queries: {3}'''.format(clients, ads_blocked, ads_percentage, dns_queries))

        if c.options.draw_logo:
            Renderer.draw_logo(c, frame_black, frame_red)
        else:
            Renderer.draw_charts(c, (black, domains), (red, ads))

        ads_blocked_label = random.choice(c.labels_ads)
        percentage_format = ('{0:.2f}%', '{0:.1f}%')[ads_blocked > 9999]

        g.current_row = 0

        Text.row(g, black, c.chart.x_stat, 'HOST:', host)
        Text.row(g, black, c.chart.x_stat, 'IP:',   ip)
        Text.row(g, black, c.chart.x_stat, 'Mem:',  mem)
        Text.row(g, black, c.chart.x_stat, 'Disk:', disk)

        Text.line(g, red, 2, 31, mem_part, align = 'right')
        Text.line(g, red, 2, 46, disk_part, align = 'right')

        Text.row(g, black, c.chart.x_result, 'Clients:', clients)
        Text.row(g, black, c.chart.x_result, ads_blocked_label + ':', ads_blocked)
        Text.row(g, black, c.chart.x_result, 'DNS Queries:', dns_queries)

        Text.line(g, red, 2, 76, percentage_format.format(ads_percentage), align = 'right')

        Text.line(g, red, 7,  g.height - 24, 'Pi', size = 11)
        Text.line(g, red, 20, g.height - 24, '-hole', True)

        Text.line(g, black, 13, g.height - 14, u'↻:')
        Text.line(g, black, 23, g.height - 12, strftime('%H:%M', localtime()), size = 8)

        rotation = (Image.ROTATE_90, Image.ROTATE_270)[c.options.draw_inverted]
        Renderer.frame(display, frame_black.transpose(rotation), frame_red.transpose(rotation))

        IO.log(c, 'Rendering completed',
            'Sleeping for {0} min at {1}'.format(c.options.interval_minutes, strftime('%H:%M:%S', localtime())))
        display.sleep()
        display.delay_ms(c.options.interval_minutes * 60 * 1000)

        # Awakening the display
        display.init()

        # Rendering was successful.
        return True

def main():
    IO.read_cfg(global_settings);
    IO.log(global_settings.cfg, 'Initiating screen...')
    display = Display.EPD()
    display.init()

    try:
        Stats(display, global_settings)
    finally:
        IO.log(global_settings.cfg, 'Sleeping display before leaving')
        display.sleep()
if __name__ == '__main__':
    main()