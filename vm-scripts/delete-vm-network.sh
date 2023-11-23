#!/bin/bash


#Variables
VM_DIR='/root/vm/vms'
NETWORK_CONFIG_FILE="${VM_DIR}/network_config"

exit_out() {
    echo ${1} && echo && exit -1
}


echo -e "[+] Detected network config ${NETWORK_CONFIG_FILE}"
[ -f ${NETWORK_CONFIG_FILE} ] && cat ${NETWORK_CONFIG_FILE}

echo 
echo -e "[+] Deleting network vm-net"
VBoxManage natnetwork remove --netname vm-net 
[ $? -ne 0 ] && exit_out "ERROR:: Detected an error...exiting!!"

rm -rf ${NETWORK_CONFIG_FILE}

exit 0 