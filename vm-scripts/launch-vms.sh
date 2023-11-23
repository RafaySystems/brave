#!/bin/bash

VMS_NAME=""
VM_COUNT=1
VM_CPUS=2
VM_MEM=16384
VM_IMAGE="bento/ubuntu-20.04"    # VM_IMAGE='jtyr/pxe'
VM_OS_FAMILY="ubuntu"            # Future options pxe, centos, rockyos , rhel  etc.


while getopts ":n:c:p:m:o:i:" opt; do
  case ${opt} in
    n )
      VMS_NAME=$OPTARG
      ;;
    c )
      VM_COUNT=$OPTARG
      ;;
    p )
      VM_CPUS=$OPTARG
      ;;   
    m )
      VM_MEM=$OPTARG
      ;;  
    o )
      VM_OS_FAMILY=$OPTARG
      ;;                
    i )
      VM_IMAGE=$OPTARG
      ;;         
    \? )
      echo "Usage: $0 -n <vm-name> [-c <#vms> -p <vm_num_cpus> -m <vm_mem_size> -o <vm_os_family> -i <vm_image>]"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))


if [[ -z $VMS_NAME ]]; then
    echo "Usage: $0 -n <vm-name> [-c <#vms> -p <vm_num_cpus> -m <vm_mem_size> -o <vm_os_family> -i <vm_image>]"
    exit 1
fi

[ -z $VM_COUNT ] && VM_COUNT=1
[ -z $VM_CPUS ] && VM_CPUS=2
[ -z $VM_MEM ] && VM_MEM=16384
[ -z $VM_IMAGE ] && VM_IMAGE="bento/ubuntu-20.04"
[ -z $VM_OS_FAMILY ] && VM_OS_FAMILY="ubuntu"


VM_BASE_DIR='/root/vm/vms'
NETWORK_CONFIG_FILE="${VM_BASE_DIR}/network_config"
GLOBAL_ALLOCATION_TABLE="${VM_BASE_DIR}/global_allocation_table"
VM_NET=$(grep 'NetworkCidr' ${NETWORK_CONFIG_FILE}  | awk -F':' '{print $2}')
GATEWAY=$(grep 'NetworkGateway' ${NETWORK_CONFIG_FILE}   | awk -F':' '{print $2}')


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
    NETWORK=$(echo ${VM_NET} | awk -F/ '{print $1}')
    PREFIX=$(echo ${VM_NET} | awk -F/ '{print $2}')
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

exit_out() {
    echo ${1} && echo && exit -1
}

pre-checks(){
    [ -f ${GLOBAL_ALLOCATION_TABLE} ] || touch ${GLOBAL_ALLOCATION_TABLE}
}


