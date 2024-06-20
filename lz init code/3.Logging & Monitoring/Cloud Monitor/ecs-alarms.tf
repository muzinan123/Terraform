
resource "alicloud_cms_alarm" "cpu_total" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "ecs-cpu-alarm-rule"
  project = "acs_ecs_dashboard"
  metric  = "cpu_total"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 95
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}

resource "alicloud_cms_alarm" "memory_usedutilization" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "ecs-memory-alarm-rule"
  project = "acs_ecs_dashboard"
  metric  = "memory_usedutilization"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 95
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}

resource "alicloud_cms_alarm" "diskusage_utilization" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "ecs-disk-alarm-rule"
  project = "acs_ecs_dashboard"
  metric  = "diskusage_utilization"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 90
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}



