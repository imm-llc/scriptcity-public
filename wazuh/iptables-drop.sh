#!/usr/bin/env bash
LOG_FILE="/var/ossec/logs/active-responses.log"
ACTION=$1
IP=$3

firewall () {
    DATE="$(date)"
    echo "${DATE} $0 ${ACTION} ${2} ${IP}" >> ${LOG_FILE}
    if [ "${ACTION}" == "add" ]
    then
        sudo iptables -I INPUT -s ${IP} -j DROP
        exit 0
    else
        sudo iptables -D INPUT -s ${IP} -j DROP
        exit 0
    fi
}
check_lock_file