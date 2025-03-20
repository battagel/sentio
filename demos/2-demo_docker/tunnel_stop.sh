#!/bin/bash

# This script will delete all tunnels created in the tunnel.sh script.

echo "Stopping all SSH tunnels..."

pkill -f "ssh -f -N -L"

if [[ $? -eq 0 ]]; then
    echo "All SSH tunnels have been stopped."
else
    echo "No SSH tunnels found or failed to stop."
fi
