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
exit 369
fi
ping -c 3 -W 2 "${TARGET}" > /dev/null
if [ "$?" != "0" ]
then
COUNT=$(expr $COUNT + 1)
sleep 30
test_connection
fi
}
test_connection
