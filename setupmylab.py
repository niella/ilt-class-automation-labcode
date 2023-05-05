import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Global Static Variables
HOST = morpheus["morpheus"]["applianceHost"]
INTERNAL_HOST = morpheus["customOptions"]["internalHost"]
TOKEN = morpheus["morpheus"]["apiAccessToken"]
AWS_KEY = morpheus["customOptions"]["awsKey"]
AWS_SECRET = morpheus["customOptions"]["awsSecret"]
AWS_VPC = morpheus["customOptions"]["awsVpc"]
AWS_REGION = morpheus["customOptions"]["awsRegion"]
INTERNAL_URL = "https://%s" % (INTERNAL_HOST)
CLOUD_INIT_PASSWORD = "Password123?"
WINDOWS_PASSWORD = "Password123?"

## Variables
AMI_UBUNTU = morpheus["customOptions"]["amiubuntu"]
AMI_CENTOS = morpheus["customOptions"]["amicentos"]

## Request headers
HTTP_HEADERS = {"Content-Type":"application/json","Accept":"application/json","Authorization": "BEARER " + (TOKEN)}
HTTP_UPLOAD_HEADERS = {"Authorization": "BEARER " + (TOKEN)}



## Functions
def update_provisioning_setting(setting_name, setting_value):

    url = "https://%s/api/provisioning-settings" % (HOST)

    jbody = {}
    jbody["provisioningSettings"] = {}
    jbody["provisioningSettings"][setting_name] = setting_value
    body = json.dumps(jbody)

    response = requests.put(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding provisioning settings: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Global Provisioning Settings %s updated to %s" % (setting_name, setting_value))



def update_log_setting(setting_name, setting_value):

    url = "https://%s/api/log-settings" % (HOST)

    jbody = {}
    jbody["logSettings"] = {}
    jbody["logSettings"][setting_name] = setting_value
    body = json.dumps(jbody)

    response = requests.put(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding log settings: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Log Settings %s updated to %s" % (setting_name, setting_value))



def create_group(name, code):

    url = "https://%s/api/groups" % (HOST)
    jbody = {
      "group": {
        "name": name,
        "code": code
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding group: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Group %s added" % (name))
    group_id = data["group"]["id"]
    return group_id
    


def add_cloud(name, group_id):

    url = "https://%s/api/zones" % (HOST)
    jbody = {
      "zone": {
        "name": name,
        "description": name,
        "groupId": group_id,
        "zoneType": {
          "code": "amazon"
        },
        "config": {
          "certificateProvider": "internal",
          "importExisting": "off",
          "endpoint": AWS_REGION,
          "accessKey": AWS_KEY,
          "secretKey": AWS_SECRET,
          "isVpc": "true",
          "vpc": AWS_VPC,
          "applianceUrl": INTERNAL_URL
        },
        "code": "awsLab",
        "visibility": "private"
      }
    }

    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding cloud: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Cloud %s added" % (name))



def add_naming_policy():
    name = "Instance Name"
    url = "https://%s/api/policies" % (HOST)
    jbody = {
      "policy": {
        "config": {
          "namingType": "user",
          "namingPattern": "${account.take(2).toUpperCase()}-${platform == 'windows' ? 'w':'l'.toUpperCase()}-${sequence+1000}",
          "namingConflict": "on"
        },
        "policyType": {
          "code": "naming"
        },
        "name": name,
        "enabled": "on"
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding naming policy: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Naming policy %s added" % (name))



def get_repo_id_by_name(repo_name):
    url = "https://%s/api/options/codeRepositories" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting repo '%s': Response code %s: %s" % (repo_name, response.status_code, response.text))

    data = response.json()

    for repo in data["data"]:
        if repo_name in repo["name"]:
            return repo["value"]

    raise Exception("Searched %s repos. Repo '%s' not found..." % (len(data["data"]), repo_name))



def create_credential(name, password):
    url = "https://%s/api/credentials" % (HOST)
    jbody = {
      "credential": {
        "type": "username-password",
        "integration": {
        },
        "name": name,
        "enabled": True,
        "username": "morpheusci",
        "password": password
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding credential: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Credential %s added" % (name))
    cred_id = data["credential"]["id"]
    return cred_id



def get_cred_id_by_name(cred_name):
    url = "https://%s/api/credentials" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting credential '%s': Response code %s: %s" % (cred_name, response.status_code, response.text))

    data = response.json()

    for cred in data["credentials"]:
        if cred["name"] == cred_name:
            return cred["id"]

    raise Exception("Searched %s creds. Cred '%s' not found..." % (len(data["data"]), cred_name))



def add_task(name, code, id, script_code, sudo, source_type, repo_id, content_path, execute_target):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "resultType": "value",
        "taskType": {
          "id": id,
          "code": script_code
        },
        "taskOptions": {
          "shell.sudo": sudo
        },
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": "master"
        },
        "executeTarget": execute_target,
        "retryable": False,
        "allowCustomConfig": False
      }
    }    
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Task %s added" % (name))
    return data["task"]["id"]



def add_task_remote(name, code, id, script_code, sudo, remote_host, remote_port, source_type, repo_id, content_path, execute_target,cred_id):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": id,
          "code": script_code
        },
        "taskOptions": {
          "shell.sudo": sudo,
          "host": remote_host,
          "port": remote_port
        },
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": "master"
        },
        "executeTarget": execute_target,
        "credential": {
          "id": cred_id
        },
        "retryable": False,
        "allowCustomConfig": False
      }
    }    
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Task %s added" % (name))



def add_python_task(name, code, id, script_code, result_type, source_type, repo_id, content_path, pythonargs, packages):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": id,
          "code": script_code
        },
        "resultType": result_type,
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": "master"
        },
        "taskOptions": {
          "pythonArgs": pythonargs,
          "pythonAdditionalPackages": packages
        },
        "executeTarget": "local",
        "retryable": False,
        "allowCustomConfig": False
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding python task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Python Task %s added" % (name))



