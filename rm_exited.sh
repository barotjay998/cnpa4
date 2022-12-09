#!/bin/sh
docker rm $(docker ps --filter status=exited -q)
