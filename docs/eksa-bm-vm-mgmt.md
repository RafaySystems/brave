
- [EKSA-BM VM management ](#eksa-bm-vm-management)
- [Connecting to EKSA VMs over ssh](#connecting-to-eksa-vms-over-ssh)
- [Accessing Cluster Files (hardware.csv, cluster config, kubeconfig etc)](#accessing-cluster-files-hardwarecsv-cluster-config-kubeconfig-etc)
- [Shell utilities to list and manage EKSA VM resources](#shell-utilities-to-list-and-manage-eksa-vm-resources)
    - [List all EKSA virtual resources](#list-all-eksa-virtual-resources)
    - [Launch VMs for a cluster](#launch-vms-for-a-cluster)
    - [Delete VMs of a cluster](#delete-vms-of-a-cluster)
    - [Resurrecting VMs on cloud instance reboot/stop-start](#resurrecting-vms-on-cloud-instance-rebootstop-start)
    - [Other utility scripts](#other-utility-scripts)
- [Using Virtualbox GUI to access cluster VMs and their consoles](#using-virtualbox-gui-to-access-vms-and-their-consoles)
- [Manually power VMs on/off and change boot order](#manually-power-vms-onoff-and-change-boot-order)

---

## EKSA-BM VM management 

**BRAVE** emulates the entire EKSA-BM infrastructure on a **single cloud** instance. It leverages [Virtualbox](https://www.virtualbox.org/) and [vagrant](https://www.vagrantup.com/) to `create VMs and a` [NAT Network](https://www.virtualbox.org/manual/ch06.html#network_nat_service). 

Virtualbox VMs are used to emulate cluster hardware and the **Admin machine**, whereas VirtualBox's NAT Network is used to emulate the Layer2 Network these machines are connected to. This way EKSA-BM machines are connected to each other on a Layer2 network and also are able to reach the Internet. 


### Connecting to EKSA VMs over ssh  

Once Cluster has been successfully created, you can access it using following steps:

1. SSH to the cloud instance. An entry should already have been created in your ~/.ssh/config. Example entry:
```sh
Host brave-node
  Hostname 129.153.193.176
  StrictHostKeyChecking no
  IdentityFile /opt/rafay/keys/oci
  User ubuntu
```
To ssh simply use something like `ssh brave-node`

2. From the cloud instance, ssh to eksa-admin machine
```sh
ssh eksa-admin-1
```

3. To ssh into cluster nodes, on `eksa-admin` machine ssh into the IP of node vm. The IP address can be derived from `kubectl get nodes -o wide` or from hardware.csv file under directory `/opt/rafay/<provisioner>` on `eksa-admin` machine 

```sh
sudo su - 
KUBECONFIG=/opt/rafay/native/brave/brave/brave-eks-a-cluster.kubeconfig kubectl get nodes -o wide

ssh -i /home/vagrant/ssh_private_key_file ec2-user@ip-of-node-vm
```

**NOTE**: If a config file was used for cluster creation, then the ssh private key corresponding to the ssh public key provided in config file will have to be copied over to `eksa-admin` machine and used to ssh in to cluster nodes.

```sh
ssh -i path_to_ssh_privkey_file ec2-user@ip-of-node-vm
```

### Accessing Cluster Files (hardware.csv, cluster config, kubeconfig etc)

All cluster files are located on `eksa-admin` machine. SSH to `eks-admin` machine as described [above](#connecting-to-eksa-vms-over-ssh). 

If using `eksabm_cluster` cluster_provisioner, the directory `/opt/rafay/native/` contains all cluster files generated by `eksctl` for the cluster such as hardware.csv, cluster config etc. You will need to switch to root user to access this directory using `sudo su -` on `eksa-admin` machine. 

If using `rafay_eksabm_cluster` cluster_provisioner, directory `/opt/rafay/eksabm/` contains all cluster files generated by eksctl for the cluster such as hardware.csv, cluster config etc. You will need to switch to root user to access this directory using `sudo su -` on `eksa-admin` machine.  

Vagrant files and files to manage IP allocation are located in directory `/root/eksa/vms/` on the cloud instance. [Shell utilities](#shell-utilities-to-list-and-manage-eksa-vm-resources) use files in this directory to manage VMs, network and IP allocation (including TinkerbellIP and endpointIP allocation).


### Shell utilities to list and manage EKSA VM resources

A number of utilities are provided to have a look under the hood and facilitate debugging and advanced use cases. To get access to these utilities, **connect to the cloud instance over ssh, switch to root user and cd to `/opt/rafay/vm-scripts/` directory**. The hostname of the instance should already have been programmed in ~/.ssh/config. For instance,

```sh
ssh brave-node
sudo su - 
cd /opt/rafay/vm-scripts/
```

Below is brief description of these utility scripts in `/opt/rafay/vm-scripts/` directory on the cloud instance 

#### List all EKSA virtual resources

- `list-eksabm-resources.sh` : Shell script utility to list all virtual resources created on the cloud instance at Virtualbox layer and also resources relevant to EKSA-BM cluster such as hardware.csv for the cluster, TinkerbellIP and EndpointIP reserved for the cluster.  Below is a sample output of running this utility script. 

```sh
sudo su - 
bash /opt/rafay/vm-scripts/list-eksabm-resources.sh -a
```

Output::
```sh
-------------------------------

[+]  Listing Networks
NAT Networks:

Name:         eksa-net
Enabled:      Yes
Network:      192.168.10.0/24
Gateway:      192.168.10.1
DHCP Server:  No
IPv6:         No
IPv6 Prefix:  fd17:625c:f037:2::/64
IPv6 Default: No
Port-forwarding (ipv4)
        ssh-to-eksa-admin-1:tcp:[]:5022:[192.168.10.50]:22
loopback mappings (ipv4)
        127.0.0.1=2

1 network found

-------------------------------

[+] Listing vms registered with vbox
"eksa-admin-1" {733a547d-05ba-4e44-ad82-d74a4fab8202}
"brave-cp-n-1" {0b1d7334-78b5-4509-bfda-a1ca895821e8}
"brave-dp-n-1" {becd12b0-b667-4986-8182-67ad753e5ceb}

-------------------------------

[+] Listing running vms
"eksa-admin-1" {733a547d-05ba-4e44-ad82-d74a4fab8202}
"brave-cp-n-1" {0b1d7334-78b5-4509-bfda-a1ca895821e8}
"brave-dp-n-1" {becd12b0-b667-4986-8182-67ad753e5ceb}

-------------------------------

[+] Listing vms vagrant folders
/root/eksa/vms/brave/brave-dp-n-1/
/root/eksa/vms/brave/brave-cp-n-1/
/root/eksa/vms/gw/eksa-admin-1/

-------------------------------

[+] Printing Global Allocation Table /root/eksa/vms/global_allocation_table
eksa-admin-1,08:00:27:8D:0C:F0,192.168.10.50,5022
brave-cp-n-1,08:00:27:3B:63:92,192.168.10.25
brave-tinkerbell-ip,,192.168.10.117
brave-endpoint-ip,,192.168.10.137
brave-dp-n-1,08:00:27:C9:22:A9,192.168.10.148

-------------------------------

[+] Printing Hardware Tables, TinkerbellIPs and endpointIPs for all clusters

******* Cluster brave  details ***********
[+] tinkerbell_ip=192.168.10.117 for  cluster brave
[+] endpoint_ip=192.168.10.137 for  cluster brave
[+] Hardware Table for cluster brave at /root/eksa/vms/brave/generated_hardware.csv
hostname,mac,ip_address,netmask,gateway,nameservers,labels,disk,bmc_ip,bmc_username,bmc_password
brave-cp-n-1,08:00:27:3B:63:92,192.168.10.25,255.255.255.0,192.168.10.1,8.8.8.8,type=cp,/dev/sda,,,
brave-dp-n-1,08:00:27:C9:22:A9,192.168.10.148,255.255.255.0,192.168.10.1,8.8.8.8,type=dp,/dev/sda,,,
```

**NOTE**: `VBoxManage` cli can also be used to list and manage VMs manually from the cloud instance. Refer to [VBoxManage cli docs](https://docs.oracle.com/en/virtualization/virtualbox/7.0/user/vboxmanage.html#vboxmanage-intro).

```sh
sudo su -
VBoxManage list runningvms

"eksa-admin-1" {733a547d-05ba-4e44-ad82-d74a4fab8202}
"brave-cp-n-1" {0b1d7334-78b5-4509-bfda-a1ca895821e8}
"brave-dp-n-1" {becd12b0-b667-4986-8182-67ad753e5ceb}
```

#### Launch VMs for a cluster

- `launch-eksabm-cluster-vms.sh`: Shell script utility to create VMs emulating EKSA-BM cluster machines. This  utility can be used to add additional VMs (perhaps even with custom capacity). `-c` switch is number of **additional** control plane VMs to launch  and `-d` switch is number of **additional** worker nodes/ dataplane VMs to launch. Switches `-p` and `-m` are number of cpus in vcpu and memory in MB respectively. 

```sh
sudo su - 

bash /opt/rafay/vm-scripts/launch-eksabm-cluster-vms.sh
Usage: /opt/rafay/vm-scripts/launch-eksabm-cluster-vms.sh -n <cluster-name> -c <#cp-nodes> -d <#dp-nodes> [ -p <vm_num_cpus> ] [ -m <vm_mem_size> ]
```

Examples:

```sh
Example 1: Add one control plane vm with default size 2 vcpu and 16 GB Mem
# bash /opt/rafay/vm-scripts/launch-eksabm-cluster-vms.sh -n brave -c 1 -d 0

Example 2: Add one control plane vm and one worker vm each with size 4 vcpu and 16 GB Mem
# bash /opt/rafay/vm-scripts/launch-eksabm-cluster-vms.sh -n brave -c 1 -d 1 -p 4 -m 16384

```

#### Delete VMs of a cluster
- `delete-eksabm-cluster-vms.sh`: Shell script utility to delete VMs emulating EKSA-BM cluster machines. If `-v` switch is used, it deletes that virtualbox vm. However switch `-n` can be used to delete all VMs associated with a particular cluster and also its associated tinkerbellIP and endpointIP

```sh
sudo su -
bash /opt/rafay/vm-scripts/delete-eksabm-cluster-vms.sh
Usage: /opt/rafay/vm-scripts/delete-eksabm-cluster-vms.sh [-n <cluster_name>] [-v <vm_name>]

```

Examples:

```sh
Example 1: Delete one vm named brave-cp-n-1 
# bash /opt/rafay/vm-scripts/delete-eksabm-cluster-vms.shh  -v brave-cp-n-1

Example 2: Delete all vms for cluster brave and associated tinkerbellIP and endpointIP
# bash /opt/rafay/vm-scripts/delete-eksabm-cluster-vms.sh  -n brave

```

#### Resurrecting VMs on cloud instance reboot/stop-start

Whenever cloud instance is rebooted or stopped and started, all VMs are **automatically** powered on using utility script `resurrect-vms.sh` on the cloud instance. To manually do the same, SSH to the cloud instance and run below: 

```sh
sudo su -
bash /opt/rafay/vm-scripts/resurrect-vms.sh
```

#### Other utility scripts

Few other utility scripts are listed below (although these should rarely get used in normal circumstances) :

- `create-eksabm-network.sh`: Shell script utility to create the NAT Network for deploying EKSA-BM VMs on: `eksa-net`. You should not normally have to use this script by itself.

- `delete-eksabm-network.sh`: Shell script utility to delete the `eksa-net` NAT Network for EKSA-BM VMs. You should not normally have to use this script by itself.  


- `launch-eksabm-admin-vm.sh`: Shell script utility to launch the EKSA-BM Admin machine. You should not normally have to use this script by itself.   


- `delete-eksabm-admin-vm.sh`: Shell script utility to delete the EKSA-BM Admin machine. You should not normally have to use this script by itself.   



### Using Virtualbox GUI to access VMs and their consoles 

Tightvnc server is installed on the cloud instance during cluster creation. To connect to this vnc server and hence have access to virtualbox GUI, perform following steps on your system:

1. Port forward a local port (say 59000) to vnc port on cloud instance over ssh. The host entry for cloud instance should already be configured in ~/.ssh/config hence you can use the hostname in the ssh command for port forwarding as show below. Leave this ssh command running in a terminal on your system.

```sh
ssh -C -N  -L 59000:localhost:5901 cloud-instance-display-name
```
 

2. Now use a vnc client to connect to vncserver by connecting to local forwarded port on your system (On a Mac laptop simply use Finder->Go->Connect to Server) and use below vnc url and password 

```
vnc://127.0.0.1:59000   

eksapass 
```

Now you should be able to access GUI desktop of the cloud instance and find the virtualbox application in the application finder at the bottom of the screen (as shown below)

![Finding vbox GUI](finding-vbox-GUI.jpg)


Once virtualbox GUI is open, you can acess details of all the virtualbox resources from there. 

![vbox GUI](vbox-GUI.jpg)

To access consoles of VMs, just double click on the vm name. 

![vbox GUI](vbox-vm-console-access.jpg)




### Manually power VMs on/off and change boot order 

`VBoxManage` cli can  be used to list and manage VMs manually from the cloud instance. Refer to [VBoxManage cli docs](https://docs.oracle.com/en/virtualization/virtualbox/7.0/user/vboxmanage.html#vboxmanage-intro).


In advanced use cases and while debugging, it might be necessary to power VMs on and off and also change their boot order (whether to boot from disk or from network). Below are commands to use from the cloud instance


- Power off a VM named brave-dp-n-1

```sh
sudo su -
VBoxManage controlvm brave-dp-n-1 poweroff
```


- Power on a VM named brave-dp-n-1

```sh
sudo su -
VBoxManage startvm brave-dp-n-1 --type=headless
```


- Change boot order of a VM to boot from disk

```sh
sudo su -
VBoxManage controlvm brave-dp-n-1 poweroff
VBoxManage modifyvm brave-dp-n-1 --boot1=disk
```

- Change boot order of a VM to boot from network

```sh
sudo su -
VBoxManage controlvm brave-dp-n-1 poweroff
VBoxManage modifyvm brave-dp-n-1 --boot1=net
```

- List running VMs 

```sh
sudo su -
VBoxManage list runningvms
```

- List VMs 

```sh
sudo su -
VBoxManage list vms
```