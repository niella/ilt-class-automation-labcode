# This script runs as a Morpheus remote task to remove the entry from Zabbix Server /etc/hosts for the monitored VM.
# This is required when the VM is restarted as it will come back with a different IP address, and when the VM is deleted.

IP="<%= server.externalIp %>"

grep $IP /etc/hosts

if [ $? = 0 ]
then
	sed -i '/'$IP'/d' /etc/hosts
fi