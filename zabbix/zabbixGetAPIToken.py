# Uses the Zabbix user.login method to log in to the API and generate an authentication token
# Resulting token is stored as a single value on the taskCode for use by other Morpheus tasks

import json
import requests
import sys

# Uses hidden input to declare the Zabbix Server IP address
#host = morpheus["customOptions"]["zabbixServer"]

# Uses cypher to declare the Zabbix Server IP address
host = sys.argv[1]

# sys.argv is used to pull in the 1st command argument which is defined under COMMAND ARGUMENTS in the Morpheus task
# In JSON, auth is set to null, but as jbody is declared as a dictionary, you cannot have null. Use the python equivalent which is None
# json.dumps converts the dictionary to a JSON string and will set it back to null
jbody = {
	"jsonrpc": "2.0",
	"method": "user.login",
	"params": {
		"user": "api",
		"password": sys.argv[2]
	},
	"id": 1,
	"auth": None
}
body = json.dumps(jbody)

headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
url = "http://%s/zabbix/api_jsonrpc.php" % (host)

response = requests.post(url, headers=headers, data=body, verify=False)
if not response.ok:
    print("Error executing request: Response code %s: %s" % (response.status_code, response.text))
    raise Exception("Request error occured")

# Printing the result gives us the token. Added end="" to force python not to print a newline 
response_json = response.json()
print(response_json["result"], end="")