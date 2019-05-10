from config import SLACK_CHANNEL, SLACK_USERNAME, SLACK_WEBHOOK, SLACK_EMOJI

import time
import json
import requests

def slack_alert(alert_message):

    headers = {
        "content-type": "application/json"
    }

    slack_message = {
        "channel": SLACK_CHANNEL,
        "icon_emoji": SLACK_EMOJI,
        "username": SLACK_USERNAME,
        "attachments": [
            {
                "fallback": "Unable to connect to Netezza database",
                "color": "danger",
                "title": "Unable to connect to Netezza database",
                "fields": [
                    {
                        "title": "Timestamp",
                        "value": str(time.asctime()),
                        "short": "true"
                    },
                    {
                        "title": "ConnectionError",
                        "value": alert_message,
                        "short": "false"
                    }
                ]
            }
        ]
    }

    requests.post(SLACK_WEBHOOK, data=json.dumps(slack_message), headers=headers)