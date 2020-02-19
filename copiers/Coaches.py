"""
File to copy coaches scraped by TeamInfo to the database.
"""
import unicodecsv

import Database
import FileUtils


def copy_coaches(year, division):
    """
    Copy the coach list created by get_team_info() into the database.

    :param year: the year of the coach file
    :param division: the division of the coach file
    :return: None
    """
    print('Copying coaches... ', end='')
    
    current_coaches = set([(coach['ncaa_id'], coach['first_name'], coach['last_name']) for coach in
                           Database.get_all_coaches()])
    
    # get new coaches from this year and division
    new_coaches = []
    original_coach_file_name = FileUtils.get_scrape_file_name(year, division, 'coaches')
    with open(original_coach_file_name, 'rb') as original_coach_file:
        coach_reader = unicodecsv.DictReader(original_coach_file)
        for coach in coach_reader:
            if coach['coach_name'] != '':
                first_name = coach['coach_name'].split(' ')[0]
                last_name = coach['coach_name'].split(' ')[1]
                if (int(coach['coach_id']), first_name, last_name) not in current_coaches:
                    new_coaches.append({'ncaa_id': coach['coach_id'],
                                        'first_name': first_name,
                                        'last_name': last_name,
                                        'alma_mater': coach['alma_mater'],
                                        'year_graduated': coach['year_graduated']})
    
    copy_coach_file_name = FileUtils.get_copy_file_name('coaches')
    with open(copy_coach_file_name, 'wb') as copy_coach_file:
        coach_writer = unicodecsv.DictWriter(copy_coach_file, ['ncaa_id', 'first_name',
                                                               'last_name', 'alma_mater',
                                                               'year_graduated'])
        coach_writer.writeheader()
        coach_writer.writerows(new_coaches)
    
    Database.copy_expert('coach(ncaa_id, first_name, last_name, alma_mater, year_graduated)',
                         copy_coach_file_name)
    
    print('{} new coaches.'.format(len(new_coaches)))
