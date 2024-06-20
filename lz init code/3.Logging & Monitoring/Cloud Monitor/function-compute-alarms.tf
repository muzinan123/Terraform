
resource "alicloud_cms_alarm" "function_throttles" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "fc-throttles-alarm-rule"
  project = "acs_fc"
  metric  = "FunctionThrottles"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 10
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 60
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}

resource "alicloud_cms_alarm" "function_errors" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "fc-errors-alarm-rule"
  project = "acs_fc"
  metric  = "FunctionFunctionErrors"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 3
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 60
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}