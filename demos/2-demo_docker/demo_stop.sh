#!/bin./bash

docker compsoe down
docker rm grafana-data
docker rm prometheus-data
docker rm node0-data
docker rm node1-data
