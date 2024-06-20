terraform {
  required_providers {
    alicloud = {
      source = "hashicorp/alicloud"
      version = "1.158.0"
    }
  }
}


variable "beijing_availability_zone_1" {
    default = "cn-beijing-h"
}

variable "beijing_availability_zone_2" {
    default = "cn-beijing-g"
}

variable "beijing_availability_zone_3" {
    default = "cn-beijing-i"
}

variable "beijing_availability_zone_4" {
    default = "cn-beijing-f"
}



############ Prepare three providers and use the alias function ############


provider "alicloud" {
    alias      = "beijing"
    access_key = ""
    secret_key = ""
    region     = "cn-beijing"
    assume_role {
    role_arn           = "acs:ram::1379746643909237:role/ResourceDirectoryAccountAccessRole"
    session_name       = "AccountLandingZoneSetup"
    session_expiration = 999
  }
}


############ Create VPC and VSWITCH (Beijing) ############

resource "alicloud_vpc" "beijing_vpc_ingress" {
  provider   = alicloud.beijing
  vpc_name   = "Ingress-VPC"
  cidr_block = "10.153.158.0/24"
}
resource "alicloud_vpc" "beijing_vpc_egress" {
  provider   = alicloud.beijing
  vpc_name   = "Egress-VPC"
  cidr_block = "10.153.159.0/25"
}
resource "alicloud_vpc" "beijing_vpc_network" {
  provider   = alicloud.beijing
  vpc_name   = "Network-VPC"
  cidr_block = "10.153.157.0/25"
}

resource "alicloud_vswitch" "beijing_vsw_ingress1" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_ingress.id
  vswitch_name      =  "Ingress_BJ_H"
  cidr_block        = "10.153.158.64/27"
  zone_id = var.beijing_availability_zone_1
}

resource "alicloud_vswitch" "beijing_vsw_ingress2" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_ingress.id
  vswitch_name      =  "Ingress_BJ_G"
  cidr_block        = "10.153.158.96/27"
  zone_id = var.beijing_availability_zone_2
}

resource "alicloud_vswitch" "beijing_vsw_ingress3" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_ingress.id
  vswitch_name      =  "Ingress_CP_1"
  cidr_block        = "10.153.158.0/27"
  zone_id = var.beijing_availability_zone_3
}

resource "alicloud_vswitch" "beijing_vsw_ingress4" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_ingress.id
  vswitch_name      =  "Ingress_CP_2"
  cidr_block        = "10.153.158.32/27"
  zone_id = var.beijing_availability_zone_4
}

resource "alicloud_vswitch" "beijing_vsw_egress1" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_egress.id
  vswitch_name      =  "Egress_BJ_H"
  cidr_block        = "10.153.159.64/27"
  zone_id = var.beijing_availability_zone_1
}

resource "alicloud_vswitch" "beijing_vsw_egress2" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_egress.id
  vswitch_name      =  "Egress_BJ_G"
  cidr_block        = "10.153.159.96/27"
  zone_id = var.beijing_availability_zone_2
}

resource "alicloud_vswitch" "beijing_vsw_egress3" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_egress.id
  vswitch_name      =  "Egress_CP_1"
  cidr_block        = "10.153.159.0/27"
  zone_id = var.beijing_availability_zone_3
}

resource "alicloud_vswitch" "beijing_vsw_egress4" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_egress.id
  vswitch_name      =  "Egress_CP_2"
  cidr_block        = "10.153.159.32/27"
  zone_id = var.beijing_availability_zone_4
}

resource "alicloud_vswitch" "beijing_vsw_network1" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_network.id
  vswitch_name      =  "Network_BJ_H"
  cidr_block        = "10.153.157.64/27"
  zone_id = var.beijing_availability_zone_1
}

resource "alicloud_vswitch" "beijing_vsw_network2" {
  provider   = alicloud.beijing
  vpc_id            = alicloud_vpc.beijing_vpc_network.id
  vswitch_name      =  "Network_BJ_G"
  cidr_block        = "10.153.157.96/27"
  zone_id = var.beijing_availability_zone_2
}


############ Create the CEN(Cloud Enterprise Network) ############

resource "alicloud_cen_instance" "default" {
  provider   = alicloud.beijing
  cen_instance_name = "eec-ali-eits-cen-bj"
   description    = "create by terraform"
}

############ Create TR and bind VPC (Beijing) ############

resource "alicloud_cen_transit_router" "beijing" {
  provider   = alicloud.beijing
  transit_router_name = "eec-ali-eits-tr-bj"
  cen_id              = alicloud_cen_instance.default.id
}

############ Creating cen_transit_router ############
resource "alicloud_cen_transit_router_route_table" "beijing_route_table" {
 provider   = alicloud.beijing
  transit_router_route_table_name = "ingress"
  transit_router_id = alicloud_cen_transit_router.beijing.transit_router_id
}

resource "alicloud_cen_transit_router_route_table" "beijing_route_table2" {
 provider   = alicloud.beijing
  transit_router_route_table_name = "egress"
  transit_router_id = alicloud_cen_transit_router.beijing.transit_router_id
}

resource "alicloud_cen_transit_router_vpc_attachment" "beijing_ingress" {
  provider   = alicloud.beijing
  cen_id            = alicloud_cen_instance.default.id
  transit_router_id = alicloud_cen_transit_router.beijing.transit_router_id
  vpc_id            = alicloud_vpc.beijing_vpc_ingress.id
  zone_mappings {
    zone_id    = var.beijing_availability_zone_1
    vswitch_id = alicloud_vswitch.beijing_vsw_ingress1.id
  }
  zone_mappings {
    zone_id    = var.beijing_availability_zone_2
    vswitch_id = alicloud_vswitch.beijing_vsw_ingress2.id
  }
}

resource "alicloud_cen_transit_router_vpc_attachment" "beijing_egress" {
  provider   = alicloud.beijing
  cen_id            = alicloud_cen_instance.default.id
  transit_router_id = alicloud_cen_transit_router.beijing.transit_router_id
  vpc_id            = alicloud_vpc.beijing_vpc_egress.id
  zone_mappings {
    zone_id    = var.beijing_availability_zone_1
    vswitch_id = alicloud_vswitch.beijing_vsw_egress1.id
  }
  zone_mappings {
    zone_id    = var.beijing_availability_zone_2
    vswitch_id = alicloud_vswitch.beijing_vsw_egress2.id
  }
}

resource "alicloud_cen_transit_router_vpc_attachment" "beijing_network" {
  provider   = alicloud.beijing
  cen_id            = alicloud_cen_instance.default.id
  transit_router_id = alicloud_cen_transit_router.beijing.transit_router_id
  vpc_id            = alicloud_vpc.beijing_vpc_network.id
  zone_mappings {
    zone_id    = var.beijing_availability_zone_1
    vswitch_id = alicloud_vswitch.beijing_vsw_network1.id
  }
  zone_mappings {
    zone_id    = var.beijing_availability_zone_2
    vswitch_id = alicloud_vswitch.beijing_vsw_network2.id
  }
}





