"""
File to get each school's ID from https://stats.ncaa.org/game_upload/team_codes.
"""
import unicodecsv

import WebUtils

def get_school_ids():
    url = 'https://stats.ncaa.org/game_upload/team_codes'
    page = WebUtils.get_page(url, 0.5, 10)
    
    # selects the school name and id from each row in the school code table
    school_ids = [[col.select('td')[1].text, col.select('td')[0].text]
                  for col in [row for row in page.select_one('table').select('tr')[2:]]]
    
    header = ['school', 'id']
    file_name = 'scraped-data/school_ids.csv'
    with open(file_name, 'wb') as file:
        writer = unicodecsv.writer(file)
        writer.writerow(header)
        writer.writerows(school_ids)
