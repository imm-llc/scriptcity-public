#!/usr/bin/env python3
import requests, json, datetime, sys
TODAY = str(datetime.date.today())
RH_API = "https://access.redhat.com/labs/securitydataapi/cvrf.json?after="+TODAY
LOG_FILE = "/opt/rhAPI/{}.log".format(TODAY)

def check_api():
    r = requests.get(RH_API)
    json_ = json.loads(r.text)
    for i in range(0,200):
        try:
            rhsa = json_[i]["RHSA"]
            severity = json_[i]["severity"]
            fixes = json_[i]["released_packages"]
            with open(LOG_FILE, "a") as LF:
                LF.write("RHSA: {} || Severity: {} || Updates: ".format(rhsa, severity)+"\n")
                for fix in fixes:
                    LF.write(fix+"\n")
        except:
            LF.close()
            return slack()
        LF.close()
    pass
    
def slack():
    global LOG_FILE
    MESSAGE = open(LOG_FILE, "r")
    MESSAGE = MESSAGE.read()
    INCOMING_WEBHOOK = ""
    USER = "Red Hat Security Announcements"
    ICON = "https://gigaom.com/wp-content/uploads/sites/1/2012/08/redhat.jpg"
    CHANNEL = "#vulnerability"
    HEADERS = {'content-type': 'application/json'}
    JSON_MESSAGE = {}
    JSON_MESSAGE['channel'] = CHANNEL
    JSON_MESSAGE['icon_url'] = ICON
    JSON_MESSAGE['username'] = USER
    JSON_MESSAGE['text'] = MESSAGE
    requests.post(INCOMING_WEBHOOK, data=json.dumps(JSON_MESSAGE), headers=HEADERS)
check_api()