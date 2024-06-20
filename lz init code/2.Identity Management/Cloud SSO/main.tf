 provider "alicloud" {
  access_key = var.access_key
  secret_key = var.secret_key
  region = var.region
}

# The cloud sso directory id is the precondition of other cloud sso resources
# In this module, you can specify an existing directory id or create a new one using this resource
#resource "alicloud_cloud_sso_directory" "this" {
#  count                     = var.create_directory ? 1 : 0
#  directory_name            = var.directory_name
#  mfa_authentication_status = var.mfa_authentication_status
#  dynamic "saml_identity_provider_configuration" {
#    for_each = var.saml_identity_provider_configuration
#    content {
#      encoded_metadata_document = saml_identity_provider_configuration.value.encoded_metadata_document
#      sso_status                = saml_identity_provider_configuration.value.sso_status
#   }
#  }
#  scim_synchronization_status = var.scim_synchronization_status
#}

# Create a new cloud sso group
resource "alicloud_cloud_sso_group" "this" {
  count        = var.create_group ? 1 : 0
  directory_id = var.directory_id
  group_name   = var.group_name
  description  = var.description
}

# Create several cloud sso users
resource "alicloud_cloud_sso_user" "this" {
  count        = var.create_user ? length(var.users) : 0
  directory_id = var.directory_id
  user_name    = lookup(var.users[count.index], "user_name", )
  description  = lookup(var.users[count.index], "description", null)
  display_name = lookup(var.users[count.index], "display_name", null)
  email        = lookup(var.users[count.index], "email", null)
  first_name   = lookup(var.users[count.index], "first_name", null)
  last_name    = lookup(var.users[count.index], "last_name", null)
  status       = lookup(var.users[count.index], "status", "Enabled")
}

# Add a list of cloud sso users into cloud sso group
resource "alicloud_cloud_sso_user_attachment" "this" {
  count        = var.add_user_to_group ? length(var.adds) : 0
  directory_id = var.directory_id
  user_id      = lookup(var.adds[count.index],"user_id")
  group_id     = lookup(var.adds[count.index],"group_id")
}

# Create several cloud sso access configurations
resource "alicloud_cloud_sso_access_configuration" "this" {
  count                     = var.create_access_configuration ? length(var.access_configurations) : 0
  access_configuration_name = lookup(var.access_configurations[count.index], "access_configuration_name", )
  description               = lookup(var.access_configurations[count.index], "description", )
  directory_id              = var.directory_id
  dynamic "permission_policies" {
    for_each = lookup(var.access_configurations[count.index], "permission_policies", )
    content {
      permission_policy_document = permission_policies.value.permission_policy_document
      permission_policy_type     = lookup(permission_policies.value, "permission_policy_type", "Inline")
      permission_policy_name     = permission_policies.value.permission_policy_name
    }
  }
  relay_state                      = lookup(var.access_configurations[count.index], "relay_state", )
  session_duration                 = lookup(var.access_configurations[count.index], "session_duration", )
  force_remove_permission_policies = lookup(var.access_configurations[count.index], "force_remove_permission_policies", true)
}


resource alicloud_cloud_sso_access_assignment default {
  count        = var.create_access_assignment ? length(var.sso_assignment) : 0
  directory_id            = var.directory_id 
  access_configuration_id = lookup(var.sso_assignment[count.index], "access_configuration_id")
  target_type             = "RD-Account"
  target_id               = lookup(var.sso_assignment[count.index], "target_id")
  principal_type          = lookup(var.sso_assignment[count.index], "principal_type")
  principal_id            = lookup(var.sso_assignment[count.index],"principal_id")
  deprovision_strategy    = "DeprovisionForLastAccessAssignmentOnAccount"
}

