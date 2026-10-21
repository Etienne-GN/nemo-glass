def _rgba(hex_color, alpha):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "rgba(%d, %d, %d, %.2f)" % (r, g, b, alpha)


def _white(alpha):
    return "rgba(255, 255, 255, %.2f)" % min(alpha, 1.0)


def _rule(selectors, body):
    return "%s {\n%s}\n" % (",\n".join(selectors), "".join("\t%s;\n" % d for d in body))


_CLEAR = ["background-color: transparent", "background-image: none"]

_SURFACES = [
    ".nemo-window scrolledwindow",
    ".nemo-window viewport",
    ".nemo-window .nemo-window-pane",
    ".nemo-window notebook",
    ".nemo-window notebook > header",
    ".nemo-window notebook > stack",
    ".nemo-window .view",
    ".nemo-window iconview",
    ".nemo-window treeview",
]

_SIDEBAR = [
    ".nemo-window .sidebar",
    ".nemo-window .nemo-places-sidebar",
    ".nemo-window .nemo-places-sidebar treeview",
]

_BARS = [
    ".nemo-window menubar",
    ".nemo-window toolbar",
    ".nemo-window .primary-toolbar",
    ".nemo-window statusbar",
    ".nemo-window .nemo-window-pane > box",
    ".nemo-window actionbar",
    ".nemo-window actionbar > revealer > box",
]

# The CSD titlebar is a sibling of the window contents, not drawn on top of
# the window background, so it needs its own background.
_TITLEBAR = [
    ".nemo-window .titlebar",
    ".nemo-window .titlebar:backdrop",
    ".nemo-window headerbar",
    ".nemo-window headerbar:backdrop",
]

_BUTTONS = [
    ".nemo-window toolbar button",
    ".nemo-window .primary-toolbar button",
    ".nemo-window .path-bar button",
    ".nemo-window .linked button",
    ".nemo-window statusbar button",
    ".nemo-window .nemo-window-pane > box button",
    ".nemo-window actionbar button",
]

_COLUMN_HEADERS = [
    ".nemo-window treeview.view header",
    ".nemo-window treeview.view header button",
    ".nemo-window treeview.view header button:backdrop",
]

_LINES = [
    ".nemo-window separator",
]

_BORDERED = _SURFACES + _SIDEBAR + _BARS + [
    ".nemo-window frame > border",
    ".nemo-window .frame",
]


def _states(selectors, state):
    return ["%s:%s" % (s, state) for s in selectors]


