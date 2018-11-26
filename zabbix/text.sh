#!/bin/bash
# Configuration > Actions > Action > Operations:
# DISASTER: {TRIGGER.NAME}
# HOST IP: {HOST.IP}
# Configuration > Actions > Action > Recovery Operations:
# Resolved:  {TRIGGER.NAME}
# Configuration > Actions > Action > Update Operations
# {USER.FULLNAME} update: {EVENT.UPDATE.MESSAGE}
# Script parameters = {ALERT.MESSAGE}
alert="$1"
twilio_sid=""
twilio_auth_token=""
sms="Body=${1}"
IT=('+11231231234'
    '+11231231234')
#example number: +17201234567 --> must include country code
for savior in ${IT[*]};
do
curl "https://api.twilio.com/2010-04-01/Accounts/$twilio_sid/Messages.json" -X POST \
--data-urlencode "To=$savior" \
--data-urlencode 'From=+11231231234' \
--data-urlencode "$sms" \
-u $twilio_sid:$twilio_auth_token > /dev/null
done