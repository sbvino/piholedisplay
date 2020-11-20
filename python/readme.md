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

| Setting     | Default | Function |
|-------------|---------|----------|
| `draw_inverted`    | `true`  | Set to `true` or `false` to flip the screen upside-down, depending on how you want your PI to be oriented. |
| `draw_logo`        | `false` | Set to `true` to render the "Pi-Hole" logo, or `false` to render the graph. |
| `interval_minutes` | `10`    | The time between screen refreshes. If set to `0`, the loop will terminate after the next refresh. |
| `newline`          | `"\n"`  | The newline sequence to use in debug prints / logs. |
| `log_level`        | `40`    | Determines the minimum log level for messages to be logged to file. The log levels will be listed below this table. |
| `log_dir`          | `"log"` | Which dir the logs will be written to, relative to the `stats.py` file. |

### Log levels:
The following log levels are available
```
DEBUG    - 10
INFO     - 20
WARNING  - 30
ERROR    - 40
CRITICAL - 50
```
