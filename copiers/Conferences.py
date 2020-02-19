"""
File to copy conferences scraped by ConferenceStats to the database.
"""
import unicodecsv

import Database
import FileUtils


def copy_conferences(year, division):
    """
    Copy the conference list created by get_conference_stats() into the database.
    
    :param year: the year of the conference file
    :param division: the division of the conference file
    :return: None
    """
    print('Copying conferences... ', end='')
    
    current_conferences = set([conference['name'] for conference in Database
                              .get_all_conferences()])
    
    # get new conferences from this year and division
    new_conferences = []
    original_conference_file_name = FileUtils.get_scrape_file_name(year, division, 'conferences')
    with open(original_conference_file_name, 'rb') as original_conference_file:
        conference_reader = unicodecsv.DictReader(original_conference_file)
        for conference in conference_reader:
            if conference['conference_name'] not in current_conferences:
                new_conferences.append({'conference_name': conference['conference_name'],
                                        'division':        division})
    
    copy_conference_file_name = FileUtils.get_copy_file_name('conferences')
    with open(copy_conference_file_name, 'wb') as copy_conference_file:
        conference_writer = unicodecsv.DictWriter(copy_conference_file, ['conference_name',
                                                                         'division'])
        conference_writer.writeheader()
        conference_writer.writerows(new_conferences)
    
    Database.copy_expert('conference(name, division)', copy_conference_file_name)
    
    print('{} new conferences.'.format(len(new_conferences)))
