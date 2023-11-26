import requests
import json
import base64
import sys
import paramiko
import time
import subprocess
import yaml
import os
import threading

staging_dir="/opt/rafay"
input_yaml = f"{staging_dir}/input.yaml"
tf_dir_prefix = "tf"   
eksa_vm_dir='/root/eksa/vms'
vm_dir='/root/vm/vms'
valid_operations=["provision", "upgrade", "scale"]
conditions_type_list = ["ClusterInitialized","ClusterBootstrapNodeInitialized","ClusterEKSCTLInstalled","ClusterHardwareCSVCreated","ClusterConfigCreated","ClusterSpecApplied","ClusterControlPlaneReady","ClusterWorkerNodeGroupsReady","ClusterOperatorSpecApplied","ClusterHealthy","ClusterUpgraded"]

# make HTTP request 
def make_request(url, method, headers, data):
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            if data!="":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                response = requests.post(url, headers=headers,  timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)    

        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error while sending request to ", url, "with method", method)
        print(errh.args[0])
        return None
    except requests.exceptions.ReadTimeout as errrt:
        print("Time out while sending request to ", url, "with method", method)
        return None
    except requests.exceptions.ConnectionError as conerr:
        print("Connection Error while sending request to ", url, "with method", method)
        return None
    except requests.exceptions.RequestException as errex:
        print("Exception request while sending request to ", url, "with method", method)
        return None  

