import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connection = psycopg2.connect(user=os.getenv('NCAABaseballUser'),
                              password=os.getenv('NCAABaseballPassword'),
                              host='localhost',
                              port=5432,
                              database='postgres')

connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # <-- ADD THIS LINE

cursor = connection.cursor()

cursor.execute('CREATE DATABASE ncaa_baseball')
