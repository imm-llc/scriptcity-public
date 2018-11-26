# Red Hat Security Announcements 2 Slack

Parses a JSON from the Red Hat Security Data API (https://access.redhat.com/documentation/en-us/red_hat_security_data_api/1.0/html-single/red_hat_security_data_api/index) and looks for the ID, severity, and released_packages. Formats and writes to file. Reads that file into a Slack notification.

Only grabs announcements from that day, otherwise things would get weird.

All you need to do to use it is assign a value to INCOMING_WEBHOOK and probably change the path to LOG_FILE
