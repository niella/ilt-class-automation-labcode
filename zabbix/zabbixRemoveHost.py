monitoring = morpheus["customOptions"]["enableMonitoring"]

if monitoring == "on":
    import json
    import requests
    import sys

    #host = morpheus["customOptions"]["zabbixServer"]
    host = sys.argv[1]

    jbody = {
        "jsonrpc": "2.0",
        "method": "host.delete",
        "params": [
            morpheus["results"]["zabbixGetHost"]
        ],
        "auth": morpheus["results"]["zabbixAPIToken"],
        "id": 2
    }

    body = json.dumps(jbody)

    headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
    url = "http://%s/zabbix/api_jsonrpc.php" % (host)

    response = requests.post(url, headers=headers, data=body, verify=False)
    if not response.ok:
        print("Error removing host: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    print("Host removed: Response code %s: %s" % (response.status_code, response.text))