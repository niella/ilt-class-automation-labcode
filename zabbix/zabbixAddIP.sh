# This script runs as a Morpheus remote task to update the Zabbix Server /etc/hosts file with the IP and Name of the provisioned VM
set -x
NAME="<%= server.name %>"
IP="<%= server.externalIp %>"
MONITORING="<%= customOptions.enableMonitoring %>"

if [ $MONITORING = on ]
then
	echo "$IP $NAME" >> /etc/hosts
fi