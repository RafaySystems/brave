

```sh
$ source venv/bin/activate

$ ./brave.py

[+] Processing input file input.yaml

[+] Generating terraform file tf/oci/terraform.tfvars

[+] Detected infrastructure provider: oci

[+] Detected cluster provisioner: vms_only

[+] Launching infrastructure on provider oci

[+] Switching to  directory tf/oci to launch infrastructure

------ TERRAFORM OUTPUT ----------

Apply complete! Resources: 9 added, 0 changed, 0 destroyed.

Outputs:

instance_public_ip = "152.70.132.182"

[+] IP of launched instance: 152.70.132.182

[+] Switching back to directory /Users/rgill/brave

[+] Waiting 5 minutes to allow infrastructure to boot up on oci
SSH config updated successfully.

[+] Executing on remote host: 152.70.132.182 command: sudo mkdir -p /opt/rafay/; sudo chown -R ubuntu /opt/rafay/

[+] Executed on remote host: 152.70.132.182 command: sudo mkdir -p /opt/rafay/; sudo chown -R ubuntu /opt/rafay/ stdout:  stderr:

[+] Copying ./input.yaml to /opt/rafay/ on 152.70.132.182

[+] Copying ./vm-scripts to /opt/rafay/ on 152.70.132.182
[+]   Copying ./vm-scripts/delete-eksabm-network.sh to /opt/rafay/vm-scripts/delete-eksabm-network.sh on 152.70.132.182
[+]   Copying ./vm-scripts/list-vms.sh to /opt/rafay/vm-scripts/list-vms.sh on 152.70.132.182
[+]   Copying ./vm-scripts/resurrectvms.service to /opt/rafay/vm-scripts/resurrectvms.service on 152.70.132.182
[+]   Copying ./vm-scripts/launch-vms.sh to /opt/rafay/vm-scripts/launch-vms.sh on 152.70.132.182
[+]   Copying ./vm-scripts/install-vbox-vagrant.sh to /opt/rafay/vm-scripts/install-vbox-vagrant.sh on 152.70.132.182
[+]   Copying ./vm-scripts/resurrect-vms.sh to /opt/rafay/vm-scripts/resurrect-vms.sh on 152.70.132.182
[+]   Copying ./vm-scripts/delete-eksabm-cluster-vms.sh to /opt/rafay/vm-scripts/delete-eksabm-cluster-vms.sh on 152.70.132.182
[+]   Copying ./vm-scripts/create-eksabm-network.sh to /opt/rafay/vm-scripts/create-eksabm-network.sh on 152.70.132.182
[+]   Copying ./vm-scripts/create-vm-network.sh to /opt/rafay/vm-scripts/create-vm-network.sh on 152.70.132.182
[+]   Copying ./vm-scripts/list-eksabm-resources.sh to /opt/rafay/vm-scripts/list-eksabm-resources.sh on 152.70.132.182
[+]   Copying ./vm-scripts/check-ubuntu-os.sh to /opt/rafay/vm-scripts/check-ubuntu-os.sh on 152.70.132.182
[+]   Copying ./vm-scripts/launch-eksabm-cluster-vms.sh to /opt/rafay/vm-scripts/launch-eksabm-cluster-vms.sh on 152.70.132.182
[+]   Copying ./vm-scripts/autobot.py to /opt/rafay/vm-scripts/autobot.py on 152.70.132.182
[+]   Copying ./vm-scripts/delete-vm.sh to /opt/rafay/vm-scripts/delete-vm.sh on 152.70.132.182
[+]   Copying ./vm-scripts/delete-eksabm-admin-vm.sh to /opt/rafay/vm-scripts/delete-eksabm-admin-vm.sh on 152.70.132.182
[+]   Copying ./vm-scripts/delete-vm-network.sh to /opt/rafay/vm-scripts/delete-vm-network.sh on 152.70.132.182
[+]   Copying ./vm-scripts/launch-eksabm-admin-vm.sh to /opt/rafay/vm-scripts/launch-eksabm-admin-vm.sh on 152.70.132.182

[+] Copying ./cluster_configs to /opt/rafay/ on 152.70.132.182
[+]   Copying ./cluster_configs/eksa-bm-config.yaml to /opt/rafay/cluster_configs/eksa-bm-config.yaml on 152.70.132.182
[+]   Copying ./cluster_configs/rafay-eksa-bm-config.yaml to /opt/rafay/cluster_configs/rafay-eksa-bm-config.yaml on 152.70.132.182

[+] Copying /opt/rafay/keys/oci to /opt/rafay/ on 152.70.132.182

[+] Executing on remote host: 152.70.132.182 command: sudo chown -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/*

[+] Executed on remote host: 152.70.132.182 command: sudo chown -R ubuntu /opt/rafay/; chmod 600 /opt/rafay//ssh_private_key_file; sudo chmod +x /opt/rafay//vm-scripts/* stdout:  stderr:

[+] Executing on remote host: 152.70.132.182 command: sudo cp -p /opt/rafay//vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service

[+] Executed on remote host: 152.70.132.182 command: sudo cp -p /opt/rafay//vm-scripts/resurrectvms.service /etc/systemd/system/resurrectvms.service; sudo systemctl daemon-reload; sudo systemctl enable resurrectvms.service stdout:  stderr: Created symlink /etc/systemd/system/default.target.wants/resurrectvms.service → /etc/systemd/system/resurrectvms.service.


[+] Installing required system packages on 152.70.132.182

[+] Executing on remote host: 152.70.132.182 command: sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip

[+] Executed on remote host: 152.70.132.182 command: sudo apt-get update; sudo apt-get install -y python3 python-is-python3 python3-pip 
  ---- OUTPUT -----

[+] Installing required python packages on 152.70.132.182

[+] Executing on remote host: 152.70.132.182 command: sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko

[+] Executed on remote host: 152.70.132.182 command: sudo rm -rf /usr/lib/python3/dist-packages/OpenSSL; sudo pip3 uninstall -y pyopenssl; sudo pip3 install --force-reinstall pyopenssl; sudo pip3 install requests pyyaml paramiko stdout:

---- OUTPUT -----

[+] Executing script on 152.70.132.182

Sending command cd /opt/rafay/; sudo python3 vm-scripts/autobot.py
 to 152.70.132.182:22

ubuntu@brave-node:~$ cd /opt/rafay/; sudo python3 vm-scripts/autobot.py

[+] Processing input file /opt/rafay/input.yaml

[+] Detected provisioner: vms_only

[+] Installing vbox. This step may take a while, please be patient.....

---- OUTPUT -----

[+] Creating vm vbox network. This step may take a while, please be patient....
b'[+] Flushing local iptables\n[+] Creating natnetwork vm-net with cidr 192.168.10.0/24 and gateway 192.168.10.1\n[+] Populating network config /root/vm/vms/network_config\nNetworkCidr:192.168.10.0/24\nNetworkGateway:192.168.10.1\n'

[+] Detected vm config:: vm_name: workers, vm_count:2, vm_cpu:3, vm_mem:16384, vm_os_family:ubuntu, vm_vagrant_box:bento/ubuntu-20.04
vm count 2
[+] Checking if vm workers has been launched 2 times already. Detected it has been launched 0 times already

[+] Creating 2 vms of name workers. This step may take a while, please be patient...

---- OUTPUT -----

[+] Detected vm config:: vm_name: storage, vm_count:1, vm_cpu:2, vm_mem:16384, vm_os_family:ubuntu, vm_vagrant_box:bento/ubuntu-20.04
vm count 1
[+] Checking if vm storage has been launched 1 times already. Detected it has been launched 0 times already

[+] Creating 1 vms of name storage. This step may take a while, please be patient...

---- OUTPUT -----

[+] Processed global allocation table /root/vm/vms/global_allocation_table and detected below vms:
vm_name: workers-1, vm_details: {'MAC': '08:00:27:AB:C3:71', 'IP': '192.168.10.89', 'Port': '3389'}
vm_name: workers-2, vm_details: {'MAC': '08:00:27:7E:20:13', 'IP': '192.168.10.221', 'Port': '3221'}
vm_name: storage-1, vm_details: {'MAC': '08:00:27:FD:77:85', 'IP': '192.168.10.23', 'Port': '3323'}

[+] vms created:: vm_name: workers-1, vm_ip:192.168.10.89, vm_mac:08:00:27:AB:C3:71, vm_local_forwarded_port:3389

[+] Waiting 1 minute to allow vm workers-1 to boot up

[+] Copying ssh_public key to authorized keys of vm workers-1

[+] vms created:: vm_name: workers-2, vm_ip:192.168.10.221, vm_mac:08:00:27:7E:20:13, vm_local_forwarded_port:3221

[+] Waiting 1 minute to allow vm workers-2 to boot up

[+] Copying ssh_public key to authorized keys of vm workers-2

[+] vms created:: vm_name: storage-1, vm_ip:192.168.10.23, vm_mac:08:00:27:FD:77:85, vm_local_forwarded_port:3323

[+] Waiting 1 minute to allow vm storage-1 to boot up

[+] Copying ssh_public key to authorized keys of vm storage-1

[+] vms launched. To ssh to vms, run 'ssh <vm_name>' from cloud instance

```