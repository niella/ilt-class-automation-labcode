import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Global Static Variables
HOST = morpheus["morpheus"]["applianceHost"]
TOKEN = morpheus["morpheus"]["apiAccessToken"]
ZABSERVERIP = morpheus["results"]["zabbixServerIP"]

## Request headers
HTTP_HEADERS = {"Content-Type":"application/json","Accept":"application/json","Authorization": "BEARER " + (TOKEN)}



## Functions
def create_cypher_secret(key, ttl, value):
    url = "https://%s/api/cypher/v1/secret/%s?type=string&ttl=%s" % (HOST, key, ttl)
    jbody = {
      "value": value
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding cypher: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Cypher %s added" % (key))
    

## Main
create_cypher_secret("zServerIP", "0", ZABSERVERIP)