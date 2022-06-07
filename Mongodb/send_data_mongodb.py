import os
import json
import asyncio
import websockets
import netifaces
import datetime
from pymongo import MongoClient
from decimal import Decimal


DBMS = 'Brooklyn-MongoDB'
port = 8763
database = 'nyc_open_data_brooklyn'
collection_name = 'violations'
collection = None


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
    global collection
    while True:
        try:
            b_date_range = await websocket.recv()
            date_range = json.loads(b_date_range.decode('utf-8'))
            r_addr = websocket.remote_address[0]
            print("{} requested data segment from {} to {}...".format(r_addr, date_range[0], date_range[1]))
        except websockets.ConnectionClosed:
            break

        violation_records = list()
        try:
            start_date = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            end_date = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')

            rows = collection.find({'issue_date': {'$gte': start_date, '$lte': end_date}})
            for row in rows:
                violation_table = {'summons_number': None, 'state': None, 'county': None, 'plate': None,
                                   'license_type': None,
                                   'issue_date': None, 'violation_time': None, 'violation': None, 'fine_amount': None,
                                   'penalty_amount': None, 'interest_amount': None, 'reduction_amount': None,
                                   'issuing_agency': None, 'violation_status': None, 'summons_image': None}
                row.pop('_id')
                violation_table.update(row)
                violation_records.append(list(violation_table.values()))
        except Exception as e:
            print("Error operating on Postgres database: ", e)

        mongodb_data = {'dbms': DBMS, 'port': port, 'data': violation_records}
        dmp_mongodb_data = json.dumps(mongodb_data, default=default)
        b_mongodb_data = dmp_mongodb_data.encode('utf-8')
        await websocket.send(b_mongodb_data)
        print('Total bytes out: {}'.format(len(b_mongodb_data)))

ip_addr = netifaces.ifaddresses(netifaces.interfaces()[6])[2][0]['addr']

client = MongoClient()
brooklyn_db = client[database]
collection = brooklyn_db[collection_name]
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
    client.close()
    asyncio.get_event_loop().close()
