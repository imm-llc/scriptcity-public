#!/usr/bin/env python3
import boto3
import json

from sys import argv

access_key = argv[1]

secret_key = argv[2]

region = argv[3]


client = boto3.client(
    'ec2',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region
)

for instance_status in client.describe_instance_status()['InstanceStatuses']:
    status_dict = instance_status['InstanceStatus']
    if status_dict['Status'] != "ok":
        print("DANGER WILL ROBINSON")