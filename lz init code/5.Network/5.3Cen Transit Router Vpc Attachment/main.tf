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

resource "alicloud_cen_transit_router_vpc_attachment" "default"  {
  provider =alicloud.account1
  cen_id  = var.cen_id
  transit_router_id = var.transit_router_id
  vpc_id  = var.vpc_id
  vpc_owner_id = var.vpc_owner_id
  zone_mapping{
	zone_id = lookup(var.availability_zone_map, var.region_id,["cn-beijing-h","cn-beijing-g"]).0
	vswitch_id =var.vswitch_id_1
  }
  zone_mapping{
 	zone_id = lookup(var.availability_zone_map, var.region_id,["cn-beijing-h","cn-beijing-g"]).1
	vswitch_id =var.vswitch_id_2	
  }
  transit_router_attachment_name = var.transit_router_attachment_name
}
