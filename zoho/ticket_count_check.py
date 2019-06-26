#!/usr/bin/env python3.6

import requests
import json

API_KEY = ""

ORG_ID = ""

TICKET_URL = "https://desk.zoho.com/api/v1/tickets"

headers = {
    "Authorization": f"Zoho-authtoken {API_KEY}",
    "orgId": f"{ORG_ID}"
}

parameters = {
    "status": "Open"
}
class OpenTicketChecker:

    def __init__(self):

        self.count = 0


    def checker(self):

        try:
            self.r = requests.get(TICKET_URL, headers=headers, params=parameters)
        except Exception as e:
            print("Error")
        try:


            loaded_json = json.loads(self.r.text)

            for item in loaded_json['data']:
                self.count += 1

            print(self.count)
        except json.decoder.JSONDecodeError:
            print(0)

if __name__ == "__main__":

    tc = OpenTicketChecker()
    tc.checker()
