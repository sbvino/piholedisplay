import re as regex

from PIL import ImageFont

# Public methods
def row(global_settings, draw, x, label, value):
    y = global_settings.current_row * 15
    line(global_settings, draw, x[0], y,     str(label), True)
    line(global_settings, draw, x[1], y + 1, str(value), False)
    global_settings.current_row += 1

def line(global_settings, draw, x, y, string, bold = False, size = 10, align = ''):
    top = global_settings.cfg.chart.margin

    font_name = ('DejaVuSansMono', 'DejaVuSansMono-Bold')[bold]
    font_size = (size, 11)[bold]
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + font_name + '.ttf', font_size)

    if 'right' in align or 'bottom' in align:
        w, h = draw.textsize(string, font = font)
        if 'right' in align:
            x = global_settings.width - (w + x)
        if 'bottom' in align:
            y = global_settings.height - (h + y)

    draw.text(
        (x, top + y),
        string,
        font = font,
        fill = 0)

def replace(str, replacements):
    for old, new in replacements:
        str = regex.sub(old, new, str)
    return str
