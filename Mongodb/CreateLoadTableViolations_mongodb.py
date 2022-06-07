import requests
from pymongo import MongoClient
from pymongo import errors
from datetime import datetime


# Brooklyn violations records - 2021
# will be store in a MongoDB database
borough = 'BK'
borough_id = 3
year = '2021'
# Set the number of row to be inserted into the table
# total records in 2021 - > 1779940
limit = 1779940

# NYC Open Data API + query
base_api = 'https://data.cityofnewyork.us/resource/nc67-uf89.json?'
select_query = '$SELECT=plate,state,county,license_type,summons_number,issue_date,violation_time,violation,fine_amount,penalty_amount,interest_amount,reduction_amount,issuing_agency,violation_status,summons_image'
where_query = '&$WHERE=contains(issue_date,"{}") AND county="{}"&$limit={}'
api = base_api + select_query + where_query.format(year, borough, limit)


# Information about database
database = 'nyc_open_data_brooklyn'
collection_name = 'violations'

# Connect to the nyc_open_data_brooklyn database and create a collection
client = MongoClient()
brooklyn_db = client[database]
violation_collection = brooklyn_db[collection_name]


print('\nThe collection violations was successfully created.\n')

# request data from NYC Open Data api
print("Retrieving data...")
response = requests.get(api)

# If data cannot be retrieved, the program will exit
if response.status_code != 200:
    print("Error code", response.status_code, api)
    exit()

parking_cam_violations = response.json()

if parking_cam_violations:
    print("Inserting new records into violations table...")

# Inserting documents into collection
for violation in parking_cam_violations:
    # ignore records with invalid dates
    valid_date = ''
    try:
        valid_date = datetime.strptime(violation['issue_date'], '%m/%d/%Y')
    except:
        valid_date = None

    if valid_date:
        violation['issue_date'] = valid_date
        violation['county'] = borough_id
        violation['fine_amount'] = float(violation.get('fine_amount', 0))
        violation['penalty_amount'] = float(violation.get('penalty_amount', 0))
        violation['interest_amount'] = float(violation.get('interest_amount', 0))
        violation['reduction_amount'] = float(violation.get('reduction_amount', 0))
        if violation.get('summons_image'):
            violation['summons_image'] = violation['summons_image']['url']
        try:
            v_time = violation['violation_time'].replace('.', '0') + 'M'
            v_time = datetime.strptime(v_time, '%I:%M%p').time()
            violation['violation_time'] = str(v_time)
        except:
            violation['violation_time'] = '00:00:00'

        try:
            violation_collection.insert_one(violation)
        except errors as e:
            print('Error inserting values {} into mongodb database.'.format(violation))
            print('Error:', e)
            # exit()

print('\nParking and Camera violation records were successfully inserted.')

# We will constantly search for records using summons_id and dates as reference,
# so, need to create a index on summons date and one on issue_date to speed up the data retrieval
# cur.execute('''CREATE INDEX ix_date ON violations(issue_date);''')

violation_collection.createIndex({'summons_number': 1})
violation_collection.createIndex({'issue_date': 1})

client.close()
print('Indexes were successfully created.')
