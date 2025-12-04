#!/bin/bash

number=3
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

delfile_sql=$(ls -t $backup_dir/*.sql.gz 2>/dev/null | tail -1)
count_sql=$(ls -1 $backup_dir/*.sql.gz 2>/dev/null | wc -l)

if [ $count_sql -gt $number ]
then
  rm $delfile_sql
  echo "delete $delfile_sql" >> ./logs/log.txt
fi

delfile_csv=$(ls -t $backup_dir/*.csv 2>/dev/null | tail -1)
count_csv=$(ls -1 $backup_dir/*.csv 2>/dev/null | wc -l)

if [ $count_csv -gt $number ]
then
  rm $delfile_csv
  echo "delete $delfile_csv" >> ./logs/log.txt
fi