import json
import pprint
import requests
import subprocess

from dotmap import DotMap

from . import Collections, Text
from .Enums import Logging

# Public methods
def shell(command):
    return str(subprocess.check_output(command, shell = True)).strip()

def get_stats_pihole(cfg):
    data = __get_json(cfg.pihole.api_url)

    clients        = data['unique_clients']
    ads_blocked    = data['ads_blocked_today']
    ads_percentage = data['ads_percentage_today']
    dns_queries    = data['dns_queries_today']

    log_obj(cfg, 'API response:', data)
    return (clients, ads_blocked, ads_percentage, dns_queries)

def get_stats_pihole_history(cfg):
    data = __get_json(cfg.pihole.api_url + '?overTimeData10mins')

    domains = Collections.dict_to_columns(cfg, data['domains_over_time'])
    ads     = Collections.dict_to_columns(cfg, data['ads_over_time'])

    return (domains, ads)

def read_cfg(global_settings):
    with open('config.json') as json_file:
        config = DotMap(json.load(json_file))
    global_settings.cfg = config

def log(cfg, *args):
    o = cfg.options

    if o.log_level < Logging.Enabled:
        return

    print(o.newline + o.newline.join(args))

def log_obj(cfg, title, obj, depth = 1):
    o = cfg.options

    if o.log_level < Logging.Extended:
        return

    pretty_print = pprint.PrettyPrinter(indent = 2, depth = depth)

    str = Text.replace(
        pretty_print.pformat(obj),
        [
            ('u?\'', '\''),
            ('^{', '{' + o.newline + ' '),
            ('}$', o.newline + '}')
        ])

    log(cfg, title, str)

# Private methods
def __get_json(url):
    r = requests.get(url)
    return json.loads(r.text)
