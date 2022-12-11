#!/bin/bash
IMAGE=192.168.2.61:5000/jay_nwclass

remove old services
docker service rm jay_client
docker service rm jay_server
for ((i=1; i<=5; i++))
do 
  docker service rm jay_router${i}
done

## client
docker service create --name jay_client --cap-add NET_ADMIN --constraint node.hostname==compnw-worker10 --network overlay_nw1 --publish published=30002,target=4444  ${IMAGE}

docker service update --network-add overlay_nw2 jay_client
docker service update --network-add overlay_nw3 jay_client

## Router1
docker service create --name jay_router1 --cap-add NET_ADMIN --constraint node.hostname==compnw-worker1 --network overlay_nw1 --publish published=31005,target=4444  ${IMAGE}

docker service update --network-add overlay_nw4 jay_router1
docker service update --network-add overlay_nw7 jay_router1

## Router2
docker service create --name jay_router2 --cap-add NET_ADMIN --constraint node.hostname==compnw-worker2 --network overlay_nw2 --publish published=31006,target=4444  ${IMAGE}

docker service update --network-add overlay_nw6 jay_router2
docker service update --network-add overlay_nw7 jay_router2
docker service update --network-add overlay_nw8 jay_router2

## Router3
docker service create --name jay_router3 --cap-add NET_ADMIN --constraint node.hostname==compnw-worker3 --network overlay_nw3 --publish published=31007,target=4444  ${IMAGE}

docker service update --network-add overlay_nw5 jay_router3
docker service update --network-add overlay_nw8 jay_router3

## Router4
docker service create --name jay_router4 --cap-add NET_ADMIN --constraint node.hostname==compnw-worker4 --network overlay_nw4 --publish published=31008,target=4444  ${IMAGE}

docker service update --network-add overlay_nw9 jay_router4

## Router5
docker service create --name jay_router5 --cap-add NET_ADMIN --constraint node.hostname==compnw-worker5 --network overlay_nw5 --publish published=31009,target=4444  ${IMAGE}

docker service update --network-add overlay_nw10 jay_router5

## Server
docker service create --name jay_server --cap-add NET_ADMIN --constraint node.hostname==compnw-worker9 --network overlay_nw6 --publish published=30003,target=5555  ${IMAGE}
docker service update --network-add overlay_nw9 jay_server
docker service update --network-add overlay_nw10 jay_server
