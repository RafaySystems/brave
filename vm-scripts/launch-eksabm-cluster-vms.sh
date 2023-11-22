#!/bin/bash
# launch-cluster-vms.sh (Robbie Gill Feb 2023)

CLUSTER_NAME=""
NUM_CP_NODES=""
NUM_DP_NODES=""
CP_NODE_VM_CPUS=""
CP_NODE_VM_MEM=""

while getopts ":n:c:d:p:m:" opt; do
  case ${opt} in
    n )
      CLUSTER_NAME=$OPTARG
      ;;
    c )
      NUM_CP_NODES=$OPTARG
      ;;
    d )
      NUM_DP_NODES=$OPTARG
      ;;
    p )
      CP_NODE_VM_CPUS=$OPTARG
      ;;   
    m )
      CP_NODE_VM_MEM=$OPTARG
      ;;            
    \? )
      echo "Usage: $0 -n <cluster-name> -c <#cp-nodes> -d <#dp-nodes> [ -p <vm_num_cpus> ] [ -m <vm_mem_size> ]"
      echo "Example:$0 -n robbie-eksa -c 1 -d 0"
      echo "Example:$0 -n robbie-eksa -c 1 -d 0 -p 2 -m 16384"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))


if [[ -z $CLUSTER_NAME || -z $NUM_CP_NODES || -z $NUM_DP_NODES ]]; then
    echo "Usage: $0 -n <cluster-name> -c <#cp-nodes> -d <#dp-nodes> [ -p <vm_num_cpus> ] [ -m <vm_mem_size> ]"
    echo "Example:$0 -n robbie-eksa -c 1 -d 0"
    echo "Example:$0 -n robbie-eksa -c 1 -d 0 -p 2 -m 16384"
    exit 1
fi

[ -z $CP_NODE_VM_CPUS ] && CP_NODE_VM_CPUS='2'
[ -z $CP_NODE_VM_MEM ] && CP_NODE_VM_MEM='16384'

#Variables
VM_DIR='/root/eksa/vms'
GLOBAL_ALLOCATION_TABLE="${VM_DIR}/global_allocation_table"
NETWORK_CONFIG_FILE="${VM_DIR}/network_config"
EKSA_NET=$(grep 'NetworkCidr' ${NETWORK_CONFIG_FILE}  | awk -F':' '{print $2}')
GATEWAY=$(grep 'NetworkGateway' ${NETWORK_CONFIG_FILE}   | awk -F':' '{print $2}')
NAMESERVERS='8.8.8.8'
EKSA_NET_CIDR=`echo ${EKSA_NET}| awk -F'/' '{print $2}'`


DP_NODE_VM_CPUS=${CP_NODE_VM_CPUS}
DP_NODE_VM_MEM=${CP_NODE_VM_MEM}

HARDWARE_CSV_LOCATION="${VM_DIR}/${CLUSTER_NAME}/generated_hardware.csv"
CLUSTER_TINKERBELL_IP_FILE="${VM_DIR}/${CLUSTER_NAME}/tinkerbell_ip"
CLUSTER_ENDPOINT_IP_FILE="${VM_DIR}/${CLUSTER_NAME}/endpoint_ip"
CLUSTER_TINKERBELL_IP=""
CLUSTER_ENDPOINT_IP=""

calc_netmask(){
  cidr=$1
  if [[ ! $cidr =~ ^([0-9]|[1-2][0-9]|3[0-2])$ ]]; then
    echo "ERROR:: Invalid CIDR notation: $cidr" >&2
    exit 1
  fi

  mask=$((0xffffffff << (32 - $cidr)))
  o1=$((($mask >> 24) & 0xff))
  o2=$((($mask >> 16) & 0xff))
  o3=$((($mask >> 8) & 0xff))
  o4=$(($mask & 0xff))
  netmask="$o1.$o2.$o3.$o4"

  echo $netmask
}

NETMASK=$(calc_netmask ${EKSA_NET_CIDR})

generate_mac(){
    MAC=$(echo -n 08:00:27; dd bs=1 count=3 if=/dev/random 2>/dev/null |hexdump -v -e '/1 ":%02X"')
    grep -q ${MAC} ${GLOBAL_ALLOCATION_TABLE}
    while [ $? -eq 0 ]
    do 
        MAC=$(echo -n 08:00:27; dd bs=1 count=3 if=/dev/random 2>/dev/null |hexdump -v -e '/1 ":%02X"')
        grep -q ${MAC} ${GLOBAL_ALLOCATION_TABLE}
    done 
    echo ${MAC}
}

