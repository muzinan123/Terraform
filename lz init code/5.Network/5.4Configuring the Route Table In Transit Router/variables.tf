variable "access_key" {}

variable "secret_key" {}

variable "accountid" {}

variable "region" {}

variable "create_route_entry" {
    description = "Whether to create route entry."
    type        = bool
    default     = false
}

variable "route_entry" {
    type        = list(map(string))
    default     = []
}

variable "create_association" {
    description = "Whether to create cen transit router route table association."
    type        = bool
    default     = false
}
variable "association" {
    type        = list(map(string))
    default     = []
}


