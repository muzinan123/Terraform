provider "alicloud" {
  # ......TF..................provider......#
  alias      = "beijing"
  access_key = ""
  secret_key = ""
  region     = "cn-beijing"
  assume_role {
    role_arn           = "acs:ram::ACCOUNT_ID:role/ResourceDirectoryAccountAccessRole"
    session_name       = "AccountLandingZoneSetup"
    session_expiration = 999
  }
}

resource "alicloud_actiontrail_trail" "default" {
    provider = alicloud.beijing
trail_name         = "action-trail"
  event_rw           = "All"
is_organization_trail = true
  sls_project_arn = "acs:log:cn-beijing:ACCOUNT_ID:project/eec-log"
  sls_write_role_arn ="acs:ram::ACCOUNT_ID:role/ActionTrailDelivery"
}
