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
    for service in my_services:
        service_networks[service] = [dictionary["Target"] for dictionary in service.attrs["Spec"]["TaskTemplate"]["Networks"]]
        print(service_networks, "\n")

get_service_map(my_services)