access_key = ""
secret_key = ""
region = "cn-shanghai"


   create_directory = false
   directory_id     = ""
   create_group     = false
   group_name       = "sso-test"
   description      = "sso group description "

   create_user = true
   users = [
      {
         user_name = "user-01"
      },
      {
         user_name    = "user-02"
         description  = "cloud user"
         display_name = "foo"
         email        = "abc@163.com"
         first_name   = "weijie"
         last_name    = "qi"
         status       = "Enabled"
      },
      {
         user_name = "user-03"
         status    = "Disabled"
      }
   ]

   create_access_configuration = true
   access_configurations = [
      {
         access_configuration_name = "ac-01"
         description               = "ac 01"
         permission_policies = [
            {
               permission_policy_document = <<EOF
            {
              "Statement":[
                {
                  "Action":"ecs:Get*",
                  "Effect":"Allow",
                  "Resource":[
                    "*"
                  ]
                }
              ],
              "Version": "1"
            }
          EOF
               permission_policy_type     = "Inline"
               permission_policy_name     = "ecs-policy"
            }
         ]
         relay_state                      = "https://cloudsso.console.aliyun.com/test1"
         session_duration                 = 1800
         force_remove_permission_policies = true
      },
      {
         access_configuration_name = "ac-02"
         description               = "ac 02"
         permission_policies = [
            {
               permission_policy_document = <<EOF
            {
              "Statement":[
                {
                  "Action":"vpc:Get*",
                  "Effect":"Allow",
                  "Resource":[
                    "*"
                  ]
                }
              ],
              "Version": "1"
            }
          EOF
               permission_policy_type     = "Inline"
               permission_policy_name     = "vpc-policy"
            }
         ]
         relay_state                      = "https://cloudsso.console.aliyun.com/test2"
         session_duration                 = 1800
         force_remove_permission_policies = true
      }
   ]
}