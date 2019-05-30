#!/usr/bin/env bash

API=http://inhouse.slack.alert.api/api/v1/alert

JOB_NAME=$1

STATUS=$2

COLOR=$3

gen_data()
{
    cat <<EOF
{"channel": "#jenkins",
  "username": "Jenkins",
  "icon": ":jenkins:",
  "color": "$COLOR",
  "message": "$STATUS for job $JOB_NAME"}
EOF
}


curl -H 'Content-Type:application/json' -X POST $API -d "$(gen_data)"