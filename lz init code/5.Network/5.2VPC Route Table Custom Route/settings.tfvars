access_key=""
secret_key=""
region="cn-beijing"
accountid=
create_route_entry = true
route_entry =[
#VPC Route Ingress_VPC
	{
	route_table_id = "vtb-2zekd4hp45vz9087s4y6i"
  	destination_cidrblock = "10.153.159.0/25"
  	nexthop_type = "Attachment"
  	nexthop_id  = "tr-attach-3o8gt6q9575hrimmgq"
	},
#Bind to Egress VPC	
	{
	route_table_id = "vtb-2ze0lvxeasyulf9xi2zh7"
  	destination_cidrblock = "10.153.158.0/24"
  	nexthop_type = "Attachment"
  	nexthop_id  = "tr-attach-n3pipu9s5jwbyjpr6b"
	},
#Bind to Shared Service VPC,BU Account VPC
	{
	route_table_id = "vtb-2ze2ebxztl3nob3kq1hop"
  	destination_cidrblock = "10.153.158.0/24"
  	nexthop_type = "Attachment"
  	nexthop_id  = "tr-attach-ygbkum0jxkvdgiex1u"
	}
]
