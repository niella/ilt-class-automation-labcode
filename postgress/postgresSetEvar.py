import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Global Static Variables
HOST = morpheus["morpheus"]["applianceHost"]
TOKEN = morpheus["morpheus"]["apiAccessToken"]
INSTANCE_ID = morpheus["instance"]["id"]

## Request headers
HTTP_HEADERS = {"Content-Type":"application/json","Accept":"application/json","Authorization": "BEARER " + (TOKEN)}

## Functions
def get_haproxy_ip(var_dump):
    # var_dump contains the morpheus vaiable map
    # local_ip will be the IP of the node the code is currently executing on
    local_ip = var_dump["internalIp"]
    # containers will be an array of the containers contained within the instance
    containers = var_dump["instance"]["containers"]
    # Iterate through each container in the instance
    # Check if container shortname is haproxy and the container internalIP matches the local_ip.
    # If it is the haproxy node and local_ip matches container internalIP, then return the container internalIp and externalPort.
    for container in containers:
        if container["containerTypeShortName"] == "haproxy" and container["internalIp"] == local_ip:
            return {"ip": container["internalIp"], "port": container["externalPort"]}
    
    return False


def set_evar(name, value):
    url = "https://%s/api/instances/%s/envs" % (HOST, INSTANCE_ID)
    jbody = {
      "envs": [
        {
          "name": name,
          "value": value,
          "export": True,
          "masked": False
        }
      ]
    }
    body = json.dumps(jbody)
    
    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding evar: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Evar %s added" % (name))

# First part of if statement checks if we have provisioned the standalone layout by checking the shortname of the node
# If this is true, set DB_IP to IP of server and DB_PORT to 5432
if morpheus["instance"]["containers"][0]["containerTypeShortName"] == "pgStandaloneNode":
    lb_ip = morpheus["instance"]["containers"][0]["internalIp"]
    lb_port = "5432"
    set_evar("DB_IP", lb_ip)
    set_evar("DB_PORT", lb_port)
else:
    # If we are not using the standalone layout, then we must have provisioned the cluster layout.
    # Run the get_haproxy_ip function pulling in the morpheus variable map. 
    # Runs this function for each VM in the instance
    # Output from get_haproxy_ip os the haproxy IP and port
    lb_details = get_haproxy_ip(morpheus)
    if lb_details:
        lb_ip = lb_details["ip"]
        lb_port = lb_details["port"]
        print(lb_ip)
        # Run the set_evar function to create variables on the instance
        set_evar("DB_IP", lb_ip)
        set_evar("DB_PORT", lb_port)
    else:
        print("Not Haproxy node")