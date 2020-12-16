import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

text = input('Are you sure you want to delete database? WARNING: This will remove all data in the database.(y/n)')
if text.lower() != 'y':
    print('Input other than y received, cancelling deletion of database and exiting.')
    exit(0)

connection = psycopg2.connect(user=os.getenv('NCAABaseballUser'),
                              password=os.getenv('NCAABaseballPassword'),
                              host='localhost',
                              port=5432,
                              database='postgres')

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor = connection.cursor()

cursor.execute('DROP DATABASE IF EXISTS ncaa_baseball')
