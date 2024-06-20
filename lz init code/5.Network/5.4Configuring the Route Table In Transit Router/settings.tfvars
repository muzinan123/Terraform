access_key=""
secret_key=""
region="cn-beijing"
accountid=1379746643909237
create_route_entry = true
route_entry =[
#Bind to Ingress VPC
	{
	transit_router_route_table_id = "vtb-2zesx8saitg7gqomigww0"
  	transit_router_route_entry_destination_cidr_block = "10.153.159.0/24"
  	transit_router_route_entry_name = "Engress"
  	transit_router_route_entry_next_hop_id  = "tr-attach-n3pipu9s5jwbyjpr6b"
	},{
	transit_router_route_table_id = "vtb-2zesx8saitg7gqomigww0"
  	transit_router_route_entry_destination_cidr_block = "10.153.157.0/25"
  	transit_router_route_entry_name = "VPN"
  	transit_router_route_entry_next_hop_id  = "tr-attach-ygbkum0jxkvdgiex1u"
	},{
	transit_router_route_table_id = "vtb-2zesx8saitg7gqomigww0"
  	transit_router_route_entry_destination_cidr_block = "10.153.1.0/25"
  	transit_router_route_entry_name = "BUCustom"
  	transit_router_route_entry_next_hop_id  = "tr-attach-1p9obz3y3aokcl96hn"
	},
#Bind to Egress VPC	
	{
	transit_router_route_table_id = "vtb-2ze91myy53426auumi5b7"
  	transit_router_route_entry_destination_cidr_block = "10.153.158.0/24"
  	transit_router_route_entry_name = "Ingress"
  	transit_router_route_entry_next_hop_id  = "tr-attach-3o8gt6q9575hrimmgq"
	},
	{
	transit_router_route_table_id = "vtb-2ze91myy53426auumi5b7"
  	transit_router_route_entry_destination_cidr_block = "10.153.157.0/25"
  	transit_router_route_entry_name = "VPN"
  	transit_router_route_entry_next_hop_id  = "tr-attach-ygbkum0jxkvdgiex1u"
	},{
	transit_router_route_table_id = "vtb-2ze91myy53426auumi5b7"
  	transit_router_route_entry_destination_cidr_block = "10.153.1.0/25"
  	transit_router_route_entry_name = "BUCustom"
  	transit_router_route_entry_next_hop_id  = "tr-attach-1p9obz3y3aokcl96hn"
	},
#Bind to Shared Service VPC,BU Account VPC
	{
	transit_router_route_table_id = "vtb-2zetp7oslzcvekzrwl813"
  	transit_router_route_entry_destination_cidr_block = "10.153.158.0/24"
  	transit_router_route_entry_name = "Ingress"
  	transit_router_route_entry_next_hop_id  = "tr-attach-3o8gt6q9575hrimmgq"
	},
	{
	transit_router_route_table_id = "vtb-2zetp7oslzcvekzrwl813"
  	transit_router_route_entry_destination_cidr_block = "0.0.0.0/0"
  	transit_router_route_entry_name = "Egress"
  	transit_router_route_entry_next_hop_id  = "tr-attach-n3pipu9s5jwbyjpr6b"
	},{
	transit_router_route_table_id = "vtb-2zetp7oslzcvekzrwl813"
  	transit_router_route_entry_destination_cidr_block = "10.0.0.0/8"
  	transit_router_route_entry_name = "VPN1"
  	transit_router_route_entry_next_hop_id  = "tr-attach-ygbkum0jxkvdgiex1u"
	},
	{
	transit_router_route_table_id = "vtb-2zetp7oslzcvekzrwl813"
  	transit_router_route_entry_destination_cidr_block = "167.107.0.0/16"
  	transit_router_route_entry_name = "VPN2"
  	transit_router_route_entry_next_hop_id  = "tr-attach-ygbkum0jxkvdgiex1u"
	}
]


create_association = false
association=[
	{
 	transit_router_route_table_id = ""
	transit_router_attachment_id =""
	}
]
