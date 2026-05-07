#!/bin/bash

# Start aria2, qBittorrent, SABnzbd as background daemons
bash aria-nox-nzb.sh

# Wait for services to be ready
sleep 5

# Activate venv and start the bot
source mltbenv/bin/activate
python3 update.py
python3 -m bot
