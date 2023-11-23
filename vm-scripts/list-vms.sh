#!/bin/bash


#Variables
VM_DIR='/root/vm/vms'
GLOBAL_ALLOCATION_TABLE="${VM_DIR}/global_allocation_table"
LIST_ALL=""

list_all_resources(){
    echo
    echo '-------------------------------'
    echo
    echo -e "[+]  Listing Networks"
    VBoxManage natnetwork list

    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Listing vms registered with vbox"
    VBoxManage list vms
    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Listing running vms "
    VBoxManage list runningvms
    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Listing vms vagrant folders"
    find $VM_DIR -type f | grep Vagrantfile | sed -e 's/Vagrantfile//g'
    echo
    echo '-------------------------------'
    echo
    echo -e "[+] Printing Global Allocation Table $VM_DIR/global_allocation_table"
    echo  "VM_NAME,VM_MAC,VM_IP,VM_LOCAL_FORWARD_PORT"
    [ -f $VM_DIR/global_allocation_table ] &&  cat $VM_DIR/global_allocation_table
    echo
    echo '-------------------------------'

}



list_all_resources


exit 0 