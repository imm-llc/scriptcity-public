#!/usr/bin/env bash
source /export/home/nz/.bash_profile

# Set dateformat to Year-Month-Day
DATE=$(date +%F)

# Set backup directory
BACKUP_DIR="/mnt/nzbkup/nz/${DATE}"

# Set log directory
LOG_FILE="${BACKUP_DIR}/backup.log"

# Make backup directory 
mkdir "${BACKUP_DIR}"

NZ_USER=admin        # Default NZ username
NZ_DATABASE=system   # Default NZ database
NZ_HOST=immnz01

for DB in $@
do
  echo "" >> "${LOG_FILE}"
  echo "STARTED BACKING UP $DB AT $(date)" >> "${LOG_FILE}"
  echo "" >> "${LOG_FILE}"
  START_TIME=$(date +%s)
  /nz/kit/bin/nzbackup -v -dir ${BACKUP_DIR} -db $DB
  END_TIME=$(date +%s)
  echo "FINISHED BACKING UP ${DB} :: TOOK $(expr $END_TIME - $START_TIME) seconds" >> "${LOG_FILE}"
done
curl -X POST http://slack.imm.corp/api/v1/alert -d '{"channel": "#alerts", "icon": ":dancing_penguin:", "message": "Netezza backup complete", "title": "Netezza backup", "username": "NZ Backup", "color": "good"}'