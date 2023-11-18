terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0.0"
    }
  }
}

variable "region" {
  description = "the aws region where resources will be created"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  type = string
  default = "c5n.metal"
}

variable "ssh_public_key" {
  description = "Public key to be used for SSH access to compute instances"
  type        = string
}

variable "ssh_key_name" {
  type = string
}


variable "cidr_block" {
  description = "CIDR block of the VPN"
  type        = string
  default     = "10.10.10.0/24"

  validation {
    condition     = can(cidrsubnets(var.cidr_block, 2))
    error_message = "The value of cidr_block variable must be a valid CIDR address with a prefix no greater than 30."
  }
}

variable "host_name" {
  description = "(Updatable) A user-friendly name for the instance. Does not have to be unique, and it's changeable."
  type        = string
  default     = "eksainst"
}


provider "aws" {
  region = var.region
}


data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]  
  }

  # Canonical
  owners = ["099720109477"]
}

locals {
    tags = {
        Name = var.host_name
        email = "robbie@rafay.co"
        env = "dev"
    }
}


resource "aws_vpc" "vpc" {
  cidr_block       = var.cidr_block
  instance_tenancy = "default"

  tags = local.tags
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.vpc.id

  tags = local.tags
}

data "aws_availability_zones" "available" {
  state = "available"
}



resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = var.cidr_block
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = local.tags
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = local.tags
}

resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_security_group" "sshin" {
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port = 22
    protocol = "tcp"
    to_port = 22
    cidr_blocks = ["0.0.0.0/0"]
  }
    egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "eksabmsshkey" {
  key_name   = var.ssh_key_name
  public_key = var.ssh_public_key
}


resource "aws_instance" "eksabm_instance" {
  ami           = "${data.aws_ami.ubuntu.id}"

  instance_type = "c5n.metal"
  key_name = "eksabmsshkey" 
  security_groups = [aws_security_group.sshin.id]
  subnet_id = aws_subnet.subnet.id
  volume_tags = local.tags

  root_block_device  {
    volume_size = 250
    #tags = local.tags
    

  }

  tags = local.tags
}

resource "aws_eip" "eip" {
  domain = "vpc"
}


resource "aws_eip_association" "eip_assoc" {
  instance_id   = aws_instance.eksabm_instance.id
  allocation_id = aws_eip.eip.id
}

output "instance_public_ip" {
  description = "instance public IP address"
  value       = aws_eip.eip.public_ip
}

