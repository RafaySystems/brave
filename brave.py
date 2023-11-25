#!/usr/bin/env python3
import yaml
import os 
import json 
import paramiko
import sys 
import subprocess
import json

input_yaml = "input.yaml"
tf_dir_prefix = "tf"   
remote_staging_dir="/opt/rafay/"
ssh_config_path = os.path.expanduser('~/.ssh/config')

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

# launch the infrastructure instance 
def launch_infra_on_cloud_provider(tf_dir):
    try:
        original_directory = os.getcwd()
        print(f"\n[+] Switching to  directory {tf_dir} to launch infrastructure")
        # Run the terraform commands
        os.chdir(tf_dir)
        os.system("terraform init")
        #os.system("terraform plan")
        os.system("terraform apply -auto-approve")
        os.system("terraform output -json > terraform_output.json")

        with open('terraform_output.json', 'r') as json_file:
            data = json.load(json_file)
            instance_public_ip = data.get("instance_public_ip", {}).get("value")
        
        print(f"\n[+] IP of launched instance: {instance_public_ip}")
        print(f"\n[+] Switching back to directory {original_directory}")
        os.chdir(original_directory)
    except Exception as e:
        print(f"[-] Error launching infrastructure : {e}")
        exit(1)
    return instance_public_ip 

# execute remote command
def execute_remote_command(host, port, username, password, command, ssh_private_key_path=None):

    print(f"\n[+] Executing on remote host: {host} command: {command}")

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if ssh_private_key_path:
            # Connect to the remote host using private key
            private_key = paramiko.RSAKey(filename=ssh_private_key_path)
            ssh_client.connect(host, port=port, username=username, pkey=private_key)
        else:
            # Connect to the remote host using password
            ssh_client.connect(host, port=port, username=username, password=password)

        # Execute the command on the remote host
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Read the output of the command
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        print(f"\n[+] Executed on remote host: {host} command: {command} stdout: {output} stderr: {error}")

    except paramiko.AuthenticationException:
        print(f"ERROR:: SSH authentication failed to eksa-admin host {host}:{port} username:{username}")
        sys.exit(1)
    except paramiko.SSHException as ssh_exception:
        print(f"ERROR:: SSH error when connecting to eksa-admin host {host}:{port} username:{username} error: {ssh_exception}")
        sys.exit(1)
    finally:
        ssh_client.close()

    return output, error

# execute remote command in an interactive shell
def execute_remote_command_shell(hostname, port, username, password, command, ssh_private_key_path=None):

    # Initialize an SSH client
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote system
        if ssh_private_key_path:
            # Connect to the remote host using private key
            private_key = paramiko.RSAKey(filename=ssh_private_key_path)
            client.connect(hostname, port=port, username=username, pkey=private_key)
        else:
            # Connect to the remote host using password
            client.connect(hostname, port=port, username=username, password=password)

        # Open a SSH session
        ssh_session = client.invoke_shell()

        print(f"\nSending command {command} to {hostname}:{port}")
        # Send the command to the remote system

        ssh_session.send(command)

        # Read and print the output from the command
        while True:
            output = ssh_session.recv(1024).decode('utf-8')
            if ('Cluster created' in output) or ('Traceback' in output) or ('ERROR::' in output) or (':EXITING:' in output) or ('vms launched.' in output):
                print(output, end='')
                ssh_session.close()
                client.close()
                break
            if not output:
                break
            print(output, end='')

    except Exception as e:
        print(f"Error: {str(e)}")
    

    finally:
        # Close the SSH session and the client
        ssh_session.close()
        client.close()


# copy files recursively over SSH to the infra instanc
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


