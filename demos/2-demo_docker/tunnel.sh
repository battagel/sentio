#!/bin/bash

# This script is intended to be run on a locally running machine in order to
# port-forward certain ports from a remote host. This means you can access the
# Grafana, Prometheus, and Sentio GUIs/APIs on your local machine.
#
# You must set the following environment variables:
# SENTIO_SSH_HOST: Address of the host
# SENTIO_SSH_USER: User on the host
# SENTIO_SSH_PASSWORD: Password for the user

# Ensure required environment variables are set
if [[ -z "$SENTIO_SSH_HOST" ]]; then
    echo "Error: SENTIO_SSH_HOST environment variable is not set!"
    exit 1
fi
if [[ -z "$SENTIO_SSH_USER" ]]; then
    echo "Error: SENTIO_SSH_USER environment variable is not set!"
    exit 1
fi
if [[ -z "$SENTIO_SSH_PASSWORD" ]]; then
    echo "Error: SENTIO_SSH_PASSWORD environment variable is not set!"
    exit 1
fi

# List of ports to forward
PORTS=(3000 8000 9090)

# The function to run the ssh command using expect to pass the password
ssh_tunnel() {
    local port=$1
    /usr/bin/expect <<EOF
    spawn ssh -f -N -L $port:localhost:$port $SENTIO_SSH_USER@$SENTIO_SSH_HOST
    expect "password:"
    send "$SENTIO_SSH_PASSWORD\r"
    expect eof
EOF
}

# Establish SSH tunnels in the background
for PORT in "${PORTS[@]}"; do
    ssh_tunnel $PORT &
done

echo "All tunnels established in the background!"
