#!/usr/bin/env python3
# Forked from https://serverlesscode.com/post/ssl-expiration-alerts-with-lambda/
import sys, datetime, ssl, socket, json
try:
    import requests
except:
    print("It doesn't seem like you've installed requests")
    print("Try pip install --requests")

# Hosts to monitor
HOSTS = ['imm.com', 'boulderheavyindustries.com', 'factandfiction.work', 'respondology.com', 'visiqua.com']
# How many days prior to cert expiration should we alert?
ALERT_TIME = 10

# Slack stuff
INCOMING_WEBHOOK = ""
USERNAME = "TLS Certificate Checker"
CHANNEL = "#cert-alerts"
EMOJI = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRihczVMjBKJqN7uFHZRTcwcsq1M-3ulBsfgb-5ZqMaLavLsEnYsA"


# If running on a Mac, follow the steps in this answer: https://stackoverflow.com/questions/41691327/ssl-sslerror-ssl-certificate-verify-failed-certificate-verify-failed-ssl-c/41692664
def ssl_expiry_datetime():
    for HOST in HOSTS:
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=HOST,
        )
        # 3 second timeout because Lambda has runtime limitations
        conn.settimeout(3.0)
        conn.connect((HOST, 443))
        ssl_info = conn.getpeercert()
        # parse the string from the certificate into a Python datetime object
        expire_date = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        remaining_lifetime = expire_date - datetime.datetime.utcnow()
        if remaining_lifetime < datetime.timedelta(days=ALERT_TIME):
            slack_alert(HOST, remaining_lifetime)
        else:
            continue



def slack_alert(host, time_left):
    json_message = {
        'channel': CHANNEL,
        'username': USERNAME,
        'icon_url': EMOJI,
        'attachments': [
            {
                'title': "ALERT: %s" %host,
                'color': 'danger',
                'fallback': 'Certificate Expiring',
                'text': "The TLS certificate for %s expires in %s" %(host, time_left)
            }
        ]
    }
    requests.post(INCOMING_WEBHOOK, data=json.dumps(json_message), headers={'Content-Type': 'application/json'})
ssl_expiry_datetime()



