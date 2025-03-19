# Demo 1

This demo will create 2 sql containers and read their CPU usage metrics using
Telegraf. These are then collected via Prometheus and predictions will be made
base on these metrics. A Grafana will also be launched with some useful
visualisations of the predictions and error range

## Launching the Demo

``` sh
docker compose up -d

./demo.sh
```

This will open the Grafana page for you to monitor the CPU usage.

## Bringing Down the Demo

``` sh
docker compose down
```

Optionally, you can delete all backing data from the demo

``` sh
docker volume prune
```
