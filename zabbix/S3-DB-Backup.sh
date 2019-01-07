#!/usr/bin/env bash
##################
# Local settings #
##################
DB_USER=""
DB_PASS=""
BACKUP_DIRECTORY="/zabbix-s3"
BACKUP_NAME="zabbix-latest.sql"
FULL_BACKUP="${BACKUP_DIRECTORY}/${BACKUP_NAME}"

###############
# S3 Settings #
###############
BUCKET="zabbix-backups-bucket"
STORAGE_CLASS="STANDARD_IA"
########################
# Storage class options:
# STANDARD | REDUCED_REDUNDANCY | STANDARD_IA | ONEZONE_IA | INTELLIGENT_TIERING | GLACIER
# Default is STANDARD
########################
PROFILE="zabbix-s3"
#########################
# AWS Profile to use ^^ #
#########################

##########

mysqldump -u "${DB_USER}" -p"${DB_PASS}" -h localhost zabbix > "${FULL_BACKUP}"

aws s3 mv "${FULL_BACKUP}" s3://"${BUCKET}"/"${BACKUP_NAME}" --storage-class "${STORAGE_CLASS}" --profile "${PROFILE}"