# This shell script will install JSON server and configure it to serve the app.json file

IP="<%= server.internalIp %>"

apt update
curl -sL https://deb.nodesource.com/setup_19.x | sudo bash -
apt install -y nodejs

cat <<EOF > /opt/jsonserver/package.json
{
  "name": "test-json-server",
  "version": "1.0.0",
  "description": "",
  "main": "",
  "dependencies": {},
  "scripts": {
    "start": "json-server -H $IP -p 8101 --watch /opt/jsonserver/app.json"
  },
  "author": "",
  "license": "ISC"
}
EOF

npm install -g json-server