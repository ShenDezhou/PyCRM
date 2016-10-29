#!/bin/bash
ssh root@app.tsingdata.com "mysqldump --user=root --host=localhost --protocol=tcp --port=3306 --default-character-set=utf8 --skip-triggers -pmarsadmin marsapp" > marsapp.sql

echo "export done"

mysql --protocol=tcp --host=localhost --user=root --port=3306 --default-character-set=utf8 --comments --database=marsapp -pasiencredit < marsapp.sql

echo "All done  ^_^"