# Instructor: Aniruddha Gokhale
# Student: Jay Barot
# Created: Fall 2022
# 
# This code was create for Programming Assignment 4
# This is my own custom SDN Controller for our PA4 docker network
# I first the information regarding the docker servies I initiated
# By using the python docker SDK. And the associated networks these services are using.
# Then implement Dijkstras algorithm on the network
#
# Nothing is hardcoded, this controller can be used for ANY network with appropriate network data,
# and the Dijkstras algorithm will give the shortest path to each node in the network given the startnode.

# import the needed packages
import argparse # for argument parsing
import docker
import json
import pyfiglet # Just for fun, Good looking banners

############################################
# SDN Controller Exceptions
############################################

############################################
# SDN Controller Exceptions: Ends
############################################


def get_service_to_network_neighbours_map(my_services):
    """
    Gives information more information about services
    It generates the follwing mapping information in two return variables
        service_and_networks: Gives information about what networks the service is part of
        service_and_neighbours: Gives information about what are the neighbours of the service
    """
    service_and_networks = {}
    service_and_neighbours = {}

    # Get the network list for each service.
    for service in my_services:
        service_and_networks[service] = [
            dictionary["Target"] 
            for dictionary in service.attrs["Spec"]["TaskTemplate"]["Networks"]
        ]

    # Assign the key of the service_and_neighbours map as the service IDs
    for service in service_and_networks:
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

def dijkstras_shortest_path(service_and_neighbours, networks_and_service, networks_and_cost, source_vertex):
    """
    Dijkstra’s Shortest Path Algorithm
    Attributes:
        service_and_neighbours: dictionary of services IDs as key and their respective service 
                                neighbours IDs as values.
        networks_and_service: dictionary of networks IDs as key and their respective service IDs
                              which are a part of that network.
        networks_and_cost: dictionary of networks IDs as key and their respctive cost to choose that
                           network (our each network of is considered as a link in dijkstra)
        source_vertex: we have the n.w info from the above attributes, dijkstras needs a starting
                       vertex w.r.t which it will calculate shortest path to each node. 
                       for the purpose of our assignment PA4 this is our client.
    """
    ############################################
    # Algorithm: Initial Setup
    ############################################
    # Create necessary data structures
    dijkstras = {
        "vertex": [], 
        "shortest_from_origin": [], 
        "previous_vertex": []
    }
    visited = []
    unvisited = []

    # Add the list of vertices
    for service in service_and_neighbours:
        dijkstras["vertex"].append(service) # giving the list of vertices.
        dijkstras["shortest_from_origin"].append(1000000) # setting to very high value initially.
        dijkstras["previous_vertex"].append(None) # current no previous nodes have been found.
        unvisited.append(service)

    # Identify the source vertex, set it to minimum value
    for service in service_and_neighbours:
        if service.name == source_vertex:
            startvertex = service
            dijkstras["shortest_from_origin"][unvisited.index(startvertex)] = 0
            break

    ############################################
    # Algorithm: Initial Setup Ends
    ############################################

    ################################## 
    # Begin Algorithm 
    ##################################
    while len(visited) < len(unvisited):
        # Keep running the algorithm untill all vertices are visited

        # ------------------------------------------
        # Step 1: Get the Node.
        # Checking: The current vertex must not be in visited AND must be minimum
        min_buf = {}
        temp = {}
        for i in range(len(dijkstras["vertex"])):
            temp[dijkstras["vertex"][i]] = dijkstras["shortest_from_origin"][i]

        for k, v in temp.items():
            if k not in visited:
                min_buf[k] = v

        current_vertex = min(min_buf, key=min_buf.get)
        # print("Current Service: {0}, Name: {1}".format(current_vertex, current_vertex.name))

        # ------------------------------------------
        # Step 2: Get the Node's Unvisited Neighbours.
        neighbours = service_and_neighbours[current_vertex]
        unvisited_neighbours = []
        for item in neighbours:
            if item not in visited:
                unvisited_neighbours.append(item)
        # print("Unvisited Neighbours: ",unvisited_neighbours)
        
        # ------------------------------------------
        # Step 3: Get the each Neighbours distance from the start vertex.
        #   Make the use of previous nodes distance value 
        
        # Update the "previous node" for each of the unvisited_neighbours to the current vertex
        # This helps us to calculate the cost.
        # If the cost is not minimum: we will change this back to old value that 
        #                             we store in "buffer_oldvertex".
        # If the cost is minimum: we anyway have to change this previous node 
        #                         as current vertex as per algorithm.
        buffer_oldvertex = {}
        for un in unvisited_neighbours:
            buffer_oldvertex[un] = dijkstras["previous_vertex"][dijkstras["vertex"].index(un)]
            dijkstras["previous_vertex"][dijkstras["vertex"].index(un)] = current_vertex
       
        for un in unvisited_neighbours:
            # Find the previous vertex of the unvisited neighbour.
            for n, s in networks_and_service.items():
                previous_vertex = dijkstras["previous_vertex"][dijkstras["vertex"].index(un)]
                current_cost = dijkstras["shortest_from_origin"][dijkstras["vertex"].index(un)]
                cost_previous_vertex = dijkstras["shortest_from_origin"][dijkstras["vertex"].index(previous_vertex)]
                
                # The network in which both: the previous vertex & the unvisited neighbour
                # exist is the link for which we need to calculate cost.
                if (previous_vertex in s) and (un in s):
                    # print("got the link: ", networks_and_cost[n])
                    # print(previous_vertex)
                    cost = cost_previous_vertex + networks_and_cost[n]

                    # If this cost is less than the existing cost update this
                    if cost < current_cost:
                        dijkstras["shortest_from_origin"][dijkstras["vertex"].index(un)] = cost
                    else:
                        # change the previous vertex back to original from buffer
                        dijkstras["previous_vertex"][dijkstras["vertex"].index(un)] = buffer_oldvertex[un]

        # put the vertex in the visited section
        visited.append(current_vertex)
        # print(dijkstras, "\n")
    
    ################################## 
    # Algorithm Ends.
    ##################################
    # Note that the algorithm output "dijkstras" dictionary will contain shortest path to every node
    # in the network from the startnode.
    # For the purpose of our assignment, extract the shortest path data only for server.
    ##################################

    return dijkstras

