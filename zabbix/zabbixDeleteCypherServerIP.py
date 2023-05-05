import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Global Static Variables
HOST = morpheus["morpheus"]["applianceHost"]
TOKEN = morpheus["morpheus"]["apiAccessToken"]

## Request headers
HTTP_HEADERS = {"Content-Type":"application/json","Accept":"application/json","Authorization": "BEARER " + (TOKEN)}

url = "https://%s/api/cypher/v1/secret/zServerIP" % (HOST)
response = requests.delete(url, headers=HTTP_HEADERS, verify=False)

if not response.ok:
    print("Error deleteing cypher: Response code %s: %s" % (response.status_code, response.text))
    raise Exception("Request error occured")
data = response.json()
print("Cypher deleted")