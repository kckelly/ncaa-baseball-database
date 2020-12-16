"""
This file adds default values for the tables that need them in the database.

@author: Kevin Kelly
"""
from jmu_baseball_utils import ncaa_database
from database_files.ncaa_database import NCAADatabase


def insert_default_conferences(database: NCAADatabase):
    """
    Insert the default values for the conference table. This includes the default conference and
    3 conferences for Independent teams at each division.
    
    :param database: the ncaa database
    :return: None
    """
    cursor = database.cursor
    cursor.execute('SELECT * '
                   'FROM conference '
                   'WHERE conference.name = %s;', [ncaa_database.DEFAULT_CONFERENCE_NAME])
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO conference(name, division) '
                       'VALUES(%s, NULL),'
                       '      (\'Independent\', 1),'
                       '      (\'Independent\', 2),'
                       '      (\'Independent\', 3);', [ncaa_database.DEFAULT_CONFERENCE_NAME])
