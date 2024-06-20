locals{
  eip_count            = var.number_of_eips
}

resource "alicloud_eip" "this" {
  count = var.create ? local.eip_count : 0

  address_name         = local.eip_count > 1 || var.use_num_suffix ? format("%s%03d", var.name, count.index + 1) : var.name
  description          = var.description
  bandwidth            = var.bandwidth
  internet_charge_type = var.internet_charge_type
  payment_type         = var.payment_type != "" ? var.payment_type : var.instance_charge_type == "PostPaid" ? "PayAsYouGo" : "Subscription"
  period               = var.period
  isp                  = var.isp
  resource_group_id    = var.resource_group_id
  tags = merge(
    {
      Name = local.eip_count > 1 || var.use_num_suffix ? format("%s%03d", var.name, count.index + 1) : var.name
    },
    var.tags,
  )
}