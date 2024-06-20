accountid=
access_key=""
secret_key=""
region=""
number_of_instances = 5
name                        = "my-ecs-cluster"
use_num_suffix              = true
image_id                    = ""
instance_type               = "ecs.sn1ne.large"
vswitch_id                  = "vsw-fhuqie"
security_group_ids          = ["sg-12345678"]
associate_public_ip_address = true
internet_max_bandwidth_out  = 10

key_name = "for-ecs-cluster"

system_disk_category = "cloud_ssd"
system_disk_size     = 50

tags = {
   Created      = "Terraform"
   Environment = "dev"
}