generate_ip() {
    NETWORK=$(echo ${EKSA_NET} | awk -F/ '{print $1}')
    PREFIX=$(echo ${EKSA_NET} | awk -F/ '{print $2}')
    NUM_HOSTS=$((2**(32-$PREFIX)-2))
    RAND=$RANDOM
    IP=$(echo $NETWORK | awk -F. '{print $1"."$2"."$3"."(($4 + 1 + '${RAND}') % '${NUM_HOSTS}' + 1)}')
    grep -q ${IP} ${GLOBAL_ALLOCATION_TABLE}
    while [ $? -eq 0 ]
    do 
        IP=$(echo $NETWORK | awk -F. '{print $1"."$2"."$3"."(($4 + 1 + '${RAND}') % '${NUM_HOSTS}' + 1)}')
        grep -q ${IP} ${GLOBAL_ALLOCATION_TABLE}
    done 

    echo ${IP} 
}

allocate_tinkerbell_ip() {
  
  if [ -f ${CLUSTER_TINKERBELL_IP_FILE} ] 
  then
      CLUSTER_TINKERBELL_IP=$(head -1 ${CLUSTER_TINKERBELL_IP_FILE}| awk '{print $1}')
  else
      CLUSTER_TINKERBELL_IP=$(generate_ip)
      echo ${CLUSTER_TINKERBELL_IP} > ${CLUSTER_TINKERBELL_IP_FILE}
      echo -e "[+] Generated TinkerbellIP ${CLUSTER_TINKERBELL_IP} for cluster ${CLUSTER_NAME} and populated ${CLUSTER_TINKERBELL_IP_FILE}"
  fi 

  grep -q ${CLUSTER_TINKERBELL_IP} ${GLOBAL_ALLOCATION_TABLE} 
  [ $? -ne 0 ] &&  ( echo -e "${CLUSTER_NAME}-tinkerbell-ip,,${CLUSTER_TINKERBELL_IP}" >> ${GLOBAL_ALLOCATION_TABLE}  && echo -e "[+] Updated global allocation table with tinkerbellIP:  ${CLUSTER_NAME}-tinkerbell-ip,,${CLUSTER_TINKERBELL_IP}")

}


allocate_endpoint_ip() {
  
  if [ -f ${CLUSTER_ENDPOINT_IP_FILE} ] 
  then
      CLUSTER_ENDPOINT_IP=$(head -1 ${CLUSTER_ENDPOINT_IP_FILE}| awk '{print $1}')
  else
      CLUSTER_ENDPOINT_IP=$(generate_ip)
      echo ${CLUSTER_ENDPOINT_IP} > ${CLUSTER_ENDPOINT_IP_FILE}
      echo -e "[+] Generated endpointIP ${CLUSTER_ENDPOINT_IP} for cluster ${CLUSTER_NAME} and populated ${CLUSTER_ENDPOINT_IP_FILE}"
  fi 

  grep -q ${CLUSTER_ENDPOINT_IP} ${GLOBAL_ALLOCATION_TABLE} 
  [ $? -ne 0 ] &&  (echo -e "${CLUSTER_NAME}-endpoint-ip,,${CLUSTER_ENDPOINT_IP}" >> ${GLOBAL_ALLOCATION_TABLE}  && echo -e "[+] Updated global allocation table with endpointIP:  ${CLUSTER_NAME}-endpoint-ip,,${CLUSTER_ENDPOINT_IP}")

}

exit_out() {
    echo ${1} && echo && exit -1
}

pre-checks(){
    [ -f ${GLOBAL_ALLOCATION_TABLE} ] || touch ${GLOBAL_ALLOCATION_TABLE}
}


