# Add the Zabbix repo
cd /tmp
file_url_zabbix="<%= archives.link('Automation Training Archive', 'zabbix-release_6.2-1 ubuntu20.04_all.deb', 1200) %>"
wget $file_url_zabbix -O "./zabbix-release_6.2-1 ubuntu20.04_all.deb" --no-check-certificate
dpkg -i zabbix-release_6.2-1\ ubuntu20.04_all.deb
apt update

# Install Zabbix Agent
apt -y install zabbix-agent