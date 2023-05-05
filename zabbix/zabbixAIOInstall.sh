RPass="<%=cypher.read('secret/mariaDBRootPass')%>"
ZDBPass="<%=cypher.read('secret/zDBPass')%>"

# Add the Zabbix repo
cd /tmp
file_url_zabbix="<%= archives.link('Automation Training Archive', 'zabbix-release_6.2-1 ubuntu20.04_all.deb', 1200) %>"
wget $file_url_zabbix -O "./zabbix-release_6.2-1 ubuntu20.04_all.deb" --no-check-certificate
dpkg -i zabbix-release_6.2-1\ ubuntu20.04_all.deb
apt update

# Install MariaDB
apt install software-properties-common -y
file_url_mariadb="<%= archives.link('Automation Training Archive', 'mariadb_repo_setup', 1200) %>"
wget $file_url_mariadb -O "./mariadb_repo_setup" --no-check-certificate
chmod +x mariadb_repo_setup
./mariadb_repo_setup  --mariadb-server-version="mariadb-10.6"
apt update
apt-get install mariadb-server mariadb-client -y

# Restart MariaDB and enable on boot
systemctl stop mariadb.service
systemctl start mariadb.service
systemctl enable mariadb.service

# The following commands are from the mysql secure installation guidance
mysql -u root -e "UPDATE mysql.user SET Password=PASSWORD('$RPass') WHERE User='root';"
mysql -u root -e "flush privileges"
mysql -u root -p$RPass -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p$RPass -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -p$RPass -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p$RPass -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';"
mysql -u root -p$RPass -e "FLUSH PRIVILEGES;"

# Create the Zabbix database and user
mysql -uroot -p$RPass -e "create database zabbix character set utf8mb4 collate utf8mb4_bin;"
mysql -uroot -p$RPass -e "grant all privileges on zabbix.* to zabbix@localhost identified by '$ZDBPass';"

# Import the initial schema and data
apt -y install zabbix-sql-scripts
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql -uzabbix -p$ZDBPass zabbix

# Install Zabbix software
apt -y install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-agent

# Add the Zabbix DB user password to the server config file
echo "DBPassword=$ZDBPass" >> /etc/zabbix/zabbix_server.conf

systemctl restart zabbix-server zabbix-agent
systemctl enable zabbix-server zabbix-agent
systemctl restart apache2
systemctl enable apache2