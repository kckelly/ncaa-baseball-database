"""
This file adds default values for the tables that need them in the database.
"""
import Database


def insert_default_values():
    """
    Insert the default values for the conference table. This includes the default conference and
    3 conferences for Independent teams at each division.
    :return: None
    """
    connection = Database.connect()
    cursor = connection.cursor()
    cursor.execute('SELECT * '
                   'FROM conference '
                   'WHERE conference.name = \'Other\';')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO conference(name, division) '
                       'VALUES(\'{conference_name}\', NULL),'
                       '      (\'Independent\', 1),'
                       '      (\'Independent\', 2),'
                       '      (\'Independent\', 3);'.format(conference_name='Other'))
        connection.commit()
    connection.close()