def network_and_service_mapping(network_data, service_and_networks):
    networks_and_service = {}
    networks = network_data["networks"]

    for network in networks:
        networks_and_service[network["ID"]] = []
    
    for network in networks_and_service:
        for service, service_nets in service_and_networks.items():
            for nets in service_nets:
                if nets == network:
                    networks_and_service[network].append(service)
    return networks_and_service

def network_and_cost_mapping(network_data, manual_cost):
    networks_and_cost = {}
    networks = network_data["networks"]

    for network in networks:
        networks_and_cost[network["ID"]] = manual_cost
    
    return networks_and_cost

def network_and_latency_cost_mapping(network_data):
    networks_and_cost = {}
    networks = network_data["networks"]

    for network in networks:
        networks_and_cost[network["ID"]] = network["l"]
    
    return networks_and_cost

def service_and_ip_mapping(my_services):
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

def generate_routing_table(dijkstras_table, initial_vertex, final_vertex, service_and_ip):
    routing_table = {}

    # Reverse traverse dijkstra table untill you reach the initial vertex
    current_vertex = final_vertex
    while current_vertex != initial_vertex:
        for item in dijkstras_table["vertex"]:
            if item.name == current_vertex:
                # Add its previous vertex and itself to the routing table.
                index = dijkstras_table["vertex"].index(item)
                ip_previous =service_and_ip[dijkstras_table["previous_vertex"][index].name]
                ip_current = service_and_ip[dijkstras_table["vertex"][index].name]
                routing_table[ip_previous] = ip_current

                # Update current vertex to previous vertex
                current_vertex = dijkstras_table["previous_vertex"][index].name
                break
    
    # Reverse the routing table to get the forward path starting from inital vertex to final vertex
    routing_table = dict(reversed(list(routing_table.items())))

    with open("routing_table.json", "w") as outfile:
        json.dump(routing_table, outfile)


##################################
# Driver program
##################################
def driver (args):
    # Get the docker client to execute docker commands
    # Lets you do anything the docker command does, but from within Python apps.
    try:
        docker_client = docker.from_env()
    except:
        print ("Exception occured in getting the docker client")
    
    # Get all the networks data
    try:
        networks = docker_client.networks.list()
        services = docker_client.services.list()

        # Get Network IDs
        network_ids = []
        for network in networks:
            network_ids.append(network.id)
        
        # Get all services, service IDs:
        # Target specific services with service_unique_idexpr.
        my_services = []
        my_service_ids = set()
        for service in services:
            if service.name.startswith(args.srvuniqueid):
                my_services.append(service)
                my_service_ids.add(service.id)
    except:
        print ("Exception occured while trying to acquire network data")
    
    # Generate some useful maps from network data
    try:
        file = open('network_data.json') # consists of network and node IDs info
        network_data = json.load(file)
        service_and_neighbours, service_and_networks = get_service_to_network_neighbours_map(my_services)
        networks_and_service= network_and_service_mapping(network_data, service_and_networks)
        networks_and_cost = network_and_cost_mapping(network_data, 1)
        # networks_and_cost = network_and_latency_cost_mapping(network_data)
        service_and_ip = service_and_ip_mapping(my_services)
    except:
         print ("Exception occured while trying generating maps")

    # Calculate shortest path
    try: 
        dijkstras =  dijkstras_shortest_path (
                        service_and_neighbours, 
                        networks_and_service, 
                        networks_and_cost, 
                        source_vertex=args.innode
                    )
    except:
        print ("Exception occured while calculating shortest path")
    
    # Generate routing table
    try: 
        generate_routing_table(dijkstras, args.innode, args.finalnode, service_and_ip)
    except:
        print ("Exception occured while generating routing tables")
    
    from netifaces import interfaces, ifaddresses, AF_INET

    def ip4_addresses():
        ip_list = []
        for interface in interfaces():
            for link in ifaddresses(interface)[AF_INET]:
                print(link)

        # for interface in interfaces():
        #     for link in ifaddresses(interface)[AF_INET]:
        #         ip_list.append(link['addr'])
        return ip_list
    
    print(ip4_addresses())


##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-s", "--srvuniqueid", default="jay", help="Service unique identification expression")
    parser.add_argument ("-i", "--innode", default="jay_client", help="Starting node for calculating shortest path")
    parser.add_argument ("-f", "--finalnode", default="jay_server", help="Final node for which we need shortest path")

    args = parser.parse_args ()

    return args

#------------------------------------------
# main function
def main ():
    """ Main program """

    banner1 = pyfiglet.figlet_format("Jay Maharaj")
    banner2 = pyfiglet.figlet_format("SDN Controller Engine")
    print(banner1)
    print(banner2)
    print("SDN Controller initialized...")

    # parse the command line args
    parsed_args = parseCmdLineArgs ()

    # start the driver code
    driver (parsed_args)

#----------------------------------------------
if __name__ == '__main__':
    main ()