launch-cp-node-vm() {

    CP_NODE_NAME=${1}
    CP_NODE_IP=${2}
    CP_NODE_MAC_ADDR=${3}
    CP_NODE_DIR="${VM_DIR}/${CLUSTER_NAME}/${CP_NODE_NAME}"
    CP_NODE_MAC_ADDR_CONCISE=`echo $CP_NODE_MAC_ADDR | sed -e 's/://g'`

    echo -e "[+] Launching cp-node-vm ${CP_NODE_NAME} with IP ${CP_NODE_IP} and MAC ${CP_NODE_MAC_ADDR}"
    [ -d ${CP_NODE_DIR} ] && exit_out "ERROR:: Detected an error...${CP_NODE_DIR} exists. Exiting"

    # Ensure ${CP_NODE_IP} is present in ${GLOBAL_ALLOCATION_TABLE}
    echo -e "${CP_NODE_NAME},${CP_NODE_MAC_ADDR},${CP_NODE_IP}" >> ${GLOBAL_ALLOCATION_TABLE} && echo -e "[+] Updated global allocation table with entry for ${CP_NODE_NAME} vm:  ${CP_NODE_NAME},${CP_NODE_MAC_ADDR},${CP_NODE_IP}"

    echo -e "\t[+] Creating and switching to directory ${CP_NODE_DIR}"
    mkdir -p ${CP_NODE_DIR} && cd ${CP_NODE_DIR}
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Populate Vagrantfile for cp-node-vm ${CP_NODE_NAME}"
    echo -e  "Vagrant.configure(2) do |config|\n  config.vm.box = 'jtyr/pxe'\n  config.vm.box_check_update = false\n  config.disksize.size = '100GB'\n  config.vm.boot_timeout = 30\n  config.persistent_storage.enabled = true\n  config.persistent_storage.location = \"virtualdrive.vdi\"\n  config.persistent_storage.size = 102400\n  config.persistent_storage.diskdevice = '/dev/sdc'\n  config.persistent_storage.partition = false\n  config.persistent_storage.use_lvm = false\n  config.vm.provider 'virtualbox' do |vb|\n    vb.cpus = ${CP_NODE_VM_CPUS}\n    vb.memory = ${CP_NODE_VM_MEM}\n    vb.name = '${CP_NODE_NAME}'\n    vb.customize ['modifyvm', :id, '--nic1', 'natnetwork', '--nat-network1', 'eksa-net']\n    vb.customize ['modifyvm', :id, '--macaddress1', '${CP_NODE_MAC_ADDR_CONCISE}']\n    vb.customize ['modifyvm', :id, '--boot1', 'net']\n    vb.customize ['modifyvm', :id, '--boot2', 'disk']\n    vb.customize ['modifyvm', :id, '--ostype', 'Linux_64']    \n  end\nend\n\n"  > ./Vagrantfile
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Running vagrant up for cp-node-vm ${CP_NODE_NAME}. IGNORE ERROR - Timed out while waiting for the machine to boot."
    vagrant up

    echo -e "\t[+] Powering off cp-node-vm ${CP_NODE_NAME}"
    VBoxManage controlvm ${CP_NODE_NAME} poweroff

    echo -e "\t[+] Injecting entry in ${HARDWARE_CSV_LOCATION}: ${CP_NODE_NAME},${CP_NODE_MAC_ADDR},${CP_NODE_IP},${NETMASK},${GATEWAY},${NAMESERVERS},type=cp,/dev/sda,,, "
    [ ! -f ${HARDWARE_CSV_LOCATION} ] && echo "hostname,mac,ip_address,netmask,gateway,nameservers,labels,disk,bmc_ip,bmc_username,bmc_password" > ${HARDWARE_CSV_LOCATION}
    echo "${CP_NODE_NAME},${CP_NODE_MAC_ADDR},${CP_NODE_IP},${NETMASK},${GATEWAY},${NAMESERVERS},type=cp,/dev/sda,,," >> ${HARDWARE_CSV_LOCATION}
}

