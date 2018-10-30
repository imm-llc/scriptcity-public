#!/usr/bin/env python3
import boto3, datetime, json, requests, os, subprocess
from datetime import date, timedelta
from subprocess import call
CREDS_FILE = "/opt/ec2Snapshots/.env"
with open(CREDS_FILE, "r")as OPEN_CREDS:
	CREDS = OPEN_CREDS.read().splitlines()
	ACCESS = CREDS[1]
	SECRET = CREDS[3]
	REGION = CREDS[5]
	CREDS_FILE.close()
ec2 = boto3.resource('ec2', aws_access_key_id=ACCESS, aws_secret_access_key=SECRET, region_name=REGION)
client = boto3.client('ec2', aws_access_key_id=ACCESS, aws_secret_access_key=SECRET, region_name=REGION)

def log_dir():
	CURRENT_DIR = os.getcwd()
	LOG_DIR = os.path.join(CURRENT_DIR, "logs")
	LOG_FILE = os.path.join(LOG_DIR, "ec2Snap.log")
	LOG_DIR_EXIST = os.path.exists(LOG_DIR)
	if LOG_DIR_EXIST is True:
		snapshot_instances(LOG_FILE)
	else:
		print("Log directory does not exist\nCreating...")
		print("Created", LOG_DIR)
		os.mkdir(LOG_DIR, mode=0o750)
		return log_dir()

def snapshot_instances(LOG_FILE):
	TODAY = date.today()
	global ec2
	global client
	instances = ec2.instances.filter(
		Filters = [{
		'Name': 'instance-state-name', 'Values': ['running'],
		'Name': 'tag:backup', 'Values':["yes"]
		}]
	)
	with open(LOG_FILE, "a") as LF:
		LF.write("\n")
		LF.write(str(TODAY))
		LF.write("\n")
		LF.close()
	for instance in instances:
		for tag in instance.tags:
			if tag['Key'] == "Name":
				FRIENDLY_NAME = (tag['Value'])
				with open(LOG_FILE, "a") as LF:
					LF.write("Creating snapshots for: "+FRIENDLY_NAME)
					LF.write("\n")
					LF.close()

		for disk in instance.block_device_mappings:
			VOL_ID = (disk.get('Ebs').get('VolumeId'))
			#print("Snapshotting:", FRIENDLY_NAME, VOL_ID)
			ec2.create_snapshot(
			VolumeId=VOL_ID,
			Description=FRIENDLY_NAME,
			TagSpecifications=[
				{
					'ResourceType': 'snapshot',
					'Tags': [
						{
							'Key': "allowDelete",
							'Value': 'yes'
						},
					]
				},
			],
			#DryRun=True
			)
	with open(LOG_FILE, "a") as LF:
		LF.write("\n")
		LF.write("Snapshots complete!")
		LF.close()
	return delete_old_snaps(LOG_FILE)

def delete_old_snaps(LOG_FILE):
	global ec2
	global client

	TODAY = date.today()

	RETENTION_DAYS = 3
	TO_DELETE_TAG = TODAY + timedelta(RETENTION_DAYS)
	MAX_AGE = TODAY - datetime.timedelta(RETENTION_DAYS)

	OLD_SNAPS = client.describe_snapshots(
		Filters=[
			{
				'Name': 'tag:allowDelete',
				'Values': ['yes']
			},
		],
		OwnerIds=[
			'self'
		]
	)
	with open(LOG_FILE, "a") as LF:
		LF.write("\n")
		LF.write("Looking for old snapshots to delete\n")
		LF.close()
	for SNAP in OLD_SNAPS['Snapshots']:
		C_TIME = SNAP['StartTime']

		PRETTY_TIME = C_TIME.date()
		if MAX_AGE > PRETTY_TIME:
			#print("Deleting", SNAP['SnapshotId'])
			with open(LOG_FILE, "a") as LF:
				LF.write("Found: "+SNAP['SnapshotId'])
				LF.write("\n")
				LF.close()
			try:
				client.delete_snapshot(
					SnapshotId=SNAP['SnapshotId'],
					#DryRun=True
				)
				with open(LOG_FILE, "a") as LF:
					LF.write("Deleted: "+SNAP['SnapshotId'])
					LF.write("\n")
					LF.close()
			except:
				with open(LOG_FILE, "a") as LF:
					LF.write("An error has occurred")
					LF.close()
	notify()
def notify():
	with open(CREDS_FILE, "r")as OPEN_CREDS:
		CREDS = OPEN_CREDS.read().splitlines()
		SLACK_URL = CREDS[7]
		OPEN_CREDS.close()
	UNAME = 'EC2Snapper'
	CHANNEL = '#alerts'
	EMOJI = ':turdel:'
	MSG = "EC2 instances snapshotted"
	PAYLOAD = {}
	PAYLOAD['username'] = UNAME
	PAYLOAD['channel'] = CHANNEL
	PAYLOAD['icon_emoji'] = EMOJI
	PAYLOAD['text'] = MSG
	
	REQ = requests.post(SLACK_URL, data=json.dumps(PAYLOAD), headers={'Content-Type': 'application/json'})
log_dir()