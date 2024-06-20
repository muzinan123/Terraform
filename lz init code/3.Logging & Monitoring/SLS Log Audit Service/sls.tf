provider "alicloud" {
  # 目前TF无法支持动态provider功能
  alias      = "beijing"
  access_key = ""
  secret_key = ""
  region     = "cn-beijing"
  assume_role {
    role_arn           = "acs:ram::1207xxxx440xxxxx:role/ResourceDirectoryAccountAccessRole"
    session_name       = "AccountLandingZoneSetup"
    session_expiration = 999
  }
}


resource "alicloud_log_project" "example" {
  provider = alicloud.beijing
  name        = "eec-log"
  description = "created by terraform"
}

resource "alicloud_log_store" "actiontrail" {
  provider = alicloud.beijing
  project               = alicloud_log_project.example.name
  name                  = "eec-actiontrail-store"
  shard_count           = 3
  auto_split            = true
  max_split_shard_count = 60
  retention_period = 90
  append_meta           = true
}


resource "alicloud_log_store" "log" {
provider = alicloud.beijing
  project               = alicloud_log_project.example.name
  name                  = "eec-log-store"
  shard_count           = 3
  auto_split            = true
  max_split_shard_count = 60
  retention_period = 90
  append_meta           = true
}