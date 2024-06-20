
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

resource "alicloud_vpc" "vpc" {
  provider   = alicloud.account1
  count             = var.vpc_id != "" ? 0 : var.create ? 1 : 0
  name              = var.vpc_name
  cidr_block        = var.vpc_cidr
  description       = var.vpc_description
  tags = merge(
    {
      "Name" = format("%s", var.vpc_name)
    },
    var.vpc_tags,
  )
}

// According to the vswitch cidr blocks to launch several vswitches
resource "alicloud_vswitch" "vswitches" {
  provider   = alicloud.account1
  count             = local.create_sub_resources ? length(var.vswitch_cidrs) : 0
  vpc_id            = var.vpc_id != "" ? var.vpc_id : concat(alicloud_vpc.vpc.*.id, [""])[0]
  cidr_block        = var.vswitch_cidrs[count.index]
  availability_zone = element(var.availability_zones, count.index)
  name              = element(var.vswitch_names,count.index)
  description       = var.vswitch_description
}


resource "alicloud_cen_instance_grant" "foo" {
  provider          = alicloud.account1
  count        = var.cen_grant ? length(var.grant_information) : 0
  cen_id            = lookup(var.grant_information[count.index],"cen_id")
  child_instance_id = alicloud_vpc.vpc[count.index].id
  cen_owner_id      = lookup(var.grant_information[count.index],"cen_owner_id")
}


