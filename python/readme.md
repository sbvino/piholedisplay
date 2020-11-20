# Configuration

The `config.json` file is where all the settings for the stats module are stored.
In it's default form, it looks like this:

```json
{
    "options": {
        "draw_inverted": true,
        "draw_logo": false,
        "interval_minutes": 10,
        "newline": "\n",
        "log_level": 40,
        "log_dir": "log"
    },
    "pihole" : {
        "api_url": "http://localhost/admin/api.php"
    },
    "chart": {
        "margin": 2,
        "col_count": 20,
        "height": 80.0,
        "x_stat":   [62, 102],
        "x_result": [62, 148]
    },
    "labels_ads": [
        "Ads Blocked",
        "<...>"
    ]
}
```

## `"options"`
This section contains options that apply to how the stats module behaves.

|       Setting       | Default | Function |
|---------------------|---------|----------|
| `draw_inverted`     | `true`  | Set to `true` or `false` to flip the screen upside-down, depending on how you want your PI to be oriented. |
| `draw_logo`         | `false` | Set to `true` to render the "Pi-Hole" logo, or `false` to render the graph. |
| `interval_minutes`  | `10`    | The time between screen refreshes. If set to `0`, the loop will terminate after the next refresh. |
| `newline`           | `"\n"`  | The newline sequence to use in debug prints / logs. |
| `log_level`         | `40`    | Determines the minimum log level for messages to be logged to file. The log levels will be listed at the [bottom of this page](#log-levels). |
| `log_dir`           | `"log"` | Which dir the logs will be written to, relative to the `stats.py` file. |

## `"options"`
This section contains options concerning the Pi-Hole instance.

|  Setting  |               Default               | Function |
|-----------|-------------------------------------|----------|
| `api_url` | `"http://localhost/admin/api.php"`  | The URL the Pi-Hole's API can be accessed at. You normaly shouldn't need to change this. |

## `"chart"`
This section contains options concerning the Pi-Hole instance.

|   Setting   |   Default   | Function |
|-------------|-------------|----------|
| `margin`    | `2`         | The top margin when rendering screen contents. |
| `col_count` | `20`        | How many chart columns are rendered. |
| `height`    | `80.0`      | The chart height. Should be a float. |
| `x_stat`    | `[62, 102]` | The x-coordinates for the first 4 text rows (system info): `[label, value]` |
| `x_result`  | `[62, 148]` | The x-coordinates fot the last 3 text rows (Pi-Hole stats): `[label, value]` |

## `"options"`
This section contains options concerning the Pi-Hole instance.

|    Setting    |        Default        | Function |
|---------------|-----------------------|----------|
| `labels_ads`  | `["some", "strings"]` | A bunch of different labes for the "Ads blocked" stat, of which one will be selected randomly each refresh. Values can be at most 11 characters long. |

### Log levels:
The following log levels are available
```
DEBUG    - 10
INFO     - 20
WARNING  - 30
ERROR    - 40
CRITICAL - 50
```
