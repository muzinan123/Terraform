############provider The first way#########
provider "alicloud" {
  # 目前TF无法支持动态provider功能
   access_key = var.access_key
   secret_key = var.secret_key
  assume_role {
    role_arn           = "acs:ram::137974xxxxxxxxx:role/ResourceDirectoryAccountAccessRole"
    session_name       = "AccountLandingZoneSetup"
    session_expiration = 999
  }
}


##########provider The second way###########
# provider "alicloud" {
#  access_key = var.access_key
#  secret_key = var.secret_key
#}

resource "alicloud_cms_alarm_contact_group" "contact_group" {
  alarm_contact_group_name = var.contact_group_name
  contacts = [
    alicloud_cms_alarm_contact.first_contact.alarm_contact_name,
    alicloud_cms_alarm_contact.second_contact.alarm_contact_name
  ]
}

resource "alicloud_cms_alarm_contact" "first_contact" {
  alarm_contact_name = "first_contact"
  describe           = "the first contact of the alarm"
  channels_mail      = var.first_contact.mail
  channels_sms       = var.first_contact.sms
  lang               = var.first_contact.lang
}

resource "alicloud_cms_alarm_contact" "second_contact" {
  alarm_contact_name = "second_contact"
  describe           = "the second contact of the alarm"
  channels_mail      = var.second_contact.mail
  channels_sms       = var.second_contact.sms
  lang               = var.second_contact.lang
}
