import os
import requests
import psycopg2
from datetime import datetime
from CreateDBConnections import create_postgres_connection


# Manhattan violations records - 2021
# will be store in a Postgresql database
borough = 'NY'  # Manhattan
borough_id = 1
year = '2021'
# Set the number of row to be inserted into the table
# total records in 2021 - > 3638036
limit = 3638036

# NYC Open Data API + query
base_api = 'https://data.cityofnewyork.us/resource/nc67-uf89.json?'
select_query = '$SELECT=plate,state,county,license_type,summons_number,issue_date,violation_time,violation,fine_amount,penalty_amount,interest_amount,reduction_amount,issuing_agency,violation_status,summons_image'
where_query = '&$WHERE=contains(issue_date,"{}") AND county="{}"&$limit={}'
api = base_api + select_query + where_query.format(year, borough, limit)


# Information about database
database = 'nyc_open_data_manhattan'
table_name = 'violations'
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')

# Connect to the nyc_open_data_manhattan and create a table
conn = create_postgres_connection(user=user, password=password, database=database)
cur = conn.cursor()

create_violations_table_stm = '''
CREATE TABLE IF NOT EXISTS violations(
    summons_number BIGSERIAL,
    state VARCHAR(2),
    county INTEGER,
    plate VARCHAR(10),
    license_type VARCHAR (3),
    issue_date DATE,
    violation_time TIME,
    violation VARCHAR(50),
    fine_amount FLOAT,
    penalty_amount FLOAT,
    interest_amount FLOAT,
    reduction_amount FLOAT,
    issuing_agency VARCHAR(40),
    violation_status VARCHAR(30),
    summons_image TEXT,
    PRIMARY KEY(summons_number)
);
'''
cur.execute(create_violations_table_stm)
conn.commit()
print('\nThe table violations was successfully created.\n')

# request data from NYC Open Data api
print("Retrieving data...")
response = requests.get(api)

# If data cannot be retrieved, the program will exit
if response.status_code != 200:
    print("Error code", response.status_code, api)
    exit()

insert_stm = '''
INSERT INTO violations({}) VALUES({}) ON CONFLICT DO NOTHING;
'''

parking_cam_violations = response.json()

if parking_cam_violations:
    print("Inserting new records into violations table...")

# Inserting records into Table
for violation in parking_cam_violations:
    columns = ','.join(list(violation.keys()))
    placeholder = ', '.join(['%s'] * len(violation))
    if violation.get('violation_time'):
        v_time = violation['violation_time'].replace('.', '0') + 'M'
        try:
            v_time = datetime.strptime(v_time, '%I:%M%p').time()
            violation['violation_time'] = str(v_time)
        except:
            violation['violation_time'] = '00:00:00'
    if violation.get('county'):
        violation['county'] = borough_id
    if violation.get('summons_image'):
        violation['summons_image'] = violation['summons_image']['url']
    try:
        cur.execute(insert_stm.format(columns, placeholder), tuple(violation.values()))
    except psycopg2.Error as e:
        conn.rollback()
        # conn.close()
        print('Error inserting values {} into Postgresql DB.'.format(violation))
        print('Error:', e)
        # exit()
conn.commit()
print('\nParking and Camera violation records were successfully inserted.')

# We will constantly search for records using dates as reference,
# so, need to create a index on issue_date to speed up the data retrieval
cur.execute('''CREATE INDEX ix_date ON violations(issue_date);''')
conn.commit()
conn.close()
print('Index ix_date was successfully created for issue_date column in violations table.')





