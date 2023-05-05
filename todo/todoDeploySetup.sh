FILE=/etc/systemd/system/todo.service
 
#Move app into place
mv /opt/todo/todo-deployment-appv* /opt/todo/todo
 
#Set permissions
chmod 764 /opt/todo/todo

#Create service file
if ! test -f $FILE;then
cat << EOF > $FILE
[Unit]
Description=todo service
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=/opt/todo/todo -config /opt/todo/config.env

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
fi

#Restart service
systemctl restart todo