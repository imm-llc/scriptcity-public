#!/usr/bin/env python3
import requests, json, argparse

SLACK_URL = "https://hooks.slack.com/services/AAAAAA/BBBBBBB/CCCCCC"
CHANNEL = "#alerts"
EMOJI = ":terminator:"
COLOR = "danger"

def alert():
    parser = argparse.ArgumentParser(description='Send an alert when the Opstoolbox backup fails.')
    parser.add_argument('error_file', help="The log file")
    args = parser.parse_args()
    error_file = args.error_file
    slack(error_file)

def slack(error_file):
    with open(error_file, "r") as err_file:
        MSG = err_file.read().strip()
    MESSAGE = {
        "username": "Opstoolbox Backup",
        "channel": CHANNEL,
        "icon_emoji": EMOJI,
        "attachments": [
            {
                "fallback": "There was an error backing up Opstoolbox and an error sending this message. Check /opt/backup/TODAY/backup.log",
                "color": "danger",
                "title": "Opstoolbox Backup Issue",
                "text": MSG
            },
        ],
    }
    requests.post(SLACK_URL, data=json.dumps(MESSAGE), headers={'Content-Type': 'application/json'})
    err_file.close()

alert()