def add_library_task(name, code, templateid):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": 3,
          "code": "containerTemplate"
        },
        "resultType": "value",
        "taskOptions": {
          "containerTemplate": templateid
        },
        "executeTarget": "resource",
        "retryable": False,
        "allowCustomConfig": False
      }
    }
    
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding library task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Library task %s added" % (name))
    return data["task"]["id"]



def add_script_template(name, script_type, script_phase, script, runas, sudo):
    url = "https://%s/api/library/container-scripts" % (HOST)
    jbody = {
      "containerScript": {
        "name": name,
        "scriptType": script_type,
        "scriptPhase": script_phase,
        "script": script,
        "runAsUser": runas,
        "sudoUser": sudo
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding script template: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Script template %s added" % (name))



def create_file_template(file_content, phase, name, filename, filepath, fileowner, settingname, settingcategory):

    json_file = open(file_content, mode='r')
    json_content = json_file.read()
    json_file.close()

    url = "https://%s/api/library/container-templates" % (HOST)
    jbody = {
      "containerTemplate": {
        "templatePhase": phase,
        "name": name,
        "fileName": filename,
        "filePath": filepath,
        "template": json_content,
        "fileOwner": fileowner,
        "settingName": settingname,
        "settingCategory": settingcategory
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding template: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Template %s added" % (name))



def add_python_task(name, code, id, script_code, result_type, source_type, repo_id, content_path, pythonargs, packages):
    url = "https://%s/api/tasks" % (HOST)
    jbody = {
      "task": {
        "name": name,
        "code": code,
        "taskType": {
          "id": id,
          "code": script_code
        },
        "resultType": result_type,
        "file": {
          "sourceType": source_type,
          "repository": {
            "id": repo_id
          },
          "contentPath": content_path,
          "contentRef": "master"
        },
        "taskOptions": {
          "pythonArgs": pythonargs,
          "pythonAdditionalPackages": packages
        },
        "executeTarget": "local",
        "retryable": False,
        "allowCustomConfig": False
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding python task: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Python Task %s added" % (name))



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



def create_virtual_image(name, ostype, amiid):
    url = "https://%s/api/virtual-images" % (HOST)
    jbody = {
      "virtualImage": {
        "name": name,
        "osType": ostype,
        "minRamGB": 1,
        "isCloudInit": "on",
        "installAgent": "on",
        "externalId": amiid,
        "virtioSupported": "off",
        "vmToolsInstalled": "off",
        "isForceCustomization": "off",
        "trialVersion": "off",
        "isSysprep": "off",
        "isAutoJoinDomain": "off",
        "visibility": "private",
        "imageType": "ami"
      }
    }
  
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error creating virtual image: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Virtual Image %s added" % (name))



def get_vi_id_by_name(vi_name):
    url = "https://%s/api/virtual-images" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting virtual image '%s': Response code %s: %s" % (vi_name, response.status_code, response.text))

    data = response.json()

    for vi in data["virtualImages"]:
        if vi["name"] == vi_name:
            return vi["id"]

    raise Exception("Searched %s virtual images. Virtual image '%s' not found..." % (len(data["credentials"]), vi_name))



def create_node_type(name, shortname, version, viid):
    url = "https://%s/api/library/container-types" % (HOST)
    jbody = {
      "containerType": {
        "name": name,
        "shortName": shortname,
        "containerVersion": version,
        "provisionTypeCode": "amazon",
        "virtualImageId": viid,
        "statTypeCode": "amazon",
        "logTypeCode": "amazon",
        "serverType": "vm",
        "config": {
        }
      },
      "instanceType": {
        "backupType": "amazonSnapshot",
        "viewSet": "amazonCustom"
      }
    }
  
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error creating node type: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Node Type %s added" % (name))



def get_node_type_id_name(ct_name):
    url = "https://%s/api/library/container-types" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting node type '%s': Response code %s: %s" % (ct_name, response.status_code, response.text))

    data = response.json()

    for ct in data["containerTypes"]:
        if ct["name"] == ct_name:
            return ct["id"]

    raise Exception("Searched %s container types. Container type '%s' not found..." % (len(data["credentials"]), ct_name))



def create_instance_type(name, code):
    url = "https://%s/api/library" % (HOST)
    jbody = {
      "instanceType": {
        "name": name,
        "code": code,
        "category": "os",
        "visibility": "private"
      }
    }
  
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error creating instance type: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Instance Type %s added" % (name))



def get_instance_type_id_name(it_name):
    url = "https://%s/api/library" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting instance type '%s': Response code %s: %s" % (it_name, response.status_code, response.text))

    data = response.json()

    for it in data["instanceTypes"]:
        if it["name"] == it_name:
            return it["id"]

    raise Exception("Searched %s instances. Instance type '%s' not found..." % (len(data["instances"]), it_name))



def add_instance_logo(instance_id, name):
    url = "https://%s/api/library/instance-types/%s/update-logo" % (HOST, instance_id)
    files = {'logo': open(name, "rb")}

    response = requests.put(url, headers=HTTP_UPLOAD_HEADERS, files=files, verify=False)

    if not response.ok:
        print("Error adding logo: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    print("Logo %s added" % (name))



def create_layout(name, instance_id, container_id, workflow_id):
    url = "https://%s/api/library/%s/layouts" % (HOST, instance_id)
    jbody = {
      "instanceTypeLayout": {
        "name": name,
        "instanceVersion": "Latest",
        "creatable": True,
        "provisionTypeCode": "amazon",
        "memoryRequirement": "1024",
        "taskSetId": workflow_id,
        "optionTypes": [
    
        ],
        "containerTypes": [
          container_id
        ],
        "specTemplates": [
    
        ],
        "permissions": {
        }
      }
    }
  
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error creating layout: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")
    data = response.json()
    print("Layout %s added" % (name))



def get_file_template_id_name(file_template_name):
    url = "https://%s/api/library/container-templates" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting file template '%s': Response code %s: %s" % (file_template_name, response.status_code, response.text))

    data = response.json()

    for ft in data["containerTemplates"]:
        if ft["name"] == file_template_name:
            return ft["id"]

    raise Exception("Searched %s file templates. FIle template '%s' not found..." % (len(data["containerTemplates"]), file_template_name))



def get_workflow_id_by_name(workflow_name):
    url = "https://%s/api/task-sets" % (HOST)

    response = requests.get(url, headers=HTTP_HEADERS, verify=False)
    if not response.ok:
        raise Exception("Error getting workflow '%s': Response code %s: %s" % (workflow_name, response.status_code, response.text))

    data = response.json()

    for workflow in data["taskSets"]:
        if workflow["name"] == workflow_name:
            return workflow["id"]

    return 0



def add_workflow(workflow_name, taskid1, taskid2, phase):
    workflow_id = get_workflow_id_by_name(workflow_name)
    if workflow_id:
      print("Found existing workflow '%s', with workflow id %s..." % (workflow_name, workflow_id))
      return workflow_id

    url = "https://%s/api/task-sets" % (HOST)
    jbody = {
      "taskSet": {
        "name": workflow_name,
        "type": "provision",
        "tasks": [
          {
            "taskId": taskid1,
            "taskPhase": phase
          },
          {
            "taskId": taskid2,
            "taskPhase": phase
          }
        ]
      }
    }
    body = json.dumps(jbody)

    response = requests.post(url, headers=HTTP_HEADERS, data=body, verify=False)
    if not response.ok:
        print("Error adding workflow: Response code %s: %s" % (response.status_code, response.text))
        raise Exception("Request error occured")

    data = response.json()
    print("Workflow '%s' added" % (workflow_name))

    return data["taskSet"]["id"]



## Main
## Provisioning Settings
update_provisioning_setting("showPricing", True)
update_provisioning_setting("cloudInitUserName", "morpheusci")
update_provisioning_setting("cloudInitPassword", CLOUD_INIT_PASSWORD)
update_provisioning_setting("windowsPassword", WINDOWS_PASSWORD)

## Log Settings
update_log_setting("enabled", True)

## Create group and cloud
group_id = create_group("All Clouds", "allClouds")
add_cloud("AWS Lab", group_id)

## Create Virtual Images
create_virtual_image("AWS CentOS 7", "35", AMI_CENTOS)
create_virtual_image("AWS Ubuntu 20.04", "16", AMI_UBUNTU)
ubuntuvi = get_vi_id_by_name("AWS Ubuntu 20.04")

## Create Custom Ubuntu Instance
create_node_type("Custom Ubuntu 20.04 node","custUb2004node","20.04",ubuntuvi)
ubuntu_node_id = get_node_type_id_name("Custom Ubuntu 20.04 node")
create_instance_type("Custom Ubuntu", "customUbuntu")
instance_type_id = get_instance_type_id_name("Custom Ubuntu")
add_instance_logo(instance_type_id, "/ubuntu_logo.jpg")
create_layout("Custom Ubuntu Layout", instance_type_id, ubuntu_node_id, "")

## Create policies
add_naming_policy()

## Get Git repo id
## repo_id = get_repo_id_by_name("ilt-class-automation-labcode - Automation Class")
repo_id = get_repo_id_by_name("ilt-class-automation-labcode")

## Module 3 - Add task to dump variables
add_python_task("Dump Variables", "dumpVar", "12", "jythonTask", "value", "repository", repo_id, "dumpVariables.py", "", "")

## Module 3 - Create DBVAR Instance
create_instance_type("DBVAR", "dbVar")
instance_type_id = get_instance_type_id_name("DBVAR")
create_layout("DBVAR Layout", instance_type_id, ubuntu_node_id, "")

## Module 3 - Create APPVAR Instance
create_instance_type("APPVAR", "appVar")
instance_type_id = get_instance_type_id_name("APPVAR")
create_layout("APPVAR Layout", instance_type_id, ubuntu_node_id, "")

## Module 7 - Create Cyphers
create_cypher_secret("mariaDBRootPass", "0", "Password123?")
create_cypher_secret("zDBPass", "0", "Password123?")
create_cypher_secret("zAdminPass", "0", "zabbix")
create_cypher_secret("zAPIPass", "0", "Password123?")

## Module 7 - Create File Templates
create_file_template("zabbix/zabbix_frontend_config_aio", "preProvision", "Zabbix Frontend Config - AIO", "zabbix.conf.php", "/etc/zabbix/web", "www-data", "zabbix_fe_conf_aio", "Web")
#zabbix_fe_config_aio_file_template_id = get_file_template_id_name("Zabbix Frontend Config - AIO")
#add_library_task("Zabbix FE Config - AIO", "zabbixFEConfigAIO", zabbix_fe_config_aio_file_template_id)

## Module 7 - Create Tasks
add_task("Zabbix Install - AIO", "zabbixInstallAIO", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAIOInstall.sh", "resource")
add_task("Zabbix Set Permissions - AIO", "zabbixSetPermAIO", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAIOSetPerms.sh", "resource")
add_python_task("Zabbix Create API User", "zabbixCreateAPIUser", "12", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixCreateAPIUser.py", "<%= cypher.read('secret/zAdminPass',true) %> <%= cypher.read('secret/zAPIPass',true) %>", "requests")
add_task("Zabbix Get Server IP", "zabbixServerIP", "1", "script", "", "repository", repo_id, "/zabbix/zabbixGetServerIP.sh", "resource")
add_python_task("Zabbix Create Cypher Server IP", "zabbixCreateCypherServerIP", "12", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixCreateCypherServerIP.py", "", "requests")
add_python_task("Zabbix Delete Cypher Server IP", "zabbixDeleteCypherServerIP", "12", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixDeleteCypherServerIP.py", "", "requests")

## Create credential for remote tasks
create_credential("morpheusci", "Password123?")
cred_id = get_cred_id_by_name("morpheusci")

## Add tasks and templates for Zabbix Agent Install
add_task("Zabbix Agent Install", "zabbixAgentInstall", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAgentInstall.sh", "resource")
create_file_template("zabbix/zabbix_agentd.conf", "provision", "Zabbix Agent File", "zabbix_agentd.conf", "/etc/zabbix", "root", "zabbixagent", "Agent")
zabbix_agent_file_template_id = get_file_template_id_name("Zabbix Agent File")
add_library_task("Zabbix Agent File", "zabbixAgentFile", zabbix_agent_file_template_id)
add_task("Zabbix Agent Restart", "zabbixAgentRestart", "1", "script", "on", "repository", repo_id, "/zabbix/zabbixAgentRestart.sh", "resource")

## Add tasks for Zabbix Monitoring Workflow
add_task_remote("Zabbix Add IP", "zabbixAddIP", "1", "script", "on", "107.21.198.117", "22", "repository", repo_id, "/zabbix/zabbixAddIP.sh", "remote", cred_id)
add_python_task("Zabbix Get API Token", "zabbixAPIToken", "12", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixGetAPIToken.py", "<%= cypher.read('secret/zServerIP',true) %> <%= cypher.read('secret/zAPIPass',true) %>", "requests")
add_python_task("Zabbix Add Host", "zabbixAddHost", "12", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixAddHost.py", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Release API", "zabbixRelAPI", "12", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixReleaseAPI.py", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Get Host", "zabbixGetHost", "12", "jythonTask", "value", "repository", repo_id, "/zabbix/zabbixGetHost.py", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Remove Host", "zabbixRemoveHost", "12", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixRemoveHost.py", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_task_remote("Zabbix Remove IP", "zabbixRemoveIP", "1", "script", "on", "107.21.198.117", "22", "repository", repo_id, "/zabbix/zabbixRemoveIP.sh", "remote", cred_id)
add_python_task("Zabbix Disable Host", "zabbixDisableHost", "12", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixDisableHost.py", "<%= cypher.read('secret/zServerIP',true) %>", "requests")
add_python_task("Zabbix Enable Host", "zabbixEnableHost", "12", "jythonTask", "", "repository", repo_id, "/zabbix/zabbixEnableHost.py", "<%= cypher.read('secret/zServerIP',true) %>", "requests")

## Create Zabbix File Templates
create_file_template("zabbix/zabbix_frontend_config_clustered", "preProvision", "Zabbix Frontend Config - Clustered", "zabbix.conf.php", "/tmp/zabbix", "root", "zabbix_fe_conf_ha", "Web")
create_file_template("zabbix/zabbix_server_config_clustered", "preProvision", "Zabbix Server Config - Clustered", "zabbix_server.conf", "/tmp/zabbix", "root", "zabbixconfclustered", "App")

##Postgres Standalone
create_cypher_secret("postgres", "0", "Password123?")
add_script_template("postgres install standalone", "bash", "provision", "PGPass=\"<%=cypher.read('secret/postgres')%>\"\napt update\napt install -y postgresql postgresql-client\nsystemctl stop postgresql.service\nsystemctl start postgresql.service\nsystemctl enable postgresql.service\n\necho \"listen_addresses = '*'\" >> /etc/postgresql/12/main/postgresql.conf\necho \"host  all  all 0.0.0.0/0 md5\" >> /etc/postgresql/12/main/pg_hba.conf\n\nsystemctl restart postgresql.service\n\nsudo -u postgres psql template1 -c \"CREATE USER admin WITH SUPERUSER PASSWORD '$PGPass';\"", "", "on")

##Postgres Cluster Script Templates
add_script_template("etcd install centos", "bash", "preProvision", "#Disable selinux\nsetenforce 0\n#Update all packages with available update\nyum -y update --skip-broken\n#Install etcd\nyum -y install etcd\n#Make a copy of original config file\ncp -p /etc/etcd/etcd.conf /etc/etcd/etcd.conf.orig", "", "on")
add_script_template("etcd setup centos", "bash", "provision", "#Copy the file template etcd.conf into place and set ownership and permissions\ncp /tmp/patroni/etcd.conf /etc/etcd/etcd.conf\nchown root:root /etc/etcd/etcd.conf\nchmod 644 /etc/etcd/etcd.conf\n#Start etcd and enable on boot\nsystemctl enable etcd\nsystemctl start etcd", "", "on")
add_script_template("postgres install centos", "bash", "preProvision", "#Disable selinux\nsetenforce 0\n#Update all packages with available update\nyum -y update --skip-broken\n#Install the extra packages for linux repo\nyum -y install epel-release\n#Install the required software for postgres and patroni\nyum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm\nyum -y install centos-release-scl\nyum -y install postgresql12-server postgresql12 postgresql12-devel\nyum -y install https://github.com/cybertec-postgresql/patroni-packaging/releases/download/1.6.0-1/patroni-1.6.0-1.rhel7.x86_64.rpm", "", "on")
add_script_template("postgres setup centos", "bash", "provision", "HOSTNAME=`hostname`\n#Copy the file template postgresql.yml into place and set ownership and permissions\ncp /tmp/patroni/postgresql.yml /opt/app/patroni/etc/postgresql.yml\nchown postgres:postgres /opt/app/patroni/etc/postgresql.yml\nchmod 600 /opt/app/patroni/etc/postgresql.yml\n\n\nsed -i '/pg_cluster\\// a name:\\ '\"$HOSTNAME\"'' /opt/app/patroni/etc/postgresql.yml\n\n#Get the IP address of the etcd instance\necho \"<%= instance.containers.findAll{it.containerTypeShortName == 'etcd'}.collect{it.externalIp}.join(',') %>\" > /tmp/etcdip\n#Get the IP address of the postgres instances\necho \"<%= instance.containers.findAll{it.containerTypeShortName == 'postgres'}.collect{it.externalIp}.join(',') %>\" > /tmp/postgresip\n\n#Add etcd instance IP to postgresql.yml file\nETCDIP=`cat /tmp/etcdip`\nsed -i 's/ETCDIP:2379/'\"$ETCDIP\"':2379/' /opt/app/patroni/etc/postgresql.yml\n\n#Remove comma from postgres instance IPs\nPOSTGRESIP=`cat /tmp/postgresip | sed 's/,/ /'`\n\n#Add postgres IPs to postgresql.yml file\nfor i in $(echo $POSTGRESIP)\ndo\n    sed -i '/127.0.0.1\\/32 md5/ a \\ \\ -\\ host\\ replication\\ replicator '\"$i\"'\\/0 md5' /opt/app/patroni/etc/postgresql.yml\ndone\n\n#Start patroni and enable on boot\nsystemctl start patroni\nsystemctl enable patroni", "", "on")
add_script_template("haproxy install centos", "bash", "preProvision", "#Disable selinux\nsetenforce 0\n#Update all packages with available update\nyum -y update --skip-broken\n#Install haproxy\nyum -y install haproxy\n#Make a copy of original config file\nmv /etc/haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg.orig", "", "on")
add_script_template("haproxy setup centos", "bash", "provision", "#Copy the file template haproxy.cfg into place and set ownership and permissions\n\ncp /tmp/patroni/haproxy.cfg /etc/haproxy \nchown root:root /etc/haproxy/haproxy.cfg\nchmod 644 /etc/haproxy/haproxy.cfg\n\n#Get the IPs of the postgres nodes\nips=\"<%= instance.containers.findAll{it.containerTypeShortName == 'postgres'}.collect{it.externalIp}.join(',') %>\"\nhostnames=\"<%= instance.containers.findAll{it.containerTypeShortName == 'postgres'}.collect{it.server.name}.join(',') %>\"\nip1=`echo $ips| awk -F ',' {'print $1'}`\nip2=`echo $ips| awk -F ',' {'print $2'}`\nhostname1=`echo $hostnames| awk -F ',' {'print $1'}`\nhostname2=`echo $hostnames| awk -F ',' {'print $2'}`\n\n#Configure the haproxy.cfg file to load balance postgres\nsed -i '/sessions/ a \\ \\ \\ \\ server '\"$hostname1\"' '\"$ip1\"':5432 maxconn 100 check port 8008' /etc/haproxy/haproxy.cfg\nsed -i '/sessions/ a \\ \\ \\ \\ server '\"$hostname2\"' '\"$ip2\"':5432 maxconn 100 check port 8008' /etc/haproxy/haproxy.cfg\n\n#Start haproxy and enable on boot\nsystemctl enable haproxy\nsystemctl start haproxy", "", "on")

##Postgres Cluster File Templates
create_file_template("postgres/etcd.conf", "preProvision", "Etcd Configuration File", "etcd.conf", "/tmp/patroni", "root", "etcdconf", "App")
create_file_template("postgres/postgresql.yml", "preProvision", "Postgres Configuration File", "postgresql.yml", "/tmp/patroni", "root", "postgresconf", "DB")
create_file_template("postgres/haproxy.cfg", "preProvision", "Haproxy Configuration File", "haproxy.cfg", "/tmp/patroni", "root", "haproxyconf", "App")

##Postgres Tasks
add_python_task("Postgres Set Evar", "postgresSetEvar", "12", "jythonTask", "", "repository", repo_id, "/postgres/postgresSetEvar.py", "", "requests")

## Add tasks for ToDo application
add_task("ToDo Setup", "todosetup", "1", "script", "on", "repository", repo_id, "/todo/todoSetup.sh", "resource")
add_task("ToDo Deployment Setup", "tododeploysetup", "1", "script", "on", "repository", repo_id, "/todo/todoDeploySetup.sh", "resource")

## ToDo Script Templates
add_script_template("todo start service", "bash", "start", "systemctl start todo", "", "on")
add_script_template("todo stop service", "bash", "stop", "systemctl stop todo", "", "on")

## Add tasks for Update Wiki
add_python_task("Update Wiki", "updateWiki", "12", "jythonTask", "value", "repository", repo_id, "updateWiki.py", "", "requests")

## JSON Server
create_file_template("option_lists/app.json", "provision", "App JSON", "app.json", "/opt/jsonserver", "root", "appjson", "App")
app_json_template_id = get_file_template_id_name("App JSON")

task_id1 = add_library_task("App JSON", "appJSON", app_json_template_id)
task_id2 = add_task("JSON Server Install", "jsonServerInstall", "1", "script", "on", "repository", repo_id, "/option_lists/json_server_install.sh", "resource")

workflow_id = add_workflow("JSON Server Install", task_id1, task_id2, "provision")

create_node_type("JSON server node","jsonServernode","Latest",ubuntuvi)
ubuntu_node_id = get_node_type_id_name("JSON server node")
create_instance_type("JSON Server", "jsonServer")
instance_type_id = get_instance_type_id_name("JSON Server")
add_instance_logo(instance_type_id, "/JSONImage.png")

create_layout("JSON Server Layout", instance_type_id, ubuntu_node_id, workflow_id)