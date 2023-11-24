#!/bin/bash
# list-resources.sh (Robbie Gill Feb 2023)

#Variables
VM_DIR='/root/eksa/vms'
GLOBAL_ALLOCATION_TABLE="${VM_DIR}/global_allocation_table"
CLUSTER_NAME=""
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
    [ -f $VM_DIR/global_allocation_table ] &&  cat $VM_DIR/global_allocation_table
    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Printing Hardware Tables, TinkerbellIPs and endpointIPs for all clusters"

    for hw in `find $VM_DIR -type f | grep generated_hardware.csv`
    do
        CLUSTER_PATH=$(dirname $hw)
        CLUSTER=$(basename $CLUSTER_PATH)
        CLUSTER_TINKERBELL_IP=$(head -1 ${CLUSTER_PATH}/tinkerbell_ip | awk '{print $1}')
        CLUSTER_ENDPOINT_IP=$(head -1 ${CLUSTER_PATH}/endpoint_ip | awk '{print $1}')
        echo 
        echo "******* Cluster $CLUSTER  details ***********"
        echo -e "[+] tinkerbell_ip=${CLUSTER_TINKERBELL_IP} for  cluster $CLUSTER"
        echo -e "[+] endpoint_ip=${CLUSTER_ENDPOINT_IP} for  cluster $CLUSTER"
        echo -e "[+] Hardware Table for cluster $CLUSTER at $hw" && cat $hw && echo

    done
    echo


}

list_cluster_resources(){
    CLUSTER=${1}

    echo
    echo -e "[+] Listing vms for cluster $CLUSTER"
    VBoxManage list vms | grep -i $CLUSTER
    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Listing running vms for cluster $CLUSTER"
    VBoxManage list runningvms | grep -i $CLUSTER
    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Listing vms vagrant folders for cluster $CLUSTER"
    find $VM_DIR -type f | grep Vagrantfile | sed -e 's/Vagrantfile//g' | grep -i $CLUSTER
    echo
    echo '-------------------------------'
    echo
    echo -e "[+] Printing Global Allocation Table entries for cluster $grep -i $CLUSTER ($VM_DIR/global_allocation_table)"
    [ -f $VM_DIR/global_allocation_table ] &&  cat $VM_DIR/global_allocation_table | grep -i $CLUSTER
    echo
    echo '-------------------------------'

    echo
    echo -e "[+] Printing Hardware Tables, TinkerbellIPs and endpointIPs for cluster $CLUSTER"

    CLUSTER_TINKERBELL_IP_FILE="${VM_DIR}/${CLUSTER}/tinkerbell_ip"
    CLUSTER_ENDPOINT_IP_FILE="${VM_DIR}/${CLUSTER}/endpoint_ip"
    HARDWARE_CSV_LOCATION="${VM_DIR}/${CLUSTER_NAME}/generated_hardware.csv"
    CLUSTER_TINKERBELL_IP=$(head -1 ${CLUSTER_TINKERBELL_IP_FILE} | awk '{print $1}')
    CLUSTER_ENDPOINT_IP=$(head -1 ${CLUSTER_ENDPOINT_IP_FILE} | awk '{print $1}')
    echo 
    echo "******* Cluster $CLUSTER  details ***********"
    echo -e "[+] tinkerbell_ip=${CLUSTER_TINKERBELL_IP} for  cluster $CLUSTER"
    echo -e "[+] endpoint_ip=${CLUSTER_ENDPOINT_IP} for  cluster $CLUSTER"
    echo -e "[+] Hardware Table for cluster $CLUSTER at $HARDWARE_CSV_LOCATION" && cat $HARDWARE_CSV_LOCATION && echo

    echo



}

while getopts ":n:a" opt; do
  case ${opt} in
    n )
      CLUSTER_NAME=$OPTARG
      ;;
    a )
      LIST_ALL="TRUE"
      ;;      
    \? )
      echo "Usage: $0 [-n <cluster_name>] [-a]"
      echo "List all resources OR list resources for a cluster"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

[ -z $CLUSTER_NAME ] && [ -z $LIST_ALL ] && echo "Usage: $0 [-n <cluster_name>] [-a]" && echo "List all resources OR list resources for a cluster" && exit 1

if [ -z $CLUSTER_NAME ]; then
    list_all_resources
else
    list_cluster_resources $CLUSTER_NAME
fi

exit 0 