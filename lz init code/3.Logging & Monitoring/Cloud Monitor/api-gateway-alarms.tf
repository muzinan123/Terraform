
resource "alicloud_cms_alarm" "api_gateway_code4xx" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "api-gateway-code4xx-alarm-rule"
  project = "acs_apigateway_dashboard"
  metric  = "code4XX_stage"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 1000
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}

resource "alicloud_cms_alarm" "api_gateway_code5xx" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "api-gateway-code5xx-alarm-rule"
  project = "acs_apigateway_dashboard"
  metric  = "code5XX_stage"

  dimensions = {
    userId = var.target_account_id
  }

  escalations_critical {
    statistics          = "Average"
    comparison_operator = ">"
    threshold           = 1000
    times               = 1
  }

  contact_groups     = [var.contact_group_name]
  period             = 300
  silence_time       = 600
  effective_interval = "0:00-23:59"
  webhook            = var.contact_web_hook_url
}