# populate files on the instance
def populate_remote_files(remote_host, remote_port, remote_username, remote_password, remote_private_key_path=None):
   
    # Create staging directory on the instance
    ssh_command = f"sudo mkdir -p {remote_staging_dir}; sudo chown -R {remote_username} {remote_staging_dir}"
    execute_remote_command(remote_host, remote_port, remote_username, remote_password, ssh_command, remote_private_key_path)
   
    # Copy the input.yaml file to the instance
    ssh_copy("./input.yaml", remote_staging_dir, remote_host, remote_port, remote_username, "", ssh_private_key_path=remote_private_key_path,remote_file_name=None)
    
    # Copy the vmscripts directory to the instance
    ssh_copy("./vm-scripts", remote_staging_dir, remote_host, remote_port, remote_username, "", ssh_private_key_path=remote_private_key_path,remote_file_name=None)

    # Copy the cluster_configs directory to the instance
    ssh_copy("./cluster_configs", remote_staging_dir, remote_host, remote_port, remote_username, "", ssh_private_key_path=remote_private_key_path,remote_file_name=None)

   # Copy the ssh_private_key_file file to the instance
    ssh_copy(remote_private_key_path, remote_staging_dir, remote_host, remote_port, remote_username, "", ssh_private_key_path=remote_private_key_path,remote_file_name="ssh_private_key_file")

    ssh_command = f"sudo chown -R {remote_username} {remote_staging_dir}; chmod 600 {remote_staging_dir}/ssh_private_key_file; sudo chmod +x {remote_staging_dir}/vm-scripts/*"
    execute_remote_command(remote_host, remote_port, remote_username, remote_password, ssh_command, remote_private_key_path)

   # Create systemd script to resurrect vms on reboot
    ssh_command = f"sudo cp -p {remote_staging_dir}/vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service"
    execute_remote_command(remote_host, remote_port, remote_username, remote_password, ssh_command, remote_private_key_path)


# copy code and execute
def copy_code_to_remote_host_and_execute(input_data, remote_host):
    # Populate files on the instance
    infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]
    remote_username = "ubuntu"
    remote_private_key_path = infrastructure_provider_data["ssh_private_key_file"]
    remote_port = 22
    populate_remote_files(remote_host, remote_port, remote_username, "", remote_private_key_path)

    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]
    if provisioner == "rafay_eksabm_cluster":
        rafay_api_key_file = provisioner_config["rafay_api_key_file"]

    if provisioner == "rafay_eksabm_cluster" and rafay_api_key_file:
        # Copy the rafay apikey to the instance
        print(f"\n[+] Preparing credentials : {rafay_api_key_file}")
        ssh_copy(rafay_api_key_file, remote_staging_dir, remote_host, remote_port, remote_username, "", remote_private_key_path)

    # Install the dependencies on the instance
    print(f"\n[+] Installing required system packages on {remote_host}")
    ssh_command = f"sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip"
    execute_remote_command(remote_host, remote_port, remote_username, "", ssh_command, remote_private_key_path)

    print(f"\n[+] Installing required python packages on {remote_host}")
    # Install the dependencies on the instance
    ssh_command = f"sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko"
    execute_remote_command(remote_host, remote_port, remote_username, "", ssh_command, remote_private_key_path)

    print(f"\n[+] Executing script on {remote_host}")
    # Execute the autobot.py on the instance
    ssh_command = f"cd {remote_staging_dir}; sudo python3 vm-scripts/autobot.py\n"
    #ssh_command = f"cd {remote_staging_dir}; cat /home/ubuntu/test\n"
    execute_remote_command_shell(remote_host, remote_port, remote_username, "", ssh_command, remote_private_key_path)

def check_file_path(file_path):
    return file_path is not None and os.path.exists(file_path)

def check_all_input_file_paths(input_data):
    all_paths = []
    provisioner = input_data["provisioner"]
    provisioner_config = input_data["provisioner_config"][provisioner]
   
    if provisioner == "rafay_eksabm_cluster":     
        all_paths.append(provisioner_config["rafay_api_key_file"])
    
    infrastructure_provider = input_data["infrastructure_provider"]
    infrastructure_provider_data = input_data["infrastructure_provider_config"][infrastructure_provider]
    if infrastructure_provider == "oci" :
        all_paths.append(infrastructure_provider_data["private_key_path"])
        all_paths.append(infrastructure_provider_data["ssh_private_key_file"])
    elif infrastructure_provider == "infra_exists" or infrastructure_provider == "aws":
        all_paths.append(infrastructure_provider_data["ssh_private_key_file"])
    
    for file_path in all_paths:
        if not check_file_path(file_path):
            print(f"ERROR:: the file path '{file_path}' does not exist.")
            sys.exit(1)


