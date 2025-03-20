# Demo 3

This demo is much like demo 3 but using a real world data coming from an SDS
storage device. Unfortunately this means I need to hide the compose.yaml file as
it contains sensitive deployment information (see .gitignore).

## Launching the Demo

``` sh
docker compose up -d

./demo.sh
```

This will open the Grafana page for you to monitor the CPU usage.

## Tunnels

In order to use the GUI/APIs from the remote machine you must port-forward all
relevant ports. A script has been provided to make this as easy as possible.

``` sh
./tunnel.sh
```

To bring down the port forwarding, use:
``` sh
./tunnel_stop.sh
```

## Bringing Down the Demo

``` sh
docker compose down
```

Optionally, you can delete all backing data from the demo

``` sh
docker volume prune
```
