resource "alicloud_cms_alarm" "eip_net_in" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "eip-net-in-alarm-rule"
  project = "acs_vpc_eip"
  metric  = "net_in.rate_percentage"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 80
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}

resource "alicloud_cms_alarm" "eip_net_out" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "eip-net-out-alarm-rule"
  project = "acs_vpc_eip"
  metric  = "net_out.rate_percentage"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 80
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}