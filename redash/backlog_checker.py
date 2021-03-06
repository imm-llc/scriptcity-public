#!/usr/bin/env python3
import requests, json, sys, os, argparse

# Redash
REDASH_HOST = "http://redash.example.com"
API_KEY = "YOUR REDASH API KEY"
QUERY_ID = "298" # This is the power track backlog query I set up

# Slack
WEBHOOK_URL = "YOUR SLACK INCOMING WEBHOOK"
USERNAME = "RedashAlerts"
CHANNEL = "#redash-alerts"
EMOJI = "https://avatars3.githubusercontent.com/u/10746780?s=200&v=4" # Redash logo
HEADERS = {'content-type': 'application/json'}
# Previous backlog info
LOGFILE = "/opt/redash/backlog.count"

parser = argparse.ArgumentParser(description='Check DelayedJobs Backlog')
parser.add_argument('-n', help="Get count now", action='store_true')
parser.add_argument('-l', help="Get count now, locally. Don't post to Slack", action='store_true')
args = parser.parse_args()
NOW = args.n
LOCAL = args.l

def refresh_redash():
    s  = requests.Session()
    s.headers.update({'Authorization': 'Key {}'.format(API_KEY)})
    response = s.post('{}/api/queries/{}/refresh'.format(REDASH_HOST, QUERY_ID))
    if response.status_code != 200:
        return slack_bad_status(response.status_code, "0")
    else:
        response = s.get('{}/api/queries/{}/results.json'.format(REDASH_HOST, QUERY_ID))
        status_code = response.status_code
        if status_code != 200:
            return slack_bad_status(status_code, "0")
        else:
            pending_jobs = response.json()['query_result']['data']['rows'][0]['count']
            if NOW:
                return slack_good_status(pending_jobs, "#439FE0")
            elif LOCAL:
                print("Pending Jobs: %i" %(pending_jobs))
            else:
                if pending_jobs > 100:
                    with open(LOGFILE, "w") as LF:
                        LF.write(str(pending_jobs))
                        LF.close()
                    return slack_good_status(pending_jobs, "danger")
                else:
                    if os.path.isfile(LOGFILE):
                        os.remove(LOGFILE)
                        return slack_good_status(pending_jobs, "good")
                        
                    else:
                        sys.exit(0)


def slack_bad_status(http_status, pending_jobs):
    if http_status == 403:
        ERROR_MESSAGE = "403 response on request. Check your API key"
    elif http_status == 502:
        ERROR_MESSAGE = "502 response on request. Check to make sure Redash is running correctly"
    else:
        ERROR_MESSAGE = "HTTP status code: %i" %(http_status)

    JSON_RESPONSE = {}
    JSON_RESPONSE['username'] = USERNAME
    JSON_RESPONSE['channel'] = CHANNEL
    JSON_RESPONSE['icon_url'] = EMOJI
    JSON_RESPONSE['attachments'] = [{
        "text": ERROR_MESSAGE,
        "color": "danger",
        "title": "Delayed Jobs Backlog"
    }]
    requests.post(WEBHOOK_URL, data=json.dumps(JSON_RESPONSE), headers=HEADERS)


def slack_good_status(pending_jobs, status):
    JSON_RESPONSE = {}
    JSON_RESPONSE['username'] = USERNAME
    JSON_RESPONSE['channel'] = CHANNEL
    JSON_RESPONSE['icon_url'] = EMOJI
    JSON_RESPONSE['attachments'] = [{
        "text": "Power Track Backlog: "+str(pending_jobs),
        "color": status,
        "title": "Delayed Jobs Backlog"
    }]
    requests.post(WEBHOOK_URL, data=json.dumps(JSON_RESPONSE), headers=HEADERS)

refresh_redash()