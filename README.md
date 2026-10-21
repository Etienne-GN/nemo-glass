# Nemo Glass

Translucent dark styling for the Nemo file manager, packaged as a nemo-python
extension with a live settings window. Only Nemo windows are affected; the GTK
theme of other applications is left alone.

## Requirements

- Nemo 6.x
- `nemo-python` (`sudo apt install nemo-python`)
- `python3-yaml`, `python3-gi` (GTK 3)

## Install

```
./install.sh
nemo -q
```

Files are installed per user:

- `~/.local/share/nemo-python/extensions/nemo_glass_ext.py`: the extension
- `~/.local/share/nemo-glass/lib/nemo_glass/`: shared config and CSS code
- `~/.local/bin/nemo-glass-prefs`: settings window
- `~/.local/share/applications/nemo-glass-prefs.desktop`: launcher

## Settings

Open them from any of:

- Nemo > Edit > Plugins > Nemo Glass > Configure
- Right-click on a folder background > Nemo Glass Settings
- The "Nemo Glass Settings" application launcher

Changes are written to `~/.config/nemo-glass/config.yaml` and applied to open
Nemo windows immediately; no restart needed.

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `true` | Master switch |
| `opacity` | `0.85` | Window background opacity (0.30–1.0) |
| `tint` | `#1b1b1b` | Window background color |
| `titlebar_follow` | `true` | Title bar uses the window opacity |
| `titlebar_opacity` | `0.85` | Title bar opacity when not following |
| `sidebar_shade` | `0.0` | Extra darkening behind the sidebar (0–0.5) |
| `transparent_bars` | `true` | Toolbar, menu bar and status bar see-through |
| `controls_opacity` | `0.06` | White highlight on buttons, path bar, entries (0–0.4) |
| `border_opacity` | `0.08` | Borders and separator lines (0–0.4) |
| `scrollbar_opacity` | `0.30` | Scrollbar slider (0.05–1.0) |
| `inactive_pane_dim` | `0.15` | Darkening of the inactive pane in split view |
| `selection_mode` | `theme` | `theme` accent or `custom` color |
| `selection_color` | `#3584e4` | Custom selection color |
| `selection_opacity` | `0.55` | Custom selection opacity |
| `text_shadow` | `false` | Shadow under text for busy wallpapers |
| `corner_radius` | `8` | Top corner radius in px, `-1` keeps the theme's |
| `bottom_rounded` | `true` | Round the bottom corners |
| `bottom_radius` | `8` | Bottom corner radius in px (0–24) |
| `context_menu` | `true` | Show the settings entry in the right-click menu |

Presets (Subtle, Smoked, Glass, Clear) set opacity, shading and text shadow,
and round all corners to 8 px.

## Limitations

- No blur: GTK 3 cannot blur what is behind a window. A compositor extension
  such as Blur My Shell is needed for that.
- Rounded bottom corners are turned off while the window is maximized,
  tiled or fullscreen.
- Disabling the extension in Edit > Plugins takes effect after restarting Nemo.

## Uninstall

```
./uninstall.sh           # keep settings
./uninstall.sh --purge   # remove settings too
nemo -q
```

## Tests

```
python3 -m pytest tests
```
