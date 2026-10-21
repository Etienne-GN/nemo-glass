import logging
import math
import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Nemo", "3.0")
import cairo
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Nemo

LIB_DIR = os.path.join(
    os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
    "nemo-glass", "lib",
)
PREFS_BIN = os.path.expanduser("~/.local/bin/nemo-glass-prefs")

sys.path.insert(0, LIB_DIR)
from nemo_glass import config, css

log = logging.getLogger("nemo-glass")


_UNCLIPPED_STATES = (Gdk.WindowState.MAXIMIZED | Gdk.WindowState.FULLSCREEN
                     | Gdk.WindowState.TILED)


class NemoGlass(GObject.GObject, Nemo.NameAndDescProvider, Nemo.MenuProvider,
                Nemo.LocationWidgetProvider):
    def __init__(self):
        super().__init__()
        self._provider = Gtk.CssProvider()
        self._attached = False
        self._reload_pending = 0
        self._cfg = config.load()
        self._windows = {}

        self._monitor = Gio.File.new_for_path(config.CONFIG_PATH).monitor_file(
            Gio.FileMonitorFlags.WATCH_MOVES, None)
        self._monitor.connect("changed", self._on_config_changed)

        GLib.idle_add(self._attach)

    def _attach(self):
        screen = Gdk.Screen.get_default()
        if screen is None:
            log.error("no default screen, styles not applied")
            return GLib.SOURCE_REMOVE
        Gtk.StyleContext.add_provider_for_screen(
            screen, self._provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self._attached = True
        self._apply()
        return GLib.SOURCE_REMOVE

    def _apply(self):
        text = css.render(self._cfg)
        try:
            self._provider.load_from_data(text.encode())
        except GLib.Error as exc:
            log.error("generated CSS rejected by GTK, keeping previous style: %s",
                      exc.message)

    def _on_config_changed(self, _monitor, _file, _other, _event):
        if self._reload_pending:
            GLib.source_remove(self._reload_pending)
        self._reload_pending = GLib.timeout_add(100, self._reload)

    def _reload(self):
        self._reload_pending = 0
        self._cfg = config.load()
        if self._attached:
            self._apply()
        for window in self._windows:
            window.queue_draw()
        return GLib.SOURCE_REMOVE

    def get_widget(self, _uri, window):
        if window is not None and window not in self._windows:
            self._windows[window] = (
                window.connect("draw", self._on_window_draw),
                window.connect("window-state-event", lambda w, _e: w.queue_draw()),
            )
            window.connect("destroy", self._forget_window)
            window.queue_draw()
        return None

    def _forget_window(self, window):
        self._windows.pop(window, None)

    def _on_window_draw(self, window, cr):
        # CSS border-radius does not clip children in GTK 3, so the panes would
        # paint square over the rounded bottom corners; clip those wedges out.
        r = self._cfg["bottom_radius"]
        if not self._cfg["enabled"] or not self._cfg["bottom_rounded"] or r <= 0:
            return False
        gdk_window = window.get_window()
        if gdk_window is not None and gdk_window.get_state() & _UNCLIPPED_STATES:
            return False
        child = window.get_child()
        if child is None:
            return False
        a = child.get_allocation()
        right, bottom = a.x + a.width, a.y + a.height
        cr.rectangle(0, 0, window.get_allocated_width(), window.get_allocated_height())
        cr.move_to(right, bottom)
        cr.line_to(right - r, bottom)
        cr.arc_negative(right - r, bottom - r, r, math.pi / 2, 0)
        cr.close_path()
        cr.move_to(a.x, bottom)
        cr.line_to(a.x, bottom - r)
        cr.arc_negative(a.x + r, bottom - r, r, math.pi, math.pi / 2)
        cr.close_path()
        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.clip()
        cr.set_fill_rule(cairo.FILL_RULE_WINDING)
        return False

    def get_name_and_desc(self):
        return ["Nemo Glass:::Translucent dark styling for Nemo windows:::%s"
                % PREFS_BIN]

    def get_background_items(self, *args):
        if not self._cfg["context_menu"]:
            return []
        item = Nemo.MenuItem(
            name="NemoGlass::settings",
            label="Nemo Glass Settings…",
            tip="Adjust Nemo transparency and colors",
            icon="preferences-desktop-theme-symbolic",
        )
        item.connect("activate", self._open_prefs)
        return [item]

    def _open_prefs(self, _item):
        try:
            GLib.spawn_async([PREFS_BIN])
        except GLib.Error as exc:
            log.error("cannot start %s: %s", PREFS_BIN, exc.message)
