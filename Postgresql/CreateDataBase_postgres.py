import os
from psycopg2 import extensions
from CreateDBConnections import create_postgres_connection


database = 'nyc_open_data_manhattan'
table_name = 'violations'
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')

conn = create_postgres_connection(user='postgres')
cur = conn.cursor()
autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
conn.set_isolation_level(autocommit)


add_user_stm = '''
DO
$do$
BEGIN
  IF NOT EXISTS (SELECT * FROM pg_user WHERE usename = '{}') THEN
      CREATE USER {} WITH PASSWORD %s;
    END IF;
end
$do$;
'''

cur.execute(add_user_stm.format(user, user), (password, ))
conn.commit()
print('The user "{}" was successfully added to the list of Roles.'.format("*****"))

# conn.set_isolation_level(autocommit)
# conn.autocommit = True
# create_db_stm = '''
# CREATE DATABASE IF {} WITH OWNER {};
# '''
create_db_stm = '''
CREATE DATABASE {} WITH OWNER {};
'''

cur.execute(create_db_stm.format(database, user))
conn.commit()
conn.close()
print('The Database "{}" with owner {} was successfully created'.format(database, "*****"))


