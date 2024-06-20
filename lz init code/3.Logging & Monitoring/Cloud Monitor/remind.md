1.Before you can run the TerraForm script, you must complete the provider information in the contact-group.tf.



There are two examples of how providers can be provided. You can choose one of them.

first one:

```hcl
provider "alicloud" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region     = "${var.region}"
}
```



second one:

```hcl
provider "alicloud" {
  assume_role {
    role_arn           = "acs:ram::ACCOUNT_ID:role/ROLE_NAME"
    policy             = "POLICY"
    session_name       = "SESSION_NAME"
    session_expiration = 999
  }
}
```

The second way is when you need to access a member account.

