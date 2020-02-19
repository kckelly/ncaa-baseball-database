"""
File to scrape from https://stats.ncaa.org/rankings/institution_trends and get each division's
conference stats by year. Makes one file that is used to put conference names into the database and
another that holds stats for verification purposes later.
"""
import unicodecsv

import Database
import FileUtils
import WebUtils

base_url = 'https://stats.ncaa.org/rankings/conference_trends?' \
           'division={division}&id={year_id}&year_stat_category_id={year_stat_id}'
base_file_name = 'conference_{stat_type}_totals'
stat_types = ['hitting', 'pitching', 'fielding']


def get_conference_stats(year, division):
    """
    Scrape the conference totals for hitting, pitching, and fielding into 3 separate csv files.
    Also creates another csv file containing just the names of the conferences for that year and
    division.

    :param year: the year to scrape
    :param division: the division of the conferences (1, 2, 3)
    :return: None
    """
    ids = Database.get_year_info(year)
    year_id = ids['year_id']
    conference_info = []
    
    for stat_type in stat_types:
        conference_stats_file_name = FileUtils.get_scrape_file_name(year, division, base_file_name.format(
                stat_type=stat_type))
        with open(conference_stats_file_name, 'wb') as conference_stats_file:
            conference_stats_writer = unicodecsv.writer(conference_stats_file)
        
            print('Getting conference {stat_type} stats for {year} division {division}... '
                  .format(stat_type=stat_type, year=year, division=division),
                  end='')
            
            url = base_url.format(division=division, year_id=year_id, year_stat_id=ids[stat_type +
                                                                                       '_id'])
            page = WebUtils.get_page(url, 0.1, 10)
            
            table = page.select_one('#stat_grid')
            table_header = table.select_one('tr', {'style': 'background: white;'})
            
            header = [th.text for th in table_header.select('th')]
            conference_stats_writer.writerow(header)
            
            conference_dict = dict()
            rows = table.select('tr')[1:-1]
            for row in rows:
                cols = row.select('td')
                
                # Some pages have duplicate conferences, this check prevents duplicate stats from
                # being recorded
                conference_name = cols[0].text.strip()
                if conference_name not in conference_dict:
                    conference_dict.update([(conference_name, None)])
                    conference_stats = []
                    for col in cols:
                        conference_stats.append(col.text.strip())
                    conference_stats_writer.writerow(conference_stats)
                    if stat_type == stat_types[2]:
                        conference_info.append([conference_name])
            
            print('{num_conferences} conferences found.'.format(num_conferences=
                                                                len(conference_dict) - 1))
    
    conferences_file_name = FileUtils.get_scrape_file_name(year, division, 'conferences')
    with open(conferences_file_name, 'wb') as file:
        conferences_writer = unicodecsv.writer(file)
        conferences_writer.writerow(['conference_name'])
        conferences_writer.writerows(conference_info[:-1])
