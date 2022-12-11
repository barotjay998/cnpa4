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

    return service_and_neighbours, service_and_networks


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

def dijkstras_shortest_path(service_and_neighbours, networks_and_service, networks_and_cost):
    # Initial Setup
    # Create a datastructre for Dijkstra’s Shortest Path Algorithm.
    dijkstras = {"vertex": [], "shortest_from_origin": [], "previous_vertex": []}
    visited = []
    unvisited = []

    # Add the list of vertices
    for service in service_and_neighbours:
        dijkstras["vertex"].append(service)
        dijkstras["shortest_from_origin"].append(1000000)
        dijkstras["previous_vertex"].append(None)
        unvisited.append(service)

    # Identify the source vertex
    for service in service_and_neighbours:
        if service.name == "jay_client":
            startvertex = service
            dijkstras["shortest_from_origin"][unvisited.index(startvertex)] = 0
            break
    # Initial Setup Ends

    # Begin Algorithm
    while len(unvisited) != 0:
        # Keep running the algorithm untill all vertices are visited

        # Step 1: Find the vertex with the shortest distance from startvertex
        # Note: for the 1st itreation it is the startvertex itself.
        shortest_distance = dijkstras["shortest_from_origin"].index(min(dijkstras["shortest_from_origin"]))
        current_vertex = dijkstras["vertex"][shortest_distance]
        print("Current Service: {0}, Name: {1}".format(current_vertex, current_vertex.name))

        # Examine the unvisited neighbours of current vertex
        neighbours = service_and_neighbours[current_vertex]
        unvisited_neighbours = []
        for item in neighbours:
            if item not in visited:
                unvisited_neighbours.append(item)
        
        # Calculate the distance of each neighbour from the start vertex
        print("Unvisited Neighbours: ",unvisited_neighbours)

        # update the previous node for each of the unvisited_neighbours
        for un in unvisited_neighbours:
            dijkstras["previous_vertex"][dijkstras["vertex"].index(un)] = current_vertex

        for un in unvisited_neighbours:
            # check the previous vertex of this unvisited neighbour
            # find the network in which previous vertex nad unvisited neighbour
            # are in the same network (link)
            cost = 0
            for n, s in networks_and_service.items():
                previous_vertex = dijkstras["previous_vertex"][dijkstras["vertex"].index(un)]
                if (previous_vertex in s) and (un in s):
                    print("got the link: ", networks_and_cost[n])
                    print(previous_vertex)

        break    

def network_and_service_mapping(service_and_networks):
    networks_and_service = {}
    file = open('network_data.json')
    data = json.load(file)
    networks = data["networks"]

    for network in networks:
        networks_and_service[network["ID"]] = []
    
    for network in networks_and_service:
        for service, service_nets in service_and_networks.items():
            for nets in service_nets:
                if nets == network:
                    networks_and_service[network].append(service)
    return networks_and_service

def network_and_cost_mapping():
    networks_and_cost = {}
    file = open('network_data.json')
    data = json.load(file)
    networks = data["networks"]

    for network in networks:
        networks_and_cost[network["ID"]] = 1
    
    return networks_and_cost

service_and_neighbours, service_and_networks = get_service_map(my_services)
networks_and_service= network_and_service_mapping(service_and_networks)
networks_and_cost = network_and_cost_mapping()
dijkstras_shortest_path(service_and_neighbours, networks_and_service, networks_and_cost)