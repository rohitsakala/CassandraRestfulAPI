from flask import Flask,request
from flask import render_template
from flask import jsonify
from flask.ext.mongoengine import MongoEngine
from pymongo import read_preferences
from flask.ext.mongoengine.wtf import model_form
import json
import libvirt
import os
import sys
from sh import ssh


######## Cassandra Import Statements ###########
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

app = Flask(__name__)

@app.route('/')
def index():
	return "Cloud Main Project - Exposing Cassandra Data Tables are Restful API's"

####################### Code related to KeySpace Operations #######################

@app.route('/keyspaces/', methods=['GET'])
def getKeyspaces():
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select keyspace_name from schema_keyspaces')
	keyspaces={}
	for x in range(len(rows)):
	    keyspaces[x + 1] = rows[x][0]
	return jsonify(keyspaces=keyspaces)

@app.route('/keyspaces/<keyspaceid>', methods=['GET'])
def getKeyspaceInfo(keyspaceid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	if int(keyspaceid) <= (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		info['replication_factor'] = rows[int(keyspaceid) -1][3]
		info['replication_factor'] = json.loads(info['replication_factor'])['replication_factor']
		print rows
		return jsonify(keyspace=info)
	else:
		return jsonify(error="Not a valid keyspaceid")

@app.route('/keyspaces/', methods=['POST'])
def createKeyspace():
	data = request.data
	dataDict = json.loads(data)
	name = dataDict['name']
	replicationFactor = dataDict['replicationFactor']
	if name == None or replicationFactor ==  None:
		return jsonify(error="Required fields not recieved")
	else:
		cluster = Cluster()
		session = cluster.connect()
		query = "CREATE KEYSPACE " + name + " WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor': " + replicationFactor + " }"
		session.execute(query)
		return jsonify(status="Success")

@app.route('/keyspaces/<keyspaceid>', methods=['PUT'])
def updateKeyspace(keyspaceid):
	data = request.data
	dataDict = json.loads(data)
	replicationFactor = dataDict['replicationFactor']
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select keyspace_name from schema_keyspaces')
	if int(keyspaceid) <= (len(rows) + 1) and int(keyspaceid) > 0:
		strategy_options = "{'replication_factor': " + replicationFactor + " }"
		query = "ALTER KEYSPACE " + rows[int(keyspaceid) -1][0] + " WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : " + replicationFactor + " }"
		session.execute(query)
		return jsonify(status="Success")
	else:
		return jsonify(error="Not a valid keyspaceid")

@app.route('/keyspaces/<keyspaceid>', methods=['DELETE'])
def deleteKeyspace(keyspaceid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select keyspace_name from schema_keyspaces')
	if int(keyspaceid) <= (len(rows) + 1) and int(keyspaceid) > 0:
		query = "DROP KEYSPACE " + rows[int(keyspaceid) -1][0]
		session.execute(query)
	 	return jsonify(status="Success")
	else:
		return jsonify(error="Not a valid keyspaceid")

######################### Code related to adding machine to the cluster or increasing the nodes of the cluster #####################

@app.route('/nodes/', methods=['GET'])
def getNodes():
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select listen_address from local')
	info = {}
	c = 0
	for x in range(len(rows)):
		info[c+1] = rows[x][0]
		c=c+1
	rows = session.execute('select peer from peers')
	for x in range(len(rows)):
		info[c+1] = rows[x][0]
		c=c+1
	return jsonify(Info=info)

@app.route('/nodes/<nodeid>', methods=['GET'])
def getNode(nodeid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select listen_address from local')
	info = {}
	c = 0
	for x in range(len(rows)):
		info[c+1] = rows[x][0]
		c=c+1
	rows = session.execute('select peer from peers')
	for x in range(len(rows)):
		info[c+1] = rows[x][0]
		c=c+1
	if int(nodeid) <= c and int(nodeid) > 0:
		data = {}
		data['name'] = info[int(nodeid)]
		return jsonify(Data=data)
	else:
		return jsonify(error="No such nodeid")

@app.route('/nodes/', methods=['POST'])
def createNode():
	cluster = Cluster()
	session = cluster.connect('system')
	data = request.data
	dataDict = json.loads(data)
	ip = dataDict['ip']
	password = dataDict['password']
	username = dataDict['username']
	os.system("sshpass -p '" + password + "' scp addnode.sh " + username + "@" + ip + ":/home/" + username + "/")
	os.system("sshpass -p '" + password + "' ssh " + username + "@" + ip + " 'echo " + password + " | bash addnode.sh " + username + "'")
	return "success"

if __name__ == '__main__':
	app.run(debug=True)
