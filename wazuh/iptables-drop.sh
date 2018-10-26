#!/usr/bin/env bash
LOCK_FILE="IPTABLES_LOCK"
LOG_FILE="/var/ossec/logs/active-responses.log"
ACTION=$1
IP=$3

check_lock_file () {
    DATE="$(date)"
    if [ -f "${LOCK_FILE}" ]
    then
        echo "LOCKED"
        echo "${DATE} Locked" >> ${LOG_FILE}
        sleep 1
        check_lock_file
    else
        firewall
    fi
    }

firewall () {
    DATE="$(date)"
    touch "${LOCK_FILE}"
    echo "${DATE} $0 ${ACTION} ${2} ${IP}" >> ${LOG_FILE}
    if [ "${ACTION}" == "add" ]
    then
        sudo iptables -I INPUT -s ${IP} -j DROP
        rm "${LOCK_FILE}"
        exit 0
    else
        sudo iptables -D INPUT -s ${IP} -j DROP
        rm "${LOCK_FILE}"
        exit 0
    fi
}
check_lock_file