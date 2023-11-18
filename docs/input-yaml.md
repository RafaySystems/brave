
- [Example input.yaml file](#example-inputyaml-file)
- [Populating input.yaml file](#populating-inputyaml-file)
    - [Cluster configuration details](#1-cluster-configuration-details)
    - [Cluster provisioner details](#2-cluster-provisioner-details)
        - [Using `native` provisioner](#using-native-provisioner)
        - [Using `rafay` provisioner](#using-rafay-provisioner)
        - [Using `none` provisioner](#using-none-provisioner)
    - [Infrastructure provider details](#3-infrastructure-provider-details)
        - [Using AWS cloud as infrastructure provider](#using-aws-cloud-as-infrastructure-provider)
        - [Using OCI cloud as infrastructure provider](#using-oci-cloud-as-infrastructure-provider)
        - [Using pre existing cloud instance](#using-pre-existing-cloud-instance)


---
## Example input.yaml file 

Here is a full example of an `input.yaml` that instructs `brave` to 
- Launch a cluster named "brave" with k8s version 1.27, 1 control plane node and 1 worker node. 
- Use `eksctl anywhere` cli to create cluster by using `native` cluster_provisioner
- Use `aws` cloud to launch the cloud instance to host entire infrastructute (vms and network) by selecting `aws` for infrastructure_provider 

```sh
clusters:
  - cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1

# To create cluster using config file (advanced cluster configuration):
# clusters:    
#   - cluster_name: "brave-cluster"
#     operation_type: "provision"
#     config_file_name: "eksa-bm-config.yaml"


# Cluster provisioner configuration
cluster_provisioner: native # !! CHANGE THIS TO YOUR PROVISIONER (native, rafay or none) 
cluster_provisioner_config:
  native:
    config: none
  rafay:
    #rafay_controller_url: "https://console.rafay.dev/"
    #rafay_api_key_file: "/home/rgill/oci_api.key"
    #rafay_project_name: "brave"
    #rafay_eksabm_gateway_name: "brave-gw"
  none:
    #config: none

# Infrastructure provider configuration
infrastructure_provider: aws # !! CHANGE THIS TO YOUR INFRASTRUCTURE PROVIDER (aws, oci or infra_exists) 
infrastructure_provider_config:
  aws:
    region: "us-west-1"
    host_name: "brave-node"
    instance_type: "c5n.metal" #Choose a metal instance type
    ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    ssh_key_name: "eksabmsshkey"
    ssh_private_key_file: "/opt/rafay/keys/oci"    
  oci:
    #host_name: "brave-node"
    #instance_flex_memory_in_gbs: 64
    #instance_flex_ocpus: 4    
    #ssh_private_key_file: "/opt/rafay/keys/oci"
    #ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    #region: "us-phoenix-1"
    #tenancy_ocid: "ocid1.tenancy.oc1..aaaaaaaaaa3ghjcqbrbzmssbzhxzhxf24rpmuyxbaxwcj2axwoqkpd56ljkq"
    #user_ocid: "ocid1.user.oc1..aaaaaaaac6nqpe4rsz3em53qtkkfq2pd4otg3j347wgku6eidkfcf5tr7kta"
    #private_key_path: "/Users/rgill/.oci/oci_api_key.pem" # private key for OCI user
    #fingerprint: "ed:8b:e9:3c:72:4c:39:70:20:0b:97:9e:59:fb:60:e9"
  infra_exists:
    #ssh_host_ip: "129.146.86.26"
    #ssh_username: "ubuntu"
    #ssh_private_key_file: "/opt/rafay/keys/oci"
    #ssh_public_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCr/bRBFgLj5l7JiX/0H0uqLUa50x14iWXGKxrqjzPy5UYP9mIqLS4udxf5uvTpB5QsWp9Xn0r3gch0es8QVSG8g0aEHjRhxMD3sW/KhpU4fvCMXLa/ccVQA7OvvYmaoc4aKQXk/kksNQE68+UaVd/gClMq4TMlDH0KlJUADZ3+ZduBKTjKYcme24QD7wHEMipFLuA+NZ0DeMgBlU9zqVI5RX9PW+jheKzII+LZywDlSocNIxoWvgTUJAil1GUlqzWngLZiMBd1xfuJ9BahwlridMOtpbGnamHbZbfE7KKY+eiazfpTERO/T9SYJE/c2U468mO1eggRQjdw0GfcxMgy1ppcL0R80qkxtWxkFaWWxLx1Rh0BO1f+VuRuJiTdOdymmttCqBnCGmsSjIf8zmDr+r1Xmgs3W1KevIyCgezCLhdGPXFkXRAD2VDW1Qo26BDqmhv39M2CPXXil0ifMsdd0T4nIiguaAF4vzYPmmcajCyWNLqaZv4TqBFSwKN6+YE= rgill@Robbies-MBP"
    #host_name: "brave-node"
```

## Populating input.yaml file  

`input.yaml` is a yaml file and contains various sections. Below are steps to populate these

### 1. Cluster configuration details
Provide details of cluster to create. In example below a K8s version 1.27 EKSA-BM cluster named `brave` is being configured with two nodes - 1 control plane node and 1 worker node : 

```
clusters:
  - cluster_name: "brave"
    operation_type: "provision"
    k8s_version: "1.27"
    num_control_plane_nodes: 1
    num_worker_nodes: 1
```

Above block uses defaults for creating the cluster without asking for a lot of configuration. However it is also possible to create a cluster using a config file, which allows flexibility to provide advanced configuration for the cluster. 

```
clusters:    
  - cluster_name: "brave-cluster"
    operation_type: "provision"
    config_file_name: "eksa-bm-config.yaml"
```

A config file can be created using [EKSA-BM spec](https://anywhere.eks.amazonaws.com/docs/getting-started/baremetal/bare-spec/) (example [here](../cluster_configs/eksa-bm-config.yaml)) or by using [Rafay System's EKSA-BM spec](https://docs.rafay.co/clusters/eksa_bm/eksabm_schema/) (example [here](../cluster_configs/rafay-eksa-bm-config.yaml)).


### 2. Cluster provisioner details
Choose a provisioner (using key `cluster_provisioner` ) and fill out configuration for the chosen provisioner (using key `cluster_provisioner_config`). 

#### Using `native` provisioner 
In below example `native` provisioner is being used which does not require extended configuration.  This option uses `eksctl anywhere` cli directly.

```sh
cluster_provisioner: native 
cluster_provisioner_config:
  native:
    config: none
```

#### Using `rafay` provisioner 
If using `rafay` provisioner, fill out URL of the Rafay controller, an existing Rafay project name, name of the EKSA-BM gateway to create and location of a file containing a valid [RAFAY API key](https://docs.rafay.co/security/rbac/users/#manage-keys) (as demonstrated in the example below).  

```sh
cluster_provisioner: rafay
cluster_provisioner_config:
  rafay:
    rafay_controller_url: "https://console.rafay.dev/"
    rafay_api_key_file: "/home/rgill/oci_api.key"
    rafay_project_name: "brave"
    rafay_eksabm_gateway_name: "brave-gw"
```

#### Using `none` provisioner 
If you do not wish to use a provisioner at all, you can select the `none` option as shown below. This can be relevant if you wanted to perhaps use `brave`` to just launch the virtual infrastructure and want to create the cluster manually using this infrastructure. 


```sh
cluster_provisioner: none
cluster_provisioner_config:
  none:
    config: none
```

### 3. Infrastructure provider details
Choose an infrastructure_provider by configuring key `infrastructure_provider` in the input.yaml file. This provider is the cloud provider where cloud instance will be launched. This single instance will host the entire virtualized EKSA-BM environment - all vms and the network. Valid options are `aws`, `oci` and `infra_exists`.  Configuration needs to be provided using key `infrastructure_provider_config`.  

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
-  `region`: AWS region to create instance in. !!! Change as needed !!!
-  `host_name`: Name for the cloud instance. Also used to create ~/.ssh/config entry.  !!! Change as needed !!!
-  `instance_type`: An instance type that can support Virtualbox vms. Essentially any `metal` instance_type
-  `ssh_public_key`: SSH public key to inject in authorized_keys of the cloud instance. The same key is injected in authorized_keys of `eksa-admin` vm and all other vms (unless config file is being used in which case ssh public key in config file is used for cluster nodes). This should be public part of private key in `ssh_private_key_file`.  !!! Must Change from Default !!!
-  `ssh_private_key_file`: File containing private part of the SSH public key listed in `ssh_public_key`. This private key is injected in ssh host entries injected automatically to log in to cloud instance and `eksa-admin` machine. The same private key file can also be used to ssh into cluster nodes (unless config file is being used and a different ssh public key is specified there). !!! Must Change from Default !!!
-  `ssh_key_name`:  Key name you want to give to the AWS SSH key generated using the ssh public key listed in `ssh_public_key`. This object is associated with cloud instance to permit logging in via ssh.  Leave the existing default value in input.yaml if you wish. 

Ensure that capacity of cloud instance can house all vms required for desired cluster i.e. Admin vm (2 vcpu, 16GB Mem) and desired number of control plane and worker nodes (each 2 vcpu, 16GB Mem). 

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
-  `host_name`: Name for the cloud instance. Also used to create ~/.ssh/config entry.  !!! Change as needed !!!
-  `instance_flex_memory_in_gbs`: The total amount of memory available to the instance, in gigabytes.
-  `instance_flex_ocpus`: The total number of OCPUs available to the instance. 1 ocpu = 2 vcpus
-  `ssh_public_key`: SSH public key to inject in authorized_keys of the cloud instance. The same key is injected in authorized_keys of `eksa-admin` vm and all other vms (unless config file is being used in which case ssh public key in config file is used for cluster nodes). This should be public part of private key in `ssh_private_key_file`.  !!! Must Change from Default !!!
-  `ssh_private_key_file`: File containing private part of the SSH public key listed in `ssh_public_key`. This private key is injected in ssh host entries injected automatically to log in to cloud instance and `eksa-admin` machine. The same private key file can also be used to ssh into cluster nodes (unless config file is being used and a different ssh public key is specified there). !!! Must Change from Default !!!
-  `region`: OCI region to create instance in. !!! Change as needed !!!
-  `tenancy_ocid`:  Tenancy ocid where to create the sources. Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
-  `user_ocid`: Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
-  `private_key_path`: Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).
-  `fingerprint`:  Refer to more information on these in [OCI docs](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).

Ensure that capacity of cloud instance can house all vms required for desired cluster i.e. Admin vm (2 vcpu, 16GB Mem) and desired number of control plane and worker nodes (each 2 vcpu, 16GB Mem). Capacity of OCI cloud instance is defined by variables `instance_flex_memory_in_gbs`, `instance_flex_ocpus` (Note: 1 ocpu = 2 vcpus). 

All OCI infrastructure required to support the cloud instance - vcn, public subnet, Internet gateway, route table, security group etc. are created from scratch. The cloud instance created has an public IP reachable from the Internet and ONLY inbound port 22/tcp traffic permitted to the instance. Ubuntu-20.04 is used as OS for the cloud instance.

#### Using pre existing cloud instance 

If one does not wish to launch a cloud instance using **`brave`** OR such an instance pre-exists (in any cloud that supports instances that can run Virtualbox vms), `infra_exists` provider can be  used. If `infra_exists` is selected using key `infrastructure_provider`, SSH connection details need to be configured for **`brave`** to be able to connect to this instance. Use key `infrastructure_provider_config` for providing this configuration as shown in below example. 

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
-  `host_name`: Name for the pre-existing cloud instance.  Used to create ~/.ssh/config entry.  !!! Change as needed !!!
-  `ssh_host_ip`: IP of the pre-existing cloud instance.  Used to create ~/.ssh/config entry.  !!! Change as needed !!!
-  `ssh_username`: username to connect to pre-existing cloud instance over ssh.  Used to create ~/.ssh/config entry.  !!! Change as needed !!!
-  `ssh_public_key`: SSH public key that is injected in authorized_keys of the pre-existing cloud instance. The same key is injected in authorized_keys of `eksa-admin` vm and all other vms (unless config file is being used in which case ssh public key in config file is used for cluster nodes). This should be public part of private key in `ssh_private_key_file`.  !!! Must Change from Default !!!
-  `ssh_private_key_file`: File containing private part of the SSH public key listed in `ssh_public_key`. This private key is injected in ssh host entries injected automatically to log in to cloud instance and `eksa-admin` machine. The same private key file can also be used to ssh into cluster nodes (unless config file is being used and a different ssh public key is specified there). !!! Must Change from Default !!!


**Cloud Instance requirements. If using `infra_exists` provider**
- cloud instance OS must be Ubuntu 20.04 
- cloud instance must have access to the Internet 
- cloud Instance must have an IP that is publicly reachable over ssh
- cloud Instance must have enough capacity to hold all vms emulating the EKSA-BM hardware 


