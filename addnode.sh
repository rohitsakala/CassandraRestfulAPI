#!/bin/sh

# Firstly to install the packages on the machine

# Cassandra
wget http://downloads.datastax.com/community/dsc-cassandra-2.1.11-bin.tar.gz
tar -xzf dsc-cassandra-2.1.11-bin.tar.gz
echo "Successfully installed Cassandra"

# Edit the file to deploy the node in the cluster 
sed -i.bak 's/Test Cluster/rohitsakala/g' /home/$1/dsc-cassandra-2.1.11/conf/cassandra.yaml
sed -i.bak 's/127.0.0.1/10.1.36.68/g' /home/$1/dsc-cassandra-2.1.11/conf/cassandra.yaml
sed -i.bak 's/rpc_address: localhost/rpc_address: 0.0.0.0/g' /home/$1/dsc-cassandra-2.1.11/conf/cassandra.yaml
sed -i.bak 's/localhost/'$(hostname -I | cut -d' ' -f1)'/g' /home/$1/dsc-cassandra-2.1.11/conf/cassandra.yaml
sed -i.bak 's/# broadcast_rpc_address: 1.2.3.4/broadcast_rpc_address: 1.2.3.4/g' /home/$1/dsc-cassandra-2.1.11/conf/cassandra.yaml
sed -i.bak 's/endpoint_snitch: SimpleSnitch/endpoint_snitch: RackInferringSnitch/g' /home/$1/dsc-cassandra-2.1.11/conf/cassandra.yaml

# Start casssandra
cd /home/$1/dsc-cassandra-2.1.11/
bin/cassandra &






