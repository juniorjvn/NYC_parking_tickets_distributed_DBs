import os
import json
import asyncio
import sqlite3
import websockets
import netifaces
import datetime
from decimal import Decimal
from CreateDBConnections import create_sqlite_connection


DBMS = 'SQLite3-Queens'
port = 8764
database = os.environ.get('SQLITE_DB_PATH')
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
        WHERE issue_date BETWEEN ? AND ?
        ORDER BY issue_date;
        '''
        cur = connection.cursor()
        violation_records = None

        try:
            start_date = datetime.datetime.strptime(date_range[0], '%m/%d/%Y').date()
            end_date = datetime.datetime.strptime(date_range[1], '%m/%d/%Y').date()

            cur.execute(query, (start_date, end_date))
            violation_records = cur.fetchall()
        except sqlite3.OperationalError as e:
            print("Error operating on SQLite database: ", e)

        sqlite_data = {'dbms': DBMS, 'port': port, 'data': violation_records}
        dmp_sqlite_data = json.dumps(sqlite_data, default=default)
        b_sqlite_data = dmp_sqlite_data.encode('utf-8')
        await websocket.send(b_sqlite_data)
        print('Total bytes out: {}'.format(len(b_sqlite_data)))

ip_addr = netifaces.ifaddresses(netifaces.interfaces()[6])[2][0]['addr']

connection = create_sqlite_connection(path=database)
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