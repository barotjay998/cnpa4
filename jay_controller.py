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


def service_to_ip(my_services):
    service_to_ip = {}
    for service in my_services:
        # Iterate through each services
        node_name = service.attrs["Spec"]['TaskTemplate']["Placement"]['Constraints'][0].split("==")[1]
        # Network data contains all the information about the nodes and IP addresses
        file = open('network_data.json')
        data = json.load(file)
        nodes= data["nodes"]
        for node in nodes:
            if node["Name"]==node_name:
                service_to_ip[service.name] = node['IP']
    # Save the mapping in a seprate file to refer during computation.
    with open("service_to_ip_map.json", "w") as outfile:
        json.dump(service_to_ip, outfile)
    return service_to_ip


def least_hop_path(service_and_neighbours):
    for service in service_and_neighbours:
        # find the client in the network first
        if service.name == "jay_client":
            myclient = service
            print(myclient)
            break

    q = [(myclient, [])]
    print(q)
    v = set()
    # while q:
    #     s, path = q.pop(0)
    #     p = path[:]
    #     p.append(s.name)
    #     if s.name == "jay_server":
    #        return p

    #     v.add(s)
    #     for nei in service_and_neighbours[s]:
    #         if nei not in v:

    #             q.append((nei, p))

