# Creates a new host on the Zabbix Server for the provisioned VM

monitoring = morpheus["customOptions"]["enableMonitoring"]

if monitoring == "on":
    import json
    import requests
    import sys

    #host = morpheus["customOptions"]["zabbixServer"]
    host = sys.argv[1]

    # Params in jbody had [] which have been changed to {} to work in python
    jbody = {
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
            "host": morpheus["server"]["name"],
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 0,
                    "ip": "",
                    "dns": morpheus["server"]["name"],
                    "port": "10050"
                }
            ],
            "groups": [
                {
                    "groupid": "2"
                }
            ],
            "templates": [
                {
                    "templateid": "10001"
                }
            ],
            "inventory_mode": -1
        },
        "auth": morpheus["results"]["zabbixAPIToken"],
        "id": 1
    }
    body = json.dumps(jbody)

    headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
    url = "http://%s/zabbix/api_jsonrpc.php" % (host)

    response = requests.post(url, headers=headers, data=body, verify=False)
    if not response.ok:
        print("Error adding host: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    response_json = response.json()
    if "error" in response_json:
        print("Error adding host: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    json.dumps(response.json())
    print("Host added: Response code %s: %s" % (response.status_code, response.text))