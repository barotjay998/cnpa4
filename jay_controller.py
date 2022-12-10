import docker
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
    service_networks = {} # Stores the networks for each service.
    service_map = {}

    # Get the network list for each service.
    for service in my_services:
        service_networks[service] = [dictionary["Target"] for dictionary in service.attrs["Spec"]["TaskTemplate"]["Networks"]]

    # Assign the key values of the service_map as the service Ids
    for service in service_networks:
        service_map[service] = []
    
    for service in service_networks:
        for network in service_networks[service]:
            for linked_service in service_networks:
                if linked_service == service: 
                    continue
                if network in service_networks[linked_service]:
                    if linked_service not in service_map[service]:
                        service_map[service].append(linked_service)
                    if service not in service_map[linked_service]:
                        service_map[linked_service].append(service)

    return service_map    

print(get_service_map(my_services))