#!/bin/bash
# delete-cluster-vms.sh (Robbie Gill Feb 2023)

#Variables
VM_DIR='/root/eksa/vms'
GLOBAL_ALLOCATION_TABLE="${VM_DIR}/global_allocation_table"

CLUSTER=""
VM=""

exit_out() {
    echo ${1} && echo && exit -1
}


nuke_vm(){
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
            exit_out "ERROR:: Detected an error... vagrant directory for ${VM} does not exist. Could not delete vm"
        fi
        
        echo -e "[+] Removing entry for ${VM} from hardware.csv file ${VM_CLUSTER_FOLDER}/generated_hardware.csv"
        sed -i "/$VM/d" ${VM_CLUSTER_FOLDER}/generated_hardware.csv

        echo -e "[+] Removing entry for ${VM} from global_allocation_table ${GLOBAL_ALLOCATION_TABLE}"
        sed -i "/$VM/d" ${GLOBAL_ALLOCATION_TABLE}

    else
        exit_out "ERROR:: Detected an error... vm ${VM} does not exist."
    fi 

}

while getopts ":n:v:" opt; do
  case ${opt} in
    n )
      CLUSTER=$OPTARG
      ;;
    v )
      VM=$OPTARG
      ;;
    \? )
      echo "Usage: $0 [-n <cluster_name>] [-v <vm_name>]"
      echo "Provide name of the vm to delete OR name of the cluster (all vms will be deleted for the cluster)"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

if [[ -z $CLUSTER && -z $VM ]]; then
  echo "Usage: $0 [-n <cluster_name>] [-v <vm_name>]"
  echo "Provide name of the vm to delete OR name of the cluster (all vms will be deleted for the cluster)"
  exit 1
fi


if [[ ! -z $CLUSTER && ! -z $VM ]]; then
  echo "Usage: $0 [-n <cluster_name>] [-v <vm_name>]"
  echo "Provide name of the vm to delete OR name of the cluster (all vms will be deleted for the cluster)"
  exit 1
fi



# If vm is provided 
if [ ! -z $VM ]
then
    nuke_vm $VM

fi


# If cluster is provided 
if [ ! -z $CLUSTER ]
then
    echo -e "[+] Processing cluster $CLUSTER"
    CLUSTER_VMS=$(VBoxManage list vms | grep ${CLUSTER}_ | awk '{print $1}'| sed -e's/\"//g')

    for target in `echo ${CLUSTER_VMS}`
    do
        nuke_vm $target

    done

    echo -e "[+] Removing entry for cluster ${CLUSTER}'s tinkerbellIP and endpointIP from global_allocation_table ${GLOBAL_ALLOCATION_TABLE}"
    sed -i "/${CLUSTER}_/d" ${GLOBAL_ALLOCATION_TABLE}

    echo -e "[+] Deleting cluster folder ${VM_DIR}/${CLUSTER}"
    rm -rf ${VM_DIR}/${CLUSTER}

fi 




