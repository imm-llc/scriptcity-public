#!/usr/bin/env bash

slack() {
    HOST="${1}"
    INCOMING_HOOK=""
    CHANNEL="#alerts"
    USER="ExternalPing"
    EMOJI="https://cdn7.bigcommerce.com/s-komfru/images/stencil/original/b/ping-brand_1456752673__69343.original.jpg"
    payload="payload={
        \"channel\": \"${CHANNEL}\",
        \"username\": \"${USER}\",
        \"icon_url\": \"${EMOJI}\",
        \"attachments\": [
            {
                \"title\": \"No Ping Response\",
                \"fallback\": \"${HOST} not responding to ping\",
                \"text\": \"${HOST} not responding to ping\",
                \"color\": \"danger\"
            }
        ]
        }
        "
    curl -m 5 --data-urlencode "${payload}" "${INCOMING_HOOK}"
}
main() {
    HOSTS=(
        'host1.example.com'
        'host2.example.com'
    )
    for HOST in ${HOSTS[@]}
    do
        if ! ping -c 2 -w 5 ${HOST} > /dev/null
        then
            slack ${HOST}
        fi
    done
}
main