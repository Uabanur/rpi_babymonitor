#! /bin/bash
cp ./services/babymonitor.service /etc/systemd/system/babymonitor.service
sudo systemctl daemon-reload
./restart_service.sh
