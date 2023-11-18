#!/bin/bash
# launch-admin-vm.sh (Robbie Gill Feb 2023)

#Variables
EKSA_ADMIN_IP=""
EKSA_ADMIN_VM_LOCAL_PORT_FWD=""
EKSA_ADMIN_VM_CPUS=""
EKSA_ADMIN_VM_MEM=""


while getopts ":i:p:c:m:" opt; do
  case ${opt} in
    i )
      EKSA_ADMIN_IP=$OPTARG
      ;;
    p )
      EKSA_ADMIN_VM_LOCAL_PORT_FWD=$OPTARG
      ;;
    c )
      EKSA_ADMIN_VM_CPUS=$OPTARG
      ;;
    m )
      EKSA_ADMIN_VM_MEM=$OPTARG
      ;;      
    \? )
      echo "Usage: $0 [-i <ip>] [-p <local_forward_port>] [-c <vm_num_cpus>] [-m <vm_mem_size>] "
      echo "Example:$0 -i 192.168.10.50/24 -p 5022 -c 2 -m 16384"
      echo "Defaults: ip=192.168.50.0/24, local_forward_port=5022, vm_num_cpus=2, vm_mem_size=16384"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

[ -z $EKSA_ADMIN_IP ] && EKSA_ADMIN_IP='192.168.10.50/24'
[ -z $EKSA_ADMIN_VM_LOCAL_PORT_FWD ] && EKSA_ADMIN_VM_LOCAL_PORT_FWD='5022'
[ -z $EKSA_ADMIN_VM_CPUS ] && EKSA_ADMIN_VM_CPUS='2'
[ -z $EKSA_ADMIN_VM_MEM ] && EKSA_ADMIN_VM_MEM='16384'


VM_DIR='/root/eksa/vms'
NETWORK_CONFIG_FILE="${VM_DIR}/network_config"
GLOBAL_ALLOCATION_TABLE="${VM_DIR}/global_allocation_table"
EKSA_ADMIN_IP_ONLY=`echo ${EKSA_ADMIN_IP}| awk -F'/' '{print $1}'`

EKSA_NET=$(grep 'NetworkCidr' ${NETWORK_CONFIG_FILE}  | awk -F':' '{print $2}')
GATEWAY=$(grep 'NetworkGateway' ${NETWORK_CONFIG_FILE}   | awk -F':' '{print $2}')


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

exit_out() {
    echo ${1} && echo && exit -1
}


[ -f ${GLOBAL_ALLOCATION_TABLE} ] || touch ${GLOBAL_ALLOCATION_TABLE}
EKSA_ADMIN_MAC=$(generate_mac)
EKSA_ADMIN_MAC_CONCISE=`echo $EKSA_ADMIN_MAC | sed -e 's/://g'`
NUM_EKSA_ADMIN_NODES=$(grep -q eksa-admin ${GLOBAL_ALLOCATION_TABLE} 2>/dev/null | wc -l)
((NUM_EKSA_ADMIN_NODES++))
EKSA_ADMIN_VM_NAME="eksa-admin-"${NUM_EKSA_ADMIN_NODES}
EKSA_ADMIN_DIR="${VM_DIR}/gw/${EKSA_ADMIN_VM_NAME}"


grep -q ${EKSA_ADMIN_IP_ONLY} ${GLOBAL_ALLOCATION_TABLE}
if [ $? -eq 0 ]
then
    exit_out "Detected an error...${EKSA_ADMIN_IP_ONLY} is already used elsewhere as per ${GLOBAL_ALLOCATION_TABLE}. PLease provide another IP"
else
    echo -e "${EKSA_ADMIN_VM_NAME},${EKSA_ADMIN_MAC},${EKSA_ADMIN_IP_ONLY},${EKSA_ADMIN_VM_LOCAL_PORT_FWD}" >> ${GLOBAL_ALLOCATION_TABLE} 
    [ $? -eq 0 ] && echo -e "[+] Updated global allocation table with entry:  ${EKSA_ADMIN_VM_NAME},${EKSA_ADMIN_MAC},${EKSA_ADMIN_IP_ONLY},${EKSA_ADMIN_VM_LOCAL_PORT_FWD}"
fi


echo -e "[+] Launching vm ${EKSA_ADMIN_VM_NAME} with IP ${EKSA_ADMIN_IP}"
[ -d ${EKSA_ADMIN_DIR} ] && exit_out "Detected an error...${EKSA_ADMIN_DIR} exists. Exiting"

