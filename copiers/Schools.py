"""
File to copy all school info to the database.

@author: Kevin Kelly
"""
import unicodecsv

import Database
import FileUtils


def copy_schools():
    """
    Copy the school list created by get_school_ids() into the database. This only includes the
    ncaa_id and school name.
    
    :return: None
    """
    print('Copying schools... ', end='')
    
    database_schools = set([school['ncaa_id'] for school in Database.get_all_schools()])
    
    new_schools = []
    school_file_name = '../scraped-data/school_ids.csv'
    with open(school_file_name, 'rb') as school_file:
        school_reader = unicodecsv.DictReader(school_file)
        for school in school_reader:
            if int(school['school_id']) not in database_schools:
                new_schools.append({'school_id': school['school_id'],
                                    'school_name': school['school_name']})
    
    # these are schools that are most likely NAIA and so do not have a school code, but played
    # games against NCAA schools at some point. They have to be added manually since the school id
    # web page does not include these schools.
    extra_schools = [['St. Catharine', 506354], ['Mid-Continent', 506155],
                     ['St. Gregory\'s', 506137], ['Concordia (OR)', 501142],
                     ['Selma', 504748], ['LIU Post', 362], ['AIB College', 506424]]
    for school in extra_schools:
        if school[1] not in database_schools:
            new_schools.append({'school_id': school[1],
                                'school_name': school[0]})
    
    header = ['school_id', 'school_name']
    Database.copy_expert('school(ncaa_id, name)', 'schools', header, new_schools)
    
    print('{} new schools.'.format(len(new_schools)))


def add_nicknames_and_urls(year, division):
    """
    Add nickname and urls for schools from this year and division.
    :param year: the year for these schools' nicknames and urls
    :param division: the division these schools competed at
    :return: None
    """
    print('Adding nicknames and urls to schools... ', end='')
    
    database_schools = {school['ncaa_id']: {'nickname': school['nickname'], 'url': school['url']}
                        for school in Database.get_all_schools()}
    
    school_updates = []
    
    school_file_name = FileUtils.get_scrape_file_name(year, division, 'team_info')
    with open(school_file_name, 'rb') as school_file:
        school_reader = unicodecsv.DictReader(school_file)
        for school in school_reader:
            database_school = database_schools.get(int(school['school_id']))
            if database_school is not None and database_school['nickname'] == school['nickname'] \
                    and database_school['url'] == school['website']:
                continue
            school_updates.append({'school_ncaa_id': school['school_id'],
                                   'school_nickname': school['nickname'],
                                   'school_url': school['website']})
    connection = Database.connect()
    cursor = connection.cursor()
    for update in school_updates:
        cursor.execute('UPDATE school '
                       'SET nickname = %s , url = %s '
                       'WHERE school.ncaa_id = %s', (update['school_nickname'],
                                                     update['school_url'],
                                                     update['school_ncaa_id']))
    connection.commit()
    connection.close()
    
    print('{updates} schools updated.'.format(updates=len(school_updates)))
