# This demo works when using Sentio as part of the demo compose.yaml provided.
# It will copy over some intensive task for container sql1 to handle. This will
# increase the CPU usage which will be reported on the Grafana. Our prediction
# service will then try to predict the CPU usage in advance. This is also
# displayed on the graph.

container=sql1
user=sa
password=password
script=CPU_Sadness.sql

# Copy over the program
docker cp ./$script $container:/opt/mssql-tools18/bin/$script
docker update $container --cpus 5.00

# Start the CPU heavy process
docker exec -d $container bash -c "/opt/mssql-tools18/bin/sqlcmd -S localhost -U $user -P '$password' -i /opt/mssql-tools18/bin/$script -No"

# Open Grafana
open http://localhost:3000/d/3MpPHQhVZ

docker stats