# execute remote command
def execute_remote_command(host, port, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote host
        ssh_client.connect(host, port=port, username=username, password=password)

        # Execute the command on the remote host
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Read the output of the command
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

    except paramiko.AuthenticationException:
        print(f"ERROR:: SSH authentication failed to eksa-admin host {host}:{port} username:{username}")
        sys.exit(1)
    except paramiko.SSHException as ssh_exception:
        print(f"ERROR:: SSH error when connecting to eksa-admin host {host}:{port} username:{username} error: {ssh_exception}")
        sys.exit(1)
    finally:
        ssh_client.close()

    return output, error


# copy a file over SSH to the remote host 
def ssh_copy(local_path, remote_path, ssh_host, ssh_port, ssh_username, ssh_password, ssh_private_key_path=None,remote_file_name=None):
    
    transport = paramiko.Transport((ssh_host, ssh_port))

    if ssh_private_key_path:
        private_key = paramiko.RSAKey(filename=ssh_private_key_path)
        transport.connect(username=ssh_username, pkey=private_key)
    else:
        transport.connect(username=ssh_username, password=ssh_password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    print(f"\n[+] Copying {local_path} to {remote_path} on {ssh_host}")

    try:
        local_filename=os.path.basename(local_path)
        if remote_file_name:
            remote_file_path=remote_path+remote_file_name
        else:
            remote_file_path=remote_path+local_filename
        if os.path.isfile(local_path):
            # If file, copy it to the remote host
            sftp.put(local_path, remote_file_path)
        elif os.path.isdir(local_path):
            remote_path=remote_path+local_filename
            # If directory, create it on the remote host recursively
            try:
                sftp.listdir(remote_path)
            except FileNotFoundError:
                sftp.mkdir(remote_path)
            
            for root, dirs, files in os.walk(local_path):
                for dir_name in dirs:
                    local_dir_path = os.path.join(root, dir_name)
                    remote_dir_path = os.path.join(remote_path, os.path.relpath(local_dir_path, local_path))
                    try:
                        sftp.listdir(remote_dir_path)
                    except FileNotFoundError:
                        sftp.mkdir(remote_dir_path)

                for file_name in files:
                    local_file_path = os.path.join(root, file_name)
                    remote_file_path = os.path.join(remote_path, os.path.relpath(local_file_path, local_path))
                    print(f"[+]   Copying {local_file_path} to {remote_file_path} on {ssh_host}")
                    sftp.put(local_file_path, remote_file_path)


    except paramiko.SSHException as e:
        print(f"SSH connection or file transfer failed: {e}")
    finally:
        transport.close()




def exceute_debug_channel_command(rafay_controller_url, headers, project_id, cluster_name, cmd_context, debug_command):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name+'/debug'
    method = 'POST'
    data = {"command": debug_command, "context": cmd_context}
    resp = make_request(url, method, headers, data)
    if resp:
        print(f"   [+] Debug channel command submitted successfully. context:{cmd_context}, command:{debug_command}")
        #print("Response Status Code:", resp.status_code)
        #print("Response JSON:", resp.json())
    else:
        print(f"\n Debug channel command failed. This could be because cluster state has progressed and context is no longer available. context:{cmd_context}, command:{debug_command}")

    return resp

# get project id 
def get_project_id(rafay_controller_url, project_name, headers, seq=1):
    url = rafay_controller_url+'/v1/auth/projects/'
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        #print (resp.json())
        data = resp.json()
        for result in data["results"]:
            if result["name"] == project_name:
                return result["id"]
    
    print(f"\nERROR:: Project id retrieval failed. Exiting... project_name:{project_name}")
    sys.exit(1)

    
# create gateway 
def create_gateway(rafay_controller_url, headers, gw_name, gw_type, gw_description, project_id, seq=1):

    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway'
    method = 'POST'

    data = {
       "metadata": {
           "name": gw_name,
           "description": gw_description
       },
       "spec": {
           "gatewayType": gw_type
       }
    }

    resp = make_request(url, method, headers, data)
    if resp:
        print(f"\n[{seq}.] Gateway creation successful. gw_name:{gw_name}, gw_type:{gw_type}, gw_description:{gw_description}, project_id:{project_id}")
        #print("Response Status Code:", resp.status_code)
        #print("Response JSON:", resp.json())
    else:
        print(f"\nERROR:: Gateway creation failed. Exiting... gw_name:{gw_name}, gw_type:{gw_type}, gw_description:{gw_description}, project_id:{project_id}")
        sys.exit(1)

    return resp

# get gateway  
def get_gateway(rafay_controller_url, headers, gw_name, project_id, seq=1):

    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway/'+gw_name
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        #print (resp.json())
        return resp.json()

    return None

# get gateway setup command 
def get_gateway_setup_cmd(rafay_controller_url, headers, gw_name, project_id, seq=1):

    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway/'+gw_name+'/download'
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        encoded_string = resp.json()['data']
        decoded_bytes = base64.b64decode(encoded_string)
        decoded_string = decoded_bytes.decode('utf-8')
        data_dict = json.loads(decoded_string)
        setup_command = data_dict['setupCommand']
        if setup_command:
            print(f"\n[{seq}.] Gateway setupCommand retrieval successful \n {setup_command}")
            return setup_command
    else:
        print("\nERROR:: Gateway setup command retrieval failed. Exiting ...")
        sys.exit(1)
    
    return None

# execute gateway setup command 
def execute_gateway_setup_cmd(host, port, username, password, setup_command, seq=1):
    print(f"[{seq}.] Gateway setup command execution started ...{setup_command}")
    full_command = f"sudo su -c '{setup_command}'"
    stdout,err = execute_remote_command(host, port, username, password, full_command)
    if err:
        print(f"\nERROR:: Executing gateway setup_command failed. err: {err}")
        sys.exit(1)
    else:
        print(f"\n[{seq}.] Gateway setup command execution successful. stdout: {stdout}")
        return True

# delete gateway 
def delete_gateway(rafay_controller_url , headers, gw_name, project_id, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway/'+gw_name
    method = 'DELETE'

    resp = make_request(url, method, headers, "")
    if resp:
        print(f"\n[{seq}.] Gateway deletion successful. gw_name:{gw_name}, project_id:{project_id}")
    else:
        print(f"\nERROR: Gateway deletion failed. gw_name:{gw_name}, project_id:{project_id}")
        
    return resp

# check gateway infraagent health
def check_gateway_infraagent_status(host, port, username, password, seq=1):

    # Check that the infraagent service is running on admin node 
    shell_command = "systemctl status infraagent.service"
    full_command = f"sudo su -c '{shell_command}'"
    stdout,err = execute_remote_command(host, port, username, password, full_command)
    if err:
        print(f"\nERROR:: Executing command to check gateway infraagent service status failed. err: {err}")
        sys.exit(1)
    else:
        if "active (running)" in stdout:
            print(f"\n[{seq}.] Gateway infraagent service is active and running")
        else:
            print(f"\nnERROR:: Gateway infraagent service is NOT ACTIVE or encountered an error. {stdout}")
            sys.exit(1)
        
# check gateway health
def check_gateway_status(rafay_controller_url, headers, gw_name, project_id, seq=1):
    # Check gateway health status from controller 
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway/'+gw_name+'/health'
    method = 'GET'

    i = 0
    while True:
        resp = make_request(url, method, headers, "")

        if resp:
            gw_health_status = resp.json()['status']
            gw_health_reason = resp.json()['reason']
            # print(f"[{seq}.] Gateway health status:{gw_health_status}, reason:{gw_health_reason}")
            if gw_health_status == 'UNHEALTHY':
                print(f"\n[{seq}.] Gateway status is UNHEALTHY. Reason:{gw_health_reason}.")
                i+=1
                if i == 4:
                    print(f"\nERROR:: [{seq}.] Gateway status is UNHEALTHY. Exiting!!")
                    sys.exit(1)
                else:
                    time.sleep(25)
            else:
                print(f"\n[{seq}.] Gateway status is HEALTHY.")
                return True
 
    return None

# build eksabm cluster data dict
def build_eksabm_cluster_create_data_dict(cluster_name,ssh_public_key):
    data = {
        "metadata": {
            "name": cluster_name,
            "description": ""
        },
        "spec": {
            "clusterType": "Eksa_bm",
            "providerID": "",
            "blueprintVersion": "latest",
            "blueprint": "minimal",
            "configJson": {
                "eksaClusterConfig": {
                    "kind": "Cluster",
                    "spec": {
                        "datacenterRef": {
                            "kind": "TinkerbellDatacenterConfig",
                            "name": cluster_name
                        },
                        "clusterNetwork": {
                            "pods": {
                                "cidrBlocks": ["192.168.0.0/16"]
                            },
                            "services": {
                                "cidrBlocks": ["10.96.0.0/12"]
                            },
                            "cniConfig": {
                                "cilium": {}
                            }
                        },
                        "kubernetesVersion": "",
                        "managementCluster": {
                            "name": cluster_name
                        },
                        "controlPlaneConfiguration": {
                            "count": 1,
                            "endpoint": {
                                "host": ""
                            },
                            "machineGroupRef": {
                                "kind": "TinkerbellMachineConfig",
                                "name": ""
                            }
                        },
                        "workerNodeGroupConfigurations": None
                    },
                    "metadata": {
                        "name": cluster_name
                    },
                    "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
                },
                "tinkerbellMachineConfig": [],
                "tinkerbellHardwareConfig": [],
                "tinkerbellTemplateConfig": [],
                "tinkerbellDatacenterConfig": {
                    "kind": "TinkerbellDatacenterConfig",
                    "spec": {
                        "tinkerbellIP": ""
                    },
                    "metadata": {
                        "name": cluster_name
                    },
                    "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
                }
            }
        }
    }
    return data

# create eksabm cluster 
def create_eksabm_cluster(rafay_controller_url, headers,cluster_name, project_id, ssh_public_key, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster'
    method = 'POST'

    data = build_eksabm_cluster_create_data_dict(cluster_name,ssh_public_key)
    resp = make_request(url, method, headers, data)
    if resp:
        print(f"\n[{seq}.] Cluster creation successful. cluster_name:{cluster_name}, project_id:{project_id}")
        #print("Response Status Code:", resp.status_code)
        #print("Response JSON:", resp.json())
    else:
        print(f"\nERROR:: Cluster creation failed. Exiting... cluster_name:{cluster_name}, project_id:{project_id}")
        sys.exit(1)

    return resp

# get eksabm cluster
def get_cluster(rafay_controller_url, headers, cluster_name, project_id, seq=1):

    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        return resp.json()

    return None

# delete eksabm cluster 
def delete_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name
    method = 'DELETE'

    resp = make_request(url, method, headers, "")
    if resp:
        print(f"\n[{seq}.] Cluster deletion successful. cluster_name:{cluster_name}, project_id:{project_id}")
    else:
        print(f"\nERROR: Cluster deletion failed. cluster_name:{cluster_name}, project_id:{project_id}")
        
    return resp

# force delete eksabm cluster 
def delete_eksabm_cluster_force(rafay_controller_url, headers, cluster_name, project_id, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name+'?force=true'
    method = 'DELETE'

    resp = make_request(url, method, headers, "")
    if resp:
        print(f"\n[{seq}.] Cluster force deletion successful. cluster_name:{cluster_name}, project_id:{project_id}")
    else:
        print(f"\nERROR: Cluster force deletion failed. cluster_name:{cluster_name}, project_id:{project_id}")
        
    return resp

# get cluster 
def get_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        #print (resp)
        return resp.json()

    return None

# parse hardware csv file
def parse_hardware_csv_file(file_path):
    data = []
    
    with open(file_path, 'r') as file:
        # Skip the first line (header)
        next(file)
        
        for line in file:
            line_data = line.strip().split(',')
            entry = {
                "hostname": line_data[0],
                "mac": line_data[1],
                "ip_address": line_data[2],
                "netmask": line_data[3],
                "gateway": line_data[4],
                "nameservers": line_data[5],
                "labels": line_data[6],
                "disk": line_data[7],
                "bmc_ip": line_data[8],
                "bmc_username": line_data[9],
                "bmc_password": line_data[10]
            }
            data.append(entry)
    
    return data

# build eksabm cluster update data dict
def build_eksabm_cluster_update_data_dict(rafay_controller_url, headers, gw_name, cluster_name,project_id,k8s_version,cp_count,endpoint_host_ip,dp_count,tinkerbell_ip,hardware_csv_location,cluster_yaml,ssh_public_key):
    
    get_gateway_resp_json = get_gateway(rafay_controller_url, headers, gw_name, project_id)
    if get_gateway_resp_json:
        gateway_id = get_gateway_resp_json["metadata"]["id"]
    else:
        print(f"\nERROR:: Unable to get gateway details. Exiting ... gw_name:{gw_name}, project_id:{project_id}")
        sys.exit(1)

    hardware_entries = parse_hardware_csv_file(hardware_csv_location)

    if cluster_yaml is not None:
        updated_cluster_yaml = update_tinkerbell_ip(cluster_yaml, tinkerbell_ip, 'rafay')
        updated_cluster_yaml = update_endpoint_ip(updated_cluster_yaml, endpoint_host_ip, 'rafay')
        updated_cluster_yaml = update_gateway_id(updated_cluster_yaml, gateway_id, 'rafay')
        updated_cluster_yaml = update_hardware_details(updated_cluster_yaml, hardware_entries, 'rafay')
        yaml_data = yaml.safe_load_all(updated_cluster_yaml)
        json_data = json.dumps([doc for doc in yaml_data], indent=2)
        updated_spec_data = json.loads(json_data)[0]
        updated_spec_data['spec']['clusterType'] = updated_spec_data['spec'].pop('type')
        updated_spec_data['spec']['configJson'] = updated_spec_data['spec'].pop('config')
        blueprint_name = updated_spec_data['spec']['blueprint']['name']
        blueprint_version = updated_spec_data['spec']['blueprint']['version']
        del updated_spec_data['spec']['blueprint']
        updated_spec_data['spec']['blueprint'] = blueprint_name
        updated_spec_data['spec']['blueprintVersion'] = blueprint_version
    else:
        updated_spec_data = {
            "spec": {
                "clusterType": "Eksa_bm",
                "config": "",
                "blueprint": "minimal",
                "blueprintVersion": "latest",
                "agentName": "agent-cluster-"+cluster_name,
                "gatewayID": gateway_id,
                "configJson": {
                    "eksaClusterConfig": {
                        "kind": "Cluster",
                        "spec": {
                            "datacenterRef": {
                                "kind": "TinkerbellDatacenterConfig",
                                "name": cluster_name
                            },
                            "clusterNetwork": {
                                "pods": {
                                    "cidrBlocks": [
                                        "192.168.0.0/16"
                                    ]
                                },
                                "services": {
                                    "cidrBlocks": [
                                        "10.96.0.0/12"
                                    ]
                                },
                                "cniConfig": {
                                    "cilium": {
                                        "policyEnforcementMode": "default"
                                    }
                                }
                            },
                            "kubernetesVersion": k8s_version,
                            "managementCluster": {
                                "name": cluster_name
                            },
                            "controlPlaneConfiguration": {
                                "count": cp_count,
                                "endpoint": {
                                    "host": endpoint_host_ip
                                },
                                "machineGroupRef": {
                                    "kind": "TinkerbellMachineConfig",
                                    "name": "cpmc"
                                }
                            },
                            "workerNodeGroupConfigurations": [
                                {
                                    "name": "ng1",
                                    "count": dp_count,
                                    "machineGroupRef": {
                                        "kind": "TinkerbellMachineConfig",
                                        "name": "dpmc"
                                    }
                                }
                            ]
                        },
                        "metadata": {
                            "name": cluster_name
                        },
                        "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
                    },
                    "tinkerbellMachineConfig": [
                        {
                            "kind": "TinkerbellMachineConfig",
                            "spec": {
                                "users": [
                                    {
                                        "name": "ec2-user",
                                        "sshAuthorizedKeys": [
                                            ssh_public_key
                                        ]
                                    }
                                ],
                                "osFamily": "bottlerocket",
                                "templateRef": {
                                    "kind": "TinkerbellTemplateConfig",
                                    "name": ""
                                },
                                "hardwareSelector": {
                                    "type": "cp"
                                },
                                "hostOSConfiguration": {
                                    "certBundles": [
                                        {
                                            "name": "bundle",
                                            "data": "-----BEGIN CERTIFICATE-----\nMIICDDCCAXUCFFmejalQeOFMOCZ9fo/jRoIxuGSHMA0GCSqGSIb3DQEBCwUAMEUx\nCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRl\ncm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMjMwNjI3MTEwMDIwWhcNMjQwNjI2MTEw\nMDIwWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UE\nCgwYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GN\nADCBiQKBgQDQFJJAlnqahO6Rmx/pfJRF2mKV4EHExGNWWeiPD5/sx0Yu6GqNNyJb\n5DkTlP0wpCPfvkewjxZcrAondz64nLrHbTCiouzOSllnJK4GIqjwp17NoqGX5i8K\nK7r6U8pYMznME/GLCGAsDKz2yzgoCZH6mpK+iACE/gS2F/g17q44rwIDAQABMA0G\nCSqGSIb3DQEBCwUAA4GBADEeDEEp/wJXuKVGCdAsqgDxoMhIwD6TyGC91CV2AsmH\ne4fuG0Ld47mfaFamjB6K+bkeJlQyZmSX2dI3t9DnqgLy6PNHplibJkN56dQ4rKy8\nqyGU1QxiBK70lni4QuoeNvhFmlzp5mI654tmXSnoCgriUXtil3uQPmihs+KTtAdT\n-----END CERTIFICATE-----"
                                        }
                                    ]
                                }
                            },
                            "metadata": {
                                "name": "cpmc"
                            },
                            "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
                        },
                        {
                            "kind": "TinkerbellMachineConfig",
                            "spec": {
                                "users": [
                                    {
                                        "name": "ec2-user",
                                        "sshAuthorizedKeys": [
                                            ssh_public_key
                                        ]
                                    }
                                ],
                                "osFamily": "bottlerocket",
                                "templateRef": {
                                    "kind": "TinkerbellTemplateConfig",
                                    "name": ""
                                },
                                "hardwareSelector": {
                                    "type": "dp"
                                },
                                "hostOSConfiguration": {
                                    "certBundles": [
                                        {
                                            "name": "bundle",
                                            "data": "-----BEGIN CERTIFICATE-----\nMIICDDCCAXUCFFmejalQeOFMOCZ9fo/jRoIxuGSHMA0GCSqGSIb3DQEBCwUAMEUx\nCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRl\ncm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMjMwNjI3MTEwMDIwWhcNMjQwNjI2MTEw\nMDIwWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UE\nCgwYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GN\nADCBiQKBgQDQFJJAlnqahO6Rmx/pfJRF2mKV4EHExGNWWeiPD5/sx0Yu6GqNNyJb\n5DkTlP0wpCPfvkewjxZcrAondz64nLrHbTCiouzOSllnJK4GIqjwp17NoqGX5i8K\nK7r6U8pYMznME/GLCGAsDKz2yzgoCZH6mpK+iACE/gS2F/g17q44rwIDAQABMA0G\nCSqGSIb3DQEBCwUAA4GBADEeDEEp/wJXuKVGCdAsqgDxoMhIwD6TyGC91CV2AsmH\ne4fuG0Ld47mfaFamjB6K+bkeJlQyZmSX2dI3t9DnqgLy6PNHplibJkN56dQ4rKy8\nqyGU1QxiBK70lni4QuoeNvhFmlzp5mI654tmXSnoCgriUXtil3uQPmihs+KTtAdT\n-----END CERTIFICATE-----"
                                        }
                                    ]
                                }
                            },
                            "metadata": {
                                "name": "dpmc"
                            },
                            "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
                        }
                    ],
                    "tinkerbellHardwareConfig": hardware_entries,
                    "tinkerbellTemplateConfig": [],
                    "tinkerbellDatacenterConfig": {
                        "kind": "TinkerbellDatacenterConfig",
                        "spec": {
                            "tinkerbellIP": tinkerbell_ip
                        },
                        "metadata": {
                            "name": cluster_name
                        },
                        "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
                    }
                }
            }
        }
    
    # get cluster details
    get_cluster_resp_json = get_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id)
    if get_cluster_resp_json:
        # prepare updated spec data
        get_cluster_resp_json["spec"] = updated_spec_data["spec"]

    else:
        print(f"\nERROR:: Unable to get cluster details. Exiting ... cluster_name:{cluster_name}, project_id:{project_id}")
        sys.exit(1)    
    

    return get_cluster_resp_json

def build_native_eksabm_cluster_spec(cluster_name,k8s_version,cp_count,endpoint_host_ip,dp_count,tinkerbell_ip,ssh_public_key):

    eksa_cluster_config = {
        "kind": "Cluster",
        "spec": {
            "datacenterRef": {
                "kind": "TinkerbellDatacenterConfig",
                "name": cluster_name
            },
            "clusterNetwork": {
                "pods": {
                    "cidrBlocks": [
                        "192.168.0.0/16"
                    ]
                },
                "services": {
                    "cidrBlocks": [
                        "10.96.0.0/12"
                    ]
                },
                "cniConfig": {
                    "cilium": {
                        "policyEnforcementMode": "default"
                    }
                }
            },
            "kubernetesVersion": k8s_version,
            "managementCluster": {
                "name": cluster_name
            },
            "controlPlaneConfiguration": {
                "count": cp_count,
                "endpoint": {
                    "host": endpoint_host_ip
                },
                "machineGroupRef": {
                    "kind": "TinkerbellMachineConfig",
                    "name": "cpmc"
                }
            },
            "workerNodeGroupConfigurations": [
                {
                    "name": "ng1",
                    "count": dp_count,
                    "machineGroupRef": {
                        "kind": "TinkerbellMachineConfig",
                        "name": "dpmc"
                    }
                }
            ]
        },
        "metadata": {
            "name": cluster_name
        },
        "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
    }

    machineConfigs = [
        {
            "kind": "TinkerbellMachineConfig",
            "spec": {
                "users": [
                    {
                        "name": "ec2-user",
                        "sshAuthorizedKeys": [
                            ssh_public_key
                        ]
                    }
                ],
                "osFamily": "bottlerocket",
                "templateRef": {
                    "kind": "TinkerbellTemplateConfig",
                    "name": ""
                },
                "hardwareSelector": {
                    "type": "cp"
                }
            },
            "metadata": {
                "name": "cpmc"
            },
            "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
        },
        {
            "kind": "TinkerbellMachineConfig",
            "spec": {
                "users": [
                    {
                        "name": "ec2-user",
                        "sshAuthorizedKeys": [
                            ssh_public_key
                        ]
                    }
                ],
                "osFamily": "bottlerocket",
                "templateRef": {
                    "kind": "TinkerbellTemplateConfig",
                    "name": ""
                },
                "hardwareSelector": {
                    "type": "dp"
                }
            },
            "metadata": {
                "name": "dpmc"
            },
            "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
        }
    ]

    data_center_config = {
        "kind": "TinkerbellDatacenterConfig",
        "spec": {
            "tinkerbellIP": tinkerbell_ip
        },
        "metadata": {
            "name": cluster_name
        },
        "apiVersion": "anywhere.eks.amazonaws.com/v1alpha1"
    }
    
    yaml_data = [eksa_cluster_config, data_center_config] + machineConfigs
    
    yaml_string = yaml.dump_all(yaml_data, default_flow_style=False)  
    
    return yaml_string

def update_tinkerbell_ip(yaml_file_content, tinkerbell_ip, provisioner):
    yaml_data = yaml.safe_load_all(yaml_file_content)

    updated_yaml_documents = []

    if provisioner == "native":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "TinkerbellDatacenterConfig":
                doc["spec"]["tinkerbellIP"] = tinkerbell_ip
            updated_yaml_documents.append(doc)
    elif provisioner == "rafay":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                doc["spec"]["config"]["tinkerbellDatacenterConfig"]["spec"]["tinkerbellIP"] = tinkerbell_ip
            updated_yaml_documents.append(doc)
    
    updated_yaml_content = "\n---\n".join(yaml.dump(doc, default_flow_style=False) for doc in updated_yaml_documents)

    return updated_yaml_content

def update_endpoint_ip(yaml_file_content, endpoint_ip, provisioner):
    yaml_data = yaml.safe_load_all(yaml_file_content)

    updated_yaml_documents = []

    if provisioner == "native":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                doc["spec"]["controlPlaneConfiguration"]["endpoint"]["host"] = endpoint_ip
            updated_yaml_documents.append(doc)
    elif provisioner == "rafay":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                doc["spec"]["config"]["eksaClusterConfig"]["spec"]["controlPlaneConfiguration"]["endpoint"]["host"] = endpoint_ip
            updated_yaml_documents.append(doc)
    
    updated_yaml_content = "\n---\n".join(yaml.dump(doc, default_flow_style=False) for doc in updated_yaml_documents)

    return updated_yaml_content

def update_gateway_id(yaml_file_content, gateway_id, provisioner):
    yaml_data = yaml.safe_load_all(yaml_file_content)

    updated_yaml_documents = []

    if provisioner == "rafay":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                doc["spec"]["gatewayID"] = gateway_id
            updated_yaml_documents.append(doc)
    
    updated_yaml_content = "\n---\n".join(yaml.dump(doc, default_flow_style=False) for doc in updated_yaml_documents)

    return updated_yaml_content

def update_hardware_details(yaml_file_content, hardware_details, provisioner):
    yaml_data = yaml.safe_load_all(yaml_file_content)

    updated_yaml_documents = []

    if provisioner == "rafay_eksabm_cluster":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                doc["spec"]["config"]["tinkerbellHardwareConfig"] = hardware_details
            updated_yaml_documents.append(doc)
    
    updated_yaml_content = "\n---\n".join(yaml.dump(doc, default_flow_style=False) for doc in updated_yaml_documents)

    return updated_yaml_content

def extract_cluster_details_from_cluster_yaml(yaml_file, provisioner):
    with open(yaml_file, "r") as yaml_file:
        yaml_cluster_config = yaml_file.read().strip()

    yaml_data = yaml.safe_load_all(yaml_cluster_config)
    if provisioner == "eksabm_cluster":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                kubernetes_version=doc["spec"]["kubernetesVersion"]
                cp_count=doc["spec"]["controlPlaneConfiguration"]["count"]
                dp_count=sum(node_group['count'] for node_group in doc['spec']['workerNodeGroupConfigurations'])
    elif provisioner == "rafay_eksabm_cluster":
        for doc in yaml_data:
            if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
                kubernetes_version=doc["spec"]["config"]["eksaClusterConfig"]["spec"]["kubernetesVersion"]
                cp_count=doc["spec"]["config"]["eksaClusterConfig"]["spec"]["controlPlaneConfiguration"]["count"]
                dp_count=sum(node_group['count'] for node_group in doc["spec"]["config"]["eksaClusterConfig"]['spec']['workerNodeGroupConfigurations'])

    return kubernetes_version, cp_count, dp_count, yaml_cluster_config

def get_provisioner_by_yaml_file(yaml_file):
    with open(yaml_file, "r") as yaml_file:
        yaml_cluster_config = yaml_file.read().strip()
    
    yaml_data = yaml.safe_load_all(yaml_cluster_config)
    for doc in yaml_data:
        if doc is not None and "kind" in doc and doc["kind"] == "Cluster":
            api_version = doc["apiVersion"]
            break
    
    if api_version is not None and api_version == "anywhere.eks.amazonaws.com/v1alpha1":
        return "eksabm_cluster"
    elif api_version is not None and api_version == "infra.k8smgmt.io/v3":
        return "rafay_eksabm_cluster"
    else:
        return None

# update eksabm cluster
def update_eksabm_cluster(rafay_controller_url, headers,cluster_name, project_id,hardware_csv_location,cluster_tinkerbell_ip_file,cluster_endpoint_ip_file, k8s_version,cp_count,dp_count, gw_name, cluster_yaml,ssh_public_key, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name
    method = 'PUT'

    # read tinkerbell ip from file cluster_tinkerbell_ip_file
    with open(cluster_tinkerbell_ip_file, 'r') as f:
        tinkerbell_ip = f.read().strip()    
        
    # read endpoint ip from file cluster_endpoint_ip_file
    with open(cluster_endpoint_ip_file, 'r') as f:
        endpoint_host_ip = f.read().strip()

    updated_spec_data = build_eksabm_cluster_update_data_dict(rafay_controller_url, headers, gw_name, cluster_name,project_id,k8s_version,cp_count,endpoint_host_ip,dp_count,tinkerbell_ip,hardware_csv_location,cluster_yaml,ssh_public_key) 
    resp = make_request(url, method, headers, updated_spec_data)
    if resp:
        print(f"\n[{seq}.] Cluster update successful. cluster_name:{cluster_name}, project_id:{project_id}")
        #print("Response Status Code:", resp.status_code)
        #print("Response JSON:", resp.json())
    else:
        print(f"\nERROR:: Cluster update failed. Exiting... cluster_name:{cluster_name}, project_id:{project_id}")
        sys.exit(1)

    return resp

# provision eksabm cluster
def provision_eksabm_cluster(rafay_controller_url, headers,cluster_name, project_id, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name+'/provisioncluster'
    method = 'POST'

    resp = make_request(url, method, headers, "")
    if resp:
        print(f"\n[{seq}.] Cluster provision request submitted successfully. cluster_name:{cluster_name}, project_id:{project_id}")
        #print("Response Status Code:", resp.status_code)
        #print("Response JSON:", resp.json())
    else:
        print(f"\nERROR: Cluster provision request failed. Exiting... cluster_name:{cluster_name}, project_id:{project_id}")
        sys.exit(1)

    return resp

class CustomException(Exception):
    pass

def print_cluster_condition_status_summary(conditions_type_list,conditions_status_dict):
    for cnd in conditions_type_list:
        if conditions_status_dict.get(cnd):
            print(f"     [+] {cnd} : {conditions_status_dict[cnd][0]} ({conditions_status_dict[cnd][1]})")

# monitor eksabm cluster status progress
def monitor_eksabm_cluster_status_progress(rafay_controller_url, headers, conditions_type_list, target_condition_type, target_condition_status, cluster_name,project_id,seq=1):
    print(f"\n[{seq}.] Waiting on cluster condition {target_condition_type} to be in status {target_condition_status}, cluster_name:{cluster_name}, project_id:{project_id}")
    
    conditions_status_dict={}
    try:
        # Check cluster status in a loop until condition target_condition_type has progressed to status target_condition_status
        while True:
            # Get cluster details
            resp = get_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id)
            if resp:
                # extract cluster status conditions from response
                conditions = resp.get("status", {}).get("conditions", [])

                # parse all cluster status conditions 
                for condition in conditions:
                    cnd_type = condition.get("type", "")
                    cnd_status = condition.get("status", "")
                    cnd_reason = condition.get("reason", "")
                    conditions_status_dict[cnd_type] = [cnd_status,cnd_reason]
                    # Exit if any cluster status condition has failed 
                    if cnd_status == 'Failure':
                        print(f"\nERROR:: Cluster {target_condition_type} failed. Exiting... cluster_name:{cluster_name}, project_id:{project_id}. Cluster status condition type:{cnd_type}, status:{cnd_status}, reason:{cnd_reason}")
                        print_cluster_condition_status_summary(conditions_type_list,conditions_status_dict)
                        sys.exit(1)

                    # Exit while loop if condition target_condition_type has progressed to status target_condition_status
                    if cnd_type == target_condition_type and cnd_status == target_condition_status:
                        raise CustomException
            else:
                print(f"\nERROR: Unable to get cluster details. cluster_name:{cluster_name}, project_id:{project_id}")
                            
            # sleep for 5 minutes
            print_cluster_condition_status_summary(conditions_type_list,conditions_status_dict)
            print(f"   [+]  .... waiting for 5 minutes  .... ")
            
            time.sleep(60*5)
    
    except CustomException:
        print_cluster_condition_status_summary(conditions_type_list,conditions_status_dict)
        print(f"    [+]    Detected cluster condition {target_condition_type} has progressed to status {target_condition_status}")

# get "show debug" status of cluster conditions 
def get_show_debug_cluster_condition_status(rafay_controller_url, headers, cluster_name, project_id, cluster_condition="ClusterSpecApplied"):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name+'/conditionstatus?clusterCondition='+cluster_condition
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        #print (resp)
        return resp.json()

    return None


def power_cycle_node(node_name, boot_order="net"):
    print(f"   [+] Powering on cluster node {node_name} with boot order {boot_order}")
    cmd = f"sudo VBoxManage controlvm {node_name} poweroff; sleep 1; sudo VBoxManage modifyvm {node_name} --boot1={boot_order}; sleep 1; sudo VBoxManage startvm {node_name} --type headless"
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"\nERROR: Unable to power on cluster node {node_name} in VBox. Exiting...")


def check_if_show_debug_log_output_contains_termination_condition(condition_type,target_action,action_output,cluster_node_names,workflows_list):
    # Check if output of ekctl anywhere create cluster shows Creating new workload cluster
    if condition_type=="ClusterSpecApplied" and target_action=="EksctlCreateClusterCmdLogs" and "Creating new workload cluster" in action_output:
        return True, "Detected Creating new workload cluster in log output. This means nodes are ready to be power cycled"

    # Check if output of ekctl anywhere upgrade cluster shows Upgrading workload cluster
    if condition_type=="ClusterUpgraded" and target_action=="EksctlUpgradeClusterCmdLogs" and "Upgrading workload cluster" in action_output:
        return True, "Detected Upgrading workload cluster in log output. This means nodes are ready to be power cycled"

    # Check workflows_list is not None
    if workflows_list is None:
        return False, "Unable to get workflows list"
    
    try:
        parsed_data = yaml.safe_load(workflows_list.json()['output'])
    except:
        parsed_data = yaml.safe_load(workflows_list)

    # Extract spec.hardwareRef for workflows with status.state equal to "STATE_PENDING"
    hardware_with_pending_tb_wf = [item["spec"]["hardwareRef"] for item in parsed_data["items"] if item["status"]["state"] == "STATE_PENDING"]
    hardware_with_failed_tb_wf = [item["spec"]["hardwareRef"] for item in parsed_data["items"] if item["status"]["state"] == "STATE_FAILED"]
    hardware_with_running_tb_wf = [item["spec"]["hardwareRef"] for item in parsed_data["items"] if item["status"]["state"] == "STATE_RUNNING"]
    hardware_with_success_tb_wf = [item["spec"]["hardwareRef"] for item in parsed_data["items"] if item["status"]["state"] == "STATE_SUCCESS"]

    print(f"   [+] Tinkerbell workflows detected: PENDING:{hardware_with_pending_tb_wf} RUNNING:{hardware_with_running_tb_wf} FAILED:{hardware_with_failed_tb_wf} SUCCESS:{hardware_with_success_tb_wf}")

    # If no workflows are detected return False 
    if hardware_with_pending_tb_wf is None and hardware_with_failed_tb_wf is None and hardware_with_running_tb_wf is None and hardware_with_success_tb_wf is None:
        return False, "Unable to get workflows list"
    
    if (isinstance(hardware_with_pending_tb_wf, list) and len(hardware_with_pending_tb_wf) == 0) and (isinstance(hardware_with_failed_tb_wf, list) and len(hardware_with_failed_tb_wf) == 0) and (isinstance(hardware_with_running_tb_wf, list) and len(hardware_with_running_tb_wf) == 0) and (isinstance(hardware_with_success_tb_wf, list) and len(hardware_with_success_tb_wf) == 0):
        return False, "No workflows are detected"


    # Power cycle nodes with pending workflows with net boot order so that they PXE boot and start the workflows
    print(f"   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:{hardware_with_pending_tb_wf} OR FAILED:{hardware_with_failed_tb_wf}")
    for node_name in hardware_with_pending_tb_wf:
        power_cycle_node(node_name, "net")

    for node_name in hardware_with_failed_tb_wf:
        power_cycle_node(node_name, "net")    

    phase_list=[]
    # Check if any machine.c is in 'Provisioned' phase and if so power cycle it with boot order as disk.
    if condition_type=="ClusterSpecApplied" and target_action=="MachineStatus": 
        lines = action_output.strip().split("\n")[1:]
        for line in lines:
            parts = line.split()
            phase_list.append(parts[-3])
            if 'Provisioned'==parts[-3]:
                # hardware is in Provisioned phase. Power cycle it with boot order disk
                #namespace, machine_name, cluster, provider_id, phase, age, version = parts
                provider_id=parts[3]
                hardware=provider_id.split('/')[-1:][0]
                print(f"   [+] Power cycling machines.c with Phase Provisioned (boot order disk). {hardware}")
                power_cycle_node(hardware, "disk")

    # Check if all machines.c are in Running phase
    for phase in phase_list:    
        if phase != 'Running':
            print(f"   [+] Detected machines in phases {phase_list}")
            return False, "Not all machines.c are in Running phase"
    # All machines are in Running phase..hence exit while loop    
    return True, "All machines.c are in Running phase"    

# monitor progress of cluster status conditions 
def monitor_eksabm_condition_debug_log(rafay_controller_url, headers, condition_type,target_action,terminate_monitoring_check,cluster_node_names,cluster_name,project_id,seq=1):
    print(f"\n[{seq}.] Monitoring {condition_type} condition status debug log")
    
    try:
        while True:
            resp = get_show_debug_cluster_condition_status(rafay_controller_url, headers, cluster_name, project_id, condition_type)
            if resp:
                # extract debug_actions from response
                debug_actions = resp.get("ConditionDebugActions", [])

                # parse all debug_actions
                for action_entry in debug_actions:
                    action_action = action_entry.get("action", "")
                    action_output = action_entry.get("output", "")
                    action_status = action_entry.get("status", "")

                    # Exit while loop 
                    if action_action == target_action:
                        workflows_list = exceute_debug_channel_command(rafay_controller_url, headers, project_id, cluster_name,"kind", "kubectl get workflows -A -o yaml")
                        term_cnd,term_out = terminate_monitoring_check(condition_type,target_action,action_output,cluster_node_names,workflows_list)
                        if term_cnd:
                            raise CustomException
            else:
                print(f"\nERROR: Unable to get show debug status for cluster condition {condition_type}. cluster_name:{cluster_name}, project_id:{project_id}")
                raise CustomException
                            
            # sleep for 5 minutes
            print(f"   [+]  .... waiting for 5 minutes  .... ")
            
            time.sleep(60*5)
    
    except CustomException:
        print(f"    [+]    Exiting monitoring {condition_type} condition status debug log as progress check successful. {term_out}")

def get_cluster_node_names(hardware_csv_location):
    hardware_entries = parse_hardware_csv_file(hardware_csv_location)

    # get all cluster node names
    cluster_node_names = []
    for entry in hardware_entries:
        if "eksa-admin" in entry['hostname']:
            continue
        cluster_node_names.append(entry['hostname'])
    return cluster_node_names

# power on all cluster nodes in VBox
def power_manage_cluster_nodes_for_provision(rafay_controller_url, headers, project_id, cluster_name, hardware_csv_location, seq=1): 
    cluster_node_names = get_cluster_node_names(hardware_csv_location)
    monitor_eksabm_condition_debug_log(rafay_controller_url, headers, "ClusterSpecApplied", "MachineStatus", check_if_show_debug_log_output_contains_termination_condition, cluster_node_names, cluster_name, project_id, 10)

# process the input YAML file
def process_input_yaml(input_yaml):
    try: 
        # Load the input YAML file
        with open(input_yaml, "r") as yaml_file:
            input_data = yaml.safe_load(yaml_file)

        # Print the detected values
        #print(f"\n[+] Detected config:")
        #for key, value in input_data.items():
        #    print(f"    {key}: {value}")

    except Exception as e:
        print(f"[-] ERROR: Error processing input YAML file {input_yaml}: {e}")
        exit(1)
    
    return input_data


# run command locally in a shell and stream output 
def run_local_command_and_stream_output(command):

    # Start the command as a subprocess and capture its output and errors
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # Read and print the output in real-time
    for line in process.stdout:
        print(line)  # Strip newline characters for cleaner output

    # Wait for the command to complete and capture any remaining output
    output, errors = process.communicate()

    # Print any remaining output and errors (if any)
    if output:
        print(output)

    if errors:
        print("Errors:")
        print(errors)

    # Get the command's exit code
    return_code = process.returncode
    print(f"Command exited with return code {return_code}")


# run command locally in a shell 
def run_local_command(command):
    process = subprocess.run(command, shell=True, capture_output=True)
    print(process.stdout)
    if process.returncode != 0:
        print(process.stderr)
    return process.returncode
    
def get_eksabm_cp_vms_count(cluster_name):
    get_cp_count_cmd=f'sudo ls {eksa_vm_dir}/{cluster_name} | grep {cluster_name}-cp-n | wc -l'
    try:
        process = subprocess.run(get_cp_count_cmd, shell=True, capture_output=True, text=True)
        output = process.stdout
        if process.returncode != 0:
            print(f'encountered error while checking existing cp vms: {process.stderr}, ignoring and continuing with cp vms creation')
        cp_count_cluster = int(output)
        print(f'cp count {cp_count_cluster}')
    except subprocess.CalledProcessError as e:
        print(f"ERROR:: encountered error while checking existing cp vms: {e}, ignoring and continuing with cp vms creation")
        sys.exit(0)
    except ValueError as e:
        print(f"ERROR:: encountered error while checking existing cp vms: {e}, ignoring and continuing with cp vms creation")
        sys.exit(0)
    
    return cp_count_cluster

def get_eksabm_dp_vms_count(cluster_name):
    get_dp_count_cmd=f'sudo ls {eksa_vm_dir}/{cluster_name} | grep {cluster_name}-dp-n | wc -l'
    try:
        process = subprocess.run(get_dp_count_cmd, shell=True, capture_output=True, text=True)
        output = process.stdout
        if process.returncode != 0:
            print(f'encountered error while checking existing dp vms: {process.stderr}, ignoring and continuing with dp vms creation')
        dp_count_cluster = int(output)
        print(f'dp count {dp_count_cluster}')
    except subprocess.CalledProcessError as e:
        print(f"ERROR:: encountered error while checking existing dp vms: {e}, ignoring and continuing with dp vms creation")
        sys.exit(0)
    except ValueError as e:
        print(f"ERROR:: encountered error while checking existing dp vms: {e}, ignoring and continuing with dp vms creation")
        sys.exit(0)
    
    return dp_count_cluster

def validate_eksabm_vms_presence(cp_count, dp_count, cluster_name):
    cp_count_cluster = get_eksabm_cp_vms_count(cluster_name)
    dp_count_cluster = get_eksabm_dp_vms_count(cluster_name)

    if cp_count_cluster == cp_count and dp_count_cluster == dp_count:
        return True
    
    return False


def validate_vms_presence(vm_count, vm_name_prefix):

    get_vm_count_cmd=f'sudo ls {vm_dir} | grep {vm_name_prefix} | wc -l'
    try:
        process = subprocess.run(get_vm_count_cmd, shell=True, capture_output=True, text=True)
        output = process.stdout
        if process.returncode != 0:
            print(f'encountered error while checking existing vms: {process.stderr}, ignoring and continuing with vm creation')
        vm_present_count = int(output)
        print(f'vm count {vm_count}')
    except subprocess.CalledProcessError as e:
        print(f"ERROR encountered error while checking existing vms: {e}, ignoring and continuing with vm creation")

    except ValueError as e:
        print(f"ERROR encountered error while checking existing vms: {e}, ignoring and continuing with vm creation")
 
    print(f'[+] Checking if vm {vm_name_prefix} has been launched {vm_count} times already. Detected it has been launched {vm_present_count} times already')
    
    if vm_present_count == vm_count:
        return True
    
    return False


def eksabm_vbox_vms_dependencies(cp_count, dp_count, cluster_name): 
    print(f"\n[+] Installing vbox. This step may take a while, please be patient.....")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/install-vbox-vagrant.sh > {staging_dir}/install-vbox-vagrant.log 2>&1; cat {staging_dir}/install-vbox-vagrant.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

    print(f"\n[+] Creating vbox network. This step may take a while, please be patient....")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/create-eksabm-network.sh > {staging_dir}/create-eksabm-network.log 2>&1; cat {staging_dir}/create-eksabm-network.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

def create_eksabm_admin_vm():
    print(f"\n[+] Creating eksa admin vm. This step may take a while, please be patient...")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/launch-eksabm-admin-vm.sh > {staging_dir}/launch-eksabm-admin-vm.log 2>&1; cat {staging_dir}/launch-eksabm-admin-vm.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

def create_eksabm_cp_dp_vms(cp_count, dp_count, cluster_name):
    print(f"\n[+] Creating control plane vms. This step may take a while, please be patient...")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/launch-eksabm-cluster-vms.sh -n {cluster_name} -c {cp_count} -d 0 > {staging_dir}/launch-eksabm-cluster-vms-cp.log 2>&1; cat {staging_dir}/launch-eksabm-cluster-vms-cp.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

    print(f"\n[+] Creating data plane vms. This step may take a while, please be patient...")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/launch-eksabm-cluster-vms.sh -n {cluster_name} -c 0 -d {dp_count} > {staging_dir}/launch-eksabm-cluster-vms-dp.log 2>&1; cat {staging_dir}/launch-eksabm-cluster-vms-dp.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

# launch vbox vms for eksabm clusters
def launch_eksabm_vbox_vms(input_data):
    
    cluster_name=""
    cp_count=dp_count=0
    #infrastructure_provider = input_data["infrastructure_provider"]
    #infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]
    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]

    try:
        cluster_yaml_filename = provisioner_config["config_file_name"]
    except KeyError:
        cluster_yaml_filename = None 

    if cluster_yaml_filename is None:
        cluster_name = provisioner_config["cluster_name"]
        cp_count = provisioner_config["num_control_plane_nodes"]
        dp_count = provisioner_config["num_worker_nodes"]
    else:
        cluster_name = provisioner_config["cluster_name"]
        cluster_yaml_file=f'{staging_dir}/cluster_configs/{cluster_yaml_filename}'

        if os.path.exists(cluster_yaml_file):
                k8s_version,cp_count,dp_count,cluster_yaml = extract_cluster_details_from_cluster_yaml(cluster_yaml_file,provisioner)
        else:
            print(f"\nERROR:: cluster file {cluster_yaml_file} does not exist for cluster {cluster_name}")
            sys.exit(1)

    if cp_count <= 0 or dp_count <= 0:
        print(f"\nERROR:: CP and DP VMs count cannot be 0 or negative")
        sys.exit(1)

    operation_type = provisioner_config["operation_type"]
    
    already_vms_created = validate_eksabm_vms_presence(cp_count, dp_count, cluster_name)
    if already_vms_created:
        print(f"vms already created, skipping")
        return

    if operation_type == "provision":
        eksabm_vbox_vms_dependencies(cp_count, dp_count, cluster_name)
        create_eksabm_admin_vm()
        computed_cp_count=cp_count
        computed_dp_count=dp_count
    elif operation_type == "upgrade":
        current_cp_count=get_eksabm_cp_vms_count(cluster_name)
        current_dp_count=get_eksabm_dp_vms_count(cluster_name)
        computed_cp_count=cp_count-current_cp_count
        computed_dp_count=dp_count-current_dp_count
        if computed_cp_count <= 0 or computed_dp_count <= 0:
            print(f"\nERROR:: CP / DP VMs count are invalid")
            sys.exit(1)

    create_eksabm_cp_dp_vms(cp_count, dp_count, cluster_name)


def vbox_vms_dependencies(): 
    print(f"\n[+] Installing vbox. This step may take a while, please be patient.....")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/install-vbox-vagrant.sh > {staging_dir}/install-vbox-vagrant.log 2>&1; cat {staging_dir}/install-vbox-vagrant.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

    print(f"\n[+] Creating vm vbox network. This step may take a while, please be patient....")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/create-vm-network.sh > {staging_dir}/create-vm-network.log 2>&1; cat {staging_dir}/create-vm-network.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)

def create_vms(vm_name, vm_count, vm_cpu, vm_mem, vm_os_family, vm_vagrant_box):
    print(f"\n[+] Creating {vm_count} vms of name {vm_name}. This step may take a while, please be patient...")
    vms_launch_cmd=f"sudo bash {staging_dir}/vm-scripts/launch-vms.sh -n {vm_name} -c {vm_count} -p {vm_cpu} -m {vm_mem} -o {vm_os_family} -i {vm_vagrant_box}  > {staging_dir}/launch-vms.log 2>&1; cat {staging_dir}/launch-vms.log"
    ret_code = run_local_command(vms_launch_cmd)
    if ret_code != 0:
        print(f"\nERROR:: Command exited with error {vms_launch_cmd}..Exiting...")
        sys.exit(1)


def get_vms_ips():
    global_allocation_table=f"{vm_dir}/global_allocation_table"
    get_vms_ips_cmd=f'sudo cat {global_allocation_table}'
    try:
        process = subprocess.run(get_vms_ips_cmd, shell=True, capture_output=True, text=True)
        output = process.stdout
        if process.returncode != 0:
            print(f'ERROR:: encountered error while checking vms ips: {process.stderr}')
        
        output_lines = output.strip().split('\n')
        vms_map = {}
        
        for line in output_lines:
            fields = line.split(',')
            key = fields[0]
            values = fields[1:]
    
            value_map = {
                'MAC': values[0],
                'IP': values[1],
                'Port': values[2]
            }

            # Update vms_map with key as vm_name and value as value_map containing MAC, IP and Port
            vms_map[key] = value_map

        print(f"\n[+] Processed global allocation table {global_allocation_table} and detected below vms:")
        for key, values in vms_map.items():
            print(f"vm_name: {key}, vm_details: {values}")

    except subprocess.CalledProcessError as e:
        print(f"ERROR:: encountered error while checking vms ips: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR:: encountered error while checking vms ips: {e}")
        sys.exit(1)
    
    return vms_map


# launch vbox vms for vms_only
def launch_vbox_vms(input_data):
   
    vm_name=vm_os_family=vm_vagrant_box=""
    vm_count=vm_cpu=vm_mem=0

    infrastructure_provider = input_data["infrastructure_provider"]
    infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]
    ssh_public_key = infrastructure_provider_data["ssh_public_key"]

    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]

    # Default values
    default_values = {
        'count': 1,
        'cpu': 2,
        'mem': 16384,
        'osfamily': 'ubuntu',
        'vagrant_box': 'bento/ubuntu-20.04'
    }
    
    vbox_vms_dependencies()

    # loop over provisioner_config array and launch vms
    for vm in provisioner_config:
            vm_name = vm.get('name')
            vm_count = vm.get('count', default_values['count'])
            vm_cpu = vm.get('cpu', default_values['cpu'])
            vm_mem = vm.get('mem', default_values['mem'])
            vm_os_family = vm.get('osfamily', default_values['osfamily'])
            vm_vagrant_box = vm.get('vagrant_image', default_values['vagrant_box'])

            if vm_name is None:
                print(f"\nERROR:: vm name cannot be empty")
                sys.exit(1)

            if vm_count <= 0:
                print(f"\nERROR:: vm count cannot be 0 or negative")
                sys.exit(1)

            if vm_cpu <= 0:
                print(f"\nERROR:: vm cpu cannot be 0 or negative")
                sys.exit(1)

            if vm_mem <= 0:
                print(f"\nERROR:: vm memory cannot be 0 or negative")
                sys.exit(1)

            print(f"\n[+] Detected vm config:: vm_name: {vm_name}, vm_count:{vm_count}, vm_cpu:{vm_cpu}, vm_mem:{vm_mem}, vm_os_family:{vm_os_family}, vm_vagrant_box:{vm_vagrant_box}")

    
            already_vms_created = validate_vms_presence(vm_count, vm_name)
            if already_vms_created:
                print(f"vms already created, skipping")
                continue

            create_vms(vm_name, vm_count, vm_cpu, vm_mem, vm_os_family, vm_vagrant_box)

    # After vm creation, collect IP details from Global Allocation Table    
    vms_ip_details = get_vms_ips()
    vm_username='vagrant'
    vm_password='vagrant'
    
    # loop over vms_ip_details array and populate authorized_keys file for ssh access
    for vm in vms_ip_details.keys():
            vm_ipaddr = vms_ip_details[vm]['IP']
            vm_macaddr = vms_ip_details[vm]['MAC']
            vm_local_forwarded_port = vms_ip_details[vm]['Port']

            print(f"\n[+] vms created:: vm_name: {vm}, vm_ip:{vm_ipaddr}, vm_mac:{vm_macaddr}, vm_local_forwarded_port:{vm_local_forwarded_port}")

            # Create ssh config entry for vms node on local machine
            ssh_config_entry=f"\n\nHost {vm}\n  HostName 127.0.0.1\n  User vagrant\n  Port {vm_local_forwarded_port}\n  IdentityFile {staging_dir}/ssh_private_key_file\n  StrictHostKeyChecking no\n  UserKnownHostsFile=/dev/null\n"
            with open("/home/ubuntu/.ssh/config", "a") as ssh_config_file:
                    ssh_config_file.write(ssh_config_entry)

            print(f"\n[+] Waiting 1 minute to allow vm {vm} to boot up")
            import time
            time.sleep(60*2) 
                        
            # Copy ssh_public key to authorized keys of vm
            print(f"\n[+] Copying ssh_public key to authorized keys of vm {vm}")

            full_command = f"echo {ssh_public_key} > /home/vagrant/.ssh/authorized_keys; echo {ssh_public_key} >> /home/vagrant/ssh_public_key; chmod 600 /home/vagrant/ssh_private_key_file"
            stdout,err = execute_remote_command('127.0.0.1', vm_local_forwarded_port, vm_username, vm_password, full_command)


    print(f"\n[+] vms launched. To ssh to vms, run 'ssh <vm_name>' from cloud instance\n\n")

