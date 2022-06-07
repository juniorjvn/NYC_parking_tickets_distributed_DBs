import os
from CreateDBConnections import create_mariadb_connection


database = 'nyc_open_data_bronx'
table_name = 'violations'
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')

conn = create_mariadb_connection(user=user, password=password)
cur = conn.cursor()

cur.execute('''CREATE DATABASE IF NOT EXISTS nyc_open_data_bronx;''')
conn.commit()

conn.close()
print('The Database "{}" was successfully created'.format(database))
