from jnpr.junos.utils.config import Config
from jnpr.junos.device import Device
from jnpr.junos.exception import ConnectError, CommitError, RpcError
from lxml import etree as et
from pprint import pprint
from graphviz import Digraph



devices = []
management_ips = ['insert node you want to start exploring the topography from']
seen_routers = []

dot = Digraph(comment='Network Topology', engine='dot')


def draw_graph(dot,router_data):
    
    nodes_added = dict() 
    links_added = set()
    
    for entry in router_data:
        local = entry['lldp_local_system_name']
        local_ip = entry['lldp_local_management_address']
        neighbor = entry['lldp_remote_system_name']
        neighbor_ip = entry['lldp_remote_management_address']
        local_intf = entry['lldp_local_interface']
        neighbor_intf = entry['lldp_remote_port_description']
    
    
        if local not in nodes_added:
            dot.node(local, label=f"{local}\n{local_ip}",fontsize='10', dir='both')
            nodes_added[local] = local_ip
    
        if neighbor not in nodes_added:
            dot.node(neighbor, label=f"{neighbor}\n{neighbor_ip}")
            nodes_added[neighbor] = neighbor_ip
    
    
        link_key = tuple(sorted([local, neighbor]))
        if link_key not in links_added:
            label = f"{local_intf} <--> {neighbor_intf}"
            dot.edge(local, neighbor, label=label,fontsize = '5', dir='both')
            links_added.add(link_key)
    return dot


def get_network_topology(management_ip):
	with Device(host = management_ip, user = 'labuser', password = 'Labuser') as device:
		local_information = device.rpc.get_lldp_local_info()
		lldp_local_system_name = local_information.xpath('//lldp-local-system-name/text()')[0]
		lldp_local_management_address = local_information.xpath('//lldp-local-management-address/text()')[0]
		result = device.rpc.get_lldp_neighbors_information()
		neighbor_interface = []
		for lldp_neighbor_info in result.xpath('lldp-neighbor-information'):
			if "router" in (lldp_neighbor_info.xpath('lldp-remote-system-name/text()')[0]).lower():
				neighbor_interface.append(lldp_neighbor_info.xpath('lldp-local-interface/text()')[0])
		for interface in neighbor_interface:
			response = device.rpc.get_lldp_interface_neighbors_information(interface_name=interface)
			lldp_local_interface = response.xpath('//lldp-local-interface/text()')[0]
			lldp_remote_port_description = response.xpath('//lldp-remote-port-description/text()')[0]
			lldp_remote_system_name = response.xpath('//lldp-remote-system-name/text()')[0]
			lldp_remote_management_address = response.xpath('//lldp-remote-management-address/text()')[0]
			
			info = {
			    "lldp_local_system_name": lldp_local_system_name,
			    "lldp_local_management_address": lldp_local_management_address,
				"lldp_local_interface": lldp_local_interface,
				"lldp_remote_port_description": lldp_remote_port_description,
				"lldp_remote_system_name": lldp_remote_system_name,
				"lldp_remote_management_address": lldp_remote_management_address
				}
			devices.append(info)
			management_ips.append(lldp_remote_management_address)
	return

try:
	for management_ip in management_ips:
		if management_ip not in seen_routers:
			get_network_topology(management_ip)
			#management_ips.remove(management_ip)
			seen_routers.append(management_ip)
		else:
			management_ips.remove(management_ip)
	#pprint(devices)
	dote = draw_graph(dot, devices)
	dote.render('network_topology.gv', view=True)
except ConnectError as err:
    print("connection error: ", repr(err))
except CommitError as err:
    print("Commit Error: ", repr(err))
except Exception as err:
    print(repr(err))
