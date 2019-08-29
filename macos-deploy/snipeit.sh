#!/usr/bin/env bash
#source <(curl --silent http://yum/mac/.env)
curl --silent -o /tmp/snipe http://yum/mac/.env
source /tmp/snipe
rm -f /tmp/snipe

echo ""
echo ""
echo "*************************************************"
echo ""
echo "ASSET TIME"
echo ""
read -p "Asset tag number: " ASSET_TAG
echo ""
echo ""
echo "
15\" MBP Model Number: 11
13\" MBP Model Number: 10
13\" MBA Model Number: 9 
"
echo ""
read -p "Enter model number: " MODEL_NUMBER
echo ""
echo "" 

# 2 == "Ready to Deploy 'Deployed'"
STATUS_ID=2
HOSTNAME=$(hostname)

JSON='{"asset_tag": "'"${ASSET_TAG}"'", "status_id": 2, "model_id": "'"${MODEL_NUMBER}"'", "name": "'"${HOSTNAME}"'"}'

curl -X POST -k -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer ${SNIPEIT_API_KEY}" https://assets.imm.corp/api/v1/hardware -d "${JSON}"

