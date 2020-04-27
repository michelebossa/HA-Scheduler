#!/usr/bin/env bashio
set -e
bashio::log.info "Start"
mkdir -p /share/ha-scheduler
chmod -R 777 /share/ha-scheduler

nohup python3 /home/app.py &

bashio::log.info "ready hassio.stdin"
while read -r input; do
    # parse JSON value
    input=$(bashio::jq "${input}" '.')
    bashio::log.info "Read alias: $input"
	python3 /home/daemon_input.py $input
done		

 