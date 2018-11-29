# snap.py

Snapshots EC2 instance volumes, deletes snapshots older than 3 days, logs all of that to a file, then posts that file to Slack. 

## IAM Permissions

Create a policy allowing:

Read access to: instances, volumes, tags

List access to: describeHosts, DescribeInstances, DescribeInstanceStatus, DescribeSnapshotAttribute, DescribeSnapshots, DescribeVolumes

Write access to: CreateSnapshot, CreateTags, DeleteSnapshot, ModifySnapshotAttribute

Create a programmatic access user, assign it the policy you created, and grab the users keys.

### Usage

By default, the script thinks it's installed in `/opt/ec2snapshots/`. If that's not the case, change the `CREDS_FILE`, `LOG_DIR`, and `LOG_FILE` variables. 

Also, by default, the script looks for AWS creds to be in `/opt/ec2snapshots/.env`. Again, change that if needed.

Plug your user's keys into the `.env` file. Make sure you follow the existing format in the `.env`, Python is looking for specific values on specific lines.

Line 8 of the `.env` file should be your Slack incoming webhook.

If you want to retain backups for more (or less) than 3 days, change `RETENTION_DAYS` on line 72.

Make sure you add in your Slack variables in lines 124, 125, and 126
