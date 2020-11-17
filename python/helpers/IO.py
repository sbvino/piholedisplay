'''The io module has several helper functions to read and log data'''

import json
import pprint
import subprocess

import collections as Collections

from dotmap import DotMap

import requests

from text import Text
from enums import Logging

# Public methods
def shell(command):
    '''Execute a shell command.

    Args:
        command (striong): The shell command.

    Returns:
        string: The result from the shell command.
    '''
    return str(subprocess.check_output(command, shell = True)).strip()

def get_stats_pihole(cfg):
    '''Get stats for the Pi-Hole instance.

    Args:
        cfg (DotMap): The configuration.

    Returns:
        tuple: (string, string, string, string): Clients, ads blocked, ads percentage, dns queries.
    '''
    data = __get_json(cfg.pihole.api_url)

    clients        = data['unique_clients']
    ads_blocked    = data['ads_blocked_today']
    ads_percentage = data['ads_percentage_today']
    dns_queries    = data['dns_queries_today']

    log_obj(cfg, 'API response:', data)
    return (clients, ads_blocked, ads_percentage, dns_queries)

def get_stats_pihole_history(cfg):
    '''Get stats for the Pi-Hole instance's history.

    Args:
        cfg (DotMap): The configuration.

    Returns:
        tuple: (list, list): Data for domains & ads.
    '''
    data = __get_json(cfg.pihole.api_url + '?overTimeData10mins')

    domains = Collections.dict_to_columns(cfg, data['domains_over_time'])
    ads     = Collections.dict_to_columns(cfg, data['ads_over_time'])

    return (domains, ads)

def read_cfg(module_settings):
    '''Read the configuration from file and store it in `settings`.

    Args:
        module_settings (DotMap): The global settings object the config has to be stored in.
    '''
    with open('config.json') as json_file:
        config = DotMap(json.load(json_file))
    module_settings.cfg = config

def log(cfg, *args):
    '''Log the parameters.

    Args:
        cfg (DotMap): The configuration.
        *args (list): Parameters to be logged.
    '''
    opts = cfg.options

    if opts.log_level < Logging.ENABLED.value:
        return

    print(opts.newline + opts.newline.join(args))

def log_obj(cfg, title, obj, depth = 1):
    '''Log the object with a title, pretty printed.

    Args:
        cfg (DotMap): The configuration.
        title (string): The title to log.
        obj (dict): The object to log.
        depth (type): To what depth to object should be expanded.

    Returns:
        type: Description of returned object.

    Raises:
        ExceptionName: Why the exception is raised.

    '''
    opts = cfg.options

    if opts.log_level < Logging.EXTENDED.value:
        return

    pretty_print = pprint.PrettyPrinter(indent = 2, depth = depth)

    msg = Text.replace(
        pretty_print.pformat(obj),
        [
            ('u?\'', '\''),
            ('^{', '{' + opts.newline + ' '),
            ('}$', opts.newline + '}')
        ])

    log(cfg, title, msg)

# Private methods
def __get_json(url):
    '''Get a `dict` from the specified JSON file.

    Args:
        url (string): The path to the JSON file.

    Returns:
        dict: The parsed JSON file.
    '''
    response = requests.get(url)
    return json.loads(response.text)
