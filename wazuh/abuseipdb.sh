#!/usr/bin/env bash
# Enter API Key from AbuseIPDB
PWD=$(pwd)
API_KEY="Abuse IPDB API Key"
REPORT_URL="https://www.abuseipdb.com/report/json?"
# If you want to change the message, you have to encode it
COMMENT="Automatic%20report%20generated%20by%20Wazuh"
IP="$3"
CATEGORY="21"
FULL_URL="${REPORT_URL}key=${API_KEY}&category=${CATEGORY}&comment=${COMMENT}&ip=${IP}"
LOG_FILE="${PWD}/../../logs/active-responses.log"
curl "${FULL_URL}" | tee -a "${LOG_FILE}"