provider "alicloud" {
   access_key = ""
  secret_key = ""
}

resource "alicloud_config_aggregator" "example" {
  aggregator_accounts {
    account_id   = "123968452689****"
    account_name = "tf-test01"
    account_type = "ResourceDirectory"
  }
   aggregator_accounts {
    account_id   = "123968452689****"
    account_name = "tf-test02"
    account_type = "ResourceDirectory"
  }
   aggregator_accounts {
    account_id   = "123968452689****"
    account_name = "tf-test03"
    account_type = "ResourceDirectory"
  }
  aggregator_name = "tf-testaccConfigAggregator1234"
  description     = "tf-testaccConfigAggregator1234"
}

resource "alicloud_config_aggregate_config_rule" "pwd" {
        aggregator_id              = alicloud_config_aggregator.example.id
  aggregate_config_rule_name = "ram-password-policy-check"
  source_identifier    = "ram-password-policy-check"
  source_owner         = "ALIYUN"
  resource_types_scope = ["ACS::::Account"]
  description          = "If the settings of password policies configured for each RAM user meet the specified values, the evaluation result is compliant."
  risk_level                = 1
  input_parameters = {
    hardExpire = true,
        maxLoginAttemps = 5,
        maxPasswordAge = 90,
        minimumPasswordLength =8,
        passwordReusePrevention =3,
        requireLowercaseCharacters = true,
        requireNumbers = true,
        requireSymbols = true,
        requireUppercaseCharacters = true,
  }
  config_rule_trigger_types = "ScheduledNotification"
}

resource "alicloud_config_aggregate_config_rule" "mfa" {
        aggregator_id              = alicloud_config_aggregator.example.id
  aggregate_config_rule_name = "root-mfa-check"
   source_identifier    = "root-mfa-check"
  source_owner         = "ALIYUN"
  resource_types_scope = ["ACS::::Account"]
  description          = "If MFA is enabled for each Alibaba Cloud account, the evaluation result is compliant."
  risk_level                = 1
  config_rule_trigger_types = "ScheduledNotification"
}

resource "alicloud_config_aggregate_config_rule" "oss-bucket-public-read-prohibited" {
        aggregator_id              = alicloud_config_aggregator.example.id
  aggregate_config_rule_name= "oss-bucket-public-read-prohibited"
  source_identifier    = "oss-bucket-public-read-prohibited"
  source_owner         = "ALIYUN"
  resource_types_scope = ["ACS::OSS::Bucket"]
  description          = "If the access control list (ACL) of each Object Storage Service (OSS) bucket denies read access from the Internet, the evaluation result is compliant."
  risk_level                = 1
  config_rule_trigger_types = "ConfigurationItemChangeNotification"
}


resource "alicloud_config_aggregate_config_rule" "oss-bucket-public-write-prohibited" {
        aggregator_id              = alicloud_config_aggregator.example.id
  aggregate_config_rule_name          = "oss-bucket-public-write-prohibited"
  source_identifier    = "oss-bucket-public-write-prohibited"
  source_owner         = "ALIYUN"
  resource_types_scope = ["ACS::OSS::Bucket"]
  description          = "If the ACL of each OSS bucket denies read and write access from the Internet, the evaluation result is compliant."
  risk_level                = 1
  config_rule_trigger_types = "ConfigurationItemChangeNotification"
}

resource "alicloud_config_aggregate_config_rule" "oss-bucket-server-side-encryption-enabled" {
        aggregator_id              = alicloud_config_aggregator.example.id
  aggregate_config_rule_name = "oss-bucket-server-side-encryption-enabled"
  source_identifier    = "oss-bucket-server-side-encryption-enabled"
  source_owner         = "ALIYUN"
  resource_types_scope = ["ACS::OSS::Bucket"]
  description          = "create by terraform."
  risk_level                = 1
  config_rule_trigger_types = "ConfigurationItemChangeNotification"
}

resource "alicloud_config_aggregate_config_rule" "sg-risky-ports-check" {
        aggregator_id              = alicloud_config_aggregator.example.id
  aggregate_config_rule_name = "sg-risky-ports-check"
  source_identifier    = "sg-risky-ports-check"
  source_owner         = "ALIYUN"
  resource_types_scope = ["ACS::ECS::SecurityGroup"]
  description          = "create by terraform."
  risk_level                = 1
  input_parameters = {
    ports = "22,3389",
  }
  config_rule_trigger_types = "ConfigurationItemChangeNotification"
}




