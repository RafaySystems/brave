
- [Populating input.yaml file](#populating-inputyaml-file)
    - [Infrastructure provider details](#3-infrastructure-provider-details)
        - [Using AWS cloud as infrastructure provider](#using-aws-cloud-as-infrastructure-provider)
        - [Using OCI cloud as infrastructure provider](#using-oci-cloud-as-infrastructure-provider)
        - [Using pre existing cloud instance](#using-pre-existing-cloud-instance)
    - [Cluster provisioner details](#2-cluster-provisioner-details)
        - [Using `vms_only` provisioner](#using-native-provisioner)
        - [Using `eksabm_cluster` provisioner](#using-native-provisioner)
        - [Using `rafay_eksabm_cluster` provisioner](#using-rafay-provisioner)
        - [Using `none` provisioner](#using-none-provisioner)
- [Example input.yaml files](#example-inputyaml-files)

---
## Populating input.yaml file  

`input.yaml` is a yaml file that contains configuration for `b.r.a.v.e`. Below is detailed explaination of its structure:

### 1. Infrastructure provider details
Choose an infrastructure_provider by configuring key `infrastructure_provider` in the `input.yaml` file. This provider is the cloud provider where cloud instance will be launched. This single instance will host the entire virtualized environment - all vms and the network. Valid options are `aws`, `oci` and `infra_exists`.  Configuration needs to be provided using key `infrastructure_provider_config`.  

#### Using AWS cloud as infrastructure provider 
See example below for using AWS cloud as infrastructure provider.

```sh
infrastructure_provider: aws
infrastructure_provider_config:
  aws:
    region: "us-west-1"
    host_name: "brave-node"
    instance_type: "c5n.metal" 
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    ssh_key_name: "eksabmsshkey"
    ssh_private_key_file: "/opt/rafay/keys/oci"  
```

Configuration items under `infrastructure_provider_config.aws` key are:
-  `region`: AWS region to create instance in. **!!! Change as needed !!!**
-  `host_name`: Name for the cloud instance. Also used to create ~/.ssh/config entry.  **!!! Change as needed !!!**
-  `instance_type`: An instance type that can support Virtualbox VMs. Essentially any `metal` instance_type
-  `ssh_public_key`: SSH public key to inject in authorized_keys of the cloud instance. For VMs launched by `vms_only` provisioner, this key is automatically injected in ssh authorized_keys. For an EKSA-BM cluster, the same key is injected in authorized_keys of `eksa-admin` VM and all other cluster VMs (unless config file is being used in which case ssh public key in config file is used for cluster nodes). This should be public part of private key in `ssh_private_key_file`.   **!!! Must Change from Default !!!**
-  `ssh_private_key_file`: File containing private part of the SSH public key listed in `ssh_public_key`. This private key is injected in local ssh host entries injected automatically to log in to cloud instance. For VMs launched by `vms_only` provisioner, this key is injected in Host entries created automatically to ssh to VMs from cloud instance. For EKSA-BM clusters, this is also done on cloud instance to ssh in to `eksa-admin` machine. The same private key file can also be used to ssh into cluster nodes frpm `eksa-admin` machine (unless config file is being used and a different ssh public key is specified there). **!!! Must Change from Default !!!**
-  `ssh_key_name`:  Key name you want to give to the AWS SSH key generated using the ssh public key listed in `ssh_public_key`. This object is associated with cloud instance to permit logging in via ssh.  Leave the existing default value in input.yaml if you wish. 

When creating EKSA-BM clusters, ensure that capacity of cloud instance can house all VMs required for desired cluster i.e. Admin vm (2 vcpu, 16GB Mem) and desired number of control plane and worker nodes (each 2 vcpu, 16GB Mem). 

**AWS Authentication Credentials**
Credentials for AWS can be provided in any manner compatible with terraform provider for AWS. Most convenoent are:
- [Exporting env variables](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#environment-variables) `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` 
- OR [Providing ~/.aws/credentials file](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#shared-configuration-and-credentials-files) 

All AWS infrastructure required to support the cloud instance - vpc, public subnet, Internet gateway, route table, security group etc. are created from scratch. The cloud instance created has an elastic IP reachable from the Internet and ONLY inbound port 22/tcp traffic permitted. Ubuntu-20.04 is used as OS for the cloud instance.

#### Using OCI cloud as infrastructure provider  
See example below for using OCI cloud as infrastructure provider.

```sh
infrastructure_provider: oci 
infrastructure_provider_config:  
  oci:
    host_name: "brave-node"
    instance_flex_memory_in_gbs: 64
    instance_flex_ocpus: 4    
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    region: "us-phoenix-1"
    tenancy_ocid: "ocid1.tenancy.oc1..aaaaaaaaaa3ghjcqbrbzmssbzhxzhxf24rpmuyxbaxwcj2axwoqkpd56ljkq"
    user_ocid: "ocid1.user.oc1..aaaaaaaac6nqpe4rsz3em53qtkkfq2pd4otg3j347wgku6eidkfcf5tr7kta"
    private_key_path: "/Users/rgill/.oci/oci_api_key.pem" 
    fingerprint: "ed:8b:e9:3c:72:4c:39:70:20:0b:97:9e:59:fb:60:e9"
```

Configuration items under `infrastructure_provider_config.oci` key are:
-  `host_name`: Name for the cloud instance. Also used to create ~/.ssh/config entry.  **!!! Change as needed !!!**
-  `instance_flex_memory_in_gbs`: The total amount of memory available to the instance, in gigabytes.
-  `instance_flex_ocpus`: The total number of OCPUs available to the instance. 1 ocpu = 2 vcpus
-  `ssh_public_key`: SSH public key to inject in authorized_keys of the cloud instance. For VMs launched by `vms_only` provisioner, this key is automatically injected in ssh authorized_keys. For an EKSA-BM cluster, the same key is injected in authorized_keys of `eksa-admin` VM and all other cluster VMs (unless config file is being used in which case ssh public key in config file is used for cluster nodes). This should be public part of private key in `ssh_private_key_file`.   **!!! Must Change from Default !!!**
-  `ssh_private_key_file`: File containing private part of the SSH public key listed in `ssh_public_key`. This private key is injected in local ssh host entries injected automatically to log in to cloud instance. For VMs launched by `vms_only` provisioner, this key is injected in Host entries created automatically to ssh to VMs from cloud instance. For EKSA-BM clusters, this is also done on cloud instance to ssh in to `eksa-admin` machine. The same private key file can also be used to ssh into cluster nodes frpm `eksa-admin` machine (unless config file is being used and a different ssh public key is specified there). **!!! Must Change from Default !!!**
-  `region`: OCI region to create instance in. **!!! Change as needed !!!**
-  `tenancy_ocid`:  Tenancy ocid where to create the sources. Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
-  `user_ocid`: Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
-  `private_key_path`: Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
-  `fingerprint`:  Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).

When creating EKSA-BM clusters, ensure that capacity of cloud instance can house all VMs required for desired cluster i.e. Admin VM (2 vcpu, 16GB Mem) and desired number of control plane and worker nodes (each 2 vcpu, 16GB Mem). Capacity of OCI cloud instance is defined by variables `instance_flex_memory_in_gbs`, `instance_flex_ocpus` (Note: 1 ocpu = 2 vcpus). 

All OCI infrastructure required to support the cloud instance - vcn, public subnet, Internet gateway, route table, security group etc. are created from scratch. The cloud instance created has an public IP reachable from the Internet and ONLY inbound port 22/tcp traffic permitted to the instance. Ubuntu-20.04 is used as OS for the cloud instance.

#### Using pre existing cloud instance 

If one does not wish to launch a cloud instance using **`b.r.a.v.e`** OR such an instance pre-exists (in any cloud that supports instances that can run Virtualbox vms), `infra_exists` provider can be  used. If `infra_exists` is selected using key `infrastructure_provider`, SSH connection details need to be configured for **`brave`** to be able to connect to this instance. Use key `infrastructure_provider_config` for providing this configuration as shown in below example. 

```
infrastructure_provider: infra_exists 
infrastructure_provider_config: 
  infra_exists:
    host_name: "brave-node"
    ssh_host_ip: "129.146.86.26"
    ssh_username: "ubuntu"
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
```
Configuration items under `infrastructure_provider_config.infra_exists` key are:
-  `host_name`: Name for the pre-existing cloud instance.  Used to create ~/.ssh/config entry.  **!!! Change as needed !!!**
-  `ssh_host_ip`: IP of the pre-existing cloud instance.  Used to create ~/.ssh/config entry.  **!!! Change as needed !!!**
-  `ssh_username`: username to connect to pre-existing cloud instance over ssh.  Used to create ~/.ssh/config entry.  **!!! Change as needed !!!**
-  `ssh_public_key`: SSH public key to inject in authorized_keys of the cloud instance. For VMs launched by `vms_only` provisioner, this key is automatically injected in ssh authorized_keys. For an EKSA-BM cluster, the same key is injected in authorized_keys of `eksa-admin` VM and all other cluster VMs (unless config file is being used in which case ssh public key in config file is used for cluster nodes). This should be public part of private key in `ssh_private_key_file`.   **!!! Must Change from Default !!!**
-  `ssh_private_key_file`: File containing private part of the SSH public key listed in `ssh_public_key`. This private key is injected in local ssh host entries injected automatically to log in to cloud instance. For VMs launched by `vms_only` provisioner, this key is injected in Host entries created automatically to ssh to VMs from cloud instance. For EKSA-BM clusters, this is also done on cloud instance to ssh in to `eksa-admin` machine. The same private key file can also be used to ssh into cluster nodes frpm `eksa-admin` machine (unless config file is being used and a different ssh public key is specified there). **!!! Must Change from Default !!!**


**Cloud Instance requirements. If using `infra_exists` provider**
- cloud instance OS must be Ubuntu 20.04 
- cloud instance must have access to the Internet 
- cloud Instance must have an IP that is publicly reachable over ssh
- cloud Instance must have enough capacity to hold all vms emulating the EKSA-BM hardware 


### 2. Provisioner details

Choose a provisioner (using key `provisioner` ) and fill out configuration for the chosen provisioner (using key `provisioner_config`).  Four provisioners are supported : `vms_only`, `eksabm_cluster`, `rafay_eksabm_cluster`, or `none`

#### Using `vms_only` provisioner 

This provisioner deploys VMs on the cloud instance. Below is an example configuration for using this provisioner to launch VMs on the cloud instance created using `infrastructure_provider`. This configuration instructs `b.r.a.v.e` to deploy total 3 Virtualbox VMs:
     - 2x ubuntu 20.04 VMs with name *workers* and capacity cpu=3vcpus and memory=16GB. These VMs will be named `workers-1` and `workers-2`
     - 1x ubuntu 20.04 VM with name *storage* and capacity cpu=2vcpus and memory=16GB. This VM will be named `storage-1`. 

```sh
provisioner: vms_only 
provisioner_config:
  vms_only:
    - name: "workers"
      count: 2
      cpu: 3       
      mem: 16384   
      osfamily: ubuntu 
      vagrant_box: "bento/ubuntu-20.04"
    - name: "storage"
```

VMs are described as an array under `provisioner_config.vms_only` key and each array element is a VM configuration set and contains following items:

- `name`: Name prefix used for the VM set. Each VM within a set is named "name-count" e.g. if name is "workers" and count is 2, then 2 VMs will be created with names "workers-1" and "workers-2" for this set. **!!! Change as needed !!!**
- `count`: Number of VMs to launch within the set. Default value is 1 
- `cpu`:  Number of vcpus to allocate to each VM in the set. Default value is 2
- `mem`:  Memory (in MB) to allocate to each VM in the set. Default value is 16384
- `osfamily`: OS family of each VM in the set. Only supported value and Default currently is "ubuntu"
- `vagrant_box`: Vagrant Box used for each VM in the set. Default value is bento/ubuntu-20.04


#### Using `eksabm_cluster` provisioner 

This provisioner creates EKSA-BM cluster on the cloud instance using VMs. Below is an example configuration for using this provisioner to launch EKSA-BM cluster on the cloud instance created using `infrastructure_provider`. This configuration instructs `b.r.a.v.e` to create a EKSA-BM cluster named "brave" with K8s version 1.27 and 1 control plane node and 1 worker node. Provisioner will use defaults for all rest of EKSA-BM cluster configuration. 

```sh
provisioner: eksabm_cluster 
provisioner_config:
  eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1    
```

However it is also possible to create a cluster using a config file, which allows flexibility to provide advanced configuration for the cluster. A config file can be created using [EKSA-BM spec](https://anywhere.eks.amazonaws.com/docs/getting-started/baremetal/bare-spec/) (example [here](../cluster_configs/eksa-bm-config.yaml)). The config file is expected to be located under **cluster_configs** directory. 

```sh
provisioner: eksabm_cluster 
provisioner_config:
  eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    config_file_name: "eksa-bm-config.yaml" 
```


#### Using `rafay_eksabm_cluster` provisioner 

`rafay_eksabm_cluster` provisioner can also be used to create an EKSA-BM cluster. However rather than using eksctl cli directly, an Rafay controller is used to create the cluster. Some additional configuration is required such as the URL of the Rafay controller, an existing Rafay project name, name of the EKSA-BM gateway to create and location of a file containing a valid [RAFAY API key](https://docs.rafay.co/security/rbac/users/#manage-keys) (as demonstrated in the example below).  

```sh
provisioner: rafay_eksabm_cluster 
provisioner_config:
  rafay_eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1
    rafay_controller_url: "https://console.rafay.dev/"
    rafay_api_key_file: "/home/rgill/oci_api.key"
    rafay_project_name: "brave"
    rafay_eksabm_gateway_name: "brave-gw" 
```

It is also possible to create a cluster using a config file, which allows flexibility to provide advanced configuration for the cluster. A config file can be created using by using [Rafay System's EKSA-BM spec](https://docs.rafay.co/clusters/eksa_bm/eksabm_schema/) (example [here](../cluster_configs/rafay-eksa-bm-config.yaml)). The config file is expected to be located under **cluster_configs** directory. 

```sh
provisioner: rafay_eksabm_cluster 
provisioner_config:
  rafay_eksabm_cluster:
     cluster_name: "brave-rafay-cluster"
     operation_type: "provision"
     config_file_name: "rafay-eksa-bm-config.yaml" 
     rafay_controller_url: "https://console.rafay.dev/"
     rafay_api_key_file: "/home/rgill/oci_api.key"
     rafay_project_name: "brave"
     rafay_eksabm_gateway_name: "brave-gw" 
```



#### Using `none` provisioner 
If you do not wish to use a provisioner at all, you can select the `none` option as shown below. This can be relevant if you wanted to perhaps just want to create the cloud instance.


```sh
provisioner: none 
provisioner_config:
  none:
    config: none
```


---

## Example configuration files 

### Complete Example input.yaml file 

```sh
# Infrastructure provider  !! CHANGE THIS TO YOUR INFRASTRUCTURE PROVIDER (aws, oci or infra_exists) 
infrastructure_provider: oci  

infrastructure_provider_config:
# AWS infrastructure provider configuration
  aws:
    region: "us-west-1"
    host_name: "brave-node"
    instance_type: "c5n.metal" #Choose a metal instance type
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    ssh_key_name: "eksabmsshkey"
    ssh_private_key_file: "/opt/rafay/keys/oci"    

# OCI infrastructure provider configuration
  oci:
    host_name: "brave-node"
    instance_flex_memory_in_gbs: 80
    instance_flex_ocpus: 6    
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    region: "us-phoenix-1"
    tenancy_ocid: "ocid1.tenancy.oc1..aaaaaaaaaa3ghjcqbrbzmssbzhxzhxf24rpmuyxbaxwcj2axwoqkpd56ljkq"
    user_ocid: "ocid1.user.oc1..aaaaaaaac6nqpe4rsz3em53qtkkfq2pd4otg3j347wgku6eidkfcf5tr7kta"
    private_key_path: "/Users/rgill/.oci/oci_api_key.pem" # private key for OCI user
    fingerprint: "ed:8b:e9:3c:72:4c:39:70:20:0b:97:9e:59:fb:60:e9"

# "Infrastructure exists" provider configuration
  infra_exists:
    ssh_host_ip: "144.24.62.189"
    ssh_username: "ubuntu"
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    host_name: "brave-node"



# provisioner !! CHANGE THIS TO YOUR PROVISIONER (vms_only, eksabm_cluster, rafay_eksabm_cluster, or none) 
provisioner: vms_only 

provisioner_config:
# VM Provisioner configuration
  vms_only:
    - name: "workers"
      count: 2
      cpu: 3       # in vcpus 
      mem: 16384   # in MB 
      osfamily: ubuntu # currently only ubuntu is supported
      vagrant_box: "bento/ubuntu-20.04"
    - name: "storage"
      #count: 1             # (default value)
      #cpu: 2               # (default value)
      #mem: 16384           # (default value)
      #osfamily: ubuntu     # (default value)
      #vagrant_box: "bento/ubuntu-20.04"  # (default value)

# EKSA-BM Provisioner configuration
  eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1      

# Rafay EKSA-BM Provisioner configuration
  rafay_eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1
    rafay_controller_url: "https://console.rafay.dev/"
    rafay_api_key_file: "/home/rgill/oci_api.key"
    rafay_project_name: "brave"
    rafay_eksabm_gateway_name: "brave-gw"  


# None Provisioner 
  none:
    config: none

  # To create eksabm cluster using config file (advanced cluster configuration): 
  # eksabm_cluster:
  #   cluster_name: "brave-cluster"
  #   operation_type: "provision"
  #   config_file_name: "eksa-bm-config.yaml"      

  # To create rafay eksabm cluster using config file (advanced cluster configuration):
  # rafay_eksabm_cluster:
  #   cluster_name: "brave-rafay-cluster"
  #   operation_type: "provision"
  #   config_file_name: "rafay-eksa-bm-config.yaml" 
  #   rafay_controller_url: "https://console.rafay.dev/"
  #   rafay_api_key_file: "/home/rgill/oci_api.key"
  #   rafay_project_name: "brave"
  #   rafay_eksabm_gateway_name: "brave-gw"     

```


### Example : Launch VMs using OCI cloud

```sh

infrastructure_provider: oci  
infrastructure_provider_config:
  oci:
    host_name: "brave-node"
    instance_flex_memory_in_gbs: 80
    instance_flex_ocpus: 6    
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    region: "us-phoenix-1"
    tenancy_ocid: "ocid1.tenancy.oc1..aaaaaaaaaa3ghjcqbrbzmssbzhxzhxf24rpmuyxbaxwcj2axwoqkpd56ljkq"
    user_ocid: "ocid1.user.oc1..aaaaaaaac6nqpe4rsz3em53qtkkfq2pd4otg3j347wgku6eidkfcf5tr7kta"
    private_key_path: "/Users/rgill/.oci/oci_api_key.pem" # private key for OCI user
    fingerprint: "ed:8b:e9:3c:72:4c:39:70:20:0b:97:9e:59:fb:60:e9"

provisioner: vms_only 
provisioner_config:
  vms_only:
    - name: "workers"
      count: 2
      cpu: 3      
      mem: 16384   
      osfamily: ubuntu 
      vagrant_box: "bento/ubuntu-20.04"
    - name: "storage"

```

### Example : Launch EKSA-BM Cluster using AWS cloud

```sh

infrastructure_provider: aws  
infrastructure_provider_config:
  aws:
    region: "us-west-1"
    host_name: "brave-node"
    instance_type: "c5n.metal" #Choose a metal instance type
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    ssh_key_name: "eksabmsshkey"
    ssh_private_key_file: "/opt/rafay/keys/oci"    

provisioner: eksabm_cluster
provisioner_config:
  eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1         

```

### Example : Launch EKSA-BM Cluster using Config File and OCI cloud

```sh

infrastructure_provider: oci  
infrastructure_provider_config:
  oci:
    host_name: "brave-node"
    instance_flex_memory_in_gbs: 80
    instance_flex_ocpus: 6    
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    region: "us-phoenix-1"
    tenancy_ocid: "ocid1.tenancy.oc1..aaaaaaaaaa3ghjcqbrbzmssbzhxzhxf24rpmuyxbaxwcj2axwoqkpd56ljkq"
    user_ocid: "ocid1.user.oc1..aaaaaaaac6nqpe4rsz3em53qtkkfq2pd4otg3j347wgku6eidkfcf5tr7kta"
    private_key_path: "/Users/rgill/.oci/oci_api_key.pem" # private key for OCI user
    fingerprint: "ed:8b:e9:3c:72:4c:39:70:20:0b:97:9e:59:fb:60:e9"

provisioner: eksabm_cluster 
provisioner_config:
  eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    config_file_name: "eksa-bm-config.yaml"     

```

### Example : Launch EKSA-BM Cluster on Rafay using AWS cloud

```sh
infrastructure_provider: aws  
infrastructure_provider_config:
  aws:
    region: "us-west-1"
    host_name: "brave-node"
    instance_type: "c5n.metal" #Choose a metal instance type
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    ssh_key_name: "eksabmsshkey"
    ssh_private_key_file: "/opt/rafay/keys/oci"    

provisioner: rafay_eksabm_cluster 
provisioner_config:
  rafay_eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1
    rafay_controller_url: "https://console.rafay.dev/"
    rafay_api_key_file: "/home/rgill/oci_api.key"
    rafay_project_name: "brave"
    rafay_eksabm_gateway_name: "brave-gw"     

```

### Example : Launch EKSA-BM Cluster on Rafay using Config File and OCI cloud

```sh

infrastructure_provider: aws  
infrastructure_provider_config:
  aws:
    region: "us-west-1"
    host_name: "brave-node"
    instance_type: "c5n.metal" #Choose a metal instance type
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    ssh_key_name: "eksabmsshkey"
    ssh_private_key_file: "/opt/rafay/keys/oci"    

provisioner: rafay_eksabm_cluster 
provisioner_config:
  rafay_eksabm_cluster:
    cluster_name: "brave"
    operation_type: "provision"
    config_file_name: "rafay-eksa-bm-config.yaml" 
    rafay_controller_url: "https://console.rafay.dev/"
    rafay_api_key_file: "/home/rgill/oci_api.key"
    rafay_project_name: "brave"
    rafay_eksabm_gateway_name: "brave-gw"  
    
```

### Example : Launch VMs using pre-existing instance

```sh

infrastructure_provider: infra_exists  
infrastructure_provider_config:
  infra_exists:
    ssh_host_ip: "144.24.62.189"
    ssh_username: "ubuntu"
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    host_name: "brave-node"

provisioner: vms_only 
provisioner_config:
# VM Provisioner configuration
  vms_only:
    - name: "workers"
      count: 2
      cpu: 3       # in vcpus 
      mem: 16384   # in MB 
      osfamily: ubuntu # currently only ubuntu is supported
      vagrant_box: "bento/ubuntu-20.04"
    - name: "storage"
      #count: 1             # (default value)
      #cpu: 2               # (default value)
      #mem: 16384           # (default value)
      #osfamily: ubuntu     # (default value)
      #vagrant_box: "bento/ubuntu-20.04"  # (default value)

```

### Example : Launch cloud instance ONLY on OCI  

```sh
# Infrastructure provider  !! CHANGE THIS TO YOUR INFRASTRUCTURE PROVIDER (aws, oci or infra_exists) 
infrastructure_provider: oci  
infrastructure_provider_config:
  oci:
    host_name: "brave-node"
    instance_flex_memory_in_gbs: 80
    instance_flex_ocpus: 6    
    ssh_private_key_file: "/opt/rafay/keys/oci"
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    region: "us-phoenix-1"
    tenancy_ocid: "ocid1.tenancy.oc1..aaaaaaaaaa3ghjcqbrbzmssbzhxzhxf24rpmuyxbaxwcj2axwoqkpd56ljkq"
    user_ocid: "ocid1.user.oc1..aaaaaaaac6nqpe4rsz3em53qtkkfq2pd4otg3j347wgku6eidkfcf5tr7kta"
    private_key_path: "/Users/rgill/.oci/oci_api_key.pem" # private key for OCI user
    fingerprint: "ed:8b:e9:3c:72:4c:39:70:20:0b:97:9e:59:fb:60:e9"

provisioner: none 
provisioner_config:
  none:
    config: none
  
```
