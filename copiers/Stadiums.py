"""
File to copy stadiums scraped by TeamInfo to the database.

@author: Kevin Kelly
"""
import unicodecsv

from jmu_baseball_utils import file_utils
from database_files.ncaa_database import NCAADatabase


def copy_stadiums(database: NCAADatabase, year, division):
    """
    Copy the stadium list created by get_team_info() into the database.

    :param year: the year of the stadium file
    :param division: the division of the stadium file
    :return: None
    """
    print('Copying stadiums... ', end='')
    
    database_stadiums = set([stadium['name'] for stadium in database.get_all_stadiums()])
    
    # get new stadiums from this year and division
    new_stadiums = []
    stadium_file_name = file_utils.get_scrape_file_name(year, division, 'stadiums')
    with open(stadium_file_name, 'rb') as stadium_file:
        stadium_reader = unicodecsv.DictReader(stadium_file)
        for stadium in stadium_reader:
            if stadium['stadium_name'] != '' and stadium['stadium_name'] not in database_stadiums:
                new_stadiums.append({'stadium_name': stadium['stadium_name'],
                                     'capacity': stadium['capacity'].replace(',', ''),
                                     'year_built': stadium['year_built']})
    
    header = ['stadium_name', 'capacity', 'year_built']
    database.copy_expert('stadium(name, capacity, year_built)', 'stadiums', header, new_stadiums)
    
    print('{} new stadiums.'.format(len(new_stadiums)))
