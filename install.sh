#!/usr/bin/env bash
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data="${XDG_DATA_HOME:-$HOME/.local/share}"

if ! dpkg-query -W -f='${Status}' nemo-python 2>/dev/null | grep -q 'install ok installed'; then
    echo "nemo-python is not installed: sudo apt install nemo-python" >&2
    exit 1
fi

install -d "$data/nemo-glass/lib/nemo_glass"
install -m 644 "$src"/nemo_glass/*.py "$data/nemo-glass/lib/nemo_glass/"
install -Dm 644 "$src/extension/nemo_glass_ext.py" "$data/nemo-python/extensions/nemo_glass_ext.py"
install -Dm 755 "$src/bin/nemo-glass-prefs" "$HOME/.local/bin/nemo-glass-prefs"
install -Dm 644 /dev/stdin "$data/applications/nemo-glass-prefs.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Nemo Glass Settings
Comment=Adjust Nemo transparency and colors
Exec=$HOME/.local/bin/nemo-glass-prefs
Icon=preferences-desktop-theme
Categories=Settings;DesktopSettings;GTK;
EOF

cat <<EOF
Installed. Restart Nemo to load the extension:
    nemo -q
Settings: Nemo > Edit > Plugins > Nemo Glass > Configure,
or right-click a folder background > Nemo Glass Settings.
EOF
