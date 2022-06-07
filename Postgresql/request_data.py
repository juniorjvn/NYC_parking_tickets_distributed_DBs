import os
import json
import asyncio
import websockets
import netifaces
import datetime
import time
from decimal import Decimal
from CreateDBConnections import *

db = 'Postgresql'
port = 8765
database = 'nyc_open_data_manhattan'
global_table_name = 'global_violations'
table_name = 'violations'
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')
uris = set()
ip_address = '192.168.1.150'


async def request_data_segment(websocket, connection, start_date, end_date):
    await websocket.send(json.dumps([start_date, end_date]).encode('utf-8'))
    b_data = await websocket.recv()
    r_addr = websocket.remote_address[0]
    received_data = json.loads(b_data.decode('utf-8'))
    print('*' * 80)
    print('Data segment of {} bytes arrived from {}:{} - {}'.format(len(b_data), r_addr, received_data['port'], received_data['dbms']))
    violation_records = received_data['data']
    print_limit = 0
    insert_stm = '''INSERT INTO {} VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
    cur = connection.cursor()
    for record in violation_records:
        try:
            cur.execute(insert_stm.format(global_table_name), record)
            if print_limit < 5:
                print_limit += 1
                print(record)
        except psycopg2.Error as e:
            conn.rollback()
            conn.close()
            print('Error inserting values {} into Postgresql DB.'.format(record))
            print('Error:', e)
            exit()

    connection.commit()
    print('...')
    print('All records from {} were successfully inserted into {} table.\n'.format(received_data['dbms'], global_table_name))


async def handler_socket(uri, connection, start_date, end_date):
    async with websockets.connect(uri, max_size=300000000) as websocket:
        await request_data_segment(websocket, connection, start_date, end_date)


async def request_data(connection, start_date, end_date):
    start = time.perf_counter()
    await asyncio.gather(*[handler_socket(uri, connection, start_date, end_date) for uri in uris])
    finish = time.perf_counter()
    print('Finished in {} seconds.'.format(round(finish - start, 2)))


ip_addr = netifaces.ifaddresses(netifaces.interfaces()[6])[2][0]['addr']
# num = int(input('Enter the total number of connection: '))
# for _ in range(num):
#     ip_port = input('Enter IP:port for connection: ')
#     uris.add('ws://' + ip_port)
ip_port1 = '192.168.1.150:8761'
ip_port2 = '192.168.1.150:8762'
ip_port3 = '192.168.1.150:8763'
ip_port4 = '192.168.1.150:8764'
ip_port5 = '192.168.1.150:8765'
# uris.add('ws://' + ip_port1)
uris.add('ws://' + ip_port2)
uris.add('ws://' + ip_port3)
uris.add('ws://' + ip_port4)
uris.add('ws://' + ip_port5)

start_date = '07/01/2021'
end_date = '07/10/2021'

conn = create_postgres_connection(user=user, password=password, database=database)
print('Activated Postgres at {}...\n'.format(ip_addr))
print('*'*80)
##############
print('Inserting records from local Postgres violation table into Global_violation table...')

insert_stm = '''
INSERT INTO {}
    SELECT * FROM violations
    WHERE issue_date BETWEEN %s AND %s
    ORDER BY issue_date;
'''

try:
    cur = conn.cursor()
    cur.execute(insert_stm.format(global_table_name), (start_date, end_date))
    conn.commit()
except psycopg2.Error as e:
    conn.rollback()
    conn.close()
    print('Error inserting values {} into Postgresql DB.'.format(global_table_name))
    print('Error:', e)
    exit()
print('All records from local Postgresql-Manhattan were successfully inserted into {} table.\n'.format(global_table_name))
#################
try:
    asyncio.get_event_loop().run_until_complete(request_data(conn, start_date, end_date))
    # asyncio.Future()
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    print('Program interrupted by user...')
    pass
finally:
    print('Client closing...')
    print('Removing all records from Global_violations table...')
    cur.execute('TRUNCATE TABLE {};'.format(global_table_name))
    conn.commit()
    conn.close()
    time.sleep(2)
    print('Application closed!')
    asyncio.get_event_loop().close()