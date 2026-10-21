import logging
import os
import re

import yaml

log = logging.getLogger(__name__)

CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
    "nemo-glass",
)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")

DEFAULTS = {
    "enabled": True,
    "opacity": 0.85,
    "tint": "#1b1b1b",
    "titlebar_follow": True,
    "titlebar_opacity": 0.85,
    "sidebar_shade": 0.0,
    "transparent_bars": True,
    "controls_opacity": 0.06,
    "border_opacity": 0.08,
    "scrollbar_opacity": 0.30,
    "inactive_pane_dim": 0.15,
    "selection_mode": "theme",
    "selection_color": "#3584e4",
    "selection_opacity": 0.55,
    "text_shadow": False,
    "corner_radius": 8,
    "bottom_rounded": True,
    "bottom_radius": 8,
    "context_menu": True,
}

_ROUNDED = {"corner_radius": 8, "bottom_rounded": True, "bottom_radius": 8}

PRESETS = {
    "Subtle": {"opacity": 0.93, "sidebar_shade": 0.0, "inactive_pane_dim": 0.10,
               **_ROUNDED},
    "Smoked": {"opacity": 0.85, "sidebar_shade": 0.0, "inactive_pane_dim": 0.15,
               **_ROUNDED},
    "Glass": {"opacity": 0.70, "sidebar_shade": 0.10, "inactive_pane_dim": 0.15,
              **_ROUNDED},
    "Clear": {"opacity": 0.50, "sidebar_shade": 0.20, "inactive_pane_dim": 0.20,
              "text_shadow": True, **_ROUNDED},
}

_RANGES = {
    "opacity": (0.30, 1.0),
    "titlebar_opacity": (0.0, 1.0),
    "sidebar_shade": (0.0, 0.5),
    "inactive_pane_dim": (0.0, 0.5),
    "selection_opacity": (0.1, 1.0),
    "controls_opacity": (0.0, 0.4),
    "border_opacity": (0.0, 0.4),
    "scrollbar_opacity": (0.05, 1.0),
    "corner_radius": (-1, 24),
    "bottom_radius": (0, 24),
}
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def normalize(raw):
    cfg = dict(DEFAULTS)
    if not isinstance(raw, dict):
        return cfg
    for key, default in DEFAULTS.items():
        if key not in raw:
            continue
        value = raw[key]
        if isinstance(default, bool):
            if isinstance(value, bool):
                cfg[key] = value
            else:
                log.warning("ignoring %s=%r: expected true/false", key, value)
        elif isinstance(default, (int, float)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                log.warning("ignoring %s=%r: expected a number", key, value)
                continue
            low, high = _RANGES[key]
            cfg[key] = type(default)(min(max(value, low), high))
        elif key == "selection_mode":
            if value in ("theme", "custom"):
                cfg[key] = value
            else:
                log.warning("ignoring %s=%r: expected theme or custom", key, value)
        elif isinstance(value, str) and _HEX.match(value):
            cfg[key] = value.lower()
        else:
            log.warning("ignoring %s=%r: expected #rrggbb", key, value)
    return cfg


def load(path=CONFIG_PATH):
    try:
        with open(path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except FileNotFoundError:
        return dict(DEFAULTS)
    except (OSError, yaml.YAMLError) as exc:
        log.error("cannot read %s, using defaults: %s", path, exc)
        return dict(DEFAULTS)
    return normalize(raw)


def save(cfg, path=CONFIG_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        yaml.safe_dump(normalize(cfg), fh, sort_keys=False)
    os.replace(tmp, path)
