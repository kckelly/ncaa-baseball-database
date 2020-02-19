"""
File to copy schools to the database from the file scraped by SchoolIds.
"""
import unicodecsv

import Database
import FileUtils


def copy_schools():
    """
    Copy the school list created by get_school_ids() into the database.
    
    :return: None
    """
    print('Copying schools... ', end='')
    
    current_schools = set([school['ncaa_id'] for school in Database.get_all_schools()])
    
    new_schools = []
    school_file_name = '../scraped-data/school_ids.csv'
    with open(school_file_name, 'rb') as school_file:
        school_reader = unicodecsv.DictReader(school_file)
        for school in school_reader:
            if int(school['school_id']) not in current_schools:
                new_schools.append({'school_id': school['school_id'],
                                    'school_name': school['school_name']})
                
    copy_school_file_name = FileUtils.get_copy_file_name('schools')
    with open(copy_school_file_name, 'wb') as copy_school_file:
        school_writer = unicodecsv.DictWriter(copy_school_file, ['school_id', 'school_name'])
        school_writer.writeheader()
        school_writer.writerows(new_schools)
    
    Database.copy_expert('school(ncaa_id, name)', copy_school_file_name)
    
    print('{} new schools.'.format(len(new_schools)))
