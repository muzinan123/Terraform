
resource "alicloud_cms_alarm" "oss_internet_send" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "oss-internet-send-alarm-rule"
  project = "acs_oss_dashboard"
  metric  = "InternetSend"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 5368709120
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 60
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}

resource "alicloud_cms_alarm" "oss_metering_getrequest" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "oss-getrequest-alarm-rule"
  project = "acs_oss_dashboard"
  metric  = "MeteringGetRequest"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 60000
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 3600
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}