# using rafay provisioner
def eksabm_rafay_provisioner(input_data):
    
    # collect necessary data from config/input file
    infrastructure_provider = input_data["infrastructure_provider"]
    infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]
    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]

    try:
        cluster_yaml_filename = provisioner_config["config_file_name"]
    except KeyError:
        cluster_yaml_filename = None 

    if cluster_yaml_filename is None:
        cluster_name = provisioner_config["cluster_name"]
        k8s_version = provisioner_config["k8s_version"]
        cp_count = provisioner_config["num_control_plane_nodes"]
        dp_count = provisioner_config["num_worker_nodes"]
        cluster_yaml = None 

    else:
        cluster_name = provisioner_config["cluster_name"]
        cluster_yaml_file=f'{staging_dir}/cluster_configs/{cluster_yaml_filename}'
        provisioner_by_yaml_file=get_provisioner_by_yaml_file(cluster_yaml_file)

        if provisioner_by_yaml_file is None or provisioner_by_yaml_file != provisioner:
            print(f'\nERROR:: cluster file of cluster {cluster_name} does not match with yaml file format of {provisioner}, exiting !!')
            sys.exit(1)

        if os.path.exists(cluster_yaml_file):
                k8s_version,cp_count,dp_count,cluster_yaml = extract_cluster_details_from_cluster_yaml(cluster_yaml_file,provisioner)
        else:
            print(f"\nERROR:: cluster file {cluster_yaml_file} does not exist for cluster {cluster_name}")
            sys.exit(1)

 
    print(f"\n[+] Detected desired cluster spec for provision::  cluster_name: {cluster_name}, k8s_version:{k8s_version}, cp_count:{cp_count}, dp_count:{dp_count}")
    
    rafay_controller_url = provisioner_config["rafay_controller_url"]
    rafay_api_key_file = provisioner_config["rafay_api_key_file"]
    rafay_project_name = provisioner_config["rafay_project_name"]
    gw_name = provisioner_config["gw_name"]
    ssh_public_key = infrastructure_provider_data["ssh_public_key"]

    print(f"\n[+] Detected cluster provisioner config:: cluster_provisioner: rafay_eksabm_cluster, rafay_controller_url: {rafay_controller_url}, rafay_api_key_file:{rafay_api_key_file}, rafay_project_name:{rafay_project_name}, gw_name:{gw_name}")


    # read rafay_api_key from file rafay_api_key_file
    local_filename=os.path.basename(rafay_api_key_file)
    rafay_api_key_file = f"{staging_dir}/{local_filename}"
    with open(rafay_api_key_file, 'r') as f:
        rafay_api_key = f.read().strip()   

    headers = {'X-RAFAY-API-KEYID': rafay_api_key,'Content-Type': 'application/json'}

    eksa_admin_ip = "127.0.0.1"
    eksa_admin_port = 5022  # eksa_admin node ssh port 
    eksa_admin_username = "vagrant"
    eksa_admin_password = "vagrant"
    gw_description = gw_name
    gw_type = 'eksaBareMetal'
    
    hardware_csv_location=f"{eksa_vm_dir}/{cluster_name}/generated_hardware.csv"
    cluster_tinkerbell_ip_file=f"{eksa_vm_dir}/{cluster_name}/tinkerbell_ip"
    cluster_endpoint_ip_file=f"{eksa_vm_dir}/{cluster_name}/endpoint_ip"   
    project_id = get_project_id(rafay_controller_url, rafay_project_name, headers, seq=1)
    
    # Copy the ssh_private_key_file file to the instance
    ssh_copy(staging_dir+"/ssh_private_key_file", "/home/vagrant/", eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, ssh_private_key_path=None,remote_file_name=None)

    # Copy ssh_public_key over 
    full_command = f"echo {ssh_public_key} > /home/{eksa_admin_username}/.ssh/authorized_keys; echo {ssh_public_key} >> /home/vagrant/ssh_public_key; chmod 600 /home/vagrant/ssh_private_key_file"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)

    # uncomment line #PubkeyAuthentication yes in /etc/ssh/sshd_config and restart sshd
    full_command = f"sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config; sudo systemctl restart sshd; sudo cp -p /home/vagrant/ssh_private_key_file /opt/rafay/ssh_private_key_file"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)

   # Create ssh config entry for eksa-admin-1 node on local machine
    ssh_config_entry=f"Host eksa-admin-1\n  HostName {eksa_admin_ip}\n  User {eksa_admin_username}\n  Port {eksa_admin_port}\n  IdentityFile {staging_dir}/ssh_private_key_file\n  StrictHostKeyChecking no\n  UserKnownHostsFile=/dev/null\n"
    with open("/home/ubuntu/.ssh/config", "a") as ssh_config_file:
        ssh_config_file.write(ssh_config_entry)

    # print project_id
    #print(f"\n[+] Detected project_id: {project_id} for project_name: {rafay_project_name}")

    print(f"\n[+] Commencing cluster provision for cluster_name: {cluster_name}, gw {gw_name}, project {rafay_project_name} using provisioner rafay")
    
    # Step 1. Create gateway if it doesn't exist 
    print(f"\n[+] Step 1. Creating gateway: {gw_name}")

    gw = get_gateway(rafay_controller_url, headers, gw_name, project_id)
    if gw is not None:
        print(f'Gateway {gw_name} already exists, skipping creation')
    else:
        create_gateway(rafay_controller_url, headers, gw_name, gw_type, gw_description, project_id, 1)

    # Step 2. Setup gateway 
    gw_setup_cmd = get_gateway_setup_cmd(rafay_controller_url, headers, gw_name, project_id, 2)

    # Step 3. Execute gateway setup command
    execute_gateway_setup_cmd(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, gw_setup_cmd, 3)
    
    # Step 4. Check gateway infraagent status
    check_gateway_infraagent_status(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, 4)
    
    # Step 5. Check gateway status
    check_gateway_status(rafay_controller_url, headers, gw_name, project_id, 5)
    
    # Step 6. Create cluster
    cl = get_cluster(rafay_controller_url, headers, cluster_name, project_id)
    if cl is not None:
        print(f'Cluster {cluster_name} already exists, skipping creation')
    else:
        create_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id,ssh_public_key, 6)
    
    # Step 7. Update cluster
    update_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id, hardware_csv_location, cluster_tinkerbell_ip_file, cluster_endpoint_ip_file, k8s_version,cp_count,dp_count, gw_name, cluster_yaml, ssh_public_key, 7)
    
    # Step 8. Provision cluster
    provision_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id, 8)
    
    # Step 9. Monitor cluster provision progress by checking cluster status condition ClusterSpecApplied is in status InProgress
    monitor_eksabm_cluster_status_progress(rafay_controller_url, headers, conditions_type_list, "ClusterSpecApplied", "InProgress", cluster_name, project_id, 9)
    
    # Step 10. Monitor cluster provision progress by checking cluster status condition ClusterSpecApplied's log output for "Creating new workload cluster"
    monitor_eksabm_condition_debug_log(rafay_controller_url, headers, "ClusterSpecApplied", "EksctlCreateClusterCmdLogs", check_if_show_debug_log_output_contains_termination_condition, None, cluster_name, project_id, 10)
    
    # Step 11. Power manage cluster nodes for provision
    power_manage_cluster_nodes_for_provision(rafay_controller_url, headers, project_id, cluster_name, hardware_csv_location, 11)
    
    # Step 12. Monitor cluster provision progress by checking cluster status condition ClusterSpecApplied is in status Success
    monitor_eksabm_cluster_status_progress(rafay_controller_url, headers, conditions_type_list, "ClusterSpecApplied", "Success", cluster_name, project_id, 12)
    
    # Step 13. Monitor cluster provision progress by checking cluster status condition ClusterHealthy is in status Success
    monitor_eksabm_cluster_status_progress(rafay_controller_url, headers, conditions_type_list, "ClusterHealthy", "Success", cluster_name, project_id, 13)


