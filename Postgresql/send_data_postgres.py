import os
import json
import asyncio
import websockets
import netifaces
import datetime
from decimal import Decimal
import psycopg2
from CreateDBConnections import create_postgres_connection


DBMS = 'Postgresql-Manhattan'
port = 8761
database = 'nyc_open_data_manhattan'
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')
connection = None


def default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, datetime.timedelta):
        obj_time = (datetime.datetime.min + obj).time()
        return obj_time.isoformat()
    else:
        return None


async def send_data(websocket):
    global connection
    while True:
        try:
            b_date_range = await websocket.recv()
            date_range = json.loads(b_date_range.decode('utf-8'))
            r_addr = websocket.remote_address[0]
            print("{} requested data segment from {} to {}...".format(r_addr, date_range[0], date_range[1]))
        except websockets.ConnectionClosed:
            break

        query = '''
        SELECT * FROM violations
        WHERE issue_date BETWEEN %s AND %s
        ORDER BY issue_date;
        '''
        cur = connection.cursor()
        violation_records = None
        try:
            cur.execute(query, (date_range[0], date_range[1]))
            violation_records = cur.fetchall()
        except psycopg2.Error as e:
            print("Error operating on Postgres database: ", e)

        postgres_data = {'dbms': DBMS, 'port': port, 'data': violation_records}
        dmp_postgres_data = json.dumps(postgres_data, default=default)
        b_postgres_data = dmp_postgres_data.encode('utf-8')
        await websocket.send(b_postgres_data)
        print('Total bytes out: {}'.format(len(b_postgres_data)))

ip_addr = netifaces.ifaddresses(netifaces.interfaces()[6])[2][0]['addr']

connection = create_postgres_connection(user=user, password=password, database=database)
start_server = websockets.serve(send_data, ip_addr, port)

print("Activated {} on {} port {}...".format(DBMS, ip_addr, port))

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    print('Program interrupted by user...')
    pass
finally:
    print('Client closing...')
    connection.close()
    asyncio.get_event_loop().close()