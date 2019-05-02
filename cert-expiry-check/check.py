#!/usr/bin/env python3
# Forked from https://serverlesscode.com/post/ssl-expiration-alerts-with-lambda/
import sys, datetime, ssl, socket, json
from config import HOSTS, ALERT_TIME, CHANNEL, USERNAME, EMOJI, INCOMING_WEBHOOK
try:
    import requests
except:
    print("It doesn't seem like you've installed requests")
    print("Try pip install --requests")

# If running on a Mac, follow the steps in this answer: https://stackoverflow.com/questions/41691327/ssl-sslerror-ssl-certificate-verify-failed-certificate-verify-failed-ssl-c/41692664
def ssl_expiry_datetime():
    for HOST in HOSTS:
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=HOST,
        )
        # 3 second timeout because we don't want to wait around forever, feel free to change this
        conn.settimeout(3.0)
        # If we don't use a try block, an expired cert or unreachable host will tank the script
        try:
            conn.connect((HOST, 443))
            ssl_info = conn.getpeercert()
            # parse the string from the certificate into a Python datetime object
            expire_date = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
            remaining_lifetime = expire_date - datetime.datetime.utcnow()
            if remaining_lifetime < datetime.timedelta(days=ALERT_TIME):
                slack_alert(HOST, remaining_lifetime)
            else:
                continue
        except Exception as e:
            print(f"Hit an exception checking {HOST}:\n {str(e)}")



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



