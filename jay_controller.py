import docker
client = docker.from_env() # Lets you do anything the docker command does, but from within Python apps

services = client.services.list()
my_services = []
my_service_ids = set()
for service in services:
    if service.name.startswith('jay'):
        my_services.append(service)
        my_service_ids.add(service.id)

print("All Services: {0}".format(len(my_services)))
print(my_services)

networks = client.networks.list()

graph ={}
network_ids = []
for network in networks:
    network_ids.append(network.id)

print("\n")
print("All Network Ids: {0}".format(len(network_ids)))
print(network_ids)