#!/bin/bash
# delete-admin-vm.sh (Robbie Gill Feb 2023)

#Variables
VM_DIR='/root/eksa/vms'
GLOBAL_ALLOCATION_TABLE="${VM_DIR}/global_allocation_table"

CLUSTER=""
VM=""

exit_out() {
    echo ${1} && echo && exit -1
}


nuke_admin_vm(){
    VM=${1}
    echo -e "[+] Terminating vm $VM"
    VBoxManage list vms | grep -q ${VM}
    if [ $? -eq 0 ]
    then 
        echo -e "[+] Shutting down vm $VM"
        VBoxManage controlvm $VM poweroff

        VM_FOLDER=$(find $VM_DIR -type f | grep Vagrantfile | sed -e 's/Vagrantfile//g' | grep $VM)
        VM_CLUSTER_FOLDER=$(dirname ${VM_FOLDER})

        if [ -d ${VM_FOLDER} ]
        then
            echo -e "[+] Executing vagrant destroy in vm folder ${VM_FOLDER}" && cd ${VM_FOLDER} && vagrant destroy -f && cd .. && rm -rf ${VM_FOLDER}
        else
            exit_out "Detected an error... vagrant directory for ${VM} does not exist. Could not delete vm"
        fi

        echo -e "[+] Removing entry for ${VM} from global_allocation_table ${GLOBAL_ALLOCATION_TABLE}"
        sed -i "/$VM/d" ${GLOBAL_ALLOCATION_TABLE}

        echo -e "[+] Removing entry for ${VM} from ~/.ssh/config"
        sed -i "/eksa-admin-1/,+5d" ~/.ssh/config

        echo -e "[+] Removing local port forward for ${VM}"
        VBoxManage natnetwork modify --netname eksa-net --port-forward-4 delete ssh-to-${VM}

    else
        exit_out "Detected an error... vm ${VM} does not exist."
    fi 

}

while getopts ":v:" opt; do
  case ${opt} in
    v )
      VM=$OPTARG
      ;;
    \? )
      echo "Usage: $0 -v <vm_name>"
      echo "Provide name of the vm to delete"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

if [ -z $VM ]; then
  echo "Usage: $0 -v <vm_name>"
  echo "Provide name of the vm to delete"
  exit 1
fi


nuke_admin_vm $VM
exit 0 