def render(cfg):
    if not cfg["enabled"]:
        return ""

    controls = cfg["controls_opacity"]
    border = _white(cfg["border_opacity"])

    out = [_rule([".nemo-window", ".nemo-window.background"],
                 ["background-color: %s" % _rgba(cfg["tint"], cfg["opacity"])])]

    out.append(_rule(_SURFACES, _CLEAR))

    if cfg["sidebar_shade"] > 0:
        out.append(_rule(_SIDEBAR, [
            "background-color: rgba(0, 0, 0, %.2f)" % cfg["sidebar_shade"],
            "background-image: none",
        ]))
    else:
        out.append(_rule(_SIDEBAR, _CLEAR))

    out.append(_rule(_SIDEBAR, ["border-left-width: 0", "border-right-width: 0"]))

    if cfg["transparent_bars"]:
        out.append(_rule(_BARS, _CLEAR))

    titlebar_alpha = cfg["opacity"] if cfg["titlebar_follow"] else cfg["titlebar_opacity"]
    out.append(_rule(_TITLEBAR, [
        "background-color: %s" % _rgba(cfg["tint"], titlebar_alpha),
        "background-image: none",
        "box-shadow: none",
        "border-color: %s" % border,
    ]))

    out.append(_rule(_BORDERED, ["border-color: %s" % border]))
    out.append(_rule(_LINES, [
        "background-color: %s" % border,
        "background-image: none",
    ]))

    out.append(_rule([".nemo-window paned > separator"], [
        "background-color: %s" % border,
        "background-image: none",
        "border: none",
        "box-shadow: none",
        "min-width: 1px",
        "min-height: 1px",
        "margin: 0",
        "padding: 0",
    ]))

    out.append(_rule(_COLUMN_HEADERS, [
        "background-color: transparent",
        "background-image: none",
        "box-shadow: none",
        "text-shadow: none",
        "border-style: none solid solid none",
        "border-width: 0 1px 1px 0",
        "border-color: %s" % border,
    ]))
    out.append(_rule([".nemo-window treeview.view header button:last-child"], [
        "border-right-width: 0",
    ]))
    out.append(_rule([".nemo-window treeview.view header button:hover"], [
        "background-color: %s" % _white(controls + 0.04),
    ]))

    out.append(_rule(_BUTTONS, [
        "background-color: %s" % _white(controls),
        "background-image: none",
        "border-color: %s" % border,
        "box-shadow: none",
        "text-shadow: none",
        "-gtk-icon-shadow: none",
    ]))
    out.append(_rule(_states(_BUTTONS, "hover"), [
        "background-color: %s" % _white(controls + 0.08),
    ]))
    out.append(_rule(_states(_BUTTONS, "active") + _states(_BUTTONS, "checked"), [
        "background-color: %s" % _white(controls + 0.16),
    ]))
    out.append(_rule(_states(_BUTTONS, "backdrop"), [
        "background-color: %s" % _white(controls),
        "border-color: %s" % border,
    ]))

    out.append(_rule([".nemo-window entry"], [
        "background-color: rgba(0, 0, 0, %.2f)" % min(controls + 0.15, 1.0),
        "background-image: none",
        "border-color: %s" % _white(cfg["border_opacity"] + 0.06),
        "box-shadow: none",
    ]))

    out.append(_rule([".nemo-window scrollbar", ".nemo-window scrollbar trough"], [
        "background-color: transparent",
        "background-image: none",
        "border-color: transparent",
    ]))
    out.append(_rule([".nemo-window scrollbar slider"], [
        "background-color: %s" % _white(cfg["scrollbar_opacity"]),
    ]))
    out.append(_rule([".nemo-window scrollbar slider:hover"], [
        "background-color: %s" % _white(cfg["scrollbar_opacity"] + 0.15),
    ]))
    out.append(_rule([".nemo-window scrollbar slider:active"], [
        "background-color: %s" % _white(cfg["scrollbar_opacity"] + 0.30),
    ]))

    out.append(_rule([".nemo-window scale trough"], [
        "background-color: %s" % _white(controls + 0.10),
        "background-image: none",
        "border-color: %s" % border,
    ]))

    if cfg["inactive_pane_dim"] > 0:
        out.append(_rule(
            [".nemo-window .nemo-inactive-pane .view",
             ".nemo-window .nemo-inactive-pane iconview"],
            ["background-color: rgba(0, 0, 0, %.2f)" % cfg["inactive_pane_dim"]],
        ))

    if cfg["selection_mode"] == "custom":
        out.append(_rule(
            [".nemo-window .view:selected",
             ".nemo-window iconview:selected",
             ".nemo-window treeview:selected"],
            ["background-color: %s" % _rgba(cfg["selection_color"],
                                            cfg["selection_opacity"])],
        ))

    if cfg["text_shadow"]:
        out.append(_rule(
            [".nemo-window .view", ".nemo-window iconview", ".nemo-window treeview",
             ".nemo-window .sidebar", ".nemo-window label"],
            ["text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8)"],
        ))

    floating = ".nemo-window:not(.maximized):not(.tiled):not(.fullscreen)"

    if cfg["corner_radius"] >= 0:
        r = cfg["corner_radius"]
        out.append(_rule(["%s decoration" % floating], [
            "border-top-left-radius: %dpx" % r,
            "border-top-right-radius: %dpx" % r,
        ]))
        out.append(_rule(
            ["%s .titlebar" % floating, "%s headerbar" % floating],
            ["border-radius: %dpx %dpx 0 0" % (r, r)],
        ))

    if cfg["bottom_rounded"] and cfg["bottom_radius"] > 0:
        # The extension clips window contents to match; CSS alone does not
        # clip children in GTK 3.
        r = cfg["bottom_radius"]
        out.append(_rule([floating, "%s decoration" % floating], [
            "border-bottom-left-radius: %dpx" % r,
            "border-bottom-right-radius: %dpx" % r,
        ]))

    return "\n".join(out)
