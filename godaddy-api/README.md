# godaddy-api

## Overview

Checks GoDaddy API for "ACTIVE" domains and checks to see if they're expiring in a defined time period. The default is 30 days.

GoDaddy API docs: https://developer.godaddy.com/doc/endpoint/domains

## Variables

You'll need to generate at least a production API secret and key. This can be done here: https://developer.godaddy.com/keys

`OTE_API_KEY` => OTE API KEY

`OTE_API_SECRET` => OTE API Secret

`PROD_API_KEY` => Production API Key

`PROD_API_SECRET` => Production API Secret

`WARNING` => How many before domain expiration do you want a warning?

`INCOMING_WEBHOOK` => Slack incoming webhook

`USERNAME` => Username for Slack post

`EMOJI` => Emoji for Slack post. Currently set to `icon_url`, so you'll need to either provide a link or change line 83 to `JSON_DATA['icon_emoji']` and use a `:emoji:` for `EMOJI`

`CHANNEL` => Slack channel to post to


## TODO

* Not alert every day (i.e. not alert on T-minus 30, 29, 28)