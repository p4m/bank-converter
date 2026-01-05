#!/bin/bash
set -e

# ------------------------------------------------------------
# Installer voor BankConverter background service (macOS)
# ------------------------------------------------------------

PLIST_PATH="$HOME/Library/LaunchAgents/nl.user.bankconverter.plist"
SCRIPT_PATH="$HOME/BankConverter/convert.py"
LOG_PATH="$HOME/BankConverter/log.txt"

echo "🔧 BankConverter installer gestart..."

# 1️⃣ Controleer of convert.py bestaat
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "⚠️  Script niet gevonden op $SCRIPT_PATH"
  echo "Plaats convert.py eerst in ~/BankConverter/"
  exit 1
fi

# 2️⃣ Maak LaunchAgents-map aan
mkdir -p "$HOME/Library/LaunchAgents"

# 3️⃣ Maak plist-bestand
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>nl.user.bankconverter</string>

    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_PATH</string>
    </array>

    <key>StandardOutPath</key>
    <string>$LOG_PATH</string>
    <key>StandardErrorPath</key>
    <string>$LOG_PATH</string>
</dict>
</plist>
EOF

echo "✅ LaunchAgent bestand aangemaakt:"
echo "   $PLIST_PATH"

# 4️⃣ Zorg dat log.txt bestaat
touch "$LOG_PATH"

# 5️⃣ LaunchAgent laden
launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl load "$PLIST_PATH"

echo "🚀 BankConverter service geladen!"
echo "Het script wordt nu automatisch uitgevoerd bij elke login."
echo "Logbestand: $LOG_PATH"
echo "🔧 Installatie voltooid."