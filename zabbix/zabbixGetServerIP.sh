#Echo the zabbix server IP. -n suppresses newline. Without this, IP address will contain %0a at the end and subsequent tasks will fail

echo -n "<%= externalIp%>"