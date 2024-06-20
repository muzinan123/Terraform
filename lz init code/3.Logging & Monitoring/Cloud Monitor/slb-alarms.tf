
resource "alicloud_cms_alarm" "slb_instance_maxconnection_utilization" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "slb-maxconnection-alarm-rule"
  project = "acs_slb_dashboard"
  metric  = "InstanceMaxConnectionUtilization"

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