# Add Morpheus DB IP to mysql.env dile

APPLIANCEIP=<%=customOptions.appIP%>
sed -i 's/MORPHDBIP/'"$APPLIANCEIP"'/' /opt/dozer/mysql.env

# Set execute permission on dozer
chmod 764 /opt/dozer/dozer

# Create systemd service file
cat <<EOF >> /etc/systemd/system/dozer.service
[Unit]
Description=dozer service
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=/opt/dozer/dozer

[Install]
WantedBy=multi-user.target
EOF