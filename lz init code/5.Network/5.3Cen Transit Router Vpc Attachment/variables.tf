variable "access_key" {}

variable "secret_key" {}

variable "accountid" {}

variable "region" {}
variable "region_id" {
  default=""
}
variable "cen_id" {}
variable "availability_zone_map" {
   default ={
 "cn-beijing":["cn-beijing-h","cn-beijing-g"]
}
}
variable "transit_router_id" {}
variable "vpc_owner_id" {}
variable "vpc_id" {}
variable "vswitch_id_1" {}
variable "vswitch_id_2" {}
variable "transit_router_attachment_name" {}



