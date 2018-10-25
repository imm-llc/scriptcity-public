#!/usr/bin/env python3
import requests, json, sys

SITES_TO_CHECK = [
    'example.com',
    'example.work',
    'example.net'
]

# Google Safe Browsing API KEY
API_KEY = "Get this from Google"
LOOKUP_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

KEY = {"key": API_KEY}

def malware_check():
    for SITE in SITES_TO_CHECK:
        URL = "https://"+SITE
        PAYLOAD = {
            "client": {
                "clientId": "bhisafebrowsing",
                "clientVersion": "0.0.1"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "THREAT_TYPE_UNSPECIFIED", "POTENTIALLY_HARMFUL_APPLICATION"],
                "threatEntryTypes": ["URL"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntries": [
                    {"url": URL}
                ]
            }
        }
        send_request = requests.post(LOOKUP_URL, params=KEY, json=PAYLOAD)
        RESPONSE = send_request.text
        #print(json.loads(RESPONSE))
        #send_request.json()
        #print(RESPONSE)
        if "matches" in RESPONSE:
            slack(URL, RESPONSE)
def slack(REPORTED_SITE, MESSAGE):
    SLACK_URL = "Your Slack Incoming Webhook"
    FORMATTED_MESSAGE = REPORTED_SITE+" "+MESSAGE
    PAYLOAD = {
        "username": "Safe Browser",
        "channel": "#example",
        "icon_emoji": ":partyparrot:",
        "attachments": [
            {
                "fallback": "Well, shit, this didn't work",
                "color": "danger",
                "title": "Safe Browsing Alert",
                "text": FORMATTED_MESSAGE                
            }
        ]
    }

    POST_SLACK = requests.post(SLACK_URL, data=json.dumps(PAYLOAD), headers={'Content-Type': 'application/json'})
    print(POST_SLACK.text)
    print(POST_SLACK.status_code)

malware_check()
