#!/bin/bash 
# automation.sh (Robbie Gill Feb 2023)
# Top level script to be run from terraform to prep instance 
echo
echo "##################################################"
echo -e "[+] Executing script install-vbox-vagrant.sh"
sudo bash /home/ubuntu/vm-scripts/install-vbox-vagrant.sh 

echo
echo "##################################################"
echo -e "[+] Executing script create-network.sh"
sudo bash /home/ubuntu/vm-scripts/create-network.sh

echo
echo "##################################################"
echo -e "[+] Executing script launch-admin-vm.sh"
sudo bash /home/ubuntu/vm-scripts/launch-admin-vm.sh

echo
echo "##################################################"
echo -e "[+] Executing script launch-cluster-vms.sh"
sudo bash /home/ubuntu/vm-scripts/launch-cluster-vms.sh -n eksabm1 -c 1 -d 1