def eksctl_create_cluster(cluster_dir, cluster_name, eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, seq):
    eksctl_cluster_create_cmd=f"pushd {cluster_dir}; eksctl anywhere create cluster --hardware-csv hardware.csv -f {cluster_name}.yaml 2>&1 | tee -a {cluster_dir}/eksa-create-cluster.log; popd"
    print(f"\n[{seq}.] Creating cluster : {eksctl_cluster_create_cmd}")
    full_command = f"sudo su -c '{eksctl_cluster_create_cmd}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR:: Execution of command to create cluster failed. err: {err}")
        sys.exit(1)
    else:
        print(f"Execution of command to create cluster passed. stdout:\n {stdout}")


# using native provisioner
def eksabm_native_provisioner(input_data):
    
    # collect necessary data from config/input file
    infrastructure_provider = input_data["infrastructure_provider"]
    infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]
    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]

    try:
        cluster_yaml_filename = provisioner_config["config_file_name"]
    except KeyError:
        cluster_yaml_filename = None 

    if cluster_yaml_filename is None:
        cluster_name = provisioner_config["cluster_name"]
        k8s_version = provisioner_config["k8s_version"]
        cp_count = provisioner_config["num_control_plane_nodes"]
        dp_count = provisioner_config["num_worker_nodes"]
        cluster_yaml = None 

    else:
        cluster_name = provisioner_config["cluster_name"]
        cluster_yaml_file=f'{staging_dir}/cluster_configs/{cluster_yaml_filename}'
        provisioner_by_yaml_file=get_provisioner_by_yaml_file(cluster_yaml_file)

        if provisioner_by_yaml_file is None or provisioner_by_yaml_file != provisioner:
            print(f'\nERROR:: cluster file of cluster {cluster_name} does not match with yaml file format of {provisioner}, exiting !!')
            sys.exit(1)

        if os.path.exists(cluster_yaml_file):
                k8s_version,cp_count,dp_count,cluster_yaml = extract_cluster_details_from_cluster_yaml(cluster_yaml_file,provisioner)
        else:
            print(f"\nERROR:: cluster file {cluster_yaml_file} does not exist for cluster {cluster_name}")
            sys.exit(1)


    ssh_public_key = infrastructure_provider_data["ssh_public_key"]
    
    eksa_admin_ip = "127.0.0.1"
    eksa_admin_port = 5022  # eksa_admin node ssh port 
    eksa_admin_username = "vagrant"
    eksa_admin_password = "vagrant"
    hardware_csv_location=f"{eksa_vm_dir}/{cluster_name}/generated_hardware.csv"
    cluster_tinkerbell_ip_file=f"{eksa_vm_dir}/{cluster_name}/tinkerbell_ip"
    cluster_endpoint_ip_file=f"{eksa_vm_dir}/{cluster_name}/endpoint_ip"   

    cluster_dir=f"{staging_dir}/native/{cluster_name}"
    remote_hardware_csv_location=f"{cluster_dir}/hardware.csv"
    remote_cluster_yaml_location=f"{cluster_dir}/{cluster_name}.yaml"

    with open(cluster_tinkerbell_ip_file, 'r') as f:
        tinkerbell_ip = f.read().strip()    
        
    with open(cluster_endpoint_ip_file, 'r') as f:
        endpoint_host_ip = f.read().strip()

    print(f"\n[+] Detected desired cluster spec for provision::  cluster_name: {cluster_name}, k8s_version:{k8s_version}, cp_count:{cp_count}, dp_count:{dp_count}")

    # Copy the ssh_private_key_file file to the instance
    ssh_copy(staging_dir+"/ssh_private_key_file", "/home/vagrant/", eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, ssh_private_key_path=None,remote_file_name=None)

    # Copy ssh_public_key over 
    full_command = f"echo {ssh_public_key} > /home/{eksa_admin_username}/.ssh/authorized_keys; echo {ssh_public_key} >> /home/vagrant/ssh_public_key; chmod 600 /home/vagrant/ssh_private_key_file"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)

    # uncomment line #PubkeyAuthentication yes in /etc/ssh/sshd_config and restart sshd
    full_command = f"sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config; sudo systemctl restart sshd; sudo cp -p /home/vagrant/ssh_private_key_file /opt/rafay/ssh_private_key_file"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)

   # Create ssh config entry for eksa-admin-1 node on local machine
    ssh_config_entry=f"Host eksa-admin-1\n  HostName {eksa_admin_ip}\n  User {eksa_admin_username}\n  Port {eksa_admin_port}\n  IdentityFile {staging_dir}/ssh_private_key_file\n  StrictHostKeyChecking no\n  UserKnownHostsFile=/dev/null\n"
    with open("/home/ubuntu/.ssh/config", "a") as ssh_config_file:
        ssh_config_file.write(ssh_config_entry)

    print(f"\n[+] Provisioning cluster_name: {cluster_name} using provisioner native ")

    # Step 1. ensure existence of cluster directory
    create_dir_command=f"mkdir -p {cluster_dir}"
    print(f"\n[1.] Executing command to create directory on eksa-admin : {create_dir_command}")
    full_command = f"sudo su -c '{create_dir_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR:: Execution of command to create cluster directory failed. err: {err}")
        sys.exit(1)


    # Step 2. create hardware csv file
    with open(hardware_csv_location, 'r') as local_file:
        hardware_csv_content = local_file.read()
    echo_hardware_csv_content_command=f'echo "{hardware_csv_content}" > {remote_hardware_csv_location}'
    print(f"\n[2.] Creating hardware csv file on eksa-admin:\n {echo_hardware_csv_content_command}")
    full_command = f"sudo su -c '{echo_hardware_csv_content_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR:: Execution of command to create hardware csv failed. err: {err}")
        sys.exit(1)
    
    # Step 3. create cluster config file
    if cluster_yaml is not None:
        updated_cluster_yaml = update_tinkerbell_ip(cluster_yaml, tinkerbell_ip, 'native')
        updated_cluster_yaml = update_endpoint_ip(updated_cluster_yaml, endpoint_host_ip, 'native')
        echo_cluster_config_content_command=f'echo "{updated_cluster_yaml}" > {remote_cluster_yaml_location}'
    else:
        cluster_yaml=build_native_eksabm_cluster_spec(cluster_name,k8s_version,cp_count,endpoint_host_ip,dp_count,tinkerbell_ip,ssh_public_key)
        escaped_cluster_yaml = cluster_yaml.replace("'", r"'\''")
        echo_cluster_config_content_command=f'echo "{escaped_cluster_yaml}" > {remote_cluster_yaml_location}'

    print(f"\n[3.] Creating cluster config yaml on eksa-admin:\n {echo_cluster_config_content_command}")
    full_command = f"sudo su -c '{echo_cluster_config_content_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR: Execution of command to create cluster config yaml failed. err: {err}")
        sys.exit(1)

    # Step 4. install eksctl
    install_eksctl_command='curl "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" --silent --location | tar xz -C /tmp; install -m 0755 /tmp/eksctl /usr/local/bin/eksctl'
    print(f"\n[4.] Installing eksctl cli on eksa-admin:\n {install_eksctl_command}")
    full_command = f"sudo su -c '{install_eksctl_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR:: Execution of command to install eksctl cli failed. err: {err}")
        sys.exit(1)

    # Step 5. install yq
    install_yq_command='wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq; chmod +x /usr/bin/yq'
    print(f"\n[5.] Installing yq cli on eksa-admin:\n {install_yq_command}")
    full_command = f"sudo su -c '{install_yq_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err and 'https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64' not in err:
        print(f"\nERROR:: Execution of command to install yq cli failed. err: {err}")
        sys.exit(1)
    
    # Step 6. install eksctl anywhere
    install_eksctl_anywhere_command='RELEASE_VERSION=$(curl https://anywhere-assets.eks.amazonaws.com/releases/eks-a/manifest.yaml --silent --location | yq ".spec.latestVersion"); EKS_ANYWHERE_TARBALL_URL=$(curl https://anywhere-assets.eks.amazonaws.com/releases/eks-a/manifest.yaml --silent --location | yq ".spec.releases[] | select(.version==\\\"$RELEASE_VERSION\\\").eksABinary.$(uname -s | tr A-Z a-z).uri"); curl $EKS_ANYWHERE_TARBALL_URL --silent --location | tar xz ./eksctl-anywhere; install -m 0755 ./eksctl-anywhere /usr/local/bin/eksctl-anywhere'
    print(f"\n[6.] Installing eksctl cli on eksa-admin:\n {install_eksctl_anywhere_command}")
    full_command = f"sudo su -c '{install_eksctl_anywhere_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR:: Execution of command to install eksctl anywhere plugin failed. err: {err}")
        sys.exit(1)


    # Step 7. install kubectl
    install_kubectl_command='export OS="$(uname -s | tr A-Z a-z)"; ARCH=$(test "$(uname -m)" = "x86_64" && echo "amd64" || echo "arm64"); curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/${OS}/${ARCH}/kubectl"; install -m 0755 ./kubectl /usr/local/bin/kubectl'
    print(f"\n[7.] Installing kubectl cli on eksa-admin:\n {install_kubectl_command}")
    full_command = f"sudo su -c '{install_kubectl_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err and '% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current' not in err:
        print(f"\nERROR:: Execution of command to install kubectl cli failed. err: {err}")
        sys.exit(1)


    # Step 8. install docker
    install_docker_command='apt-get update; apt-get -y install ca-certificates curl gnupg; install -m 0755 -d /etc/apt/keyrings; curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg; chmod a+r /etc/apt/keyrings/docker.gpg; echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null; apt-get update; apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin'
    print(f"\n[8.] Installing docker on eksa-admin:\n {install_docker_command}")
    full_command = f"sudo su -c '{install_docker_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    # if err:
    #     print(f"\nERROR:: Execution of command to install docker failed. err: {err}")
    #     # sys.exit(1)
    # else:
    #     print(f"\nExecution of command to install docker passed. stdout: {stdout}")

    # Step 9. create cluster
    thread = threading.Thread(target=eksctl_create_cluster, args=(cluster_dir, cluster_name, eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, 9))
    thread.start()
    print("   [+] Cluster creation in progress...")

    # Step 10. monitor 'Creating new workload cluster' in cluster creation logs
    fetch_cluster_creation_logs_command=f'cat {cluster_dir}/eksa-create-cluster.log'
    wait_count=0
    while True:
        print(f"\n[10.] Monitoring cluster creation logs for string: 'Creating new workload cluster' : {fetch_cluster_creation_logs_command}")
        full_command = f"sudo su -c '{fetch_cluster_creation_logs_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err and 'No such file or directory' not in err:
            print(f"\nERROR:: Execution of command to fetch cluster creation logs failed. err: {err}")
            sys.exit(1)
        else:
            print(f"   [+] Execution of command to fetch cluster creation logs passed. stdout:\n {stdout}")
            if 'Creating new workload cluster' in stdout:
                break
        print(f"   [+]  .... waiting for 60 seconds to recheck logs .... ")
        time.sleep(60*1)
    
    # Step 11. monitor workflow and machine status & power cycle based on that
    wait_count=0
    fetch_workflows_command=f'KUBECONFIG={cluster_dir}/{cluster_name}/generated/{cluster_name}.kind.kubeconfig kubectl get workflows -A -o yaml'
    fetch_machine_status_command=f'KUBECONFIG={cluster_dir}/{cluster_name}/generated/{cluster_name}.kind.kubeconfig kubectl get machines.cluster.x-k8s.io -A'
    while True:
        #print('*****************************')
        print(f"\n[11.] Fetching Tinkerbell workflows from cluster : {fetch_workflows_command}")
        full_command = f"sudo su -c '{fetch_workflows_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err:
            print(f"\nERROR: Execution of command to fetch workflows failed. err: {err}")
            break
        else:
            #print(f"\nExecution of command to fetch workflows passed.  stdout: {stdout}")
            workflows_list=stdout
        
        print(f"   [+] Fetching machine status from cluster to perform power management tasks: {fetch_machine_status_command}")
        full_command = f"sudo su -c '{fetch_machine_status_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err:
            print(f"\nERROR: Execution of command to fetch machine status failed. err: {err}")
            break
        else:
            print(f"   [+] Execution of command to fetch machine status passed. stdout:\n {stdout}")
            action_output=stdout
        
        cluster_node_names=get_cluster_node_names(hardware_csv_location)
        condition_type="ClusterSpecApplied"
        target_action="MachineStatus"

        term_cnd,term_out = check_if_show_debug_log_output_contains_termination_condition(condition_type,target_action,action_output,cluster_node_names,workflows_list)
        if term_cnd:
            break
        print(f"   [+]  .... waiting for 5 minutes to recheck logs .... ")
        time.sleep(60*5)


    # Step 12. monitor 'Cluster created' in cluster creation logs
    fetch_cluster_creation_logs_command=f'cat {cluster_dir}/eksa-create-cluster.log'
    wait_count=0
    while True:
        print(f"\n[12.] Monitoring cluster creation logs for cluster creation success message: {fetch_cluster_creation_logs_command}")
        full_command = f"sudo su -c '{fetch_cluster_creation_logs_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err and 'No such file or directory' not in err:
            print(f"\nERROR:: Execution of command to fetch cluster creation logs failed. err: {err}")
            sys.exit(1)
        else:
            print(f"   [+] Execution of command to fetch cluster creation logs passed. stdout: {stdout}")
            if 'Cluster created' in stdout:
                break
        print(f"   [+]  .... waiting for 60 seconds to recheck logs .... ")
        time.sleep(60*1)

    return

