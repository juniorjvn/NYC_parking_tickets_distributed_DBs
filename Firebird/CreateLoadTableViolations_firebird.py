import os
import requests
import firebirdsql
from datetime import datetime
from CreateDBConnections import create_firebird_connection


# Staten Island violations records - 2021
# will be store in a firebird database
borough = 'ST'
borough_id = 5
year = '2021'
# Set the number of row to be inserted into the table
# total records in 2021 - > 371634
limit = 371634

# NYC Open Data API + query
base_api = 'https://data.cityofnewyork.us/resource/nc67-uf89.json?'
select_query = '$SELECT=plate,state,county,license_type,summons_number,issue_date,violation_time,violation,fine_amount,penalty_amount,interest_amount,reduction_amount,issuing_agency,violation_status,summons_image'
where_query = '&$WHERE=contains(issue_date,"{}") AND county="{}"&$limit={}'
api = base_api + select_query + where_query.format(year, borough, limit)


# Information about database
database = os.environ.get('FB_DB_PATH')
table_name = 'violations'
user = os.environ.get('FB_DB_USER')
password = os.environ.get('DB_PASS')

# Connect to the nyc_open_data_staten_island database  and create a table
conn = create_firebird_connection(user=user, password=password, database=database)
cur = conn.cursor()

create_violations_table_stm = '''
CREATE TABLE violations(
    summons_number BIGINT NOT NULL,
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
    summons_image VARCHAR(200),
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

insert_stm = '''UPDATE OR INSERT INTO violations({}) VALUES({});'''

parking_cam_violations = response.json()

if parking_cam_violations:
    print("Inserting new records into violations table...")

# Inserting records into Table
# Firebird cannot allocate more than 65k handles for statement, transaction,
# blob or request in a single connection.
# Thus, we will insert 64k records and close the connection, then connect to our firebird db again
# insert another 64k records, and so on
for i in range(0, limit, 64000):
    for violation in parking_cam_violations[i:i+64000]:
        # ignore records with invalid dates
        valid_date = ''
        try:
            valid_date = datetime.strptime(violation['issue_date'], '%m/%d/%Y').date()
        except:
            valid_date = None

        if valid_date:
            columns = ','.join(list(violation.keys()))
            placeholder = ', '.join(['?'] * len(violation))
            violation['issue_date'] = valid_date

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
            except firebirdsql.OperationalError as e:
                conn.rollback()
                # conn.close()
                print('Error inserting values {} into FireBird DB.'.format(violation))
                print('Error:', e)
                # exit()
    conn.commit()
    conn.close()
    conn = create_firebird_connection(user=user, password=password, database=database, messages=False)
    cur = conn.cursor()

print('\nParking and Camera violation records were successfully inserted.')

# We will constantly search for records using dates as reference,
# so, need to create a index on issue_date to speed up the data retrieval
cur.execute('''CREATE INDEX ix_date ON violations(issue_date);''')
conn.commit()
conn.close()
print('Index ix_date was successfully created for issue_date column in violations table.')