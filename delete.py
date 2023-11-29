#!/usr/bin/env python3
import yaml
import os 
import json 
import paramiko
import sys 
import requests

input_yaml = "input.yaml"
tf_dir_prefix = "tf"   
remote_staging_dir="/opt/rafay/"

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

        # Extract the provider 
        infrastructure_provider = input_data["infrastructure_provider"]
        infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]

        if infrastructure_provider == "oci":
            # Create the terraform.tfvars content
            tfvars_content = f"tenancy_ocid = \"{infrastructure_provider_data['tenancy_ocid']}\"\nregion = \"{infrastructure_provider_data['region']}\"\nhost_name = \"{infrastructure_provider_data['host_name']}\"\nuser_ocid = \"{infrastructure_provider_data['user_ocid']}\"\nprivate_key_path = \"{infrastructure_provider_data['private_key_path']}\"\nfingerprint = \"{infrastructure_provider_data['fingerprint']}\"\ninstance_flex_memory_in_gbs = {infrastructure_provider_data['instance_flex_memory_in_gbs']}\ninstance_flex_ocpus = {infrastructure_provider_data['instance_flex_ocpus']}\n\nssh_public_key = \"{infrastructure_provider_data['ssh_public_key']}\"\n"
        elif infrastructure_provider == "aws":
            # Create the terraform.tfvars content
            tfvars_content = f"region = \"{infrastructure_provider_data['region']}\"\nhost_name = \"{infrastructure_provider_data['host_name']}\"\ninstance_type = \"{infrastructure_provider_data['instance_type']}\"\nssh_public_key = \"{infrastructure_provider_data['ssh_public_key']}\"\nssh_key_name = \"{infrastructure_provider_data['ssh_key_name']}\"\n"

        if infrastructure_provider == "oci" or infrastructure_provider == "aws": 
            tf_dir = f"{tf_dir_prefix}/{infrastructure_provider}"
            tf_file_path = f"{tf_dir}/terraform.tfvars"
            print(f"\n[+] Generating terraform file {tf_file_path}")
            with open(tf_file_path, "w") as tfvars_file:
                tfvars_file.write(tfvars_content)

    except Exception as e:
        print(f"[-] Error processing input YAML file {input_yaml}: {e}")
        exit(1)
    
    return input_data

# destroy the infrastructure instance 
def destroy_infra_on_cloud_provider(tf_dir):
    try:
        original_directory = os.getcwd()
        print(f"\n[+] Switching to  directory {tf_dir} to destroy infrastructure")
        os.chdir(tf_dir)
        os.system("terraform destroy -auto-approve")

        print(f"\n[+] Switching back to directory {original_directory}")
        os.chdir(original_directory)
    except Exception as e:
        print(f"[-] Error destroy infrastructure: {e}")
        exit(1)

def get_project_id(rafay_controller_url, project_name, headers, seq=1):
    url = rafay_controller_url+'/auth/v1/projects/'
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

def get_gateway(rafay_controller_url, headers, gw_name, project_id, seq=1):

    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway/'+gw_name
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        return resp.json()

    return None

def get_cluster(rafay_controller_url, headers, cluster_name, project_id, seq=1):

    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/cluster/'+cluster_name
    method = 'GET'

    resp = make_request(url, method, headers, "")

    if resp:
        return resp.json()

    return None

def delete_gateway(rafay_controller_url , headers, gw_name, project_id, seq=1):
    url = rafay_controller_url+'/v2/infra/project/'+project_id+'/gateway/'+gw_name
    method = 'DELETE'

    resp = make_request(url, method, headers, "")
    if resp:
        print(f"\n[{seq}.] Gateway deletion successful. gw_name:{gw_name}, project_id:{project_id}")
    else:
        print(f"\nERROR: Gateway deletion failed. gw_name:{gw_name}, project_id:{project_id}")
        
    return resp

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


if __name__ == "__main__":

    print(f"\n[+] Processing input file {input_yaml}")

    # Read the input YAML file
    input_data = process_input_yaml(input_yaml)
    if not input_data:
        print(f"[-] Error processing input YAML file {input_yaml}")
        exit(1)

    infrastructure_provider = input_data["infrastructure_provider"]
    print(f"\n[+] Detected infrastructure provider: {infrastructure_provider}")

    tf_dir = f"{tf_dir_prefix}/{infrastructure_provider}"
    tf_out_json_file = f"{tf_dir}/terraform_output.json"

    print(f"\n[+] Destroying infrastructure on provider {infrastructure_provider}")
    # run terraform destroy
    if infrastructure_provider == "oci" or infrastructure_provider == "aws":
        destroy_infra_on_cloud_provider(tf_dir)

    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]    
    print(f"\n[+] Detected provisioner: {provisioner}")
    

    if provisioner == "rafay_eksabm_cluster":
        print(f"\n[+] Deleting gateway & cluster on provisioner {provisioner}")
       
        rafay_api_key_file = provisioner_config["rafay_api_key_file"]

        with open(rafay_api_key_file, 'r') as f:
            rafay_api_key = f.read().strip() 

        rafay_controller_url = provisioner_config["rafay_controller_url"]
        # check for trailing / in rafay_controller_url and remove it
        if rafay_controller_url.endswith('/'):
            rafay_controller_url = rafay_controller_url[:-1]
        gw_name = provisioner_config["rafay_eksabm_gateway_name"]
        rafay_project_name = provisioner_config["rafay_project_name"]
        cluster_name = provisioner_config["cluster_name"]

        headers = {'X-RAFAY-API-KEYID': rafay_api_key,'Content-Type': 'application/json'}
        project_id = get_project_id(rafay_controller_url, rafay_project_name, headers, seq=1)


        cl = get_cluster(rafay_controller_url, headers, cluster_name, project_id)
        if cl is not None:
            delete_eksabm_cluster_force(rafay_controller_url, headers, cluster_name, project_id)
        else:
            print(f'Cluster {cluster_name} does not exist')
        
        gw = get_gateway(rafay_controller_url, headers, gw_name, project_id)
        if gw is not None:
            delete_gateway(rafay_controller_url, headers, gw_name, project_id)
        else:
            print(f'Gateway {gw_name} does not exist')
    


    
    
    
    
