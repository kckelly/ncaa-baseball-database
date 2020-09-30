"""
File to get each school's ID from https://stats.ncaa.org/game_upload/team_codes.

@author: Kevin Kelly
"""
import unicodecsv

import WebUtils


def get_school_ids():
    """
    Get all school ids from https://stats.ncaa.org/game_upload/team_codes for all divisions,
    regardless if they have a baseball team or not. Creates a csv file called
    'scraped-data/school_ids.csv'.
    :return: None
    """
    url = 'https://stats.ncaa.org/game_upload/team_codes'
    page = WebUtils.get_page(url, 0.1, 10)

    # selects the school name and id from each row in the school code table
    school_ids = [[col.select('td')[1].text, col.select('td')[0].text]
                  for col in [row for row in page.select_one('table').select('tr')[2:]]]

    # these are schools that are most likely NAIA and so do not have a school code, but played
    # games against NCAA schools at some point. They have to be added manually since the school id
    # web page does not include these schools.
    '''extra_schools = [['St. Catharine', 506354], ['Mid-Continent', 506155],
                     ['St. Gregory\'s', 506137], ['Concordia (OR)', 501142],
                     ['Selma', 504748], ['LIU Post', 362], ['AIB College', 506424],
                     ['Newport News', 506016], ['Pacifica, 506349'],
                     ['Lubbock Chrst.', 502820], ['Victory', 506197],
                     ['Virginia Intermont', 505507], ['St. Louis Christian', 504577],
                     ['Briarcliffe (NY)', 506283], ['Northwood (TX)', 506009],
                     ['Concordia Irvine', 501121]]

    school_ids.extend(extra_schools)'''

    file_name = '../scraped-data/school_ids.csv'
    header = ['school_name', 'school_id']
    with open(file_name, 'wb') as file:
        writer = unicodecsv.writer(file)
        writer.writerow(header)
        writer.writerows(school_ids)
