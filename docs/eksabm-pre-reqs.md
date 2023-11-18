#### EKSA-BM Cluster Infrastructure Pre-requisites

[EKSA-BM](https://anywhere.eks.amazonaws.com/docs/getting-started/baremetal/overview/) enables running EKSA Kubernetes clusters on bare metal machines. An EKSA-BM cluster must meet  [hardware and networking requirements](https://anywhere.eks.amazonaws.com/docs/getting-started/baremetal/bare-prereq/) as described below:

**Hardware Requirements** 
1. One Administrative machine 
2. At least one control-plane machine
3. Zero or more worker/data-plane machines

Each cluster machine must meet the minimal capacity requirements of vCPU: 2, Memory: 8GB RAM, Storage: 25GB. Amazon has published a list of [validated hardware](https://anywhere.eks.amazonaws.com/docs/getting-started/baremetal/bare-prereq/#validated-hardware)

**Networking Requirements** 
1. Each machine must include at least one network card capable of network booting.
2. Baseboard Management Controller (BMC) integration (recommended) for automatically powering machines on and off. Without BMC support, machines have to be powered on and off manually at the correct time during provisioning, upgrading and scaling.
3. All EKS Anywhere machines, including the Admin, control plane and worker/data plane machines, must be on the same layer 2 network and have network connectivity to the BMC.
4. You must be able to run DHCP on the control plane/worker machine network. If you have another DHCP service running on the network, you need to prevent it from interfering with the EKS Anywhere DHCP service.
5. Both the Admin machine and the cluster machines need outbound (tcp/443) access to EKSA artifacts on the Internet. 
6. Two IP addresses routable from the cluster, but excluded from DHCP offering. One IP address is to be used as the Control Plane Endpoint IP. The other is for the Tinkerbell IP address on the target cluster. 
7. On the Admin machine, a [number of ports](https://anywhere.eks.amazonaws.com/docs/getting-started/ports/#bare-metal-provider) need to be accessible to all the machines in the cluster, from the same level 2 network. 
