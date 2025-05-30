#!/bin/bash

# Скрипт для создания резервной копии базы данных

source .env

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/skudweb_backup_$DATE.sql"

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

echo "📦 Создание резервной копии базы данных..."

# Создание дампа базы данных
docker-compose exec mysql mysqldump \
    -u$MYSQL_USER \
    -p$MYSQL_PASSWORD \
    $MYSQL_DATABASE > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Резервная копия создана: $BACKUP_FILE"
    
    # Сжатие бэкапа
    gzip $BACKUP_FILE
    echo "✅ Бэкап сжат: $BACKUP_FILE.gz"
    
    # Удаление старых бэкапов (старше 7 дней)
    find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
    echo "🧹 Старые бэкапы удалены"
else
    echo "❌ Ошибка при создании резервной копии"
    exit 1
fi