#####################
# Cloud SSO Directory
#####################
variable "create_directory" {
  description = "Controls if cloud sso directory should be created (it affects almost all resources)"
  type        = bool
  default     = true
}

variable "directory_id" {
  description = "The id of an existing cloud sso directory. It will be ignored when `create_directory` is true."
  type        = string
  default     = ""
}

variable "directory_name" {
  description = "The name of a new cloud sso directory."
  type        = string
  default     = ""
}
variable "mfa_authentication_status" {
  description = "The mfa authentication status. Valid values: Enabled or Disabled. Default to Enabled."
  type        = string
  default     = "Enabled"
}
variable "scim_synchronization_status" {
  description = "The scim synchronization status. Valid values: Enabled or Disabled. Default to Disabled."
  type        = string
  default     = "Disabled"
}

variable "saml_identity_provider_configuration" {
  description = "The saml identity provider configuration. See: https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/cloud_sso_directory#saml_identity_provider_configuration"
  type        = list(map(string))
  default     = null
}
#####################
# Cloud SSO Group
#####################
variable "create_group" {
  description = "Controls if cloud sso user group should be created"
  type        = bool
  default     = true
}

variable "group_id" {
  description = "The id of an existing cloud sso group. It will be ignored when `create_group` is true."
  type        = string
  default     = ""
}

variable "group_name" {
  description = "The name of a new cloud sso user group."
  type        = string
  default     = ""
}
variable "description" {
  description = "The description of a new cloud sso user group."
  type        = string
  default     = ""
}

#####################
# Cloud SSO User
#####################
variable "create_user" {
  description = "Should be true to create cloud sso user and add them into the new user group."
  type        = bool
  default     = false
}

variable "add_user_to_group" {
  description = "Should be true to create cloud sso user and add them into the new user group."
  type        = bool
  default     = false
}

variable "adds" {
  description = "A list mapping used to add users to group"
  type        = list(map(string))
  default     = []
}


variable "users" {
  description = "List of maps of cloud sso access configuration permission policies. See https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/cloud_sso_access_configuration#permission_policies"
  type        = list(map(string))
  default     = null
}

#####################
# Cloud SSO Access Configuration
#####################
variable "create_access_configuration" {
  description = "Should be true to create cloud sso access configuration and then assign them to the new user group"
  type        = bool
  default     = false
}

variable "access_configurations" {
  description = "List of maps of cloud sso access configurations. See https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/cloud_sso_access_configuration"
  type = list(object({
    access_configuration_name        = string
    description                      = string
    permission_policies              = list(map(string))
    relay_state                      = string
    session_duration                 = number
    force_remove_permission_policies = bool
  }))
  default = []
}

variable "create_access_assignment" {
  type        = bool
  default     = false
}

variable "sso_assignment"{
  type        = list(map(string))
  default     = []
}

variable "access_key" {}

variable "secret_key" {}

variable "region" {}