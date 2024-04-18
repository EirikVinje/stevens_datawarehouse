#!/bin/bash -e

echo "Sudo password:"

read -s password

echo ""
echo "Initializing databases mongo, neo4j and sql..."

cd dw
echo $password | sudo -S docker-compose up -d
sleep 10
cd ..


dbpass="secret"
dbuser="dbuser"

sudo docker exec -it dw_mysql-odb-server_1 bash -c "mysql -P15000 -p${dbpass} -e \"CREATE USER '$dbuser'@'%' IDENTIFIED BY 'secret';\"; exit;"
sudo docker exec -it dw_mysql-odb-server_1 bash -c "mysql -P15000 -p${dbpass} -e \"GRANT ALL PRIVILEGES ON odb.* to '$dbuser'@'%';\"; exit;"

sudo docker exec -it dw_mysql-dw-server_1 bash -c "mysql -P25000 -p${dbpass} -e \"CREATE USER '$dbuser'@'%' IDENTIFIED BY 'secret';\"; exit;"
sudo docker exec -it dw_mysql-dw-server_1 bash -c "mysql -P25000 -p${dbpass} -e \"GRANT ALL PRIVILEGES ON dw.* to '$dbuser'@'%';\"; exit;"

echo "Created MySQL users"


echo ""
echo "Initializing databases"
python dw/init_neo4j.py all
python dw/init_mongodb.py 
python dw/init_sql.py

echo "Done!"