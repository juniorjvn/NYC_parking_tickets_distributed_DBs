import os
from CreateDBConnections import create_postgres_connection


# Violations records from all databases
# will be store in a Postgresql tables - global_violations

# Information about database
database = 'nyc_open_data_manhattan'
table_name = 'global_violations'
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')

# Connect to the nyc_open_data_manhattan and create global_violations table
conn = create_postgres_connection(user=user, password=password, database=database)
cur = conn.cursor()

create_violations_table_stm = '''
CREATE TABLE IF NOT EXISTS global_violations(
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
print('\nThe table global_violations was successfully created.\n')

# We will constantly search for records using dates as reference,
# so, need to create a index on issue_date to speed up the data retrieval
cur.execute('''CREATE INDEX ixg_date ON global_violations(issue_date);''')
conn.commit()
conn.close()
print('Index ixg_date was successfully created for issue_date column in violations table.')





