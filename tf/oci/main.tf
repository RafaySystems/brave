terraform {
  required_version = ">= 0.13" 
  required_providers {
    oci = {
      version = ">= 4.0.0" 
      source = "oracle/oci"
    }
  }
}

variable "fingerprint" {
  description = "fingerprint of oci api private key"
  type        = string
}

variable "private_key_path" {
  description = "path to oci api private key used"
  type        = string
}

variable "region" {
  description = "the oci region where resources will be created"
  type        = string
}

variable "tenancy_ocid" {
  description = "tenancy ocid where to create the sources"
  type        = string
}

variable "user_ocid" {
  description = "ocid of user that terraform will use to create the resources"
  type        = string
}

variable "name" {
  description = "Display name for resources"
  type        = string
  default     = "eksa-bm"
}

variable "cidr_block" {
  description = "CIDR block of the VCN"
  type        = string
  default     = "10.10.10.0/24"

  validation {
    condition     = can(cidrsubnets(var.cidr_block, 2))
    error_message = "The value of cidr_block variable must be a valid CIDR address with a prefix no greater than 30."
  }
}

variable "ssh_public_key" {
  description = "Public key to be used for SSH access to compute instances"
  type        = string
}

variable "host_name" {
  description = "(Updatable) A user-friendly name for the resources."
  type        = string
  default     = "eksabm"
}

variable "instance_flex_memory_in_gbs" {
  type        = number
  description = "(Updatable) The total amount of memory available to the instance, in gigabytes."
  default     = null
}

variable "instance_flex_ocpus" {
  type        = number
  description = "(Updatable) The total number of OCPUs available to the instance."
  default     = null
}

variable "boot_volume_size_in_gbs" {
  type        = number
  default     = 250
}

locals {
  protocol_number = {
    icmp   = 1
    icmpv6 = 58
    tcp    = 6
    udp    = 17
  }

  shapes = {
    flex : "VM.Standard3.Flex"
  }
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

resource "oci_identity_compartment" "this" {
  compartment_id = var.tenancy_ocid
  description    = var.name
  name           = replace(var.name, " ", "-")

  enable_delete = true
}

resource "oci_core_vcn" "this" {
  compartment_id = oci_identity_compartment.this.id

  cidr_blocks  = [var.cidr_block]
  display_name = var.name
  dns_label    = "vcn"
}

resource "oci_core_internet_gateway" "this" {
  compartment_id = oci_identity_compartment.this.id
  vcn_id         = oci_core_vcn.this.id

  display_name = oci_core_vcn.this.display_name
}

resource "oci_core_default_route_table" "this" {
  manage_default_resource_id = oci_core_vcn.this.default_route_table_id

  display_name = oci_core_vcn.this.display_name

  route_rules {
    network_entity_id = oci_core_internet_gateway.this.id

    description = "Default route"
    destination = "0.0.0.0/0"
  }
}

resource "oci_core_default_security_list" "this" {
  manage_default_resource_id = oci_core_vcn.this.default_security_list_id

  dynamic "ingress_security_rules" {
    for_each = [22]
    iterator = port
    content {
      protocol = local.protocol_number.tcp
      source   = "0.0.0.0/0"

      description = "SSH and HTTPS traffic from any origin"

      tcp_options {
        max = port.value
        min = port.value
      }
    }
  }

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"

    description = "All traffic to any destination"
  }
}

resource "oci_core_subnet" "this" {
  cidr_block     = oci_core_vcn.this.cidr_blocks.0
  compartment_id = oci_identity_compartment.this.id
  vcn_id         = oci_core_vcn.this.id

  display_name = oci_core_vcn.this.display_name
  dns_label    = "subnet"
}

resource "oci_core_network_security_group" "this" {
  compartment_id = oci_identity_compartment.this.id
  vcn_id         = oci_core_vcn.this.id

  display_name = oci_core_vcn.this.display_name
}

resource "oci_core_network_security_group_security_rule" "this" {
  direction                 = "INGRESS"
  network_security_group_id = oci_core_network_security_group.this.id
  protocol                  = local.protocol_number.icmp
  source                    = "0.0.0.0/0"
}

data "oci_identity_availability_domains" "this" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_shapes" "this" {
  for_each = toset(data.oci_identity_availability_domains.this.availability_domains[*].name)

  compartment_id = var.tenancy_ocid

  availability_domain = each.key
}


data "oci_core_images" "this" {
  compartment_id = oci_identity_compartment.this.id

  operating_system         = "Canonical Ubuntu"
  shape                    = local.shapes.flex
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
  state                    = "available"

  filter {
    name   = "display_name"
    values = ["^Canonical-Ubuntu-([\\.0-9-]+)$"]
    regex  = true
  }
}


resource "oci_core_instance" "this" {
  #count = 1

  availability_domain = data.oci_identity_availability_domains.this.availability_domains.0.name
  compartment_id      = oci_identity_compartment.this.id
  shape               = local.shapes.flex

  display_name         = var.host_name
  preserve_boot_volume = false

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  agent_config {
    are_all_plugins_disabled = true
    is_management_disabled   = true
    is_monitoring_disabled   = true
  }

  availability_config {
    is_live_migration_preferred = null
  }

  create_vnic_details {
    assign_public_ip = true
    display_name     = var.host_name
    hostname_label   = var.host_name
    nsg_ids          = [oci_core_network_security_group.this.id]
    subnet_id        = oci_core_subnet.this.id
  }

  shape_config {
    memory_in_gbs = var.instance_flex_memory_in_gbs
    ocpus         = var.instance_flex_ocpus
  }

  source_details {
    source_id               = data.oci_core_images.this.images.0.id
    source_type             = "image"
    boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
  }

  lifecycle {
    ignore_changes = [source_details.0.source_id]
  }
}

data "oci_core_private_ips" "this" {
  ip_address = oci_core_instance.this.private_ip
  subnet_id  = oci_core_subnet.this.id
}


# output instance public IPs 
output "instance_public_ip" {
  description = "instance public ip"
  value       = oci_core_instance.this.public_ip
}









