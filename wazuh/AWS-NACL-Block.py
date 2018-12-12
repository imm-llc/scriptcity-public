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
    <extra_args>-e company1 company2 -n acl-123 acl-456 -r us-east-2 us-west-1</extra_args>
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

===AWS Config===
Config:
Store in ~/.aws/config
Make sure you have [profile something]

The extra_args for the environment will be the "something" listed above.
Example:

~/.aws/config
[profile company1]

[profile company2]

/var/ossec/etc/ossec.conf

<extra_args>-e company1 company2 -n acl-123 acl-456 -r us-east-2 us-west-1</extra_args>

Credentials:
Store in ~/.aws/credentials
You must specify aws_access_key_id and aws_secret_access_key. These should belong to the user you created above. I haven't written Assume Role support yet.

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
parser.add_argument("-e", nargs="+", help="Environment to use (e.g. dev or prod)", action="store")
parser.add_argument("-n", nargs="+", help="NACL ID", action="store")
parser.add_argument("-r", nargs="+", help="NACL Region", action="store")

# Try to parse the arguments, write error to file if it fails. 
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
# Add mask because Wazuh only gives us an IP and AWS requires CIDR notation
IP = IP + '/32'

# Use zip() to match profile (ENV), NACL (NACL_ID), and region (REGION). This is 1 to 1
# Loop through each extra_args
for ENV, NACL_ID, REGION in zip(args.e, args.n, args.r):
    AWS_PROFILE = ENV
    AWS_REGION = REGION
    
    # Create session so we can use profile 
    session = boto3.Session(profile_name=AWS_PROFILE)

    # Create resource so we can make changes. Good explanation of diff between client, resource, and session here: https://stackoverflow.com/questions/42809096/difference-in-boto3-between-resource-client-and-session
    client = session.resource('ec2', region_name=AWS_REGION)

    network_acl = client.NetworkAcl(NACL_ID)

    
    # Create empty list for rules
    EXISTING_ENTRIES = []

    # Get existing entries
    ENTRIES = network_acl.entries
    
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
            
        except Exception as err:
            EXTRA_LOG = {'wazuhAction': "addRule", 'ip': IP, 'rulenumber': str(NEW_RULE_NUMBER)}
            logging.error("|| Error adding rule: {}".format(err), extra=EXTRA_LOG)
            # We shouldn't stop just because one ACL entry didn't work
            continue
            


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
        except Exception as err:
            EXTRA_LOG = {'wazuhAction': "removeRule", 'ip': IP, 'rulenumber': str(RULE_NUMBER)}
            logging.error("|| Error removing rule: {}".format(err), extra=EXTRA_LOG)
            continue