launch-dp-node-vm() {

    DP_NODE_NAME=${1}
    DP_NODE_IP=${2}
    DP_NODE_MAC_ADDR=${3}
    DP_NODE_DIR="${VM_DIR}/${CLUSTER_NAME}/${DP_NODE_NAME}"
    DP_NODE_MAC_ADDR_CONCISE=`echo $DP_NODE_MAC_ADDR | sed -e 's/://g'`


    echo -e "[+] Launching dp-node-vm ${DP_NODE_NAME} with IP ${DP_NODE_IP} and MAC ${DP_NODE_MAC_ADDR}"
    [ -d ${DP_NODE_DIR} ] && exit_out "ERROR:: Detected an error...${DP_NODE_DIR} exists. Exiting"

    # Ensure ${DP_NODE_IP} is present in ${GLOBAL_ALLOCATION_TABLE}
    echo -e "${DP_NODE_NAME},${DP_NODE_MAC_ADDR},${DP_NODE_IP}" >> ${GLOBAL_ALLOCATION_TABLE} && echo -e "[+] Updated global allocation table with entry for ${DP_NODE_NAME} vm:  ${DP_NODE_NAME},${DP_NODE_MAC_ADDR},${DP_NODE_IP}"

    echo -e "\t[+] Creating and switching to directory ${DP_NODE_DIR}"
    mkdir -p ${DP_NODE_DIR} && cd ${DP_NODE_DIR}
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Populate Vagrantfile for dp-node-vm ${DP_NODE_NAME}"
    echo -e  "Vagrant.configure(2) do |config|\n  config.vm.box = 'jtyr/pxe'\n  config.vm.box_check_update = false\n  config.disksize.size = '100GB'\n  config.vm.boot_timeout = 30\n  config.persistent_storage.enabled = true\n  config.persistent_storage.location = \"virtualdrive.vdi\"\n  config.persistent_storage.size = 102400\n  config.persistent_storage.diskdevice = '/dev/sdc'\n  config.persistent_storage.partition = false\n  config.persistent_storage.use_lvm = false\n  config.vm.provider 'virtualbox' do |vb|\n    vb.cpus = ${DP_NODE_VM_CPUS}\n    vb.memory = ${DP_NODE_VM_MEM}\n    vb.name = '${DP_NODE_NAME}'\n    vb.customize ['modifyvm', :id, '--nic1', 'natnetwork', '--nat-network1', 'eksa-net']\n    vb.customize ['modifyvm', :id, '--macaddress1', '${DP_NODE_MAC_ADDR_CONCISE}']\n    vb.customize ['modifyvm', :id, '--boot1', 'net']\n    vb.customize ['modifyvm', :id, '--boot2', 'disk']\n    vb.customize ['modifyvm', :id, '--ostype', 'Linux_64']    \n  end\nend\n\n"  > ./Vagrantfile
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Running vagrant up for dp-node-vm ${DP_NODE_NAME}. IGNORE ERROR - Timed out while waiting for the machine to boot."
    vagrant up

    echo -e "\t[+] Powering off dp-node-vm ${CP_NODE_NAME}"
    VBoxManage controlvm ${DP_NODE_NAME} poweroff

    echo -e "\t[+] Injecting entry in ${HARDWARE_CSV_LOCATION}: ${DP_NODE_NAME},${DP_NODE_MAC_ADDR},${DP_NODE_IP},${NETMASK},${GATEWAY},${NAMESERVERS},type=dp,/dev/sda,,, "
    [ ! -f ${HARDWARE_CSV_LOCATION} ] && echo "hostname,mac,ip_address,netmask,gateway,nameservers,labels,disk,bmc_ip,bmc_username,bmc_password" > ${HARDWARE_CSV_LOCATION}
    echo "${DP_NODE_NAME},${DP_NODE_MAC_ADDR},${DP_NODE_IP},${NETMASK},${GATEWAY},${NAMESERVERS},type=dp,/dev/sda,,," >> ${HARDWARE_CSV_LOCATION}

}


pre-checks

CPCNT=0
CUMULATIVE_CP_NODES=0
while [ ${CPCNT} -lt ${NUM_CP_NODES} ]
do
  ((CPCNT++))
  CUMULATIVE_CP_NODES=`grep "${CLUSTER_NAME}-cp-n-" ${HARDWARE_CSV_LOCATION} 2> /dev/null | wc -l`
  ((CUMULATIVE_CP_NODES++)) 
  CP_NODE_NAMES="${CLUSTER_NAME}-cp-n-${CUMULATIVE_CP_NODES}"
  CP_NODE_IP_ADDR=$(generate_ip)
  CP_NODE_MAC=$(generate_mac)
  launch-cp-node-vm ${CP_NODE_NAMES} ${CP_NODE_IP_ADDR} ${CP_NODE_MAC}
done


DPCNT=0
CUMULATIVE_DP_NODES=0
while [ ${DPCNT} -lt ${NUM_DP_NODES} ]
do
  ((DPCNT++))
  CUMULATIVE_DP_NODES=`grep "${CLUSTER_NAME}-dp-n-" ${HARDWARE_CSV_LOCATION} 2> /dev/null| wc -l` 
  ((CUMULATIVE_DP_NODES++)) 
  DP_NODE_NAMES="${CLUSTER_NAME}-dp-n-${CUMULATIVE_DP_NODES}"
  DP_NODE_IP_ADDR=$(generate_ip)
  DP_NODE_MAC=$(generate_mac)
  launch-dp-node-vm ${DP_NODE_NAMES} ${DP_NODE_IP_ADDR} ${DP_NODE_MAC}
done

allocate_tinkerbell_ip
allocate_endpoint_ip

echo 

CLUSTER_TINKERBELL_IP=$(head -1 ${CLUSTER_TINKERBELL_IP_FILE}| awk '{print $1}')
echo -e "[+] TinkerbellIP ${CLUSTER_TINKERBELL_IP} for cluster ${CLUSTER_NAME}"

CLUSTER_ENDPOINT_IP=$(head -1 ${CLUSTER_ENDPOINT_IP_FILE}| awk '{print $1}')
echo -e "[+] EndpointIP ${CLUSTER_ENDPOINT_IP} for cluster ${CLUSTER_NAME}"

echo -e "[+] Generated Hardware.csv"
cat ${HARDWARE_CSV_LOCATION}
echo 
