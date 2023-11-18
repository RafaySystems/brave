
```sh
$ source venv/bin/activate
$ python3 ./launch.py
[+] Processing input file input.yaml

[+] Generating terraform file tf/oci/terraform.tfvars

[+] Detected infrastructure provider: oci

[+] Detected cluster provisioner: rafay

[+] Launching infrastructure on provider aws

[+] Switching to  directory tf/oci to launch infrastructure

Initializing the backend...

---- TERRAFORM OUTPUT ------

Apply complete! Resources: 10 added, 0 changed, 0 destroyed.

Outputs:

instance_public_ip = "54.151.22.254"

[+] IP of launched instance: 54.151.22.254

[+] Switching back to directory /Users/rgill/testbeds/eksa-bm-vbox

[+] Waiting 120 seconds to allow infrastructure to boot up oci
SSH config updated successfully.

[+] Executing on remote host: 54.151.22.254 command: sudo mkdir -p /opt/rafay/; sudo chown -R ubuntu /opt/rafay/

[+] Executed on remote host: 54.151.22.254 command: sudo mkdir -p /opt/rafay/; sudo chown -R ubuntu /opt/rafay/ stdout:  stderr:

[+] Copying ./input.yaml to /opt/rafay/ on 54.151.22.254

[+] Copying ./vm-scripts to /opt/rafay/ on 54.151.22.254
[+]   Copying ./vm-scripts/launch-admin-vm.sh to /opt/rafay/vm-scripts/launch-admin-vm.sh on 54.151.22.254
[+]   Copying ./vm-scripts/delete-network.sh to /opt/rafay/vm-scripts/delete-network.sh on 54.151.22.254
[+]   Copying ./vm-scripts/create-network.sh to /opt/rafay/vm-scripts/create-network.sh on 54.151.22.254
[+]   Copying ./vm-scripts/delete-admin-vm.sh to /opt/rafay/vm-scripts/delete-admin-vm.sh on 54.151.22.254
[+]   Copying ./vm-scripts/resurrectvms.service to /opt/rafay/vm-scripts/resurrectvms.service on 54.151.22.254
[+]   Copying ./vm-scripts/install-vbox-vagrant.sh to /opt/rafay/vm-scripts/install-vbox-vagrant.sh on 54.151.22.254
[+]   Copying ./vm-scripts/resurrect-vms.sh to /opt/rafay/vm-scripts/resurrect-vms.sh on 54.151.22.254
[+]   Copying ./vm-scripts/delete-cluster-vms.sh to /opt/rafay/vm-scripts/delete-cluster-vms.sh on 54.151.22.254
[+]   Copying ./vm-scripts/launch-cluster-vms.sh to /opt/rafay/vm-scripts/launch-cluster-vms.sh on 54.151.22.254
[+]   Copying ./vm-scripts/check-ubuntu-os.sh to /opt/rafay/vm-scripts/check-ubuntu-os.sh on 54.151.22.254
[+]   Copying ./vm-scripts/autobot.py to /opt/rafay/vm-scripts/autobot.py on 54.151.22.254
[+]   Copying ./vm-scripts/automation.sh to /opt/rafay/vm-scripts/automation.sh on 54.151.22.254
[+]   Copying ./vm-scripts/list-resources.sh to /opt/rafay/vm-scripts/list-resources.sh on 54.151.22.254

[+] Copying ./cluster_configs to /opt/rafay/ on 54.151.22.254
[+]   Copying ./cluster_configs/robbie-nat2.yaml to /opt/rafay/cluster_configs/robbie-nat2.yaml on 54.151.22.254
[+]   Copying ./cluster_configs/rafay-hitesh-cluster1.yaml to /opt/rafay/cluster_configs/rafay-hitesh-cluster1.yaml on 54.151.22.254
[+]   Copying ./cluster_configs/hitesh-cluster1.yaml to /opt/rafay/cluster_configs/hitesh-cluster1.yaml on 54.151.22.254

[+] Copying /opt/rafay/keys/oci to /opt/rafay/ on 54.151.22.254

[+] Executing on remote host: 54.151.22.254 command: sudo chown -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/*

[+] Executed on remote host: 54.151.22.254 command: sudo chown -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/* stdout: 

[+] Executing on remote host: 54.151.22.254 command: sudo cp -p /opt/rafay//vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service

[+] Executed on remote host: 54.151.22.254 command: sudo cp -p /opt/rafay//vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service stdout:  stderr: Created symlink /etc/systemd/system/default.target.wants/resurrectvms.service → /etc/systemd/system/resurrectvms.service.


[+] Installing required system packages on 54.151.22.254

[+] Executing on remote host: 54.151.22.254 command: sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip

[+] Executed on remote host: 54.151.22.254 command: sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip stdout:
  ---- OUTPUT -----


[+] Installing required python packages on 54.151.22.254

[+] Executing on remote host: 54.151.22.254 command: sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko

[+] Executed on remote host: 54.151.22.254 command: sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko stdout:
  ---- OUTPUT -----

[+] Executing script on 54.151.22.254

---- Banner ----

ubuntu@ip-10-10-10-34:~$ cd /opt/rafay/; sudo python3 vm-scripts/autobot.py

[+] Processing input file /opt/rafay/input.yaml

[+] Detected cluster provisioner: native
cp count 0
dp count 0

[+] Installing vbox. This step may take a while, please be patient.....

[+] Creating vbox network. This step may take a while, please be patient....
b'[+] Flushing local iptables\n[+] Creating natnetwork eksa-net with cidr 192.168.10.0/24 and gateway 192.168.10.1\n[+] Populating network config /root/eksa/vms/network_config\nNetworkCidr:192.168.10.0/24\nNetworkGateway:192.168.10.1\n'

[+] Creating eksa admin vm. This step may take a while, please be patient...

[+] Creating control plane vms. This step may take a while, please be patient...

[+] Creating data plane vms. This step may take a while, please be patient...

[+] Detected desired cluster spec for provision::  cluster_name: robbie-cluster-rg5, k8s_version:1.27, cp_count:1, dp_count:1

[+] Detected cluster provisioner config:: cluster_provisioner: rafay, rafay_controller_url: https://console-robbie2.dev.rafay-edge.net, rafay_api_key_file:/opt/rafay/keys/rafay_api.key, rafay_project_name:robbie, gw_name:robbie-gw-rg5

[+] Commencing cluster provision for cluster_name: robbie-cluster-rg5, gw robbie-gw-rg5, project robbie using provisioner rafay

[+] Step 1. Creating gateway: robbie-gw-rg5

[1.] Gateway creation successful. gw_name:robbie-gw-rg5, gw_type:eksaBareMetal, gw_description:robbie-gw-rg5, project_id:4qkolkn

[2.] Gateway setupCommand retrieval successful

[3.] Gateway setup command execution successful. stdout: Create /infra directory
Downloading infra-agent binary

[4.] Gateway infraagent service is active and running

[5.] Gateway status is HEALTHY.
HTTP Error while sending request to  https://console-robbie2.dev.rafay-edge.net/v2/infra/project/4qkolkn/cluster/robbie-cluster-rg6 with method GET
404 Client Error: Not Found for url: https://console-robbie2.dev.rafay-edge.net/v2/infra/project/4qkolkn/cluster/robbie-cluster-rg6

[6.] Cluster creation successful. cluster_name:robbie-cluster-rg6, project_id:4qkolkn

[7.] Cluster update successful. cluster_name:robbie-cluster-rg6, project_id:4qkolkn

[8.] Cluster provision request submitted successfully. cluster_name:robbie-cluster-rg6, project_id:4qkolkn

[9.] Waiting on cluster condition ClusterSpecApplied to be in status InProgress, cluster_name:robbie-cluster-rg6, project_id:4qkolkn
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
    [+]    Detected cluster condition ClusterSpecApplied has progressed to status InProgress

[10.] Monitoring ClusterSpecApplied condition status debug log
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:[] FAILED:[] SUCCESS:[]
   [+]  .... waiting for 5 minutes  ...

    [+]    Exiting monitoring ClusterSpecApplied condition status debug log as progress check successful. Detected Creating new workload cluster in log output. This means nodes are ready to be power cycled

[10.] Monitoring ClusterSpecApplied condition status debug log
   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:['robbie-cluster-rg6-cp-n-1'] RUNNING:[] FAILED:[] SUCCESS:[]
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:['robbie-cluster-rg6-cp-n-1'] OR FAILED:[]
   [+] Powering on cluster node robbie-cluster-rg6-cp-n-1 with boot order net
   [+] Detected machines in phases ['Provisioning', 'Pending']
   [+]  .... waiting for 5 minutes  ....


   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:['robbie-cluster-rg6-cp-n-1'] FAILED:[] SUCCESS:[]
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:[] OR FAILED:[]
   [+] Power cycling machines.c with Phase Provisioned (boot order disk). robbie-cluster-rg6-cp-n-1
   [+] Powering on cluster node robbie-cluster-rg6-cp-n-1 with boot order disk
   [+] Detected machines in phases ['Provisioned', 'Pending']
   [+]  .... waiting for 5 minutes  ....

   [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:['robbie-cluster-rg6-dp-n-1'] RUNNING:['robbie-cluster-rg6-cp-n-1'] FAILED:[] SUCCESS:[]
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:['robbie-cluster-rg6-dp-n-1'] OR FAILED:[]
   [+] Powering on cluster node robbie-cluster-rg6-dp-n-1 with boot order net
   [+] Detected machines in phases ['Running', 'Provisioning']
   [+]  .... waiting for 5 minutes  ....

    [+] Debug channel command submitted successfully. context:kind, command:kubectl get workflows -A -o yaml
   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:['robbie-cluster-rg6-cp-n-1'] FAILED:[] SUCCESS:['robbie-cluster-rg6-dp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:[] OR FAILED:[]
   [+] Power cycling machines.c with Phase Provisioned (boot order disk). robbie-cluster-rg6-dp-n-1
   [+] Powering on cluster node robbie-cluster-rg6-dp-n-1 with boot order disk
   [+] Detected machines in phases ['Running', 'Provisioned']
   [+]  .... waiting for 5 minutes  ....
   

[12.] Waiting on cluster condition ClusterSpecApplied to be in status Success, cluster_name:robbie-cluster-rg6, project_id:4qkolkn
     [+] ClusterInitialized : Success (cluster initialized)
     [+] ClusterBootstrapNodeInitialized : Success (Gateway is reachable and cluster folder is created on admin node)
     [+] ClusterEKSCTLInstalled : Success (eksctl installed)
     [+] ClusterHardwareCSVCreated : Success (cluster hardware csv is created)
     [+] ClusterConfigCreated : Success (cluster config is created)
     [+] ClusterSpecApplied : Success (cluster spec is applied)
    [+]    Detected cluster condition ClusterSpecApplied has progressed to status Success

[13.] Waiting on cluster condition ClusterHealthy to be in status Success, cluster_name:robbie-cluster-rg6, project_id:4qkolkn
     [+] ClusterInitialized : Success (cluster initialized)
     [+] ClusterBootstrapNodeInitialized : Success (Gateway is reachable and cluster folder is created on admin node)
     [+] ClusterEKSCTLInstalled : Success (eksctl installed)
     [+] ClusterHardwareCSVCreated : Success (cluster hardware csv is created)
     [+] ClusterConfigCreated : Success (cluster config is created)
     [+] ClusterSpecApplied : Success (cluster spec is applied)
     [+] ClusterControlPlaneReady : Success (Cluster is ready)
     [+] ClusterWorkerNodeGroupsReady : Success (cluster worker groups machines have started)
     [+] ClusterOperatorSpecApplied : Success (operator spec applied)
     [+] ClusterHealthy : InProgress (monitoring cluster health)
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
     [+] ClusterHealthy : InProgress (monitoring cluster health)
   [+]  .... waiting for 5 minutes  ....



Execution of command to create cluster passed. 
Warning: The recommended number of control plane nodes is 3 or 5
Warning: The recommended number of control plane nodes is 3 or 5
Performing setup and validations
✅ Tinkerbell Provider setup is valid
✅ Validate OS is compatible with registry mirror configuration
✅ Validate certificate for registry mirror
✅ Validate authentication for git provider
✅ Validate cluster's eksaVersion matches EKS-A version
Creating new bootstrap cluster
Provider specific pre-capi-install-setup on bootstrap cluster
Installing cluster-api providers on bootstrap cluster
Provider specific post-setup
Creating new workload cluster
Installing networking on workload cluster
Creating EKS-A namespace
Installing cluster-api providers on workload cluster
Installing EKS-A secrets on workload cluster
Installing resources on management cluster
Moving cluster management from bootstrap to workload cluster
Installing EKS-A custom components (CRD and controller) on workload cluster
Installing EKS-D components on workload cluster
Creating EKS-A CRDs instances on workload cluster
Installing GitOps Toolkit on workload cluster
GitOps field not specified, bootstrap flux skipped
Writing cluster config file
Deleting bootstrap cluster
🎉 Cluster created!
--------------------------------------------------------------------------------------
The Amazon EKS Anywhere Curated Packages are only available to customers with the
Amazon EKS Anywhere Enterprise Subscription
--------------------------------------------------------------------------------------
Enabling curated packages on the cluster
Installing helm chart on cluster	{"chart": "eks-anywhere-packages", "version": "0.3.12-eks-a-52"}

      
```