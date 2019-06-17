#!/usr/bin/env bash

# Host that isn't on a UPS. If the power is out, it will be unreachable
CHECK_HOST=""

# Ping this host that IS on a UPS to make sure we don't have an issue network gear
NETWORK_VERIFICATION_HOST=""

LOG_FILE="/export/home/nz/pf_watchdog/log"

init_shutdown_procedure() {
    echo "Initiaiting shutdown procedure due to power loss" >> ${LOG_FILE}
    # Stop netezza server
    nzstop
    echo "Stopped Netezza server" >> ${LOG_FILE}
    # Stop clustering
    ssh ha2 "service heartbeat stop"
    echo "Stopped clustering processes" >> ${LOG_FILE}
    echo "Starting shutdown on NZ02" >> ${LOG_FILE}
    ssh ha2 "shutdown -h now"
    echo "Starting shutdown on NZ01" >> ${LOG_FILE}
    shutdown -h now 
}

check_verify_host() {
    ping -c 3 ${NETWORK_VERIFICATION_HOST} || init_shutdown_procedure
}

check_main_host() {
    ping -c 3 ${CHECK_HOST} || check_verify_host
}

check_main_host

