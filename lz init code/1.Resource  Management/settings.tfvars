access_key = ""
secret_key = ""


create_folder    = false
parent_folder_id = ""
folder_names     = ["SANDBOX","DEVL","TEST","UAT","STAG","PROD"]

attach_policy = true
attachment = [
    {
        policy_id = ""
        target_id = ""
    }
]

create_account        = false
accounts = [
    {
        folder_id  = "fd-xxxxx"
        account_name_prefix = "test"
        payer_account_id =""
        display_name = "test"
    }
]

create_control_policy = false


control_policy=[
 {
        control_policy_name="unapproved-creating-or-deleting"
        description="Deny public domain to be created or deleted in Domain Service."
        effect_scope="RAM"
        policy_document=<<EOF
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "alidns:AddDomain",
        "alidns:DeleteDomain",
        "pvtz:AddZone",
        "pvtz:DeleteZone"
      ],
      "Resource": "*",
      "Condition": {}
    }
  ]
 }     
        EOF
        }
]
