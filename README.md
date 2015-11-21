# CassandraRestfulAPI
=====================

## Description

**CassandraRestfulAPI** project exposes the cassandra data tables with the help of Restful API's. The project follows the standard Restful API rules. This project is developed as Major project of the Cloud Computing course by Team 15. The project is developed using Python Driver provided by Datastax using Flask framework.

## Installation

### Flask

<code>$ sudo pip install Flask</code>

### Cassandra

Follow these steps to install python cassandra driver [Python Driver Cassandra](https://datastax.github.io/python-driver/installation.html)

## API's

## Nodes

### List all the nodes

<code> [GET] http://127.0.0.1:5000/nodes/ </code>

### Creates a new node

<code> [POST] http://127.0.0.1:5000/nodes/ </code>

##### Body

        * { 'username' : <usernamename> , 'password' : <password>, 'ip' : <ip> }

## Keyspaces

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
