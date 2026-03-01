#!/bin/bash
pkill -f 'python.*api.py'
sleep 2
cd /root/Roomie-Claude
nohup python3 api.py > api.log 2>&1 &
echo "started"
