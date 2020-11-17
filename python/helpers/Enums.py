'''Enums'''

from enum import Enum, unique

# pylint: disable=invalid-name
@unique
class Logging(Enum):
    '''Logging levels.

    Attributes:
        DISABLED (int): Logging is disabled.
        ENABLED (int): Only basic logging is shown.
        EXTENDED (int): All logging is shown.
    '''
    DISABLED = 0
    ENABLED = 1
    EXTENDED = 2
