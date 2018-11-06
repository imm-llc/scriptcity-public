#!/usr/bin/env bash
# Opstoolbox Backup Script
# Install in /opt/backups/
# Cron = 15 3 * * * root /opt/backups/backup.sh & > /opt/backups/cron.log 2>&1
source "/opt/backups.env"
DATE=$(date +%F)
BACKUP_DIR=/opt/backups/"${DATE}"
LOG_FILE="${BACKUP_DIR}/backup.log"
# Don't bail on error, we want to alert if there's an error
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
            cleanup_old_backups
        else
            exit 2
        fi
    else
        cleanup_old_backups
    fi
}

cleanup_old_backups () {
    for item in $(find /opt/backups -name "*.gz" -ctime +5)
    do
        # You need to run `aws configure` first
        aws s3 cp s3://"${BUCKET}/${FOLDER}/${item}"
        echo "Backing up ${item} to S3" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
        rm -f $item
        echo "Removed ${item}" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
    done
    for item in $(find /opt/backups -maxdepth 1 -type d -mtime +3)
    do
        echo "Zipping ${item}" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
        tar -zcf ${item}.tgz $item
    done
    main
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
    if mysqldump -u zabbix -p"${zabbix_db_pw}" zabbix > "${BACKUP_DIR}/zabbix/db/db.sql"
    then
        echo "Successfully backed up Zabbix DB" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
    else
        echo "Failed to backup Zabbix DB" >> "${LOG_FILE}"
        echo "" >> "${LOG_FILE}"
        touch "${BACKUP_DIR}/error"
    fi

    if [ -f "${BACKUP_DIR}/error" ]
    then
        /opt/backups/backup_alert.py "${BACKUP_DIR}/backup.log"
        exit 1
    else
        exit 0
    fi
}
check_backup_dir_exists
