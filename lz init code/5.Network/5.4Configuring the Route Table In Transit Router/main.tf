locals{
 accountid = var.accountid
}
provider "alicloud" {
  alias = "account1"
  region = var.region
  access_key = var.access_key
  secret_key = var.secret_key
  # ......TF..................provider......
  assume_role {
     role_arn           = "acs:ram::${local.accountid}:role/ResourceDirectoryAccountAccessRole"
    session_name       = "AccountLandingZoneSetup"
    session_expiration = 999
  }
}

terraform {
  required_providers {
    alicloud = {
      source = "hashicorp/alicloud"
      version = "1.158.0"
    }
  }
}

resource "alicloud_cen_transit_router_route_entry" "default" {
  count           = var.create_route_entry? length(var.route_entry) : 0
  provider =alicloud.account1
  transit_router_route_table_id                     = lookup(var.route_entry[count.index],"transit_router_route_table_id")
  transit_router_route_entry_destination_cidr_block = lookup(var.route_entry[count.index],"transit_router_route_entry_destination_cidr_block")
  transit_router_route_entry_next_hop_type          = "Attachment"
  transit_router_route_entry_name                   = lookup(var.route_entry[count.index],"transit_router_route_entry_name")
  transit_router_route_entry_description            = "createbyterraform"
  transit_router_route_entry_next_hop_id            = lookup(var.route_entry[count.index],"transit_router_route_entry_next_hop_id")
}

resource "alicloud_cen_transit_router_route_table_association" "default" {
  count           = var.create_association? length(var.association) : 0
  transit_router_route_table_id = lookup(var.association[count.index],"transit_router_route_table_id")
  transit_router_attachment_id  = lookup(var.association[count.index],"transit_router_attachment_id")
}