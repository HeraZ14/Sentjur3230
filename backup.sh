#!/bin/bash
# Avtomatski Django DB backup za Sentjur3230

PROJECT_DIR="/home/sentmet/Sentjur3230"  # Tvoja pot (preveri z pwd, če ni točna)
VENV_DIR="$PROJECT_DIR/virtualenv/Sentjur3230/3.11"  # Iz tvojega terminala
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_DIR="$PROJECT_DIR/logs"
DATE=$(date +%Y-%m-%d_%H-%M-%S)  # Datum/čas za ime

# Ustvari mape
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"

# Zaženi backup
python manage.py dbbackup -O "$BACKUP_DIR/db_$DATE.backup" -z

# Preveri in logiraj
if [ $? -eq 0 ]; then
    echo "$DATE: Backup uspešen (datoteka: db_$DATE.backup)" >> "$LOG_DIR/backup.log"
else
    echo "$DATE: Backup failal!" >> "$LOG_DIR/backup.log"
fi