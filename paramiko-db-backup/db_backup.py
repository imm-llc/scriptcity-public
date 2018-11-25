#!/usr/bin/env python3
import sys, os, datetime
try:
    import paramiko
except:
    print("Unable to import paramiko. Please make sure it's installed")
    sys.exit(1)
try:
    import scp
    from scp import SCPClient
except:
    print("Unable to import scp. Please make sure it's installed")
    sys.exit(1)

# SSH info
# Key needs to be RSA because of Paramiko limitations
SSH_KEY = ''
SSH_USER = ''
SSH_PORT = '22'
HOST = ''
# DB info
DB_USER = ''
DB_PASS = ''
DB_NAME = ''
DB_HOST = '' # remote or local host
DB_DUMP_LOCATION = ''
LOCAL_LOCATION = os.path.join('/db_backups/backups/', str(datetime.date.today()))
BACKUP_COMMAND = "mysqldump -u %s -p%s -h %s %s > %s" %(DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_DUMP_LOCATION)
REMOVE_EXISTING_BACKUP_COMMAND = "rm /tmp/latest.sql"
def remove_remote_backup():
    SSH_CLIENT = paramiko.SSHClient()
    SSH_CLIENT.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH_CLIENT.connect(HOST, port=SSH_PORT, username=SSH_USER, key_filename=SSH_KEY)
    try:
        stdin, stdout, stderr = SSH_CLIENT.exec_command(REMOVE_EXISTING_BACKUP_COMMAND)
        for item in stdout.readlines():
            print(item)
        for item in stderr.readlines():
            print(item)
        SSH_CLIENT.close()
        return dump_database()

    except:
        print("An error occurred. The file probably doesn't exist on the remote system")
        for item in stdout.readlines():
            print(item)
        for item in stderr.readlines():
            print(item)
        SSH_CLIENT.close()
        return dump_database()

def dump_database():
    SSH_CLIENT = paramiko.SSHClient()
    SSH_CLIENT.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH_CLIENT.connect(HOST, port=SSH_PORT, username=SSH_USER, key_filename=SSH_KEY)
    stdin, stdout, stderr = SSH_CLIENT.exec_command(BACKUP_COMMAND)
    for item in stdout.readlines():
        print(item)

    if stderr:
        for item in stderr.readlines():
            print(item)

    SSH_CLIENT.close()
    return grab_backup()

def grab_backup():
    # Make backup directory first
    os.makedirs(LOCAL_LOCATION)
    # Connect
    SSH_CLIENT = paramiko.SSHClient()
    SSH_CLIENT.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH_CLIENT.connect(HOST, port=SSH_PORT, username=SSH_USER, key_filename=SSH_KEY)
    scp = SCPClient(SSH_CLIENT.get_transport())
    scp.get(DB_DUMP_LOCATION, LOCAL_LOCATION)
    scp.close()
    SSH_CLIENT.close()
    cleanup()
    
def cleanup():
    # We don't want to leave a DB dump sitting arond
    SSH_CLIENT = paramiko.SSHClient()
    SSH_CLIENT.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH_CLIENT.connect(HOST, port=SSH_PORT, username=SSH_USER, key_filename=SSH_KEY)
    SSH_CLIENT.exec_command(REMOVE_EXISTING_BACKUP_COMMAND)
    SSH_CLIENT.close()
dump_database()

