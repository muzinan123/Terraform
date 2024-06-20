
resource "alicloud_cms_alarm" "rds_cpu_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "rds-cpu-alarm-rule"
  project = "acs_rds_dashboard"
  metric  = "CpuUsage"

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

resource "alicloud_cms_alarm" "rds_disk_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "rds-disk-alarm-rule"
  project = "acs_rds_dashboard"
  metric  = "DiskUsage"

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

resource "alicloud_cms_alarm" "rds_ipos_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "rds-ipos-alarm-rule"
  project = "acs_rds_dashboard"
  metric  = "IOPSUsage"

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

resource "alicloud_cms_alarm" "rds_connection_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "rds-connection-usage-alarm-rule"
  project = "acs_rds_dashboard"
  metric  = "ConnectionUsage"

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

resource "alicloud_cms_alarm" "rds_memory_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "rds-memory-alarm-rule"
  project = "acs_rds_dashboard"
  metric  = "MemoryUsage"

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