SET PATH=D:\Program Files\MySQL\MySQL Server 5.7\bin;%PATH%

plink -ssh root@app.tsingdata.com -pw cdk@9MIU@# "mysqldump --user=root --host=localhost --protocol=tcp --port=3306 --default-character-set=utf8 --skip-triggers -pmarsadmin marsapp" > marsapp.sql

echo "export done"

plink -ssh root@192.168.1.128 -pw tsing123 "mysql --protocol=tcp --host=localhost --user=root --port=3306 --default-character-set=utf8 --comments --database=marsapp -pasiencredit" < marsapp.sql

echo "All done  ^_^"