"""
File to copy coaches scraped by TeamInfo to the database.

@author: Kevin Kelly
"""
import unicodecsv

import FileUtils
from ncaadatabase import NCAADatabase


def copy_coaches(database: NCAADatabase, year, division):
    """
    Copy the coach list created by get_team_info() into the database.

    :param year: the year of the coach file
    :param division: the division of the coach file
    :return: None
    """
    print('Copying coaches... ', end='')
    
    database_coaches = set([(coach['ncaa_id'], coach['first_name'], coach['last_name']) for coach in
                            database.get_all_coaches()])
    
    # get new coaches from this year and division
    new_coaches = []
    coach_file_name = FileUtils.get_scrape_file_name(year, division, 'coaches')
    with open(coach_file_name, 'rb') as coach_file:
        coach_reader = unicodecsv.DictReader(coach_file)
        for coach in coach_reader:
            if coach['coach_name'] != '':
                first_name = coach['coach_name'].split(' ')[0]
                last_name = coach['coach_name'].split(' ')[1]
                if (int(coach['coach_id']), first_name, last_name) not in database_coaches:
                    try:
                        coach['year_graduated'] = int(coach['year_graduated'])
                    except ValueError:
                        coach['year_graduated'] = None
                    new_coaches.append({'ncaa_id': coach['coach_id'],
                                        'first_name': first_name,
                                        'last_name': last_name,
                                        'alma_mater': coach['alma_mater'],
                                        'year_graduated': coach['year_graduated']})
    
    header = ['ncaa_id', 'first_name', 'last_name', 'alma_mater', 'year_graduated']
    database.copy_expert('coach(ncaa_id, first_name, last_name, alma_mater, year_graduated)',
                         'coaches', header, new_coaches)
    
    print('{} new coaches.'.format(len(new_coaches)))
