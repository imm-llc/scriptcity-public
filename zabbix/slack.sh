#!/usr/bin/env bash
# Forked from https://github.com/ericoc/zabbix-slack-alertscript
# Variables
SUBJECT=$(echo ${1} | cut -d ' ' -f 1)
SERVER=$(echo ${1} | cut -d ' ' -f 2)
MESSAGE="$2"
RESOLVED_STRING="Resolved"
PROBLEM_STRING="Problem"
UPDATE_STRING="Update"

# Logging
LOG_FILE="/var/log/zabbix/slack.log"
    
# Mail info
MAIL_ENABLED="Yes/No"
MAIL_SERVER="mail.you.com"
MAIL_PORT="25"
MAIL_FROM="zabbix@you.com"
MAIL_TO="it@you.com"

# Slack info
SLACK_URL='change me'
USERNAME='Zabbix'
EMOJI=":zabbix:"
CHANNEL="#alerts"

# Script paramenters = {ALERT.SUBJECT} and {ALERT.MESSAGE}
# Default subject: Problem {HOST.NAME}

# Test for subject content
if [ "$SUBJECT" == "$RESOLVED_STRING" ]
then
    TYPE="R"
elif [ "$SUBJECT" == "$PROBLEM_STRING" ]
then
    TYPE="P"
elif [ "$SUBJECT" == "$UPDATE_STRING" ]
then
    TYPE="U"
else
    TYPE="N"
fi

# Change message emoji, color, and (friendly) status depending on the subject
if [ "$TYPE" == "R" ]
then
    COLOR="good"
    STATUS="Resolved"
elif [ "$TYPE" == "P" ]
then 
    COLOR="danger"
    STATUS="Problem"
elif [ "$TYPE" == "U" ]
then
    COLOR="#439FE0"
    STATUS="Update"
else
    COLOR="	#808080"
    STATUS="N/A"
fi
TITLE_MESSAGE="${STATUS} | ${SERVER}"

echo "" >> ${LOG_FILE}
echo "$(date)" >> ${LOG_FILE}
echo "${TITLE_MESSAGE}" >> ${LOG_FILE}
echo "" >> ${LOG_FILE}
echo "${MESSAGE}" >> ${LOG_FILE}

# Build our JSON payload and send it as a POST request to the Slack incoming web-hook URL
# See https://api.slack.com/docs/formatting for formatting details
payload="payload={
    \"channel\": \"${CHANNEL}\",
    \"username\": \"${USERNAME}\",
    \"icon_emoji\": \"${EMOJI}\",
    \"attachments\": [
    {
        \"title\": \"${TITLE_MESSAGE}\",
        \"fallback\": \"${MESSAGE}\",
        \"text\": \"${MESSAGE}\",
        \"color\": \"${COLOR}\",
        \"mrkdwn_in\": [ \"text\" ]
    }
    ] }"
# You never know
CURL=$(which curl)
# If this command succeeds....
if ${CURL} -m 5 --data-urlencode "${payload}" ${SLACK_URL}
then
    # We're good
    echo "" >> ${LOG_FILE}
    echo "Posted to Slack successfully" >> ${LOG_FILE}
    # Exit script
    exit 0
# cURL has failed _and_ mail is enabled
elif [ "${MAIL_ENABLED}" = "Yes" ]
then
    echo "" >> ${LOG_FILE}
    echo "Issue sending to Slack" >> ${LOG_FILE}
    send_mail
# cURL has failed and mail is _disabled_
else
    echo "" >> ${LOG_FILE}
    echo "Unable to send to Slack and Mail not enabled" >> ${LOG_FILE}
    exit 9
fi

send_mail () {
    # mailx presumably doesn't exist, not the best check
    if ! $(which mailx)
    then
        MAIL=$(which mail)
    else
        MAIL=$(which mailx)
    fi
    # Echo it so it's formatted 
    # No support for auth yet
    if echo -e "${TITLE_MESSAGE}\n${MESSAGE}" | $MAIL -S smtp="${MAIL_SERVER}:${MAIL_PORT}" -s "Zabbix Alert" -r ${MAIL_FROM} ${MAIL_TO}
    then
        echo "" >> ${LOG_FILE}
        echo "Sent alert via email to ${MAIL_TO}" >> ${LOG_FILE}
        exit 0
    else
        echo "" >> ${LOG_FILE}
        echo "Error sending email alert. Happy debugging" >> ${LOG_FILE}
        exit 1
    fi

}