launch-ubuntu-vm() {

    VM_NAME=${1}
    VM_IP=${2}
    VM_MAC_ADDR=${3}
    VM_DIR="${VM_BASE_DIR}/${VM_NAME}/"
    VM_MAC_ADDR_CONCISE=`echo $VM_MAC_ADDR | sed -e 's/://g'`
    
    # extract last octet of the IP address and use that as local port forward padded in front by digit 3 to make it 4 digits
    VM_LOCAL_PORT_FWD=`echo ${VM_IP} | awk -F. '{last_octet = $4; printf "%s%d\n", substr("3333", 1, 4-length(last_octet)), last_octet}'`

    echo -e "[+] Launching vm ${VM_NAME} with IP ${VM_IP} and MAC ${VM_MAC_ADDR}"
    [ -d ${VM_DIR} ] && exit_out "ERROR:: Detected an error...${VM_DIR} exists. Exiting"

    # Ensure ${VM_IP} is present in ${GLOBAL_ALLOCATION_TABLE}
    echo -e "${VM_NAME},${VM_MAC_ADDR},${VM_IP},${VM_LOCAL_PORT_FWD}" >> ${GLOBAL_ALLOCATION_TABLE} && echo -e "[+] Updated global allocation table with entry for ${VM_NAME} vm:  ${VM_NAME},${VM_MAC_ADDR},${VM_IP},${VM_LOCAL_PORT_FWD}"

    echo -e "\t[+] Creating and switching to directory ${VM_DIR}"
    mkdir -p ${VM_DIR} && cd ${VM_DIR}
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Generating netplan file 01-netcfg.yaml to bring vm interface up on NAT network 'vm-net'"
    echo -e "network:\n  version: 2\n  ethernets:\n    eth0:\n      addresses:\n        - ${VM_IP}/24\n      nameservers:\n        addresses: [8.8.8.8]\n      routes:\n        - to: default\n          via: ${GATEWAY}\n\n" > 01-netcfg.yaml
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Generating ssh key to be embedded in authorized_keys"
    echo "n" | ssh-keygen -q -f ./vm-sshkey -t rsa -b 2048 -N ''
    echo
    echo -e "\t[+] Populate Vagrantfile for ${VM_NAME} vm"
    echo -e "Vagrant.configure(2) do |config|\n  config.vm.box = '${VM_IMAGE}'\n  config.vm.network :forwarded_port, guest: 22, host: ${VM_LOCAL_PORT_FWD}, id: \"ssh\"\n  config.vm.hostname = '${VM_NAME}'\n  config.vm.box_check_update = false\n  config.disksize.size = '500GB'\n  config.vm.boot_timeout = 300\n  config.persistent_storage.enabled = true\n  config.persistent_storage.location = \"virtualdrive.vdi\"\n  config.persistent_storage.size = 102400\n  config.persistent_storage.diskdevice = '/dev/sdc'\n  config.persistent_storage.partition = false\n  config.persistent_storage.use_lvm = false\n  config.vm.provider 'virtualbox' do |vb|\n    vb.cpus = ${VM_CPUS}\n    vb.memory = ${VM_MEM}\n    vb.name = '${VM_NAME}'\n    vb.customize ['modifyvm', :id, '--macaddress1', '${VM_MAC_ADDR_CONCISE}']\n  end\nend\n\n" > ./Vagrantfile
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Running vagrant up for ${VM_NAME} vm"
    vagrant up
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Waiting for /vagrant filesystem to be availaible in ${VM_NAME} vm \n"
    vagrant ssh -c "ls /vagrant/" | grep -q netcfg
    while [ $? -ne 0 ]; do sleep 1; vagrant ssh -c "ls /vagrant/" | grep -q netcfg; done

    echo -e "\t[+] Setting up ${VM_NAME} vm's netplan to switch to NAT network 'vm-net'"
    vagrant ssh -c "sudo cp -p /vagrant/01-netcfg.yaml /etc/netplan/01-netcfg.yaml; cat /etc/netplan/01-netcfg.yaml"

    echo -e "\t[+] Setting up ${VM_NAME} vm's ssh key based auth "
    sleep 40
    vagrant ssh -c "cat /vagrant/vm-sshkey.pub | sudo tee -a /root/.ssh/authorized_keys; cat /vagrant/vm-sshkey.pub >> /home/vagrant/.ssh/authorized_keys"
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Powering off ${VM_NAME} vm"
    sleep 10
    VBoxManage controlvm ${VM_NAME} poweroff
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Modify ${VM_NAME} vm adapter definition to be on NAT network 'vm-net'"
    sleep 10
    VBoxManage modifyvm ${VM_NAME} --nic1 'natnetwork' --nat-network1 'vm-net'
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Starting up ${VM_NAME} vm"
    sleep 10
    VBoxManage startvm ${VM_NAME} --type headless
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "Host ${VM_NAME}\n    Hostname 127.0.0.1\n    StrictHostKeyChecking no\n    IdentityFile ${VM_DIR}/vm-sshkey\n    User vagrant\n    Port ${VM_LOCAL_PORT_FWD} \n\n" | sudo tee -a /root/.ssh/config

    echo -e "\t[+] Port forward local port ${VM_LOCAL_PORT_FWD} to be able to ssh to ${VM_NAME} vm's port 22"
    VBoxManage natnetwork modify --netname vm-net --port-forward-4 "ssh-to-${VM_NAME}:tcp:[]:${VM_LOCAL_PORT_FWD}:[${VM_IP}]:22"
    [ $? -ne 0 ] && exit_out 'ERROR:: Detected an error...exiting!!'

    echo -e "\t[+] Please wait for ${VM_NAME} vm to come up and then run ssh ${VM_NAME}"
    echo
    echo
    cd - > /dev/null 2>&1
}


pre-checks

# Check if VM_NAME is already present in ${GLOBAL_ALLOCATION_TABLE}
#grep -q ${VMS_NAME} ${GLOBAL_ALLOCATION_TABLE}
#if [ $? -eq 0 ]
#then
#    echo -e "[+] ERROR:: Detected an error...${VMS_NAME} already exists in ${GLOBAL_ALLOCATION_TABLE}. Please choose another name. Exiting"
#    exit 1
#fi

CNT=0
[ ${VM_COUNT} -eq 0 ] && exit 0

while [ ${CNT} -lt ${VM_COUNT} ]
do
  ((CNT++))
  VM_NAME="${VMS_NAME}-${CNT}"
  VM_IP=$(generate_ip)
  VM_MAC_ADDR=$(generate_mac)

  # If VM_OS_FAMILY is ubuntu, launch ubuntu vm
  if [ ${VM_OS_FAMILY} == "ubuntu" ];
  then
    echo -e "[+] Launching ubuntu vm ${VM_NAME}:  IP=${VM_IP} MAC=${VM_MAC_ADDR},VM_CPUS=${VM_CPUS},VM_MEM=${VM_MEM},VM_IMAGE=${VM_IMAGE} " 
    launch-ubuntu-vm ${VM_NAME} ${VM_IP} ${VM_MAC_ADDR} 
  else
    echo -e "[+] ERROR:: Unsupported OS family ${VM_OS_FAMILY}...exiting!!"
    exit 1
  fi

done
exit 0 

