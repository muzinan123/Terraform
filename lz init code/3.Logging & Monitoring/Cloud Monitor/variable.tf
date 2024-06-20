// use-case-iac-unittest
variable "target_account_id" {
  description = "Target account id"
  type        = string
  default     = "13xxxx66439xxxxx"

  validation {
    condition     = length(var.target_account_id) == 16
    error_message = "The target_account_id value must be a valid account id."
  }
}

variable "target_account_region" {
  description = "Target account region"
  type        = string
  default     = "cn-shanghai"
}

variable "target_account_account_access_role" {
  description = "Target account account access role"
  type        = string
  default     = "acs:ram::13xxxx66439xxxxx:role/ResourceDirectoryAccountAccessRole"
}

variable "contact_group_name" {
  description = "Name of the contact group"
  type        = string
  default     = "default_contact_group"
}

variable "contact_web_hook_url" {
  // the address of Function Compute to forward alarms
  description = "URL of contact web hook"
  type        = string
  default     = ""
}

variable "first_contact" {
  type = object({
    mail = string
    sms  = string
    lang = string
  })
  default = {
    mail = ""
    sms  = ""
    lang = "zh-cn"
  }
}

variable "second_contact" {
  type = object({
    mail = string
    sms  = string
    lang = string
  })
  default = {
    mail = ""
    sms  = ""
    lang = "zh-cn"
  }
}
