# Uses the Zabbix user.logout method to log out of the API and invalidates the current authentication token
# Prevents the generation of a large number of open session records in the sessions table

import json
import requests
import sys

#host = morpheus["customOptions"]["zabbixServer"]
host = sys.argv[1]

jbody = {
    "jsonrpc": "2.0",
    "method": "user.logout",
    "params": {},
    "id": 1,
    "auth": morpheus["results"]["zabbixAPIToken"]
}
body = json.dumps(jbody)

headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
url = "http://%s/zabbix/api_jsonrpc.php" % (host)

response = requests.post(url, headers=headers, data=body, verify=False)
if not response.ok:
    print("Error executing request: Response code %s: %s" % (response.status_code, response.text))
    raise Exception("Request error occured")

response_json = response.json()
print(response_json["result"], end="")