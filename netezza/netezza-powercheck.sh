#!/usr/bin/env bash
# Is the power out? You tell me

# Set count so we can increment
COUNT=0
LOG_FILE="power_checker.log"
TARGET="172.28.254.2"
test_connection () {
if [ "${COUNT}" == "10" ]
then
echo "$(date): shutdown initiated" | tee -a $LOG_FILE
shutdown
# Throwback Thursday
exit 369
fi
if ! ping -c 3 -W 2 "${TARGET}" > /dev/null
then
COUNT=$(expr $COUNT + 1)
sleep 30
# We're waiting for 10ish minutes to see if the power comes back on
test_connection
fi
}
test_connection
