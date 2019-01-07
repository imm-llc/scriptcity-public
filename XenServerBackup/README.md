# XenServerBackup

## Overview

In our infrastructure, we run these scripts on two separate machines.

`vm-backup.sh` runs first on our XenServer. This script creates snapshots (non-quiesced, no memory) and templates of VMs.

`vm-s3.py` runs on a Samba server that XenServer mounts as its `${BACKUP_PATH}`. It's in charge of uploading `.xva` files the S3. 

## Configuration

### Graylog

If you want to use Graylog, open a GELF/UDP input.

### vm-backup.sh

Configure the `${SCRIPT_PATH}` to point to where you're executing the script from.

Configure `${BACKUP_PATH}` to point to where you want the VM templates to be saved to.

Populate `${SCRIPT_PATH}/uuid.list` with the UUIDs of the VMs you want to backup. You can get these by running `xe vm-list`.

If you want to mount a Samba share and backup to that, fill in the Samba info. *NOTE:* Samba is enabled by default!

If you want to send messages to Graylog, fille in the Graylog section. That's it.

### vm-s3.py

Make sure you have Python36 installed. I wrote this for CentOS machines, so be aware. Change the interpreter if need be.

If you want to send messages to Graylog, install `pygelf` (`pip3 install pygelf`). Whichever is the first domain in `/etc/hosts`, pygelf will use as the source in your GELF message. Usually that means localhost.localdomain. Fill out the Graylog section. *NOTE:* Graylog is enabled by default.

If you want to log locally, change `localLog` to true and provide a valid path for `localLogFile`.

Scroll down past the bad Python formatting and find the S3 section.

Make sure you've created an S3 bucket and granted an IAM user `putObject` permission on that bucket. That's all that user needs. Grab their secret and access keys and fill them into your user's aws config (i.e. `/home/xen-backup-user/.aws/credentials). There's an example in the code in case you're unsure. 

Provide a value for `BACKUP_PATH`. This is where your backups are located. If running on the same machine as `vm-backup.sh`, it will match `${BACKUP_PATH}`.

### S3 

This script does not clean up S3 for you. I recommend using lifecycle rules for that. 

