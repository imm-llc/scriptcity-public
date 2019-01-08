#!/usr/bin/env bash
##########
# CONFIG #
##########
# Path to script
SCRIPT_PATH="/opt/xenBackup"

# Where to put backups
BACKUP_PATH="/mnt/xenBackups"

###############
# Samba Info. #
###############
sambaShare=true
sambaServer="//someserver/someDir"
sambaServer="//samba.you.com/xen-exports"
credentialsFile="/path/to/credentials"

# List of VM UUIDs
# Format should be: vmfriendlyname:UUID
# Example-- ntp:d1d1d1d1d1-a6a6-9811-555d-ee9999999
VM_UUID_LIST=$(cat ${SCRIPT_PATH}/uuid.list)

# Used for formatting snapshot labels
DATE=$(date +%F)

# Send a GELF message to Graylog?
# If you want to enable Graylog messages, you'll need to install netcat, which is available in the Base repo
# All of the netcat commands assume GELF/UDP Input on Graylog
graylogEnabled=false
syslogServer=""
syslogPort=""


##############
# End config #
##############
if "${graylogEnabled}"
then
    syslog_snapshot () {
        if [ "${2}" == "FAIL" ]
        then
            shortMessage="Snapshot creation failed"
            fullMessage="Snapshot not created for ${1}"
            level="7"
        else
            shortMessage="Snapshot creation succeeded"
            fullMessage="Snapshot created for ${1}"
            level="3"
        fi
        echo -e "{\"version\": \"1.1\", \"application_name\": \"XenSnapshot\", \"VM\": \"${1}\", \"short_message\": \"${shortMessage}\", \"full_message\": \"${fullMessage} \", \"level\": \"${level}\"}"\
        | nc -w 1 -u $syslogServer $syslogPort
    }

    syslog_tempate () {
        if [ "${2}" == "FAIL" ]
        then
            shortMessage="Template creation failed"
            fullMessage="Template not created for ${1}"
            level="7"
        else
            shortMessage="Template creation succeeded"
            fullMessage="Template created for ${1}"
            level="3"
        fi
        echo -e "{\"version\": \"1.1\", \"application_name\": \"XenSnapshot\", \"VM\": \"${1}\", \"short_message\": \"${shortMessage}\", \"full_message\": \"${fullMessage} \", \"level\": \"${level}\"}"\
        | nc -w 1 -u $syslogServer $syslogPort
    }

    syslog_snapshot_delete () {
        if [ "${2}" == "FAIL" ]
        then
            shortMessage="Template deletion failed"
            fullMessage="Template not deleted for ${1}"
            level="7"
        else
            shortMessage="Template deletion succeeded"
            fullMessage="Template deleted for ${1}"
            level="3"
        fi
        echo -e "{\"version\": \"1.1\", \"application_name\": \"XenSnapshot\", \"VM\": \"${1}\", \"short_message\": \"${shortMessage}\", \"full_message\": \"${fullMessage} \", \"level\": \"${level}\"}"\
        | nc -w 1 -u $syslogServer $syslogPort
    }
fi
create_and_delete_template () {
    if xe snapshot-export-to-template snapshot-uuid="${1}" filename="${BACKUP_PATH}/${2}"
    then
        RESULT="SUCCESS"
    else
        RESULT="FAIL"
    fi
    if "${graylogEnabled}"
    then
        syslog_tempate "${2}" "${RESULT}"
    fi
    # Delete snapshots because the templates are now safely stored remotely
    if xe snapshot-uninstall force=true snapshot-uuid="${1}"
    then
        RESULT="SUCCESS"
    else
        RESULT="FAIL"
    fi
    if "${graylogEnabled}"
    then
        syslog_snapshot_delete "${2}" "${RESULT}"
    fi    
    
}
create_snapshot () {
for UUID in ${VM_UUID_LIST}
do
    VM_FRIENDLY_NAME=$(echo "${UUID}" | cut -f 1 -d ":")
    VM_FRIENDLY_NAME="${VM_FRIENDLY_NAME}-${DATE}.ova"
    VM_UUID=$(echo "${UUID}" | cut -f 2 -d ":")
    VM_SNAPSHOT_NAME="${VM_FRIENDLY_NAME}-${DATE}"
    echo "Friendly name: ${VM_FRIENDLY_NAME} || VM UUID: ${VM_UUID}"
    echo "FORMAT: ${VM_SNAPSHOT_NAME}"
    SNAPSHOT_UUID=$(xe vm-snapshot vm="${VM_UUID}" new-name-label="${VM_SNAPSHOT_NAME}")
    # Oh my god, why are you checking the exit status??!?
    # Because you need the snapshot command gives you the snapshot UUID don't fuck with it
    if [ "$?" == "0" ]
    then
        RESULT="SUCCESS"
    else
        RESULT="FAIL"
    fi
    if "${graylogEnabled}"
    then
        syslog_snapshot "${VM_FRIENDLY_NAME}" "${RESULT}"
    fi
    create_and_delete_template "${SNAPSHOT_UUID}" "${VM_FRIENDLY_NAME}"
done
umount "${BACKUP_PATH}"
exit 0
}

if "${sambaShare}"
then
    if mount -t cifs "${sambaServer}" "${BACKUP_PATH}" -o credentials="${credentialsFile}"
    then
        create_snapshot
    else
        exit 5
    fi
else
    create_snapshot
fi
