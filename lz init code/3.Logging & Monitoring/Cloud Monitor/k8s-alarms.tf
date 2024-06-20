
resource "alicloud_cms_alarm" "k8s_node_cpu_utilization" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "k8s-node-cup-alarm-rule"
  project = "acs_k8s"
  metric  = "node.cpu.utilization"

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

resource "alicloud_cms_alarm" "k8s_node_memory_utilization" {
  depends_on = [alicloud_cms_alarm_contact_group.contact_group]

  name    = "k8s-node-memory-alarm-rule"
  project = "acs_k8s"
  metric  = "node.memory.utilization"

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