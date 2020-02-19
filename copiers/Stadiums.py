"""
File to copy stadiums scraped by TeamInfo to the database.
"""
import unicodecsv

import Database
import FileUtils


def copy_stadiums(year, division):
    """
    Copy the stadium list created by get_team_info() into the database.

    :param year: the year of the stadium file
    :param division: the division of the stadium file
    :return: None
    """
    print('Copying stadiums... ', end='')
    
    current_stadiums = set([stadium['name'] for stadium in Database.get_all_stadiums()])
    
    # get new stadiums from this year and division
    new_stadiums = []
    original_stadium_file_name = FileUtils.get_scrape_file_name(year, division, 'stadiums')
    with open(original_stadium_file_name, 'rb') as original_stadium_file:
        stadium_reader = unicodecsv.DictReader(original_stadium_file)
        for stadium in stadium_reader:
            if stadium['stadium_name'] != '' and stadium['stadium_name'] not in current_stadiums:
                new_stadiums.append({'stadium_name': stadium['stadium_name'],
                                     'capacity':     stadium['capacity'].replace(',', ''),
                                     'year_built':   stadium['year_built']})
    
    copy_stadium_file_name = FileUtils.get_copy_file_name('stadiums')
    with open(copy_stadium_file_name, 'wb') as copy_stadium_file:
        stadium_writer = unicodecsv.DictWriter(copy_stadium_file, ['stadium_name', 'capacity',
                                                                   'year_built'])
        stadium_writer.writeheader()
        stadium_writer.writerows(new_stadiums)
    
    Database.copy_expert('stadium(name, capacity, year_built)', copy_stadium_file_name)
    
    print('{} new stadiums.'.format(len(new_stadiums)))
