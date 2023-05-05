import requests
import datetime

host=morpheus['morpheus']['applianceHost']
token=morpheus['morpheus']['apiAccessToken']
instanceid=morpheus['instance']['id']
user=morpheus['instance']['createdByUsername']
dept=morpheus['customOptions']['department']
app=morpheus['customOptions']['application']
servown=morpheus['customOptions']['serviceOwner']
date_object=datetime.date.today()

jbody={"page": {"content": "**Instance Details**\r\n\r\nProvisioned by: %s \r\nDate of provision: %s \r\nDepartment: %s \r\nApplication: %s \r\nService Owner: %s" % (user,date_object,dept,app,servown)} } 
body=json.dumps(jbody)
headers = {"Content-Type":"application/json","Accept":"application/json","Authorization": "BEARER " + (token)}
apiUrl = 'https://%s/api/instances/%d/wiki' % (host, instanceid)
url=str(apiUrl)

#API request to update the Wiki page
r = requests.put(url, headers=headers, data=body, verify=False)

#Returns success code
print(r)