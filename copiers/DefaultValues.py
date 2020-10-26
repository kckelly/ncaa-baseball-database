"""
This file adds default values for the tables that need them in the database.

@author: Kevin Kelly
"""
import ncaadatabase


def insert_default_conferences(database: ncaadatabase):
    """
    Insert the default values for the conference table. This includes the default conference and
    3 conferences for Independent teams at each division.
    
    :param database: the ncaa database
    :return: None
    """
    cursor = database.cursor
    cursor.execute('SELECT * '
                   'FROM conference '
                   'WHERE conference.name = %s;', [ncaadatabase.DEFAULT_CONFERENCE_NAME])
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO conference(name, division) '
                       'VALUES(%s, NULL),'
                       '      (\'Independent\', 1),'
                       '      (\'Independent\', 2),'
                       '      (\'Independent\', 3);', [ncaadatabase.DEFAULT_CONFERENCE_NAME])
