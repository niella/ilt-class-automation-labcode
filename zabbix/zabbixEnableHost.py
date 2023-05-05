# Enables monitoring for a host in Zabbix

monitoring = morpheus["customOptions"]["enableMonitoring"]

if monitoring == "on":
    import json
    import requests
    import sys

    #host = morpheus["customOptions"]["zabbixServer"]
    host = sys.argv[1]

    jbody = {
        "jsonrpc": "2.0",
        "method": "host.update",
        "params": {
            "hostid": morpheus["results"]["zabbixGetHost"],
            "status": 0
        },
        "auth": morpheus["results"]["zabbixAPIToken"],
        "id": 1
    }

    body = json.dumps(jbody)

    headers = {"Content-Type": "application/json-rpc", "Accept": "*/*"}
    url = "http://%s/zabbix/api_jsonrpc.php" % (host)

    response = requests.post(url, headers=headers, data=body, verify=False)
    if not response.ok:
        print("Error enabling host: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    print("Host enabled: Response code %s: %s" % (response.status_code, response.text))