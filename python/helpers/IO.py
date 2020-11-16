import json
import pprint
import requests
import subprocess

from dotmap import DotMap

import Text

def shell(command):
    return subprocess.check_output(command, shell = True).strip()

def get_json(url):
    r = requests.get(url)
    return json.loads(r.text)

def log(global_settings, *args):
    newline = global_settings.cfg.screen.newline
    print newline + newline.join(args)
            
def read_cfg(global_settings):
    with open('config.json') as json_file:
        config = DotMap(json.load(json_file))
    global_settings.cfg = config

def log_obj(global_settings, title, obj, depth = 1):
    newline = global_settings.cfg.screen.newline
    pp = pprint.PrettyPrinter(indent = 2, depth = depth)
    
    str = Text.replace(
        pp.pformat(obj),
        [
            ('u?\'', '\''),
            ('^{', '{' + newline + ' '),
            ('}$', newline + '}')
        ])
        
    log(global_settings, title, str)