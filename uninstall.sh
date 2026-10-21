#!/usr/bin/env bash
set -euo pipefail

data="${XDG_DATA_HOME:-$HOME/.local/share}"
config="${XDG_CONFIG_HOME:-$HOME/.config}/nemo-glass"

rm -fv "$data/nemo-python/extensions/nemo_glass_ext.py" \
       "$HOME/.local/bin/nemo-glass-prefs" \
       "$data/applications/nemo-glass-prefs.desktop"
rm -rfv "$data/nemo-glass"

if [[ "${1:-}" == "--purge" ]]; then
    rm -rfv "$config"
else
    echo "Kept settings in $config (use --purge to remove)"
fi
echo "Restart Nemo to unload the extension: nemo -q"
