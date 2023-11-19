#!/bin/bash
echo "[+] Starting nat network"
VBoxManage natnetwork start --netname eksa-net
for vm in `VBoxManage list vms | awk '{print $1}' | tr \" ' '`
do
	echo "[+] Starting vm $vm"
	VBoxManage startvm $vm --type=headless
done