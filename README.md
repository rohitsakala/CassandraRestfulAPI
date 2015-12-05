# CassandraRestfulAPI
=====================

## Description

**CassandraRestfulAPI** project exposes the cassandra data tables with the help of Restful API's. The project follows the standard Restful API rules. This project is developed as Major project of the Cloud Computing course by Team 15. The project is developed using Python Driver provided by Datastax using Flask framework.

## Installation

### Flask

<code>$ sudo pip install Flask</code>

### Cassandra

Follow these steps to install [Cassandra](http://docs.datastax.com/en/cassandra/2.1/cassandra/install/installTarball_t.html)
### Python Cassandra Driver

Follow these steps to install python cassandra driver [Python Driver Cassandra](https://datastax.github.io/python-driver/installation.html)

## API's

## --- Nodes ---

### List all the nodes

<code> [GET] http://127.0.0.1:5000/nodes/ </code>

### Get info of a node

<code> [GET] http://127.0.0.1:5000/nodes/<nodeid> </code>

### Creates a new node

<code> [POST] http://127.0.0.1:5000/nodes/ </code>

##### Body

	* { 'username' : <username> , 'password' : <password>, 'ip' : <ip> }

### Delete a node 

<code> [DELETE] http://127.0.0.1:5000/nodes/<nodeid>

##### Body
	
	* { 'username' : <username> , 'password' : <password> }

## --- Keyspaces ---

### List all the Keyspaces

<code> [GET] http://127.0.0.1:5000/keyspaces/ </code>

### Get Info about a keyspace 

<code> [GET] http://127.0.0.1:5000/keyspaces/<keyspaceid> </code>

### Creates a new keyspace

<code> [POST] http://127.0.0.1:5000/keyspaces/ </code>

##### Body

	* { 'name' : <name> , 'replicationFactor' : <number> }

### Updates the keyspace

<code> [PUT] http://127.0.0.1:5000/keyspaces/<keyspaceid> </code>

##### Body

	* { 'replicationFactor' : <number> }

### Deletes the keyspace

<code> [DELETE] http://127.0.0.1:5000/keyspaces/<keyspaceid> </code>

## ---  Column Family ---

### List all the column families of a keyspace

<code> [GET] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/ </code>

### Get info of a column family

<code> [GET] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/<columnfamilyid> </code>

### Creates a new column family

<code> [POST] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/ </code>

##### Body

	* { 'name' : <name> }

### Delete a column family 

<code> [DELETE] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/<columnfamilyid> <nodeid>

## --- Row Entries ---

### List all the rows

<code> [GET] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/ </code>

### Get Info about a row

<code> [GET] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/<entryname> </code>

### Creates a new row

<code> [POST] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/ </code>

##### Body

	* { 'field1' : <field name> , 'field1_type' : <field data type> .... }

### Deletes the row

<code> [DELETE] http://127.0.0.1:5000/keyspace/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/<entryname> </code>

Note:- 10.1.36.68 is the seed 
Note:- In delete node code, path is the directory where cassandra is installed