echo -e "\t[+] Creating and switching to directory ${EKSA_ADMIN_DIR}"
mkdir -p ${EKSA_ADMIN_DIR} && cd ${EKSA_ADMIN_DIR}
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Generating netplan file 01-netcfg.yaml to bring vm interface up on NAT network 'eksa-net'"
echo -e "network:\n  version: 2\n  ethernets:\n    eth0:\n      addresses:\n        - ${EKSA_ADMIN_IP}\n      nameservers:\n        addresses: [8.8.8.8]\n      routes:\n        - to: default\n          via: ${GATEWAY}\n\n" > 01-netcfg.yaml
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Generating ssh key to be embedded in authorized_keys"
echo "n" | ssh-keygen -q -f ./vm-sshkey -t rsa -b 2048 -N ''
echo
echo -e "\t[+] Populate Vagrantfile for ${EKSA_ADMIN_VM_NAME} vm"
echo -e "Vagrant.configure(2) do |config|\n  config.vm.box = 'bento/ubuntu-20.04'\n  config.vm.network :forwarded_port, guest: 22, host: 2322, id: \"ssh\"\n  config.vm.hostname = '${EKSA_ADMIN_VM_NAME}'\n  config.vm.box_check_update = false\n  config.disksize.size = '100GB'\n  config.vm.boot_timeout = 300\n  config.persistent_storage.enabled = true\n  config.persistent_storage.location = \"virtualdrive.vdi\"\n  config.persistent_storage.size = 102400\n  config.persistent_storage.diskdevice = '/dev/sdc'\n  config.persistent_storage.partition = false\n  config.persistent_storage.use_lvm = false\n  config.vm.provider 'virtualbox' do |vb|\n    vb.cpus = ${EKSA_ADMIN_VM_CPUS}\n    vb.memory = ${EKSA_ADMIN_VM_MEM}\n    vb.name = '${EKSA_ADMIN_VM_NAME}'\n    vb.customize ['modifyvm', :id, '--macaddress1', '${EKSA_ADMIN_MAC_CONCISE}']\n  end\nend\n\n" > ./Vagrantfile
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Running vagrant up for ${EKSA_ADMIN_VM_NAME} vm"
vagrant up
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Waiting for /vagrant filesystem to be availaible in ${EKSA_ADMIN_VM_NAME} vm \n"
vagrant ssh -c "ls /vagrant/" | grep -q netcfg
while [ $? -ne 0 ]; do sleep 1; vagrant ssh -c "ls /vagrant/" | grep -q netcfg; done

echo -e "\t[+] Setting up ${EKSA_ADMIN_VM_NAME} vm's netplan to switch to NAT network 'eksa-net'"
vagrant ssh -c "sudo cp -p /vagrant/01-netcfg.yaml /etc/netplan/01-netcfg.yaml; cat /etc/netplan/01-netcfg.yaml"

echo -e "\t[+] Setting up ${EKSA_ADMIN_VM_NAME} vm's ssh key based auth "
sleep 40
vagrant ssh -c "cat /vagrant/vm-sshkey.pub | sudo tee -a /root/.ssh/authorized_keys; cat /vagrant/vm-sshkey.pub >> /home/vagrant/.ssh/authorized_keys"
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Powering off ${EKSA_ADMIN_VM_NAME} vm"
sleep 10
VBoxManage controlvm ${EKSA_ADMIN_VM_NAME} poweroff
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Modify ${EKSA_ADMIN_VM_NAME} vm adapter definition to be on NAT network 'eksa-net'"
sleep 10
VBoxManage modifyvm ${EKSA_ADMIN_VM_NAME} --nic1 'natnetwork' --nat-network1 'eksa-net'
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Starting up ${EKSA_ADMIN_VM_NAME} vm"
sleep 10
VBoxManage startvm ${EKSA_ADMIN_VM_NAME} --type headless
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "Host ${EKSA_ADMIN_VM_NAME}\n    Hostname 127.0.0.1\n    StrictHostKeyChecking no\n    IdentityFile ${EKSA_ADMIN_DIR}/vm-sshkey\n    User vagrant\n    Port ${EKSA_ADMIN_VM_LOCAL_PORT_FWD} \n\n" | sudo tee -a /root/.ssh/config

echo -e "\t[+] Port forward local port ${EKSA_ADMIN_VM_LOCAL_PORT_FWD} to be able to ssh to ${EKSA_ADMIN_VM_NAME} vm's port 22"
VBoxManage natnetwork modify --netname eksa-net --port-forward-4 "ssh-to-${EKSA_ADMIN_VM_NAME}:tcp:[]:${EKSA_ADMIN_VM_LOCAL_PORT_FWD}:[${EKSA_ADMIN_IP_ONLY}]:22"
[ $? -ne 0 ] && exit_out 'Detected an error...exiting!!'

echo -e "\t[+] Please wait for ${EKSA_ADMIN_VM_NAME} vm to come up and then run ssh ${EKSA_ADMIN_VM_NAME}"

exit 0 