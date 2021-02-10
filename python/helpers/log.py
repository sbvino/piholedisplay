'''The logging module has several logging helper functions'''

import logging
import os
import pprint

from datetime import date

from helpers.text import Text

# pylint: disable=too-few-public-methods
class Logger():
    '''The logger helper class

    Args:
        cfg (DotMap): The configuration.

    Attributes:
        log (Function): A wrapper for the logger's `log` function.
        debug (Function): A wrapper for the logger's `debug` function.
        info (Function): A wrapper for the logger's `info` function.
        warning (Function): A wrapper for the logger's `warning` function.
        error (Function): A wrapper for the logger's `error` function.
        critical (Function): A wrapper for the logger's `critical` function.

    '''
    def __init__(self, cfg):
        log_dir = cfg.options.log_dir

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        today = date.today().isoformat()

        logging.basicConfig(
            level    = cfg.options.log_level,
            format   = '%(asctime)s [%(levelname)s]' + cfg.options.newline + '    %(message)s',
            filename = log_dir + '/' + today + '_pihole.log')

        logger = logging.getLogger()

        logging.info('Logging initialized')

        self.log      = LogWrapper(logger, logging.DEBUG)
        self.debug    = LogWrapper(logger, logging.DEBUG)
        self.info     = LogWrapper(logger, logging.INFO)
        self.warning  = LogWrapper(logger, logging.WARNING)
        self.error    = LogWrapper(logger, logging.ERROR)
        self.critical = LogWrapper(logger, logging.CRITICAL)

# pylint: disable=invalid-name
class LogWrapper():
    '''A logging helper.

    Log levels:
        DEBUG    - 10
        INFO     - 20
        WARNING  - 30
        ERROR    - 40
        CRITICAL - 50

    Args:
        log_level (int): The `log_level` this helper logs for.

    Attributes:
        log_level
    '''
    def __init__(self, logger, log_level):
        self.logger = logger
        self.log_level = log_level

    def __call__(self, cfg, *args):
        self.log(cfg, *args)

    def log(self, cfg, *args):
        '''Log the parameters.

        Args:
            cfg (DotMap): The configuration.
            *args (list): Parameters to be logged.
        '''
        opts = cfg.options

        message = opts.newline + opts.newline.join(args)
        print(message)

        # Don't log if the log level for this call is lower than the configured log level.
        if self.log_level < opts.log_level:
            return

        logfile_message = Text.replace(
            message,
            [
                ('^' + opts.newline, ''),
                (opts.newline, opts.newline + '    ')
            ])
        self.logger.log(self.log_level, logfile_message)

    def obj(self, cfg, title, obj, depth = 1):
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

        pretty_print = pprint.PrettyPrinter(indent = 2, depth = depth)

        msg = Text.replace(
            pretty_print.pformat(obj),
            [
                ('u?\'', '\''),
                ('^{', '{' + opts.newline + ' '),
                ('}$', opts.newline + '}')
            ])

        self.log(cfg, title, msg)
