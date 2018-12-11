#!/usr/bin/env python3
import boto3, argparse, json, logging, os
from sys import exit

"""
/var/ossec/etc/ossec.conf
COMMAND:
  <command>
    <name>AWS-NACL</name>
    <executable>AWS-NACL.py</executable>
    <expect>srcip</expect>
    <timeout_allowed>yes</timeout_allowed>
  </command>
ACTIVE RESPONSE: 
  <active-response>
    <command>AWS-NACL</command>
    <location>server</location>
    <rules_group>appsec</rules_group>
    <timeout>1800</timeout>
  </active-response>

IAM:
If you don't give the instance permission to make changes to ACLs, you'll need to create a programmatic user and plug those keys in below.

The user needs:

List:
DescribeNetworkAcls

Write:
DeleteNetworkAcl
DeleteNetworkAclEntry
CreateNetworkAcl
CreateNetworkAclEntry

The CreateNetworkAcl, CreateNetworkAclEntry, and DescribeNetworkAcls permissions must be set on "All resources" in order to work (that's coming from AWS, not me).
You'll end up with two separate policies; one on all resources, the other on a specific NACL (or several if you want)

"""

# Set up logging
LOG_FILE = "/var/ossec/logs/aws-nacl.log"
LOG_FORMAT = '%(asctime)-15s %(wazuhAction)-4s %(ip)-4s %(rulenumber)-2s %(message)s'
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT)
# Set up argparse
parser = argparse.ArgumentParser(description="A Wazuh tool to block traffic at the NACL level")
parser.add_argument("Action")
parser.add_argument("User")
parser.add_argument("IP")

try:
    args, unknown = parser.parse_known_args()
except Exception as err:
    with open(LOG_FILE, "a") as LF:
        LF.write(str(err))
        LF.close()
# Make variables pretty
ACTION = args.Action
USER = args.User
IP = args.IP

# Is permission granted through IAM on instance? If yes, set to True, if no, set to False
IAM = False

# The Network ACL ID. Mandatory
# It should be pretty trivial to turn this into a list and loop through it to work with multiple ACLs across VPCs
NACL_ID = ""

# If instance can't modify NACLs, add info here
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_REGION = "us-east-1" # e.g. us-east-1



# Create ec2 client
if IAM:
    client = boto3.resource('ec2')
else:
    client = boto3.resource('ec2', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

network_acl = client.NetworkAcl(NACL_ID)

# Create empty list for rules
EXISTING_ENTRIES = []

# Get existing entries
ENTRIES = network_acl.entries

IP = IP + '/32'
if ACTION == "add":

    # Add existing entries to list
    for ENTRY in ENTRIES:
        EXISTING_ENTRIES.append(ENTRY["RuleNumber"])
    
    # Sort list numerically
    EXISTING_RULES = sorted(EXISTING_ENTRIES)

    # Add a new rule as lowest rule number - 1 
    NEW_RULE_NUMBER = EXISTING_RULES[0] - 1

    # Make sure we can actually add the rule
    if NEW_RULE_NUMBER == 0:
        EXTRA_LOG = {'wazuhAction': "addRule", 'ip': IP, 'rulenumber': str(NEW_RULE_NUMBER)}
        logging.error("|| Error adding rule: Rule number would be negative", extra=EXTRA_LOG)
        exit(3)

    try:
        NEW_ACL_ENTRY = network_acl.create_entry(
            CidrBlock=IP,
            DryRun=False,
            Egress=False,
            Protocol='-1',
            RuleAction='deny',
            RuleNumber=NEW_RULE_NUMBER
        )
        EXTRA_LOG = {'wazuhAction': "addRule", 'ip': IP, 'rulenumber': str(NEW_RULE_NUMBER)}
        logging.warn("|| Success || NACL Block Added", extra=EXTRA_LOG)
        exit(0)
    except Exception as err:
        EXTRA_LOG = {'wazuhAction': "addRule", 'ip': IP, 'rulenumber': str(NEW_RULE_NUMBER)}
        logging.error("|| Error adding rule: {}".format(err), extra=EXTRA_LOG)
        exit(1)


# Action must be drop

else:

    for ENTRY in ENTRIES:
        if ENTRY["CidrBlock"] == IP:
            RULE_NUMBER = ENTRY["RuleNumber"]
    
    try:
        REMOVE_ACL_ENTRY = network_acl.delete_entry(
            DryRun=False,
            Egress=False,
            RuleNumber=RULE_NUMBER
        )
        EXTRA_LOG = {'wazuhAction': "removeRule", 'ip': IP, 'rulenumber': str(RULE_NUMBER)}
        logging.warn("|| Success || NACL Block Removed", extra=EXTRA_LOG)
        exit(0)
    except Exception as err:
        EXTRA_LOG = {'wazuhAction': "removeRule", 'ip': IP, 'rulenumber': str(RULE_NUMBER)}
        logging.error("|| Error removing rule: {}".format(err), extra=EXTRA_LOG)
        exit(1)