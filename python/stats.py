# encoding: utf-8
#!/usr/bin/env python
#  @filename   :   stats.py
#  @brief      :   Render Pi-Hole stats to 2.13inch e-paper.
#  @author     :   @Cerbrus on GitHub
#
#  Copyright (C) Waveshare     September 9 2017
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated docunetation files (the "Software"), to deal
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
# LIABILITY WHETHER IN AN ACTioN OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTioN WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##

'''Render statistics to the Pi-Hole's screen every X minutes'''

import random
import time

from PIL import Image, ImageDraw

from helpers import io as IO, renderer as Renderer
from helpers.text import Text
from helpers.collections import dot_dict
from helpers.log import Logger

from lib import epd2in13b as Display

# pylint: disable=too-few-public-methods
class Stats:
    '''The Stats class

    This class is responsible for collecting all statistics we wish to display
    on the Pi-Hole's E-paper screen, and subsequently rendering it.
    '''
    def __init__(self):
        settings = dot_dict(
            width = Display.EPD_HEIGHT,
            height = Display.EPD_WIDTH,
            current_row = 0)

        IO.read_cfg(settings)

        log = Logger(settings.cfg)

        log.info(settings.cfg, 'Initiating screen...')
        display = Display.EPD()
        display.init()

        try:
            while settings.cfg.options.interval_minutes > 0:
                success = self.__render(display, settings, log)
                if not success:
                    log.error(settings.cfg, 'Render failure! Aborting.')
                    continue
                IO.read_cfg(settings)
        finally:
            log.info(settings.cfg, 'Sleeping display before leaving')
            display.sleep()

    @classmethod
    def __get_stats_pihole(cls, cfg, log):
        try:
            clients, ads_blocked, ads_percentage, dns_queries = IO.get_stats_pihole(cfg, log)
            if cfg.options.draw_logo:
                domains, ads = IO.get_stats_pihole_history(cfg) 
            else:
                domains, ads = (None, None)
        except KeyError:
            log.error(cfg, 'Error getting Pi-Hole stats!')
            time.sleep(1)
            return False

        log.info(cfg, '''Clients:     {0}
Ads blocked: {1} {2:.2f}%
DNS Queries: {3}'''.format(clients, ads_blocked, ads_percentage, dns_queries))

        return dot_dict(
            clients        = clients,
            ads_blocked    = ads_blocked,
            ads_percentage = ads_percentage,
            dns_queries    = dns_queries,
            domains        = domains,
            ads            = ads
        )

    @classmethod
    def __get_stats_system(cls, cfg, log):
        ip_address      = IO.shell('hostname -I | cut -d" " -f1')
        host            = IO.shell('hostname').lower() + '.local'
        mem, mem_part   = IO.shell('free -m | awk \'NR==2{printf "%s/%s MB#%.2f%%", $3,$2,$3*100/$2 }\'').split('#', 1)
        disk, disk_part = IO.shell('df -h | awk \'$NF=="/"{printf "%d/%d GB#%s", $3,$2,$5}\'').split('#', 1)

        log.info(cfg, '''IP:           {0}
Host:         {1}
Memory usage: {2} {3}
Disk:         {4} {5}'''.format(ip_address, host, mem, mem_part, disk, disk_part))

        return dot_dict(
            ip_address = ip_address,
            host       = host,
            mem        = mem,
            mem_part   = mem_part,
            disk       = disk,
            disk_part  = disk_part
        )

    @classmethod
    def __render(cls, display, settings, log):
        cfg = settings.cfg
        chart = cfg.chart

        log.debug.obj(cfg, 'Configuration:', cfg.toDict(), 3)

        log.info(cfg, 'Rendering status')

        images = dot_dict(
            black = Renderer.new_image(),
            red   = Renderer.new_image()
        )
        draw = dot_dict(
            black = ImageDraw.Draw(images.black),
            red   = ImageDraw.Draw(images.red)
        )
        text = dot_dict(
            black = Text(settings, draw.black),
            red   = Text(settings, draw.red)
        )

        draw.black.rectangle((0, 0, settings.width, settings.height), outline = 0, fill = None)

        system = cls.__get_stats_system(cfg, log)
        pihole = cls.__get_stats_pihole(cfg, log)

        if cfg.options.draw_logo:
            Renderer.draw_logo(cfg, log, images)
        else:
            Renderer.draw_charts(cfg, log, draw, pihole.domains, pihole.ads)

        ads_blocked_label = random.choice(cfg.labels_ads)
        percentage_format = '{0:.1f}%' if pihole.ads_blocked > 9999 else '{0:.2f}%'

        settings.current_row = 0

        text.black.row(chart.x_stat, 'HOST:', system.host)
        text.black.row(chart.x_stat, 'IP:',   system.ip_address)
        text.black.row(chart.x_stat, 'Mem:',  system.mem)
        text.black.row(chart.x_stat, 'Disk:', system.disk)

        text.red.line(2, 31, system.mem_part, align = 'right')
        text.red.line(2, 46, system.disk_part, align = 'right')

        text.black.row(chart.x_result, 'Clients:', pihole.clients)
        text.black.row(chart.x_result, ads_blocked_label + ':', pihole.ads_blocked)
        text.black.row(chart.x_result, 'DNS Queries:', pihole.dns_queries)

        text.red.line(2, 76, percentage_format.format(pihole.ads_percentage), align = 'right')

        text.red.line(7,  settings.height - 24, 'Pi', size = 11)
        text.red.line(20, settings.height - 24, '-hole', True)

        text.black.line(13, settings.height - 14, u'↻:')
        text.black.line(23, settings.height - 12, time.strftime('%H:%M', time.localtime()), size = 8)

        rotation = Image.ROTATE_270 if cfg.options.draw_inverted else Image.ROTATE_90
        Renderer.frame(display, images.black.transpose(rotation), images.red.transpose(rotation))

        now = time.strftime('%H:%M:%S', time.localtime())
        log.info(cfg, 'Rendering completed\nSleeping for {0} min at {1}'.format(cfg.options.interval_minutes, now))
        display.sleep()
        display.delay_ms(cfg.options.interval_minutes * 60 * 1000)

        # Awakening the display
        display.init()

        # Rendering was successful.
        return True

if __name__ == '__main__':
    Stats()