# Insert or Update SSH config entry
def update_ssh_config_entry(host_name, host_ip, ssh_private_key_file):
    # Define the new host entry
    new_host_entry = f"""
Host {host_name}
  Hostname {host_ip}
  StrictHostKeyChecking no
  IdentityFile {ssh_private_key_file}
  User ubuntu
"""
    # if ~/.ssh/config does not exist, create it
    if not os.path.exists(ssh_config_path):
        with open(ssh_config_path, "w") as file:
            file.write("#\n")

    # Read the existing SSH config file
    with open(ssh_config_path, "r") as file:
        ssh_config = file.readlines()

    # Find the index of the start and end of the existing host entry
    start_index = -1
    end_index = -1
    in_host_section = False

    for i, line in enumerate(ssh_config):
        if line.strip().startswith("Host ") and line.strip().endswith(host_name):
            start_index = i
            in_host_section = True
        elif in_host_section and (not line.strip() or line.strip().startswith("Host ")):
            end_index = i - 1
            break

    # Remove the existing host entry if it was found
    if start_index != -1 and end_index != -1:
        del ssh_config[start_index:end_index + 1]

    # Inject the new host entry into the SSH config
    ssh_config.extend([new_host_entry, "\n"])

    # Write the updated SSH config file
    with open(ssh_config_path, "w") as file:
        file.writelines(ssh_config)

    print("SSH config updated successfully.")


if __name__ == "__main__":
    print(f"\n[+] Processing input file {input_yaml}")

    # Read the input YAML file
    input_data = process_input_yaml(input_yaml)
    if not input_data:
        print(f"[-] Error processing input YAML file {input_yaml}")
        exit(1)

    check_all_input_file_paths(input_data)

    infrastructure_provider = input_data["infrastructure_provider"]
    print(f"\n[+] Detected infrastructure provider: {infrastructure_provider}")

    tf_dir = f"{tf_dir_prefix}/{infrastructure_provider}"
    tf_out_json_file = f"{tf_dir}/terraform_output.json"

    provisioner = input_data["provisioner"]
    print(f"\n[+] Detected cluster provisioner: {provisioner}")

    provisioner_config = input_data["provisioner_config"][provisioner]
    if provisioner == "rafay_eksabm_cluster":
        rafay_api_key_file = provisioner_config["rafay_api_key_file"]


    print(f"\n[+] Launching infrastructure on provider {infrastructure_provider}")

    if infrastructure_provider == "oci":  
        # Launch the infrastructure instance on OCI
        remote_host = launch_infra_on_cloud_provider(tf_dir)
        host_name = input_data["infrastructure_provider_config"]["oci"]["host_name"]
        ssh_private_key_file = input_data["infrastructure_provider_config"]["oci"]["ssh_private_key_file"]
        #remote_host='144.24.3.64'
        print(f"\n[+] Waiting 2 minutes to allow infrastructure to boot up on {infrastructure_provider}")
        import time
        time.sleep(60*2)  
    elif infrastructure_provider == "infra_exists":
        remote_host = input_data["infrastructure_provider_config"]["infra_exists"]["ssh_host_ip"] 
        host_name = input_data["infrastructure_provider_config"]["infra_exists"]["host_name"]
        ssh_private_key_file = input_data["infrastructure_provider_config"]["infra_exists"]["ssh_private_key_file"]
    elif infrastructure_provider == "aws":  
        # Launch the infrastructure instance on AWS
        remote_host = launch_infra_on_cloud_provider(tf_dir)
        host_name = input_data["infrastructure_provider_config"]["aws"]["host_name"]
        ssh_private_key_file = input_data["infrastructure_provider_config"]["aws"]["ssh_private_key_file"]
        #remote_host='141.148.174.92'       
        print(f"\n[+] Waiting 2 minutes to allow infrastructure to boot up on {infrastructure_provider}")
        import time
        time.sleep(60*2)          
    
    update_ssh_config_entry(host_name, remote_host, ssh_private_key_file)
    
    copy_code_to_remote_host_and_execute(input_data,remote_host)
