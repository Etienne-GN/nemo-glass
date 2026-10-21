import itertools

import gi
import pytest

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from nemo_glass import config, css


def parse(text):
    provider = Gtk.CssProvider()
    provider.load_from_data(text.encode())


def test_defaults_render_valid_css():
    text = css.render(dict(config.DEFAULTS))
    parse(text)
    assert "rgba(27, 27, 27, 0.85)" in text


def test_disabled_renders_nothing():
    assert css.render(dict(config.DEFAULTS, enabled=False)) == ""


@pytest.mark.parametrize("name", list(config.PRESETS))
def test_presets_render_valid_css(name):
    parse(css.render(config.normalize(config.PRESETS[name])))


def test_all_toggle_combinations_render_valid_css():
    toggles = ["titlebar_follow", "transparent_bars", "text_shadow"]
    for values in itertools.product([True, False], repeat=len(toggles)):
        cfg = dict(config.DEFAULTS, **dict(zip(toggles, values)),
                   selection_mode="custom", corner_radius=8, sidebar_shade=0.2)
        parse(css.render(cfg))


def test_broken_css_is_rejected_by_gtk():
    with pytest.raises(GLib.Error):
        parse(".nemo-window { background-color: nonsense(; }")


def test_normalize_clamps_and_rejects_bad_values():
    cfg = config.normalize({
        "opacity": 5,
        "tint": "red",
        "enabled": "yes",
        "selection_mode": "rainbow",
        "corner_radius": -9,
        "unknown": 1,
    })
    assert cfg["opacity"] == 1.0
    assert cfg["tint"] == config.DEFAULTS["tint"]
    assert cfg["enabled"] is True
    assert cfg["selection_mode"] == "theme"
    assert cfg["corner_radius"] == -1
    assert "unknown" not in cfg


def test_normalize_handles_non_dict():
    assert config.normalize(None) == config.DEFAULTS
    assert config.normalize(["x"]) == config.DEFAULTS


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "nemo-glass" / "config.yaml")
    cfg = dict(config.DEFAULTS, opacity=0.6, tint="#ABCDEF")
    config.save(cfg, path)
    loaded = config.load(path)
    assert loaded["opacity"] == 0.6
    assert loaded["tint"] == "#abcdef"


def test_load_missing_and_corrupt(tmp_path):
    assert config.load(str(tmp_path / "missing.yaml")) == config.DEFAULTS
    bad = tmp_path / "bad.yaml"
    bad.write_text("opacity: [unclosed")
    assert config.load(str(bad)) == config.DEFAULTS


def _titlebar_rule(text):
    return next(r for r in text.split("}\n") if ".titlebar" in r and "box-shadow" in r)


def test_titlebar_follows_window_opacity():
    cfg = dict(config.DEFAULTS, opacity=0.6)
    assert "rgba(27, 27, 27, 0.60)" in _titlebar_rule(css.render(cfg))


def test_titlebar_separate_opacity():
    cfg = dict(config.DEFAULTS, titlebar_follow=False, opacity=0.5,
               titlebar_opacity=0.75)
    text = css.render(cfg)
    assert "rgba(27, 27, 27, 0.75)" in _titlebar_rule(text)
    parse(text)


def test_controls_and_borders_follow_settings():
    cfg = dict(config.DEFAULTS, controls_opacity=0.1, border_opacity=0.2,
               scrollbar_opacity=0.4)
    text = css.render(cfg)
    assert "rgba(255, 255, 255, 0.10)" in text
    assert "rgba(255, 255, 255, 0.20)" in text
    assert "rgba(255, 255, 255, 0.40)" in text
    parse(text)


def test_extreme_values_stay_valid():
    cfg = config.normalize(dict(config.DEFAULTS, controls_opacity=0.4,
                                border_opacity=0.4, scrollbar_opacity=1.0))
    text = css.render(cfg)
    assert "1.16" not in text and "1.30" not in text
    parse(text)


def test_bottom_radius_css():
    text = css.render(dict(config.DEFAULTS, bottom_radius=10))
    assert "border-bottom-left-radius: 10px" in text
    parse(text)
    assert "border-bottom-left-radius" not in css.render(dict(config.DEFAULTS, bottom_radius=0))


def test_bottom_rounded_toggle_disables_bottom_css():
    text = css.render(dict(config.DEFAULTS, bottom_rounded=False, bottom_radius=10))
    assert "border-bottom-left-radius" not in text
    parse(text)


@pytest.mark.parametrize("name", list(config.PRESETS))
def test_presets_round_all_corners_to_8px(name):
    text = css.render(config.normalize(config.PRESETS[name]))
    assert "border-top-left-radius: 8px" in text
    assert "border-bottom-left-radius: 8px" in text


def test_defaults_match_smoked_preset():
    assert config.normalize(config.PRESETS["Smoked"]) == config.DEFAULTS