# provision cluster
def provision_cluster(input_data):  
    # collect necessary data from input file
    provisioner = input_data["provisioner"]
    
    if provisioner == "rafay_eksabm_cluster":   
        eksabm_rafay_provisioner(input_data)
    elif provisioner == "eksabm_cluster":
        eksabm_native_provisioner(input_data)


'''
def upgrade_eksabm_cluster(rafay_controller_url, headers,cluster_name, project_id, k8s_version, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name+'/upgrade'
    method = 'POST'

    data = {
        "metadata": {
            "name": cluster_name
            },
        "eksaBmVersion": k8s_version
    }

    resp = make_request(url, method, headers, data)
    if resp:
        print(f"\n[{seq}.] Cluster provision request submitted successfully. cluster_name:{cluster_name}, project_id:{project_id}")
    else:
        print(f"\nERROR: Cluster provision request failed. Exiting... cluster_name:{cluster_name}, project_id:{project_id}")
        sys.exit(1)

    return resp


def rafay_upgrader(cluster_provision_ctx):
    cluster_name = cluster_provision_ctx["cluster_name"]
    k8s_version = cluster_provision_ctx["k8s_version"]
    cp_count = cluster_provision_ctx["cp_count"]
    dp_count = cluster_provision_ctx["dp_count"]

    print(f"\n[+] Detected desired cluster spec for upgrade::  cluster_name: {cluster_name}, k8s_version:{k8s_version}, cp_count:{cp_count}, dp_count:{dp_count}")
    
    rafay_controller_url = cluster_provision_ctx["rafay_controller_url"]
    rafay_api_key_file = cluster_provision_ctx["rafay_api_key_file"]
    rafay_project_name = cluster_provision_ctx["rafay_project_name"]
    gw_name = cluster_provision_ctx["gw_name"]

    local_filename=os.path.basename(rafay_api_key_file)
    rafay_api_key_file = f"{staging_dir}/{local_filename}"
    with open(rafay_api_key_file, 'r') as f:
        rafay_api_key = f.read().strip()   

    headers = {'X-RAFAY-API-KEYID': rafay_api_key,'Content-Type': 'application/json'}

    eksa_admin_ip = "127.0.0.1"
    eksa_admin_port = 5022  # eksa_admin node ssh port 
    eksa_admin_username = "vagrant"
    eksa_admin_password = "vagrant"
    gw_description = gw_name
    gw_type = 'eksaBareMetal'
    hardware_csv_location=f"{vm_dir}/{cluster_name}/generated_hardware.csv"
    cluster_tinkerbell_ip_file=f"{vm_dir}/{cluster_name}/tinkerbell_ip"
    cluster_endpoint_ip_file=f"{vm_dir}/{cluster_name}/endpoint_ip"   

    project_id = get_project_id(rafay_controller_url, rafay_project_name, headers, seq=1)

    launch_vbox_vms(cluster_provision_ctx)

    check_gateway_infraagent_status(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, 2)
    
    check_gateway_status(rafay_controller_url, headers, gw_name, project_id, 3)
    
    cl = get_cluster(rafay_controller_url, headers, cluster_name, project_id)
    if cl is None:
        print(f'Cluster {cluster_name} does not exists, skipping upgrade')

    upgrade_eksabm_cluster(rafay_controller_url, headers, cluster_name, project_id, k8s_version)

    monitor_eksabm_cluster_status_progress(rafay_controller_url, headers, conditions_type_list, "ClusterUpgraded", "InProgress", cluster_name, project_id, 4)

    power_manage_cluster_nodes_for_provision(rafay_controller_url, headers, project_id, cluster_name, hardware_csv_location, 5)

    monitor_eksabm_cluster_status_progress(rafay_controller_url, headers, conditions_type_list, "ClusterUpgraded", "Success", cluster_name, project_id, 6)

def eksctl_upgrade_cluster(cluster_dir, cluster_name, eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, seq):
    eksctl_cluster_upgrade_cmd=f"pushd {cluster_dir}; eksctl anywhere upgrade cluster --hardware-csv hardware.csv -f {cluster_name}.yaml 2>&1 | tee -a {cluster_dir}/eksa-upgrade-cluster.log; popd"
    print(f"[{seq}.] command to upgrade cluster : {eksctl_cluster_upgrade_cmd}")
    full_command = f"sudo su -c '{eksctl_cluster_upgrade_cmd}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR: Execution of command to upgrade cluster failed. err: {err}")
        sys.exit(1)
    else:
        print(f"\nExecution of command to upgrade cluster passed. stdout: {stdout}")


def native_upgrader(cluster_provision_ctx):
     # collect necessary data from config/input file
    cluster_name = cluster_provision_ctx["cluster_name"]
    k8s_version = cluster_provision_ctx["k8s_version"]
    cp_count = cluster_provision_ctx["cp_count"]
    dp_count = cluster_provision_ctx["dp_count"]
    ssh_public_key = cluster_provision_ctx["ssh_public_key"]
    
    eksa_admin_ip = "127.0.0.1"
    eksa_admin_port = 5022  # eksa_admin node ssh port 
    eksa_admin_username = "vagrant"
    eksa_admin_password = "vagrant"
    hardware_csv_location=f"{vm_dir}/{cluster_name}/generated_hardware.csv"
    cluster_tinkerbell_ip_file=f"{vm_dir}/{cluster_name}/tinkerbell_ip"
    cluster_endpoint_ip_file=f"{vm_dir}/{cluster_name}/endpoint_ip"   

    cluster_dir=f"{staging_dir}/native/{cluster_name}"
    remote_hardware_csv_location=f"{cluster_dir}/hardware.csv"
    remote_cluster_yaml_location=f"{cluster_dir}/{cluster_name}.yaml"

    with open(cluster_tinkerbell_ip_file, 'r') as f:
        tinkerbell_ip = f.read().strip()    
        
    with open(cluster_endpoint_ip_file, 'r') as f:
        endpoint_host_ip = f.read().strip()

    print(f"\n[+] Detected desired cluster spec for provision::  cluster_name: {cluster_name}, k8s_version:{k8s_version}, cp_count:{cp_count}, dp_count:{dp_count}")

    # check existence of cluster directory
    check_dir_command=f'if [ -d "{cluster_dir}" ]; then echo "OK"; else echo "NOT OK"; fi'
    print(f"[1.] command to check directory : {check_dir_command}")
    full_command = f"sudo su -c '{check_dir_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR: Execution of command to check cluster directory failed. err: {err}")
        sys.exit(1)
    else:
        print(f"\nExecution of command to check cluster directory passed. stdout: {stdout}")

    if stdout != "OK":
        print("\nERROR: Cluster directory does not exist")
        sys.exit(1)

    # create hardware csv file
    with open(hardware_csv_location, 'r') as local_file:
        hardware_csv_content = local_file.read()
    echo_hardware_csv_content_command=f'echo "{hardware_csv_content}" > {remote_hardware_csv_location}'
    print(f"[2.] command to create hardware csv yaml : {echo_hardware_csv_content_command}")
    full_command = f"sudo su -c '{echo_hardware_csv_content_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR: Execution of command to create hardware csv failed. err: {err}")
        sys.exit(1)
    else:
        print(f"\nExecution of command to create hardware csv passed. stdout: {stdout}")
    
    # create cluster config file
    cluster_yaml=build_native_eksabm_cluster_spec(cluster_name,k8s_version,cp_count,endpoint_host_ip,dp_count,tinkerbell_ip,ssh_public_key)
    escaped_cluster_yaml = cluster_yaml.replace("'", r"'\''")
    echo_cluster_config_content_command=f'echo "{escaped_cluster_yaml}" > {remote_cluster_yaml_location}'
    print(f"[3.] command to create cluster config yaml : {echo_cluster_config_content_command}")
    full_command = f"sudo su -c '{echo_cluster_config_content_command}'"
    stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
    if err:
        print(f"\nERROR: Execution of command to create cluster config yaml failed. err: {err}")
        sys.exit(1)
    else:
        print(f"\nExecution of command to create cluster config yaml passed. stdout: {stdout}")

    # upgrade cluster
    thread = threading.Thread(target=eksctl_upgrade_cluster, args=(cluster_dir, cluster_name, eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, 4))
    thread.start()
    print("cluster upgrade in progress...")

    # monitor 'Upgrading workload cluster' in cluster upgrade logs
    fetch_cluster_upgrade_logs_command=f'cat {cluster_dir}/eksa-upgrade-cluster.log'
    wait_count=0
    while True:
        print(f"[5.] command to fetch cluster upgrade logs : {fetch_cluster_upgrade_logs_command}")
        full_command = f"sudo su -c '{fetch_cluster_upgrade_logs_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err and 'No such file or directory' not in err:
            print(f"\nERROR: Execution of command to fetch cluster upgrade logs failed. err: {err}")
            sys.exit(1)
        else:
            print(f"\nExecution of command to fetch cluster upgrade logs passed. stdout: {stdout}")
            if 'Upgrading workload cluster' in stdout:
                break
            else:
                wait_count+=1
                if wait_count>5:
                    print("\nERROR: Time exceeded while looking for 'Upgrading workload cluster' in cluster upgrade logs")
                    sys.exit(1)
        time.sleep(60*1)
    
    # monitor workflow and machine status & power cycle based on that
    wait_count=0
    fetch_workflows_command=f'KUBECONFIG={cluster_dir}/{cluster_name}/generated/{cluster_name}.kind.kubeconfig kubectl get workflows -A -o yaml'
    fetch_machine_status_command=f'KUBECONFIG={cluster_dir}/{cluster_name}/generated/{cluster_name}.kind.kubeconfig kubectl get machines.cluster.x-k8s.io -A'
    while True:
        print('*****************************')
        print(f"[6.] command to fetch workflows : {fetch_workflows_command}")
        full_command = f"sudo su -c '{fetch_workflows_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err:
            print(f"\nERROR: Execution of command to fetch workflows failed. err: {err}")
            sys.exit(1)
        else:
            print(f"\nExecution of command to fetch workflows passed.")
            workflows_list=stdout
        
        print(f"[6.] command to fetch machine status : {fetch_machine_status_command}")
        full_command = f"sudo su -c '{fetch_machine_status_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err:
            print(f"\nERROR: Execution of command to fetch machine status failed. err: {err}")
            sys.exit(1)
        else:
            print(f"\nExecution of command to fetch machine status passed. stdout: {stdout}")
            action_output=stdout
        
        cluster_node_names=get_cluster_node_names(hardware_csv_location)
        condition_type="ClusterUpgraded"
        target_action="MachineStatus"

        term_cnd,term_out = check_if_show_debug_log_output_contains_termination_condition(condition_type,target_action,action_output,cluster_node_names,workflows_list)
        if term_cnd:
            break
        else:
            wait_count+=1
            if wait_count>5:
                print("\nERROR: Time exceeded while monitoring and power cycling")
                sys.exit(1)

        time.sleep(60*5)


    # monitor 'Cluster upgraded' in cluster upgrade logs
    fetch_cluster_upgrade_logs_command=f'cat {cluster_dir}/eksa-upgrade-cluster.log'
    wait_count=0
    while True:
        print(f"[12.] command to fetch cluster upgrade logs : {fetch_cluster_upgrade_logs_command}")
        full_command = f"sudo su -c '{fetch_cluster_upgrade_logs_command}'"
        stdout,err = execute_remote_command(eksa_admin_ip, eksa_admin_port, eksa_admin_username, eksa_admin_password, full_command)
        if err and 'No such file or directory' not in err:
            print(f"\nERROR: Execution of command to fetch cluster upgrade logs failed. err: {err}")
            sys.exit(1)
        else:
            print(f"\nExecution of command to fetch cluster upgrade logs passed. stdout: {stdout}")
            if 'Cluster created' in stdout:
                break
            else:
                wait_count+=1
                if wait_count>5:
                    print("\nERROR: Time exceeded while looking for 'Cluster created' in cluster upgrade logs")
                    sys.exit(1)
        time.sleep(60*1)

    return

# upgrade cluster
def upgrade_cluster(cluster_provision_ctx):  
    
    if cluster_provision_ctx["cluster_provisioner"] == "rafay":   
        rafay_upgrader(cluster_provision_ctx)
    elif cluster_provision_ctx["cluster_provisioner"] == "native":
        print(f"upgrade using native provisioner")
    else:
        print(f"\n[+] Detected Unsupported cluster provisioner...skipping cluster provision: {cluster_provision_ctx['cluster_provisioner']}")
'''

