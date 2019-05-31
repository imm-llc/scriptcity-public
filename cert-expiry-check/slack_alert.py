import requests

import json

import configparser


def send_alert(hostname, days):


    config = configparser.ConfigParser()

    # config.read('/etc/tls_monitor/config.cfg')
    config.read('/home/mitch/repos/scriptcity-public/cert-expiry-check/config.cfg')

    CHANNEL = config['SLACK']['CHANNEL']
    USERNAME = config['SLACK']['USERNAME']
    EMOJI = config['SLACK']['EMOJI']
    INCOMING_WEBHOOK = config['SLACK']['INCOMING_WEBHOOK']

    json_message = {
        'channel': CHANNEL,
        'username': USERNAME,
        'icon_url': EMOJI,
        'attachments': [
            {
                'title': "ALERT: {}".format(hostname),
                'color': 'danger',
                'fallback': 'Certificate Expiring',
                'text': "The TLS certificate for {} expires in {}".format(hostname, days)
            }
        ]
    }
    requests.post(INCOMING_WEBHOOK, data=json.dumps(json_message), headers={'Content-Type': 'application/json'})