from flask import Flask,request
from flask import render_template
from flask import jsonify
from flask import redirect
from flask import Blueprint
from flask.ext.paginate import Pagination
from flask.ext.mongoengine import MongoEngine
from pymongo import read_preferences
from flask.ext.mongoengine.wtf import model_form
from math import ceil
import json
import libvirt
import os
import numpy
import sys
from sh import ssh


######## Cassandra Import Statements ###########
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.query import SimpleStatement


app = Flask(__name__)

######## Global Variables #############
PER_PAGE = 10

################ Class for Pagination ###################

from math import ceil

class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num





@app.route('/')
def index():
   	return render_template('index.html')

####################### Code related to KeySpace Operations #######################

@app.route('/keyspaces/', defaults={'page': 1}, methods=['GET'])
@app.route('/keyspaces/page/<int:page>', methods=['GET'])
def getKeyspaces(page):
   	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select keyspace_name from schema_keyspaces')
	keyspaces=[]
	for x in range(len(rows)):
		keyspaces.append(rows[x][0])
    	pages = keyspaces[(page-1)*PER_PAGE:PER_PAGE*page]
    	if not pages and page != 1:
   		abort(404)
    	pagination = Pagination(page, PER_PAGE, len(rows))
   	return render_template('listkeyspace.html',pagination=pagination,pages=pages,section = 'getKeyspaces')

