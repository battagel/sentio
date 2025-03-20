#!/bin/bash

docker compsoe down
docker volume rm grafana-data
docker volume rm prometheus-data
docker volume rm node0-data
docker volume rm node1-data
