"""
File to copy conferences scraped by ConferenceStats to the database.

@author: Kevin Kelly
"""
import unicodecsv

from jmu_baseball_utils import file_utils
from database_files.ncaa_database import NCAADatabase


def copy_conferences(database: NCAADatabase, year, division):
    """
    Copy the conference list created by get_conference_stats() into the database.
    
    :param database: the ncaa database
    :param year: the year of the conference file
    :param division: the division of the conference file
    :return: None
    """
    print('Copying conferences... ', end='')
    
    database_conferences = set([conference['name'] for conference in
                                database.get_all_conferences() if conference['division'] == division])
    
    # get new conferences from this year and division
    new_conferences = []
    conference_file_name = file_utils.get_scrape_file_name(year, division, 'conferences')
    with open(conference_file_name, 'rb') as conference_file:
        conference_reader = unicodecsv.DictReader(conference_file)
        for conference in conference_reader:
            if 'Independent' in conference['conference_name']:
                continue
            if division == 1 and conference['conference_name'] == 'Mountain West':
                conference['conference_name'] = 'MWC'
            if division == 3 and conference['conference_name'] == 'MWC':
                conference['conference_name'] = 'Midwest Conference'
            if conference['conference_name'] not in database_conferences:
                new_conferences.append({'conference_name': conference['conference_name'],
                                        'division': division})
    
    header = ['conference_name', 'division']
    database.copy_expert('conference(name, division)', 'conferences', header, new_conferences)
    
    print('{} new conferences.'.format(len(new_conferences)))
