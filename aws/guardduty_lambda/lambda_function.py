import json, os
from botocore.vendored import requests

def lambda_handler(data, context):
    message = {}
    message['Region'] = data['region']
    message['ResourceCategory'] = data['detail']['resource']['resourceType']
    message['SuspectAction'] = data['detail']['service']['action']['actionType']
    message['Severity'] = data['detail']['severity']
    # We're working with an instance
    if message['ResourceCategory'] == 'Instance':
        message['SuspectResource'] = data['detail']['resource']['instanceDetails']['instanceId']
        if data['detail']['service']['action']['actionType'] == "PORT_PROBE":
            message['RemoteIP'] = data['detail']['service']['action']['portProbeDetails']['remoteIpDetails']['ipAddressV4']
            network_direction = ""
        else:
            message['RemoteIP'] = data['detail']['service']['action']['networkConnectionAction']['remoteIpDetails']['ipAddressV4']
            network_direction = data['detail']['service']['action']['networkConnectionAction']['connectionDirection']
        message['SuspectAction'] = "{} - {}".format(message['SuspectAction'], network_direction)
    elif message['ResourceCategory'] == "AccessKey":
        message['SuspectResource'] = data['detail']['resource']['accessKeyDetails']['userName']
        message['RemoteIP'] = data['detail']['service']['action']['awsApiCallAction']['remoteIpDetails']['ipAddressV4']
        message['SuspectAction'] = "AccessKey Usage"
    else:
        message['SuspectResource'] = "Unknown"
        message['RemoteIP'] = "Unknown"
        message['SuspectAction'] = "Unknown"
    message['Description'] = data['detail']['description']
    
    slack_handler(message)
    


def slack_handler(message):
    channel = os.getenv('slack_channel')
    username = os.getenv('username')
    emoji = os.getenv('emoji')
    webhook = os.getenv('webhook')
    company = os.getenv('company')
    headers = {'content-type': 'application/json'}

    if message['Severity'] < 5:
        color = "#439FE0"
    elif message['Severity'] > 7:
        color = "danger"
    else:
        color = "warning"
    JSON_MESSAGE = {}
    JSON_MESSAGE['channel'] = channel
    JSON_MESSAGE['icon_emoji'] = emoji
    JSON_MESSAGE['username'] = username
    JSON_MESSAGE['attachments'] = [
        {
            "fallback": "There is a GuardDuty Alert for {}".format(company),
            "color": color,
            "title": "{} GuardDuty Alert in {}".format(company, message['Region']),
            "fields": [
                {
                    "title": "SuspectResource",
                    "value": message['SuspectResource'],
                    "short": "true"
                },
                {
                    "title": "SuspectAction",
                    "value": message['SuspectAction'],
                    "short": "true"
                },
                {
                    "title": "RemoteIP",
                    "value": message['RemoteIP'],
                    "short": "true"
                },
                {
                    "title": "Severity",
                    "value": message['Severity'],
                    "short": "true"
                },
                    "title": "Description",
                    "value": message['Description'],
                    "short": "false"
            ]
        }
    ]

    requests.post(webhook, data=json.dumps(JSON_MESSAGE), headers={'Content-Type': 'application/json'})