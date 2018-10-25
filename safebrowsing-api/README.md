#safebrowsing-check.py

Checks a list of URLs against Google's Safe Browsing API

Currently uses API V4

To add a new site, add the domain to the `SITES_TO_CHECK` list.

If the response from Google contains the string "matches", a Slack alert fires containing the URL and the response from Google.


