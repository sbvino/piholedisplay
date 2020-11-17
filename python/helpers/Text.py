'''The text module has several helper functions manipulate strings and write text to the screen'''

import re as regex

from PIL import ImageFont

class Text:
    '''The text helper module.

    Args:
        module_settings (DotMap): The global settings object the config has to be stored in.
        draw (PIL.Image.ImageDraw): The `ImageDraw` component this chart should be drawn on.

    Attributes:
        module_settings
        draw
    '''
    def __init__(self, module_settings, draw):
        '''Initialize a new text drawing helper.

        Args:
            module_settings (DotMap): The global settings object the config has to be stored in.
            draw (PIL.Image.ImageDraw): The `ImageDraw` component this chart should be drawn on.
        '''
        self.module_settings = module_settings
        self.draw = draw

    # Public methods
    def row(self, pos_x, label, value):
        '''Render a new row of text at position `x`, for `label` with `value`.

        Args:
            pos_x (list[int, int]): The x positions of the `label` and `value`.
            label (string): The `label`.
            value (string): The `value`.
        '''
        pos_y = self.module_settings.current_row * 15
        self.line(pos_x[0], pos_y,     str(label), True)
        self.line(pos_x[1], pos_y + 1, str(value), False)
        self.module_settings.current_row += 1

    def line(self, pos_x, pos_y, message, bold = False, size = 10, align = ''):
        '''Render a line of text.

        Args:
            pos_x (int): The `x` position.
            pos_y (int): The `y` position.
            message (string): The `message`.
            bold (bool): Bold text?. Defaults to False.
            size (int): The font `size`. Defaults to 10.
            align (string): Bottom or right alignment?
        '''
        top = self.module_settings.cfg.chart.margin

        font_name = 'DejaVuSansMono-Bold' if bold else 'DejaVuSansMono'
        font_size = 11 if bold else size
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + font_name + '.ttf', font_size)

        if 'right' in align or 'bottom' in align:
            width, height = self.draw.textsize(message, font = font)
            if 'right' in align:
                pos_x = self.module_settings.width - (width + pos_x)
            if 'bottom' in align:
                pos_y = self.module_settings.height - (height + pos_y)

        self.draw.text(
            (pos_x, top + pos_y),
            message,
            font = font,
            fill = 0)

    @staticmethod
    def replace(value, replacements):
        '''Perform regex replacements on a value.

        Args:
            value (string): The `value` to perform the replacements on.
            replacements (list: tuple: (string, string)): The replacements to perform.

        Returns:
            string: The result.
        '''
        for expression, replacement in replacements:
            value = regex.sub(expression, replacement, value)
        return value
