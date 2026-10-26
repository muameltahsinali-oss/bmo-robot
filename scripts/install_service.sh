#!/bin/bash

SERVICE_FILE="/etc/systemd/system/bmo.service"
USER=$(whoami)
DIR=$(pwd)/..

echo "Creating Systemd Service..."

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=BMO Robot Service
After=network.target sound.target

[Service]
User=$USER
WorkingDirectory=$DIR
ExecStart=$DIR/scripts/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling Service..."
sudo systemctl daemon-reload
sudo systemctl enable bmo.service
echo "Service Installed. Start with: sudo systemctl start bmo.service"
