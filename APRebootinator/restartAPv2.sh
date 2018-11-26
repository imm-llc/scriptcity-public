#!/bin/bash
username=""
PASS_FILE="/path/to/file"
APs=(
	'172.28.253.65'
	'172.28.253.66'
	'172.28.253.67'
	'172.28.253.68'
	'172.28.253.70'
	'172.28.253.71'
	'172.28.253.72'
	'172.28.253.73'
	)
for ap in ${APs[@]};
do
sshpass -f "${PASS_FILE}" ssh $username@$ap reboot
done
url='https://hooks.slack.com/AAAAA/AAAAAAAAAAAAAAAAA'
emoji=":terminator:"
uname="AP REBOOTINATOR"
channel="#alerts"
message="ACCESS POINTS REBOOTED"
payload="payload={\"channel\": \"$channel\", \"username\": \"$uname\", \"icon_emoji\": \"$emoji\", \"text\": \"$message\"}"
curl -m 5 --data-urlencode "${payload}" $url
