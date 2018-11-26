#!/usr/bin/env bash
# Opstoolbox Backup Script
# Install in /opt/backups/
# Cron = 15 3 * * * root /opt/backups/backup.sh & > /opt/backups/cron.log 2>&1
source "/opt/backups/.env"
DATE=$(date +%F)
BACKUP_DIR=/opt/backups/"${DATE}"
LOG_FILE="${BACKUP_DIR}/backup.log"
# Don't bail on error
set +e
DIRECTORIES=(
    '/opt/ec2Snapshots'
    '/opt/keys'
    '/opt/patchingAlert'
    '/opt/restartAP'
    '/opt/safebrowse'
    '/opt/zabbixAPIScripts'
    '/etc/zabbix'
    '/etc/firewalld'
    '/etc/selinux'
    '/etc/ansible'
)
check_backup_dir_exists () {
    if [ -d ${BACKUP_DIR} ]
    then
        echo "BACKUP DIRECTORY ALREADY EXISTS"
        echo "==============================="
        read -p "Move existing backup directory to .old? (y/n) " choice
        if [ "$choice" == "y" ]
        then
            mv "${BACKUP_DIR}" "${BACKUP_DIR}.old"
            main
        else
            exit 2
        fi
    else
        main
    fi
}

cleanup_old_backups () {
    find /opt/backups -name "*.tgz" -ctime -1 -exec /usr/local/bin/aws s3 cp {} s3://"${BUCKET}/${FOLDER}/" \;
    echo "Backing up  to S3" >> "${LOG_FILE}"
    echo "" >> "${LOG_FILE}"
    find /opt/backups -name "*.tgz" -ctime +1 -exec rm {} \;
    find /opt/backups -maxdepth 1 -type d -ctime +3 -exec rm -rf {} \;
    find /opt/backups -maxdepth 1 -type d -mtime +3 -exec tar --selinux --xattrs -zcf {}.tgz {} \;
    if [ -f "${BACKUP_DIR}/error" ]
    then
        /opt/backups/backup_alert.py "${BACKUP_DIR}/backup.log"
        exit 1
    else
        exit 0
    fi
}

main () {
    # Make backup directory
    mkdir "${BACKUP_DIR}"
    # Backup directories
    for directory in "${DIRECTORIES[@]}":
    do
        # There's some weirdness with the last item in the array, a colon gets appended to it
        dir_name=$(echo ${directory%:} | cut -f 3 -d '/')
        directory="${directory%:}"
        if cp -r "${directory}" "${BACKUP_DIR}/${dir_name}"
        then
            echo "Backed up ${directory}" >> "${LOG_FILE}"
            echo "" >> "${LOG_FILE}"
        else
            echo "Failed to backup ${directory}" >> "${LOG_FILE}"
            echo "" >> "${LOG_FILE}"
            touch "${BACKUP_DIR}/error"
        fi
    done

    # Backup Zabbix DB
    # DB PW var is in .env
    if mkdir -p "${BACKUP_DIR}/zabbix/db/"
    then
        echo "Created Zabbix DB Backup directory" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
    else
        echo "Failed to create Zabbix DB directory" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
        touch "${BACKUP_DIR}/error"
    fi
    # MySQL user needs SELECT and LOCK TABLES
    ssh -i "${KEY}" -l "${SSH_USER}" elastic "mysqldump -u ${zabbix_backup_user} -p${zabbix_db_pw} zabbix > /tmp/zabbix.sql"
    scp -i "${KEY}" ansible@elastic:/tmp/zabbix.sql ${BACKUP_DIR}/zabbix/db/
    ssh -i "${KEY}" -l "${SSH_USER}" elastic "rm /tmp/zabbix.sql"
    cleanup_old_backups
}
check_backup_dir_exists