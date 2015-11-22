from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.query import SimpleStatement
from threading import Event, Lock, Thread

cluster = Cluster()
session = cluster.connect('system')
query = "SELECT * FROM local"  # users contains 100 rows
statement = SimpleStatement(query, fetch_size=10)
for user_row in session.execute(statement):
    print user_row