@app.route('/keyspaces/<keyspaceid>', methods=['GET'])
def getKeyspaceInfo(keyspaceid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		info['keyspaceid'] = int(keyspaceid)
		if info['name'] == "system":
			info['replication_factor'] = 0
			return jsonify(keyspace=info)
		info['replication_factor'] = rows[int(keyspaceid) -1][3]
		return render_template('keyspaceinfo.html',info=info)
	else:
		return render_template('error.html',error="Not a valid keyspace")

@app.route('/keyspaces/', methods=['POST'])
def createKeyspace():
	data = request.data
	dataDict = json.loads(data)
	name = dataDict['name']
	replicationFactor = dataDict['replicationFactor']
	if name == None or replicationFactor ==  None:
		return render_template('error.html',error="Not a valid keyspace")
	else:
		cluster = Cluster()
		session = cluster.connect('system')
		query = "CREATE KEYSPACE " + name + " WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor': " + replicationFactor + " }"
		session.execute(query)
		info = {}
		info['name'] = name
		info['replication_factor'] = replicationFactor
		rows = session.execute('select * from schema_keyspaces')
		for x in range(len(rows)):
			if rows[x][0] == name:
				info['keyspaceid'] = x + 1
		return render_template('keyspaceinfo.html',info=info)

@app.route('/keyspaces/<keyspaceid>', methods=['PUT'])
def updateKeyspace(keyspaceid):
	data = request.data
	dataDict = json.loads(data)
	replicationFactor = dataDict['replicationFactor']
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select keyspace_name from schema_keyspaces')
	if rows[int(keyspaceid) - 1][0] == "system":
		return jsonify(error="system keyspace is not modifiable")
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

@app.route('/nodes/', defaults={'page': 1}, methods=['GET'])
@app.route('/nodes/page/<int:page>', methods=['GET'])
def getnodes(page):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select listen_address from local')
	info = []
	c = 0
	for x in range(len(rows)):
		info.append(rows[x][0])
		c=c+1
	rows = session.execute('select peer from peers')
	for x in range(len(rows)):
		info.append(rows[x][0])
		c=c+1
	pages = info[(page-1)*PER_PAGE:PER_PAGE*page]
    	if not pages and page != 1:
   		abort(404)
    	pagination = Pagination(page, PER_PAGE, len(info))
   	return render_template('listnode.html',pagination=pagination,pages=pages,section = 'getNodes')
	

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
		data['nodeid'] = nodeid
		return render_template('nodeinfo.html',info=data)
	else:
		return render_template('error.html',error="Not a valid nodeid")

@app.route('/nodes/', methods=['POST'])
def createNode():
	try:
		cluster = Cluster()
		session = cluster.connect('system')
		data = request.data
		dataDict = json.loads(data)
		ip = dataDict['ip']
		password = dataDict['password']
		username = dataDict['username']
		os.system("sshpass -p '" + password + "' scp addnode.sh " + username + "@" + ip + ":/home/" + username + "/")
		os.system("sshpass -p '" + password + "' ssh " + username + "@" + ip + " 'echo " + password + " | bash addnode.sh " + username + "'")
		return jsonify(status="success")
	except:
		return render_template('error.html',error="Error adding node. Please check the configuration")

@app.route('/nodes/<nodeid>', methods=['DELETE'])
def deleteNode(nodeid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select listen_address from local')
	data = request.data
	dataDict = json.loads(data)
	password = dataDict['password']
	username = dataDict['username']
	info = {}
	host = {}
	c = 0
	h = 0
	for x in range(len(rows)):
		info[c+1] = rows[x][0]
		c=c+1
	h = c
	rows = session.execute('select peer,host_id from peers')
	for x in range(len(rows)):
		info[c+1] = rows[x][0]
		host[c+1] = rows[x][1]
		c=c+1
	if int(nodeid) <= c and int(nodeid) > h:
		os.system("sshpass -p '" + password + "' ssh " + username + "@" + info[int(nodeid)] + " ./dsc-cassandra-2.1.11/bin/nodetool decommission")
		os.system("/home/rohitsakala/dsc-cassandra-2.1.11/bin/nodetool removenode " + str(host[int(nodeid)]))
		return jsonify(status="Success")
	elif int(nodeid) <= h:
		return render_template('error.html',error="host node cannot be deleted")
	else:
		return render_template('error.html',error="No such nodeid")


############################# Code related to Column Family operations ##############################

@app.route('/keyspaces/<keyspaceid>/columnfamilys/', defaults={'page': 1}, methods=['GET'])
@app.route('/keyspaces/<keyspaceid>/columnfamilys/page/<int:page>', methods=['GET'])
def getColumnFamilys(page,keyspaceid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	info = []
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		info = []
		for x in range(len(rows)):
			info.append(rows[x][1])
	else:
		return render_template('error.html',error="Not a valid keyspaceid")
	pages = info[(page-1)*PER_PAGE:PER_PAGE*page]
    	if not pages and page != 1:
   		abort(404)
	pagination = Pagination(page, PER_PAGE, len(info))
   	return render_template('listcolumnfamily.html',pagination=pagination,keyspaceid=keyspaceid,pages=pages,section = 'getColumnFamilys')
		

@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilysid>', methods=['GET'])
def getColumnFamilyInfo(keyspaceid,columnfamilysid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		if int(columnfamilysid) <  (len(rows) + 1) and int(columnfamilysid) > 0:
			info = {}
			info['name'] = rows[int(columnfamilysid)-1][1]
			info['caching'] = rows[int(columnfamilysid)-1][3]
			info['cf_id'] = rows[int(columnfamilysid)-1][4]
			info['columnfamilyid'] = columnfamilysid
			return render_template('columnfamilyinfo.html',info=info,keyspaceid=keyspaceid)
		else:
			return render_template('error.html',error="Not a valid columnfamilyid")
	else:
		return render_template('error.html',error="Not a valid keyspaceid")

@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilysid>', methods=['DELETE'])
def deleteColumnFamily(columnfamilysid,keyspaceid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		if int(columnfamilysid) <  (len(rows) + 1) and int(columnfamilysid) > 0:
			query = "DROP TABLE " + info["name"] + "." + rows[int(columnfamilysid) -1][1]
			session.execute(query)
	 		return jsonify(status="success")
		else:
			return render_template('error.html',error="Not a valid columnfamilyid")
	else:
		return render_template('error.html',error="Not a valid keyspaceid")

@app.route('/keyspaces/<keyspaceid>/columnfamilys/', methods=['POST'])
def createColumnFamily(keyspaceid):
	cluster = Cluster()
	session = cluster.connect('system')
	data = request.data
	dataDict = json.loads(data)
	name = dataDict['name']
	field1 = dataDict['field1']
	field2 = dataDict['field2']
	field3 = dataDict['field3']
	field1_type = dataDict['field1_type']
	field2_type = dataDict['field2_type']
	field3_type = dataDict['field3_type']
	if field1 == None or field2 ==  None or field3 == None or name == None:
		return render_template('error.html',error="Fields are missing")
	else:
		rows = session.execute('select * from schema_keyspaces')
		if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
			cluster = Cluster()
			session = cluster.connect(rows[int(keyspaceid)-1][0])
			query = "CREATE TABLE " + name + "( " + field1 + " " + field1_type + " PRIMARY KEY," + field2 + " " + field2_type  + " ," + field3 + " " + field3_type  + " )"
			session.execute(query)
			return redirect("http://127.0.0.1:5000/keyspaces/" + keyspaceid + "/columnfamilys/")
		else:
			return render_template('error.html',error="Not a valid keyspaceid")	


############################# Code related to Row Entry operations ##############################

@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/', defaults={'page': 1}, methods=['GET'])
@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/page/<int:page>', methods=['GET'])
def getEntrys(page,keyspaceid,columnfamilyid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	info = []
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		keyspacename = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		columnfamilyname = rows[int(columnfamilyid)-1][1]
		session = cluster.connect(rows[int(keyspaceid)-1][0])
		rows = session.execute("SELECT * FROM " + columnfamilyname)
		info = rows
		rows = session.execute("SELECT * FROM system.schema_columns WHERE keyspace_name = '" + keyspacename + "' AND columnfamily_name = '" + columnfamilyname + "'")
		fields = []
		for i in rows:
			fields.append(i)
		temp = fields[len(rows) - 1]
		fields[len(rows) - 1] = fields[0]
		fields[0] = temp
		temp = fields[1]
		fields[1] = fields[2]
		fields[2] = temp
	else:
		return render_template('error.html',error="Not a valid keyspaceid")
	pages = info[(page-1)*PER_PAGE:PER_PAGE*page]
    	if not pages and page != 1:
   		abort(404)
	pagination = Pagination(page, PER_PAGE, len(info))
   	return render_template('listentrys.html',pagination=pagination,keyspaceid=keyspaceid,columnfamilyid=columnfamilyid,pages=pages,fields=fields,section = 'getEntrys')

@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/',methods=['POST'])
def createEntry(keyspaceid,columnfamilyid):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	info = []
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		keyspacename = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		columnfamilyname = rows[int(columnfamilyid)-1][1]
		session = cluster.connect(rows[int(keyspaceid)-1][0])
		data = request.data
		dataDict = json.loads(data)
		fields = dataDict.keys()
		values = []
		for key, value in dataDict.items():
    			values.append(value)
		rows = session.execute("INSERT INTO " + columnfamilyname + " (" + fields[0] + ", " + fields[1] + ", " + fields[2] + ") VALUES('" + values[0] + "', '" + values[1] + "', '" + values[2] + "')") 
	else:
		return render_template('error.html',error="Not a valid keyspaceid")
	return "success"

@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilyid>/entrys/<entryname>', methods=['GET'])
def getEntrysInfo(keyspaceid,columnfamilyid,entryname):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	info = []
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		keyspacename = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		columnfamilyname = rows[int(columnfamilyid)-1][1]
		primarykey = rows[int(columnfamilyid)-1]
		session = cluster.connect(rows[int(keyspaceid)-1][0])
		primarykey = primarykey[17][2:]
		primarykey = primarykey[:-2]
		query = "SELECT * FROM " + columnfamilyname + " WHERE " + primarykey + "='" + entryname + "'"
		rows = session.execute(query)
		info = rows
		query = "SELECT * FROM system.schema_columns WHERE keyspace_name='" + keyspacename + "' AND columnfamily_name = '" + columnfamilyname + "'"
		rows = session.execute(query)
		fields = []
		for i in rows:
			fields.append(i)
		temp = fields[len(rows) - 1]
		fields[len(rows) - 1] = fields[0]
		fields[0] = temp
		temp = fields[1]
		fields[1] = fields[2]
		fields[2] = temp
		return render_template('entryinfo.html',info=info,fields=fields,keyspaceid=keyspaceid,columnfamilyid=columnfamilyid,entryname=entryname)
		

@app.route('/keyspaces/<keyspaceid>/columnfamilys/<columnfamilysid>/entrys/<entryname>', methods=['DELETE'])
def deleteEntry(columnfamilysid,keyspaceid,entryname):
	cluster = Cluster()
	session = cluster.connect('system')
	rows = session.execute('select * from schema_keyspaces')
	info = []
	if int(keyspaceid) < (len(rows) + 1) and int(keyspaceid) > 0:
		info = {}
		info['name'] = rows[int(keyspaceid) -1][0]
		keyspacename = rows[int(keyspaceid) -1][0]
		rows = session.execute("SELECT * FROM schema_columnfamilies where keyspace_name='" + info['name'] + "'")
		columnfamilyname = rows[int(columnfamilysid)-1][1]
		primarykey = rows[int(columnfamilysid)-1]
		session = cluster.connect(rows[int(keyspaceid)-1][0])
		primarykey = primarykey[17][2:]
		primarykey = primarykey[:-2]
		query = "DELETE FROM " + columnfamilyname + " WHERE " + primarykey + "='" + entryname + "'"
		rows = session.execute(query)
		return "success"

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


if __name__ == '__main__':
	app.run(debug=True)
