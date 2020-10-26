"""
File to copy all school info to the database.

@author: Kevin Kelly
"""
import unicodecsv

import FileUtils
import WebUtils
from ncaadatabase import NCAADatabase


def copy_schools(database: NCAADatabase):
    """
    Copy the school list created by get_school_ids() into the database. This only includes the
    ncaa_id and school name.
    
    :param database: the ncaa database
    :return: None
    """
    print('Copying schools... ', end='')
    
    database_schools = set([school['ncaa_id'] for school in database.get_all_schools()])
    
    new_schools = []
    school_file_name = '../scraped-data/school_ids.csv'
    with open(school_file_name, 'rb') as school_file:
        school_reader = unicodecsv.DictReader(school_file)
        for school in school_reader:
            if int(school['school_id']) not in database_schools:
                new_schools.append({'school_id': school['school_id'],
                                    'school_name': school['school_name']})
    
    header = ['school_id', 'school_name']
    database.copy_expert('school(ncaa_id, name)', 'schools', header, new_schools)
    
    print('{} new schools.'.format(len(new_schools)))


def add_nicknames_and_urls(database: NCAADatabase, year, division):
    """
    Add nickname and urls for schools from this year and division. Adds any schools not already
    in the database.
    
    :param database: the ncaa database
    :param year: the year for these schools' nicknames and urls
    :param division: the division these schools competed at
    :return: None
    """
    print('Adding nicknames and urls to schools... ', end='')
    
    database_schools = {school['ncaa_id']: {'nickname': school['nickname'], 'url': school['url']}
                        for school in database.get_all_schools()}
    database_schools_by_name = {school['name']: {'ncaa_id': school['ncaa_id'],
                                                 'nickname': school['nickname'],
                                                 'url': school['url']}
                                for school in database.get_all_schools()}
    school_updates = []
    
    new_schools = []
    
    school_file_name = FileUtils.get_scrape_file_name(year, division, 'team_info')
    with open(school_file_name, 'rb') as school_file:
        school_reader = unicodecsv.DictReader(school_file)
        for school in school_reader:
            database_school = database_schools.get(int(school['school_id']))
            if database_school is None:
                database_school = database_schools_by_name.get(school['school_name'])
    
                if database_school is None:
                    new_schools.append({'ncaa_id': school['school_id'],
                                        'name': school['school_name'],
                                        'nickname': school['nickname'],
                                        'url': school['website']})
                else:
                    school['school_id'] = database_school['ncaa_id']
            if database_school is not None and (database_school['nickname'] != school['nickname']
                                                or database_school['url'] != school['website']):
                school_updates.append({'school_ncaa_id': school['school_id'],
                                       'school_nickname': school['nickname'],
                                       'school_url': school['website']})
    cursor = database.cursor
    for new_school in new_schools:
        cursor.execute('INSERT INTO school(ncaa_id, name, nickname, url) '
                       'VALUES(%s, %s, %s, %s);', (new_school['ncaa_id'], new_school['name'],
                                                   new_school['nickname'], new_school['url']))
    
    for update in school_updates:
        cursor.execute('UPDATE school '
                       'SET nickname = %s , url = %s '
                       'WHERE school.ncaa_id = %s', (update['school_nickname'],
                                                     update['school_url'],
                                                     update['school_ncaa_id']))
    
    print('{updates} schools updated.'.format(updates=len(school_updates)))


def add_other_school(database, name, school_ncaa_id):
    """
        Add the school with this ncaa_id to the database. Should only be used
        when a school is not already in the database, which should only be for non-NCAA schools.
        :param database: the ncaa database
        :param name: the name of the school
        :param school_ncaa_id: the ncaa_id of the school
        :return: the school id of the newly added school
        """
    cursor = database.cursor
    
    cursor.execute('INSERT INTO school(ncaa_id, name) '
                   'VALUES(%s, %s) '
                   'RETURNING id', (school_ncaa_id, name))
    school_id = cursor.fetchone()[0]
    
    return school_id


def find_and_add_other_school(database: NCAADatabase, name, team_sport_id):
    """
    Scrape and add the school with this team_sport_id to the database. Should only be used when a
    school is not already in the database, which should only be for non-NCAA schools.
    :param name: the name of the school
    :param team_sport_id: the team_sport_id of the school, acquired from the team link in a box
    score
    :return: the ncaa_id of the newly added school and the school id of the school
    """
    url = 'https://stats.ncaa.org/teams/{}'.format(team_sport_id)
    print(url)
    page = WebUtils.get_page(url, 0.1, 10)
    
    for link in page.select('a'):
        if link.text == 'Team History':
            school_ncaa_id = link.attrs['href'].split('/')[-1]
            break
    return school_ncaa_id, add_other_school(database, name, school_ncaa_id)
