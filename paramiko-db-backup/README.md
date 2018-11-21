# db_backup.py
Written in Python3 and uses Parmiko and SCP. Creates `backup/YYYY-MM-DD/`, establishes an SSH connection to a remote server, dumps contents of a DB to specified location, copies that backup to the local filesystem, then deletes the database dump on the remote server.

Note: The local filesystem is never cleaned up.

### Variables

Hopefully pretty straightforward. 

DB_DUMP_LOCATION -- The location on the remote system to temporarily store the backup

LOCAL_LOCATION -- Where to store the backup. Defaults to `$PWD/backups/YYYY-MM-DD/latest.sql`

DB_HOST -- The remote database to connect to.

REMOVE_EXISTING_BACKUP_COMMAND -- Defaults to `rm /tmp/latest.sql`. Change this if you change your `DB_DUMP_LOCATION`
