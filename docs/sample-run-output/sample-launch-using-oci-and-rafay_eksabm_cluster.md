
```sh

$ source venv/bin/activate

$ ./brave.py

[+] Processing input file input.yaml

[+] Generating terraform file tf/oci/terraform.tfvars

[+] Detected infrastructure provider: oci

[+] Detected cluster provisioner: rafay_eksabm_cluster

[+] Launching infrastructure on provider oci

[+] Switching to  directory tf/oci to launch infrastructure

------ TERRAFORM OUTPUT ----------

Apply complete! Resources: 9 added, 0 changed, 0 destroyed.

Outputs:

instance_public_ip = "158.101.11.162"

[+] IP of launched instance: 158.101.11.162

[+] Switching back to directory /Users/rgill/brave

[+] Waiting 2 minutes to allow infrastructure to boot up on oci
SSH config updated successfully.

[+] Executing on remote host: 158.101.11.162 command: sudo mkdir -p /opt/rafay/; sudo chown -R ubuntu /opt/rafay/

[+] Executed on remote host: 158.101.11.162 command: sudo mkdir -p /opt/rafay/; sudo chown -R ubuntu /opt/rafay/ stdout:  stderr:

[+] Copying ./input.yaml to /opt/rafay/ on 158.101.11.162

[+] Copying ./vm-scripts to /opt/rafay/ on 158.101.11.162
[+]   Copying ./vm-scripts/delete-eksabm-network.sh to /opt/rafay/vm-scripts/delete-eksabm-network.sh on 158.101.11.162
[+]   Copying ./vm-scripts/list-vms.sh to /opt/rafay/vm-scripts/list-vms.sh on 158.101.11.162
[+]   Copying ./vm-scripts/resurrectvms.service to /opt/rafay/vm-scripts/resurrectvms.service on 158.101.11.162
[+]   Copying ./vm-scripts/launch-vms.sh to /opt/rafay/vm-scripts/launch-vms.sh on 158.101.11.162
[+]   Copying ./vm-scripts/install-vbox-vagrant.sh to /opt/rafay/vm-scripts/install-vbox-vagrant.sh on 158.101.11.162
[+]   Copying ./vm-scripts/resurrect-vms.sh to /opt/rafay/vm-scripts/resurrect-vms.sh on 158.101.11.162
[+]   Copying ./vm-scripts/delete-eksabm-cluster-vms.sh to /opt/rafay/vm-scripts/delete-eksabm-cluster-vms.sh on 158.101.11.162
[+]   Copying ./vm-scripts/create-eksabm-network.sh to /opt/rafay/vm-scripts/create-eksabm-network.sh on 158.101.11.162
[+]   Copying ./vm-scripts/create-vm-network.sh to /opt/rafay/vm-scripts/create-vm-network.sh on 158.101.11.162
[+]   Copying ./vm-scripts/list-eksabm-resources.sh to /opt/rafay/vm-scripts/list-eksabm-resources.sh on 158.101.11.162
[+]   Copying ./vm-scripts/check-ubuntu-os.sh to /opt/rafay/vm-scripts/check-ubuntu-os.sh on 158.101.11.162
[+]   Copying ./vm-scripts/launch-eksabm-cluster-vms.sh to /opt/rafay/vm-scripts/launch-eksabm-cluster-vms.sh on 158.101.11.162
[+]   Copying ./vm-scripts/autobot.py to /opt/rafay/vm-scripts/autobot.py on 158.101.11.162
[+]   Copying ./vm-scripts/delete-vm.sh to /opt/rafay/vm-scripts/delete-vm.sh on 158.101.11.162
[+]   Copying ./vm-scripts/delete-eksabm-admin-vm.sh to /opt/rafay/vm-scripts/delete-eksabm-admin-vm.sh on 158.101.11.162
[+]   Copying ./vm-scripts/delete-vm-network.sh to /opt/rafay/vm-scripts/delete-vm-network.sh on 158.101.11.162
[+]   Copying ./vm-scripts/launch-eksabm-admin-vm.sh to /opt/rafay/vm-scripts/launch-eksabm-admin-vm.sh on 158.101.11.162

[+] Copying ./cluster_configs to /opt/rafay/ on 158.101.11.162
[+]   Copying ./cluster_configs/eksa-bm-config.yaml to /opt/rafay/cluster_configs/eksa-bm-config.yaml on 158.101.11.162
[+]   Copying ./cluster_configs/rafay-eksa-bm-config.yaml to /opt/rafay/cluster_configs/rafay-eksa-bm-config.yaml on 158.101.11.162

[+] Copying /opt/rafay/keys/oci to /opt/rafay/ on 158.101.11.162

[+] Executing on remote host: 158.101.11.162 command: sudo chown -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/*

[+] Executed on remote host: 158.101.11.162 command: sudo chown -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/* stdout:  stderr:

[+] Executing on remote host: 158.101.11.162 command: sudo cp -p /opt/rafay//vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service

[+] Executed on remote host: 158.101.11.162 command: sudo cp -p /opt/rafay//vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service stdout:  stderr: Created symlink /etc/systemd/system/default.target.wants/resurrectvms.service → /etc/systemd/system/resurrectvms.service.


[+] Preparing credentials : /opt/rafay/keys/rafay_api.key

[+] Copying /opt/rafay/keys/rafay_api.key to /opt/rafay/ on 158.101.11.162

[+] Installing required system packages on 158.101.11.162

[+] Executing on remote host: 158.101.11.162 command: sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip

[+] Executed on remote host: 158.101.11.162 command: sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip stdout: 

  ---- OUTPUT -----


[+] Installing required python packages on 158.101.11.162

[+] Executing on remote host: 158.101.11.162 command: sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko

[+] Executed on remote host: 158.101.11.162 command: sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko stdout: 
 stderr:

   ---- OUTPUT -----

[+] Executing script on 158.101.11.162

Sending command cd /opt/rafay/; sudo python3 vm-scripts/autobot.py
 to 158.101.11.162:22

ubuntu@brave-node:~$ cd /opt/rafay/; sudo python3 vm-scripts/autobot.py

[+] Processing input file /opt/rafay/input.yaml

[+] Detected provisioner: rafay_eksabm_cluster
cp count 0
dp count 0

[+] Installing vbox. This step may take a while, please be patient.....
  ---- OUTPUT -----

[+] Creating vbox network. This step may take a while, please be patient....
b'[+] Flushing local iptables\n[+] Creating natnetwork eksa-net with cidr 192.168.10.0/24 and gateway 192.168.10.1\n[+] Populating network config /root/eksa/vms/network_config\nNetworkCidr:192.168.10.0/24\nNetworkGateway:192.168.10.1\n'

[+] Creating eksa admin vm. This step may take a while, please be patient...
  ---- OUTPUT -----

[+] Creating control plane vms. This step may take a while, please be patient...
  ---- OUTPUT -----

[+] Creating data plane vms. This step may take a while, please be patient...
  ---- OUTPUT -----

[+] Detected desired cluster spec for provision::  cluster_name: brave, k8s_version:1.27, cp_count:1, dp_count:1

[+] Detected cluster provisioner config:: cluster_provisioner: rafay_eksabm_cluster, rafay_controller_url: https://console.stage.rafay.dev, rafay_api_key_file:/opt/rafay/keys/rafay_api.key, rafay_project_name:robbie, gw_name:brave-gw

[+] Copying /opt/rafay/ssh_private_key_file to /home/vagrant/ on 127.0.0.1

[+] Commencing cluster provision for cluster_name: brave, gw brave-gw, project robbie using provisioner rafay

[+] Step 1. Creating gateway: brave-gw
[+] Checking if gateway brave-gw already exists

[1.] Creating Gateway gw_name:brave-gw, gw_type:eksaBareMetal, gw_description:brave-gw, project_id:kr919wk
[1.] Gateway creation successful. gw_name:brave-gw, gw_type:eksaBareMetal, gw_description:brave-gw, project_id:kr919wk

[2.] Gateway setupCommand retrieval successful
 wget -q -O infra-gateway-installer-linux-amd64.tar.bz2 https://petti.stage.rafay-edge.net/publish/infra-gateway-installer-linux-amd64.tar.bz2 && tar -xjf infra-gateway-installer-linux-amd64.tar.bz2 && echo 'eyJhZ2VudElEIjoiNW0xeng2ayIsIm1heERpYWxzIjoiMiIsInJlbGF5cyI6W3siYWRkciI6ImFwcC5zdGFnZS5yYWZheS5kZXYuOjQ0MyIsImVuZHBvaW50IjoiKi5jb25uZWN0b3IuaW5mcmFyZWxheS5zdGFnZS5yYWZheS5kZXY6NDQzIiwibmFtZSI6InJhZmF5LWNvcmUtaW5mcmEtcmVsYXktYWdlbnQiLCJ0ZW1wbGF0ZVRva2VuIjoiY2JmMzNhc3BvMjI3ZTE5aGhoNWciLCJ0b2tlbiI6ImNsamhmZXNxOWs3OHVmNm9kajBnIn1dfQ==' | base64 -d > ./relayConfigData.json && ./infra-gateway-installer --configFile=./relayConfigData.json --bootstrapUrl=https://repo.stage.rafay-edge.net/repository/eks-bootstrap/v1/

[3.] Gateway setup command execution started ...wget -q -O infra-gateway-installer-linux-amd64.tar.bz2 https://petti.stage.rafay-edge.net/publish/infra-gateway-installer-linux-amd64.tar.bz2 && tar -xjf infra-gateway-installer-linux-amd64.tar.bz2 && echo 'eyJhZ2VudElEIjoiNW0xeng2ayIsIm1heERpYWxzIjoiMiIsInJlbGF5cyI6W3siYWRkciI6ImFwcC5zdGFnZS5yYWZheS5kZXYuOjQ0MyIsImVuZHBvaW50IjoiKi5jb25uZWN0b3IuaW5mcmFyZWxheS5zdGFnZS5yYWZheS5kZXY6NDQzIiwibmFtZSI6InJhZmF5LWNvcmUtaW5mcmEtcmVsYXktYWdlbnQiLCJ0ZW1wbGF0ZVRva2VuIjoiY2JmMzNhc3BvMjI3ZTE5aGhoNWciLCJ0b2tlbiI6ImNsamhmZXNxOWs3OHVmNm9kajBnIn1dfQ==' | base64 -d > ./relayConfigData.json && ./infra-gateway-installer --configFile=./relayConfigData.json --bootstrapUrl=https://repo.stage.rafay-edge.net/repository/eks-bootstrap/v1/

[3.] Gateway setup command execution successful. stdout: Create /infra directory
Downloading infra-agent binary
Setting up infraagent.service file to run infra-agent as systemd process
Starting infra-agent as systemd process
Enabling infra-agent as systemd process
Successfully downloaded and set up infra gateway agent!!


[4.] Gateway infraagent service is active and running

[5.] Gateway status is HEALTHY.

[+] Checking if cluster brave already exists
HTTP Error while sending request to  https://console.stage.rafay.dev/v2/infra/project/kr919wk/cluster/brave with method GET
404 Client Error: Not Found for url: https://console.stage.rafay.dev/v2/infra/project/kr919wk/cluster/brave

[6.] Creating cluster cluster_name:brave, project_id:kr919wk
[6.] Cluster creation successful. cluster_name:brave, project_id:kr919wk

[7.] Cluster update successful. cluster_name:brave, project_id:kr919wk

[8.] Cluster provision request submitted successfully. cluster_name:brave, project_id:kr919wk

[9.] Waiting on cluster condition ClusterSpecApplied to be in status InProgress, cluster_name:brave, project_id:kr919wk
     [+] ClusterInitialized : Pending (creating)
     [+] ClusterBootstrapNodeInitialized : NotSet (pending)
     [+] ClusterEKSCTLInstalled : NotSet (pending)
     [+] ClusterHardwareCSVCreated : NotSet (pending)
     [+] ClusterConfigCreated : NotSet (pending)
     [+] ClusterSpecApplied : NotSet (pending)
     [+] ClusterControlPlaneReady : NotSet (pending)
     [+] ClusterWorkerNodeGroupsReady : NotSet (pending)
     [+] ClusterOperatorSpecApplied : NotSet (pending)
     [+] ClusterHealthy : NotSet (pending)
     [+] ClusterUpgraded : NotSet (pending)
   [+]  .... waiting for 5 minutes  ....
     [+] ClusterInitialized : Success (cluster initialized)
     [+] ClusterBootstrapNodeInitialized : Success (Gateway is reachable and cluster folder is created on admin node)
     [+] ClusterEKSCTLInstalled : Success (eksctl installed)
     [+] ClusterHardwareCSVCreated : Success (cluster hardware csv is created)
     [+] ClusterConfigCreated : Success (cluster config is created)
     [+] ClusterSpecApplied : InProgress (started applying cluster spec)
     [+] ClusterControlPlaneReady : NotSet (pending)
     [+] ClusterWorkerNodeGroupsReady : NotSet (pending)
     [+] ClusterOperatorSpecApplied : NotSet (pending)
     [+] ClusterHealthy : NotSet (pending)
     [+] ClusterUpgraded : NotSet (pending)
    [+]    Detected cluster condition ClusterSpecApplied has progressed to status InProgress

[10.] Monitoring ClusterSpecApplied condition status debug log
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:[] FAILED:[] SUCCESS:[]
   [+]  .... waiting for 5 minutes  ....
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
    [+]    Exiting monitoring ClusterSpecApplied condition status debug log as progress check successful. Detected Creating new workload cluster in log output. This means nodes are ready to be power cycled

[10.] Monitoring ClusterSpecApplied condition status debug log
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:['brave-cp-n-1'] RUNNING:[] FAILED:[] SUCCESS:[]
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:['brave-cp-n-1'] OR FAILED:[]
   [+] Powering on cluster node brave-cp-n-1 with boot order net
   [+] Detected machines in phases ['Provisioning', 'Pending']
   [+]  .... waiting for 5 minutes  ....
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:[] FAILED:[] SUCCESS:['brave-cp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:[] OR FAILED:[]
   [+] Power cycling machines.c with Phase Provisioned (boot order disk). brave-cp-n-1
   [+] Powering on cluster node brave-cp-n-1 with boot order disk
   [+] Detected machines in phases ['Provisioned', 'Pending']
   [+]  .... waiting for 5 minutes  ....
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:['brave-dp-n-1'] RUNNING:[] FAILED:[] SUCCESS:['brave-cp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:['brave-dp-n-1'] OR FAILED:[]
   [+] Powering on cluster node brave-dp-n-1 with boot order net
   [+] Detected machines in phases ['Running', 'Provisioning']
   [+]  .... waiting for 5 minutes  ....
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:[] FAILED:[] SUCCESS:['brave-cp-n-1', 'brave-dp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:[] OR FAILED:[]
   [+] Power cycling machines.c with Phase Provisioned (boot order disk). brave-dp-n-1
   [+] Powering on cluster node brave-dp-n-1 with boot order disk
   [+] Detected machines in phases ['Running', 'Provisioned']
   [+]  .... waiting for 5 minutes  ....
HTTP Error while sending request to  https://console.stage.rafay.dev/v2/infra/project/kr919wk/cluster/brave/conditionstatus?clusterCondition=ClusterSpecApplied with method GET
500 Server Error: Internal Server Error for url: https://console.stage.rafay.dev/v2/infra/project/kr919wk/cluster/brave/conditionstatus?clusterCondition=ClusterSpecApplied

ERROR: Unable to get show debug status for cluster condition ClusterSpecApplied. cluster_name:brave, project_id:kr919wk
    [+]    Exiting monitoring ClusterSpecApplied condition status debug log as progress check successful. Not all machines.c are in Running phase

[12.] Waiting on cluster condition ClusterSpecApplied to be in status Success, cluster_name:brave, project_id:kr919wk
     [+] ClusterInitialized : Success (cluster initialized)
     [+] ClusterBootstrapNodeInitialized : Success (Gateway is reachable and cluster folder is created on admin node)
     [+] ClusterEKSCTLInstalled : Success (eksctl installed)
     [+] ClusterHardwareCSVCreated : Success (cluster hardware csv is created)
     [+] ClusterConfigCreated : Success (cluster config is created)
     [+] ClusterSpecApplied : Success (cluster spec is applied)
     [+] ClusterUpgraded : NotSet (pending)
    [+]    Detected cluster condition ClusterSpecApplied has progressed to status Success

[13.] Waiting on cluster condition ClusterHealthy to be in status Success, cluster_name:brave, project_id:kr919wk
     [+] ClusterInitialized : Success (cluster initialized)
     [+] ClusterBootstrapNodeInitialized : Success (Gateway is reachable and cluster folder is created on admin node)
     [+] ClusterEKSCTLInstalled : Success (eksctl installed)
     [+] ClusterHardwareCSVCreated : Success (cluster hardware csv is created)
     [+] ClusterConfigCreated : Success (cluster config is created)
     [+] ClusterSpecApplied : Success (cluster spec is applied)
     [+] ClusterControlPlaneReady : Success (Cluster is ready)
     [+] ClusterWorkerNodeGroupsReady : Success (cluster worker groups machines have started)
     [+] ClusterOperatorSpecApplied : Success (operator spec applied)
     [+] ClusterHealthy : Submitted (to check cluster is healthy)
     [+] ClusterUpgraded : NotSet (pending)
   [+]  .... waiting for 5 minutes  ....
     [+] ClusterInitialized : Success (cluster initialized)
     [+] ClusterBootstrapNodeInitialized : Success (Gateway is reachable and cluster folder is created on admin node)
     [+] ClusterEKSCTLInstalled : Success (eksctl installed)
     [+] ClusterHardwareCSVCreated : Success (cluster hardware csv is created)
     [+] ClusterConfigCreated : Success (cluster config is created)
     [+] ClusterSpecApplied : Success (cluster spec is applied)
     [+] ClusterControlPlaneReady : Success (Cluster is ready)
     [+] ClusterWorkerNodeGroupsReady : Success (cluster worker groups machines have started)
     [+] ClusterOperatorSpecApplied : Success (operator spec applied)
     [+] ClusterHealthy : Success (cluster is healthy)
     [+] ClusterUpgraded : NotSet (pending)
    [+]    Detected cluster condition ClusterHealthy has progressed to status Success

```