```sh
$ source ~/venv-testbeds/env/bin/activate

$ ./launch.py

[+] Processing input file input.yaml

[+] Generating terraform file tf/aws/terraform.tfvars

[+] Detected infrastructure provider: aws

[+] Detected cluster provisioner: native

[+] Launching infrastructure on provider aws

[+] Switching to  directory tf/aws to launch infrastructure

Initializing the backend...

---- TERRAFORM OUTPUT ------

Apply complete! Resources: 10 added, 0 changed, 0 destroyed.

Outputs:

instance_public_ip = "54.151.22.254"

[+] IP of launched instance: 54.151.22.254

[+] Switching back to directory /Users/rgill/testbeds/eksa-bm-vbox

[+] Waiting 120 seconds to allow infrastructure to boot up aws
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

[+] Executing on remote host: 54.151.22.254 command: sudo chmod -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/*

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

[+] Detected desired cluster spec for provision::  cluster_name: brave, k8s_version:1.27, cp_count:1, dp_count:1

[+] Copying /opt/rafay/ssh_private_key_file to /home/vagrant/ on 127.0.0.1

[+] Provisioning cluster_name: brave using provisioner native

[1.] Executing command to create directory on eksa-admin : mkdir -p /opt/rafay/native/brave

[2.] Creating hardware csv file on eksa-admin:
 echo "hostname,mac,ip_address,netmask,gateway,nameservers,labels,disk,bmc_ip,bmc_username,bmc_password
brave-cp-n-1,08:00:27:DB:D2:27,192.168.10.203,255.255.255.0,192.168.10.1,8.8.8.8,type=cp,/dev/sda,,,
brave-dp-n-1,08:00:27:CD:00:3A,192.168.10.12,255.255.255.0,192.168.10.1,8.8.8.8,type=dp,/dev/sda,,,
" > /opt/rafay/native/brave/hardware.csv

[3.] Creating cluster config yaml on eksa-admin:
 echo "apiVersion: anywhere.eks.amazonaws.com/v1alpha1
kind: Cluster
metadata:
  name: brave
spec:
  clusterNetwork:
    cniConfig:
      cilium:
        policyEnforcementMode: default
    pods:
      cidrBlocks:
      - 192.168.0.0/16
    services:
      cidrBlocks:
      - 10.96.0.0/12
  controlPlaneConfiguration:
    count: 1
    endpoint:
      host: 192.168.10.42
    machineGroupRef:
      kind: TinkerbellMachineConfig
      name: cpmc
  datacenterRef:
    kind: TinkerbellDatacenterConfig
    name: brave
  kubernetesVersion: '\''1.27'\''
  managementCluster:
    name: brave
  workerNodeGroupConfigurations:
  - count: 1
    machineGroupRef:
      kind: TinkerbellMachineConfig
      name: dpmc
    name: ng1
---
apiVersion: anywhere.eks.amazonaws.com/v1alpha1
kind: TinkerbellDatacenterConfig
metadata:
  name: brave
spec:
  tinkerbellIP: 192.168.10.155
---
apiVersion: anywhere.eks.amazonaws.com/v1alpha1
kind: TinkerbellMachineConfig
metadata:
  name: cpmc
spec:
  hardwareSelector:
    type: cp
  osFamily: bottlerocket
  templateRef:
    kind: TinkerbellTemplateConfig
    name: '\'''\''
  users:
  - name: ec2-user
    sshAuthorizedKeys:
    - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE=
      rgill@Robbies-MBP
---
apiVersion: anywhere.eks.amazonaws.com/v1alpha1
kind: TinkerbellMachineConfig
metadata:
  name: dpmc
spec:
  hardwareSelector:
    type: dp
  osFamily: bottlerocket
  templateRef:
    kind: TinkerbellTemplateConfig
    name: '\'''\''
  users:
  - name: ec2-user
    sshAuthorizedKeys:
    - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE=
      rgill@Robbies-MBP
" > /opt/rafay/native/brave/brave.yaml

[4.] Installing eksctl cli on eksa-admin:
 curl "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" --silent --location | tar xz -C /tmp; install -m 0755 /tmp/eksctl /usr/local/bin/eksctl

[5.] Installing yq cli on eksa-admin:
 wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq; chmod +x /usr/bin/yq

[6.] Installing eksctl cli on eksa-admin:
 RELEASE_VERSION=$(curl https://anywhere-assets.eks.amazonaws.com/releases/eks-a/manifest.yaml --silent --location | yq ".spec.latestVersion"); EKS_ANYWHERE_TARBALL_URL=$(curl https://anywhere-assets.eks.amazonaws.com/releases/eks-a/manifest.yaml --silent --location | yq ".spec.releases[] | select(.version==\"$RELEASE_VERSION\").eksABinary.$(uname -s | tr A-Z a-z).uri"); curl $EKS_ANYWHERE_TARBALL_URL --silent --location | tar xz ./eksctl-anywhere; install -m 0755 ./eksctl-anywhere /usr/local/bin/eksctl-anywhere

[7.] Installing kubectl cli on eksa-admin:
 export OS="$(uname -s | tr A-Z a-z)"; ARCH=$(test "$(uname -m)" = "x86_64" && echo "amd64" || echo "arm64"); curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/${OS}/${ARCH}/kubectl"; install -m 0755 ./kubectl /usr/local/bin/kubectl

[8.] Installing docker on eksa-admin:
 apt-get update; apt-get -y install ca-certificates curl gnupg; install -m 0755 -d /etc/apt/keyrings; curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg; chmod a+r /etc/apt/keyrings/docker.gpg; echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null; apt-get update; apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

[9.] Creating cluster : pushd /opt/rafay/native/brave; eksctl anywhere create cluster --hardware-csv hardware.csv -f brave.yaml 2>&1 | tee -a /opt/rafay/native/brave/eksa-create-cluster.log; popd
   [+] Cluster creation in progress...

[10.] Monitoring cluster creation logs for string: 'Creating new workload cluster' : cat /opt/rafay/native/brave/eksa-create-cluster.log
   [+] Execution of command to fetch cluster creation logs passed. stdout:

   [+]  .... waiting for 60 seconds to recheck logs ....

[10.] Monitoring cluster creation logs for string: 'Creating new workload cluster' : cat /opt/rafay/native/brave/eksa-create-cluster.log
   [+] Execution of command to fetch cluster creation logs passed. stdout:
 Warning: The recommended number of control plane nodes is 3 or 5
Warning: The recommended number of control plane nodes is 3 or 5
Performing setup and validations
✅ Tinkerbell Provider setup is valid
✅ Validate OS is compatible with registry mirror configuration
✅ Validate certificate for registry mirror
✅ Validate authentication for git provider
✅ Validate cluster's eksaVersion matches EKS-A version
Creating new bootstrap cluster

   [+]  .... waiting for 60 seconds to recheck logs ....

[10.] Monitoring cluster creation logs for string: 'Creating new workload cluster' : cat /opt/rafay/native/brave/eksa-create-cluster.log
   [+] Execution of command to fetch cluster creation logs passed. stdout:
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

   [+]  .... waiting for 60 seconds to recheck logs ....

[10.] Monitoring cluster creation logs for string: 'Creating new workload cluster' : cat /opt/rafay/native/brave/eksa-create-cluster.log
   [+] Execution of command to fetch cluster creation logs passed. stdout:
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


[11.] Fetching Tinkerbell workflows from cluster : KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get workflows -A -o yaml
   [+] Fetching machine status from cluster to perform power management tasks: KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get machines.cluster.x-k8s.io -A
   [+] Execution of command to fetch machine status passed. stdout:
 NAMESPACE     NAME                               CLUSTER   NODENAME   PROVIDERID   PHASE          AGE   VERSION
eksa-system   brave-fnlgp                        brave                             Provisioning   9s    v1.27.4-eks-1-27-10
eksa-system   brave-ng1-5899b4fd4bxjhh86-zqdgl   brave                             Pending        11s   v1.27.4-eks-1-27-10

   [+] Tinkerbell workflows detected: PENDING:['brave-cp-n-1'] RUNNING:[] FAILED:[] SUCCESS:[]
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:['brave-cp-n-1'] OR FAILED:[]
   [+] Powering on cluster node brave-cp-n-1 with boot order net
   [+] Detected machines in phases ['Provisioning', 'Pending']
   [+]  .... waiting for 5 minutes to recheck logs ....

[11.] Fetching Tinkerbell workflows from cluster : KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get workflows -A -o yaml
   [+] Fetching machine status from cluster to perform power management tasks: KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get machines.cluster.x-k8s.io -A
   [+] Execution of command to fetch machine status passed. stdout:
 NAMESPACE     NAME                               CLUSTER   NODENAME   PROVIDERID                              PHASE         AGE     VERSION
eksa-system   brave-fnlgp                        brave                tinkerbell://eksa-system/brave-cp-n-1   Provisioned   5m14s   v1.27.4-eks-1-27-10
eksa-system   brave-ng1-5899b4fd4bxjhh86-zqdgl   brave                                                        Pending       5m16s   v1.27.4-eks-1-27-10

   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:[] FAILED:[] SUCCESS:['brave-cp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:[] OR FAILED:[]
   [+] Power cycling machines.c with Phase Provisioned (boot order disk). brave-cp-n-1
   [+] Powering on cluster node brave-cp-n-1 with boot order disk
   [+] Detected machines in phases ['Provisioned', 'Pending']
   [+]  .... waiting for 5 minutes to recheck logs ....

[11.] Fetching Tinkerbell workflows from cluster : KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get workflows -A -o yaml
   [+] Fetching machine status from cluster to perform power management tasks: KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get machines.cluster.x-k8s.io -A
   [+] Execution of command to fetch machine status passed. stdout:
 NAMESPACE     NAME                               CLUSTER   NODENAME      PROVIDERID                              PHASE          AGE   VERSION
eksa-system   brave-fnlgp                        brave     brave-fnlgp   tinkerbell://eksa-system/brave-cp-n-1   Running        10m   v1.27.4-eks-1-27-10
eksa-system   brave-ng1-5899b4fd4bxjhh86-zqdgl   brave                                                           Provisioning   10m   v1.27.4-eks-1-27-10

   [+] Tinkerbell workflows detected: PENDING:['brave-dp-n-1'] RUNNING:[] FAILED:[] SUCCESS:['brave-cp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:['brave-dp-n-1'] OR FAILED:[]
   [+] Powering on cluster node brave-dp-n-1 with boot order net
   [+] Detected machines in phases ['Running', 'Provisioning']
   [+]  .... waiting for 5 minutes to recheck logs ....

[11.] Fetching Tinkerbell workflows from cluster : KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get workflows -A -o yaml
   [+] Fetching machine status from cluster to perform power management tasks: KUBECONFIG=/opt/rafay/native/brave/brave/generated/brave.kind.kubeconfig kubectl get machines.cluster.x-k8s.io -A
   [+] Execution of command to fetch machine status passed. stdout:
 NAMESPACE     NAME                               CLUSTER   NODENAME      PROVIDERID                              PHASE         AGE   VERSION
eksa-system   brave-fnlgp                        brave     brave-fnlgp   tinkerbell://eksa-system/brave-cp-n-1   Running       15m   v1.27.4-eks-1-27-10
eksa-system   brave-ng1-5899b4fd4bxjhh86-zqdgl   brave                   tinkerbell://eksa-system/brave-dp-n-1   Provisioned   15m   v1.27.4-eks-1-27-10

   [+] Tinkerbell workflows detected: PENDING:[] RUNNING:[] FAILED:[] SUCCESS:['brave-cp-n-1', 'brave-dp-n-1']
   [+] Power cycling nodes with Tinkerbell workflows (boot order net) PENDING:[] OR FAILED:[]
   [+] Power cycling machines.c with Phase Provisioned (boot order disk). brave-dp-n-1
   [+] Powering on cluster node brave-dp-n-1 with boot order disk
   [+] Detected machines in phases ['Running', 'Provisioned']
   [+]  .... waiting for 5 minutes to recheck logs ....

Execution of command to create cluster passed. stdout:
 /opt/rafay/native/brave /home/vagrant
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