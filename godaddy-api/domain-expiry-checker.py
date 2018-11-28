#!/usr/bin/env python3
import requests, json, argparse, sys, datetime, dateutil.parser, time
from datetime import timedelta, datetime

# GoDaddy API
OTE_API_KEY = ""
OTE_API_SECRET = ""

PROD_API_KEY = ""
PROD_API_SECRET = ""

# Set up arguments, either production or OTE
parser = argparse.ArgumentParser(description="A tool to scrape the GoDaddy API")
parser.add_argument("-p", help="Use production keys", action="store_true")
parser.add_argument("-o", help="Use OTE keys", action="store_true")
args = parser.parse_args()

# Warn this many days before expiration
WARNING = 30

# The /v1/domains/ method returns all DomainDetail info: see https://developer.godaddy.com/doc/endpoint/domains
if args.p:
    API_KEY = PROD_API_KEY
    API_SECRET = PROD_API_SECRET
    API_URL = "https://api.godaddy.com/v1/domains/"
elif args.o:
    API_KEY = OTE_API_KEY
    API_SECRET = OTE_API_SECRET
    API_URL = "https://api.ote-godaddy.com/v1/domains/"
elif args.p and args.o:
    print("You may only specify -p or -o")
    sys.exit(1)
else:
    print("You must specify -o or -p. See -h for more info")
    sys.exit(1)
def check_expiry():
    # Set header for auth
    HEADER = {'Authorization': 'sso-key '+API_KEY+":"+API_SECRET}
    # Send request
    r = requests.get(API_URL, headers=HEADER)
    # Make sure it worked
    if r.status_code != 200:
        print("Error communicating with {}. Status code: {}").format(API_URL, r.status_code)
    else:
        # Load json data
        JSON_DATA = json.loads(r.text)
        # arbitrary range, change as you please. There's probably a better way to do this
        for i in range(0,100):
            try:
                DOMAIN = JSON_DATA[i]['domain']
                EXPIRATION = JSON_DATA[i]['expires']
                STATUS = JSON_DATA[i]['status']
                # We only care about active domains
                if STATUS == "ACTIVE":
                    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" 
                    FORMAT_DATE = datetime.strptime(EXPIRATION, DATE_FORMAT)
                    TODAY = datetime.today()
                    # Fucking datetime
                    TODAY = datetime.strftime(TODAY, DATE_FORMAT)
                    TODAY = datetime.strptime(TODAY, DATE_FORMAT)

                    CHECK_EXPIRATION = FORMAT_DATE - timedelta(days=WARNING)

                    if CHECK_EXPIRATION < TODAY:
                        slack_notification(DOMAIN, FORMAT_DATE)
                    else:
                        pass
                else:
                    continue
                

            except:
                sys.exit(0)

def slack_notification(DOMAIN, FORMAT_DATE):
    INCOMING_WEBHOOK = ""
    HEADER = {'Content-Type': 'application/json'}
    USERNAME = ""
    EMOJI = ""
    CHANNEL = ""
    JSON_DATA = {}
    JSON_DATA['channe'] = CHANNEL
    JSON_DATA['icon_url'] = EMOJI
    JSON_DATA['username'] = USERNAME
    JSON_DATA['attachments'] = [{
        'title': "Domain Expiration Alert",
        'color': 'danger',
        'fallback': "Domain Expiring",
        'text': "%s is expiring on %s" %(DOMAIN, str(FORMAT_DATE))
    }]
    requests.post(INCOMING_WEBHOOK, data=json.dumps(JSON_DATA), headers=HEADER)

check_expiry()