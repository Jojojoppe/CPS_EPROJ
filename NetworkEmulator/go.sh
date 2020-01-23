#!/bin/bash
bash
echo "hahaha"
mate-terminal -x bash -c 'python3 netemuserver.py config.ini; exec bash'
mate-terminal -x bash -c 'python3 simulator.py; exec bash'
mate-terminal -x bash -c 'python3 simulator.py; exec bash'