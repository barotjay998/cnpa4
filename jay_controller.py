import docker
import subprocess
import shlex
import json

# Lets you do anything the docker command does, but from within Python apps
docker_client = docker.from_env()

# Get all the networks and services in the swarm
networks = docker_client.networks.list()
services = docker_client.services.list()

# Store the network IDs
network_ids = []
for network in networks:
    network_ids.append(network.id)

# Get all my services running in the swarm
my_services = []
my_service_ids = set()
for service in services:
    if service.name.startswith('jay'):
        my_services.append(service)
        my_service_ids.add(service.id)

# Get the mapping
def get_service_map(my_services):
    service_and_networks = {} # Stores the networks for each service.
    service_and_neighbours = {}

    # Get the network list for each service.
    for service in my_services:
        # service_and_networks = {service: its_networks, ..}
        # values of service and networks will be the networks the service is a part of.
        service_and_networks[service] = [dictionary["Target"] for dictionary in service.attrs["Spec"]["TaskTemplate"]["Networks"]]

    # Assign the key values of the service_map as the service Ids
    for service in service_and_networks:
        # service_map = {service: [], ..}
        # Initialize to start filling the neighbours of service.
        service_and_neighbours[service] = []
    
    for service in service_and_networks:
        # Start looking into myservices one by one
        for network in service_and_networks[service]:
            # Look into each network of that myservice
            for linked_service in service_and_networks:
                # Iterate through each myservice again to do network matching
                if linked_service == service:
                    # Skip if it is the same my service for which I am trying to find neighbours
                    continue
                if network in service_and_networks[linked_service]:
                    # If it is not the same service for which I am trying to find its neighbours
                    # Look into its networks.
                    if linked_service not in service_and_neighbours[service]:
                        # If this linkedservice is not added as service neighbour, add it.
                        service_and_neighbours[service].append(linked_service)
                    if service not in service_and_neighbours[linked_service]:
                        # Simulatneously service is also a neigbour of linkedservice.
                        service_and_neighbours[linked_service].append(service)

    return service_and_neighbours
        
print(get_service_map(my_services))

def add_service_ips(my_services):
    service_ip = {}
    for i in my_services:
        print(i.name)
        print(i.attrs["Spec"]['TaskTemplate']["Placement"]['Constraints'][0].split("==")[1])
        node_name = i.attrs["Spec"]['TaskTemplate']["Placement"]['Constraints'][0].split("==")[1]
        f = open('network_data.json')
        # returns JSON object as 
        # a dictionary
        data = json.load(f)
        nodes= data["nodes"]
        for node in nodes:
            if node["Name"]==node_name:
                service_ip[i.name] = node['IP']
                
    with open("service_ip.json", "w") as outfile:
        json.dump(service_ip, outfile)
    return service_ip


service_ip = add_service_ips(my_services)

print("--------------------------------------------")
print(service_ip)
