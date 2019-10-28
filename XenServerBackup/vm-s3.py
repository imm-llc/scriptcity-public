#!/usr/bin/env python36
import boto3, json, os, subprocess, requests


BACKUP_PATH = "/xen-exports"

# Use Graylog?
graylogEnabled = True
graylogServer = '172.16.2.3'
graylogPort = 11588

# Use local logfile?
localLog = False

localLogFile = "/path/to/log"

slackEnabled = True
slackWebHook = ""
slackChannel = "#backups"
slackUsername = "XenBackups"
slackIcon = "https://www.shapeblue.com/wp-content/uploads/2014/11/CitrixXenCenter_logo-75x75.jpg"

"""
S3 Info

We're letting lifecycle rules handle deleting old VMs

AWS credentials are configured in ~/.aws/

Example ~/.aws/config:
[xen-backup-IAM]
region = us-west-1
output = json

Example ~/.aws/credentials:
[xen-backup-IAM]
aws_access_key_id = ABCDEFGHIJLK
aws_secret_access_key = MPg6eb2HGyascWgf
"""
BUCKET = "s3-bucket-name"
AWS_PROFILE = "xen-backup-IAM"
#############################

if slackEnabled:
    HEADERS = {'content-type': 'application/json'}
    JSON_MESSAGE = {}
    JSON_MESSAGE['channel'] = slackChannel
    JSON_MESSAGE['icon_url'] = slackIcon
    JSON_MESSAGE['username'] = slackUsername


if graylogEnabled or localLog:
        import logging
        logger = logging.getLogger()
        logging.basicConfig(level=logging.INFO)
        


if graylogEnabled:

    from pygelf import GelfTcpHandler, GelfUdpHandler, GelfTlsHandler, GelfHttpHandler
    logger.addHandler(GelfUdpHandler(host=graylogServer, port=graylogPort))
    """
    Fun note about pygelf - the function it uses to get the system's hostname, `socket.getfqdn()` typically just returns the first domain in /etc/hosts
    So I suggest editing /etc/hosts and adding your system's name in there. I have a pull request open for a fix
    """

if localLog:
    localHandler = logging.FileHandler(localLogFile)
    formatter = logging.Formatter('%(asctime)s -- %(levelname)s -- %(message)s')
    localHandler.setFormatter(formatter)
    logger.addHandler(localHandler)

session = boto3.Session(profile_name=AWS_PROFILE)
s3 = session.client('s3')

for VM_EXPORT in os.listdir(BACKUP_PATH):
    try:
        VM_PATH = os.path.join(BACKUP_PATH, VM_EXPORT)
        s3.upload_file(VM_PATH, BUCKET, VM_EXPORT)
        if graylogEnabled or localLog:
            logging.info("Backed up {} to S3".format(str(VM_PATH)))
        if slackEnabled:
            JSON_MESSAGE['text'] = "Backed up {} to S3".format(str(VM_PATH))
            requests.post(slackWebHook, data=json.dumps(JSON_MESSAGE), headers=HEADERS)
        try:
            os.remove(VM_PATH)
            if graylogEnabled or localLog:
                logging.info("Removed {}".format(str(VM_PATH)))
        except Exception as err:
            logging.error("Failed to remove {} || {}".format(str(VM_EXPORT), str(err)))
    except Exception as err:
        if graylogEnabled or localLog:
            logging.error("Failed to back up {} to S3 || {}".format(str(VM_PATH), str(err)))
        if slackEnabled:
            JSON_MESSAGE['text'] = "Failed to back up {} to S3 || {}".format(str(VM_PATH), str(err))
