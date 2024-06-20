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


