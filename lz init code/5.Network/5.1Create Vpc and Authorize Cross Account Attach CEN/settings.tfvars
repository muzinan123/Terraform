access_key = ""
secret_key = ""
region = "cn-beijing"
accountid=

create            = true
vpc_name          = "BU1-Prod1-App1-Test-BJ"
vpc_cidr          = "10.153.1.0/25"



availability_zones = ["cn-beijing-h", "cn-beijing-g"]
vswitch_cidrs      = ["10.153.1.0/28", "10.153.1.16/28"]
vswitch_names = ["BU1-Prod1-App1-Test-BJ-H","BU1-Prod1-App1-Test-BJ-G"]

cen_grant = true
grant_information = [
    {
        cen_id = "cen-g71pl087knklz6nmpj"
        cen_owner_id = "1379746643909237"
    }
]


