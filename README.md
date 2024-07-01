# Managing Infrastructure with Terraform

This repository demonstrates how to use Terraform to manage cloud infrastructure.

## Prerequisites

- Terraform installed (version >= 0.12)
- Configured cloud provider account (e.g., AWS, Azure, GCP)

## Repository Structure

.
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
└── README.md

## Configuration Files

### main.tf
The `main.tf` file contains the main configuration for the infrastructure.

```hcl
provider "aws" {
  region = var.region
}

resource "aws_instance" "example" {
  ami           = var.ami
  instance_type = var.instance_type

  tags = {
    Name = "example-instance"
  }
}

variables.tf
The variables.tf file defines the required variables.
variable "region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-west-2"
}

variable "ami" {
  description = "The AMI to use for the instance"
  type        = string
}

variable "instance_type" {
  description = "The type of instance to use"
  type        = string
  default     = "t2.micro"
}

outputs.tf
The outputs.tf file defines the output variables.
output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.example.id
}

output "public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.example.public_ip
}

terraform.tfvars
The terraform.tfvars file contains the actual variable values.
region         = "us-west-2"
ami            = "ami-0c55b159cbfafe1f0"
instance_type  = "t2.micro"
