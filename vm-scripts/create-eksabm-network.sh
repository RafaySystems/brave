#!/bin/bash
# create-network.sh (Robbie Gill Feb 2023)

#Variables
EKSA_NET=""
GATEWAY=""
VM_DIR='/root/eksa/vms'
NETWORK_CONFIG_FILE="${VM_DIR}/network_config"

exit_out() {
    echo ${1} && echo && exit 0
}

flush-iptables() {
    echo -e "[+] Flushing local iptables"
    iptables -F; iptables -t nat -F; netfilter-persistent save  > /dev/null 2>&1
}


while getopts ":e:g:" opt; do
  case ${opt} in
    e )
      EKSA_NET=$OPTARG
      ;;
    g )
      GATEWAY=$OPTARG
      ;;
    \? )
      echo "Usage: $0 [-e <net_cidr>] [-g <net-gateway-ip>]"
      echo "Example:$0 -e 192.168.10.0/24 -g 192.168.10.1"
      echo "Defaults: net_cidr=192.168.10.0/24 net-gateway-ip=192.168.10.1"
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

[ -z $EKSA_NET ] && EKSA_NET='192.168.10.0/24'
[ -z $GATEWAY ] && GATEWAY='192.168.10.1'


flush-iptables

mkdir -p ${VM_DIR}

VBoxManage list natnetworks | grep  -q eksa-net
[ $? -eq 0 ] && exit_out "Detected existing network vm-net..."

echo -e "[+] Creating natnetwork eksa-net with cidr ${EKSA_NET} and gateway ${GATEWAY}"
VBoxManage natnetwork add --netname eksa-net --network "${EKSA_NET}" --enable --dhcp off
[ $? -ne 0 ] && exit_out "ERROR:: Detected an error...exiting!!"

VBoxManage natnetwork start --netname eksa-net

echo -e "[+] Populating network config ${NETWORK_CONFIG_FILE}"
echo -e "NetworkCidr:$EKSA_NET\nNetworkGateway:${GATEWAY}" > ${NETWORK_CONFIG_FILE}
cat ${NETWORK_CONFIG_FILE}

exit 0 