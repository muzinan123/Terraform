resource "alicloud_cms_alarm" "redis_standard_cpu_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "redis-cpu-alarm-rule"
  project = "acs_kvstore"
  metric  = "StandardCpuUsage"

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

resource "alicloud_cms_alarm" "redis_standard_memory_usage" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "redis-memory-alarm-rule"
  project = "acs_kvstore"
  metric  = "StandardMemoryUsage"

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

resource "alicloud_cms_alarm" "redis_max_tr" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "redis-max-rt-alarm-rule"
  project = "acs_kvstore"
  metric  = "StandardMaxRt"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 10000
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 60
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}