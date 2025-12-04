#!/bin/bash

number=180
backup_dir=/var/logs/mysql_backups
dd=$(date +%Y%m%d)
tool=mysqldump
username=root
password=root
database_name=env_db
container_name=kmu-ems-mysql

mkdir -p $backup_dir

docker exec $container_name $tool -u $username -p$password --single-transaction --routines --triggers --databases $database_name | gzip > $backup_dir/$database_name-$dd.sql.gz

echo "create $backup_dir/$database_name-$dd.sql.gz" >> ./logs/log.txt

docker exec $container_name mysql -u $username -p$password --database=$database_name --execute="SELECT * FROM kmu_ems_data ORDER BY timestamp;" --batch --raw --silent | sed 's/\t/,/g' > $backup_dir/$database_name-$dd.csv

echo "create $backup_dir/$database_name-$dd.csv" >> ./logs/log.txt

# Delete SQL backups older than 180 days
find $backup_dir -name "*.sql.gz" -type f -mtime +$number -exec rm {} \; -exec echo "delete {}" >> ./logs/log.txt \;

# Delete CSV backups older than 180 days  
find $backup_dir -name "*.csv" -type f -mtime +$number -exec rm {} \; -exec echo "delete {}" >> ./logs/log.txt \;