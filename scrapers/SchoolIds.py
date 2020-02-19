"""
File to get each school's ID from https://stats.ncaa.org/game_upload/team_codes.
"""
import unicodecsv

import WebUtils


def get_school_ids():
    """
    Get all school ids from https://stats.ncaa.org/game_upload/team_codes for all divisions,
    regardless if they have a baseball team or not. Makes a csv file called
    'scraped-data/school_ids.csv'.
    :return: None
    """
    url = 'https://stats.ncaa.org/game_upload/team_codes'
    page = WebUtils.get_page(url, 0.1, 10)
    
    # selects the school name and id from each row in the school code table
    school_ids = [[col.select('td')[1].text, col.select('td')[0].text]
                  for col in [row for row in page.select_one('table').select('tr')[2:]]]
    
    extra_schools = [['St. Catharine', '506354'], ['Mid-Continent', '506155'],
                     ['St. Gregory\'s', '506137'], ['Concordia (OR)', '501142'],
                     ['Selma', '504748'], ['LIU Post', '362'], ['AIB College', '506424']]
    school_ids.extend(extra_schools)
    
    header = ['school_name', 'school_id']
    file_name = '../scraped-data/school_ids.csv'
    with open(file_name, 'wb') as file:
        writer = unicodecsv.writer(file)
        writer.writerow(header)
        writer.writerows(school_ids)
