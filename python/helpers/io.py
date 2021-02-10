'''The io module has several helper functions to read and log data'''

import json
import requests
import subprocess

from dotmap import DotMap

import helpers.collections as Collections

# Public methods
def shell(command):
    '''Execute a shell command.

    Args:
        command (striong): The shell command.

    Returns:
        string: The result from the shell command.
    '''
    return str(subprocess.check_output(command, shell = True)).strip()

def get_stats_pihole(cfg, log):
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

    log.debug.obj(cfg, 'API response:', data)
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
