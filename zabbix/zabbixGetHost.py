# Gets the Zabbix hostid of the provisioned VM
# Resulting hostid is stored as a single value on the taskCode for use by other Morpheus tasks

monitoring = morpheus["customOptions"]["enableMonitoring"]

if monitoring == "on":
    import json
    import requests
    import sys

    #host = morpheus["customOptions"]["zabbixServer"]
    host = sys.argv[1]

    jbody = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": "extend",
            "filter": {
                "host": [morpheus["server"]["name"]]
            }
        },
        "auth": morpheus["results"]["zabbixAPIToken"],
        "id": 1
    }

    body = json.dumps(jbody)

    headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
    url = "http://%s/zabbix/api_jsonrpc.php" % (host)

    response = requests.post(url, headers=headers, data=body, verify=False)
    if not response.ok:
        print("Error getting host details: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    response_json = response.json()
    print(response_json["result"][0]["hostid"], end="")