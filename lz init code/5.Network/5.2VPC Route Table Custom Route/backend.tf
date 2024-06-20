terraform {
  backend "oss" {
    bucket = "terraformtest"
    prefix = "path/mystate"
    key = "{replace_uid}"
    region = "cn-hangzhou"
    tablestore_endpoint = "https://landingzone.cn-hangzhou.ots.aliyuncs.com"
    tablestore_table = "terraform"
    # 是为了做OSS的权限用的
//    ecs_role_name = "EcsRamRole"
    access_key = ""
    secret_key = ""
    endpoint = "oss-cn-hangzhou.aliyuncs.com"
  }
}