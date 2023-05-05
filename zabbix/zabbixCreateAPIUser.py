# This script is run during provisioning of a new Zabbix server and will create a Zabbix user called api
import json
import requests
import sys

# Get the API token for authentication
host = morpheus["server"]["externalIp"]

jbody = {
	"jsonrpc": "2.0",
	"method": "user.login",
	"params": {
		"user": "Admin",
		"password": sys.argv[1]
	},
	"id": 1,
	"auth": None
}

body = json.dumps(jbody)

headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
url = "http://%s/zabbix/api_jsonrpc.php" % (host)

response = requests.post(url, headers=headers, data=body, verify=False)
if not response.ok:
    print("Error creating API user: Response code %s: %s" % (response.status_code, response.text))
    raise Exception("Request error occured")

response_json = response.json()

# Create the api user
jbodyuser = {
    "jsonrpc": "2.0",
    "method": "user.create",
    "params": {
        "username": "api",
        "name": "api",
        "passwd": sys.argv[2],
        "roleid": "3",
        "usrgrps": [
            {
                "usrgrpid": "7"
            }
        ]
    },
    "auth": response_json["result"],
    "id": 1
}

bodyuser = json.dumps(jbodyuser)

responseuser = requests.post(url, headers=headers, data=bodyuser, verify=False)
if not responseuser.ok:
    print("Error executing request: Response code %s: %s" % (responseuser.status_code, responseuser.text))
    raise Exception("Request error occured")