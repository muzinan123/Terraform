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

resource "alicloud_route_entry" "default" {
  provider =alicloud.account1
  count           = var.create_route_entry? length(var.route_entry) : 0
  route_table_id = lookup(var.route_entry[count.index],"route_table_id")
  destination_cidrblock = lookup(var.route_entry[count.index],"destination_cidrblock")
  nexthop_type          = lookup(var.route_entry[count.index],"nexthop_type")
  nexthop_id            = lookup(var.route_entry[count.index],"nexthop_id")  
}