if __name__ == "__main__":

    print(f"\n[+] Processing input file {input_yaml}")

    # Read the input YAML file
    input_data = process_input_yaml(input_yaml)
    if not input_data:
        print(f"[-] Error processing input YAML file {input_yaml}")
        exit(1)

    # Extract provisioner from input.yaml 
    provisioner = input_data["provisioner"]
    print(f"\n[+] Detected provisioner: {provisioner}")
    provisioner_config = input_data["provisioner_config"][provisioner]

    # Process "rafay_eksabm_cluster" or "eksabm_cluster" provisioner
    if provisioner == "rafay_eksabm_cluster" or provisioner == "eksabm_cluster":
        # Launch virtual infrastructure using vagrant and Virtualbox 
        launch_eksabm_vbox_vms(input_data)

        operation_type = provisioner_config["operation_type"]
        if operation_type not in valid_operations:
            print(f"\n[INFO] Invalid operation type: {operation_type}")

        # Provision eksabm cluster
        if operation_type == "provision":
            provision_cluster(input_data)
        # elif operation_type == "upgrade": # upgrade is untested
            #upgrade_cluster(cluster_provision_ctx)
    
    elif provisioner == "vms_only":
        # Launch virtual infrastructure using vagrant and Virtualbox for vms_only provisioner
        launch_vbox_vms(input_data)
    
    elif provisioner == "none":
        # Process "vms_only" provisioner
        print(f"\n[+] Detected none provisioner. :EXITING:")
    
    else:
        print(f"\n[+] Detected Unsupported provisioner: {provisioner} :EXITING:")
