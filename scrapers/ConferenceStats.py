"""
File to scrape from https://stats.ncaa.org/rankings/conference_trends and get each division's
conference stats by year. Creates one file that is used to put conference names into the database
and another that holds stats for verification purposes later.

@author: Kevin Kelly
"""
import unicodecsv

import Database
import FileUtils
import WebUtils


def get_conference_stats(year, division):
    """
    Scrape the team totals for hitting, pitching, and fielding. Also creates another csv file
    containing just the names of the teams for that year and division. The three stat csv files
    are saved in the format 'scraped-data/{year}/division_{}/conference_{stat_type}_stats.csv'.

    :param year: the year to scrape
    :param division: the division of the conferences (1, 2, 3)
    :return: None
    """
    
    base_url = 'https://stats.ncaa.org/rankings/conference_trends?' \
               'division={division}&id={year_id}&year_stat_category_id={year_stat_id}'
    base_file_name = 'conference_{stat_type}_totals'
    
    stat_types = ['hitting', 'pitching', 'fielding']
    
    ids = Database.get_year_info(year)
    
    year_id = ids['year_id']
    
    conference_info = []  # used for the conference name file
    
    for stat_type in stat_types:
        stat_file_name = base_file_name.format(stat_type=stat_type)
        conference_stats_file_name = FileUtils.get_scrape_file_name(year, division, stat_file_name)
        with open(conference_stats_file_name, 'wb') as conference_stats_file:
            conference_stats_writer = unicodecsv.writer(conference_stats_file)
            
            print('Getting conference {stat_type} stats for {year} division {division}... '
                  .format(stat_type=stat_type, year=year, division=division),
                  end='')
            
            url = base_url.format(division=division, year_id=year_id,
                                  year_stat_id=ids[stat_type + '_id'])
            page = WebUtils.get_page(url, 0.1, 10)
            
            stat_table = page.select_one('#stat_grid')
            stat_table_header = stat_table.select_one('tr', {'style': 'background: white;'})
            
            header = [th.text for th in stat_table_header.select('th')]
            conference_stats_writer.writerow(header)
            
            conference_dict = dict()
            stat_rows = stat_table.select('tr')[1:-1]
            for stat_row in stat_rows:
                stat_cols = stat_row.select('td')
                
                # Some pages have duplicate conferences, this check prevents duplicate stats from
                # being recorded
                conference_name = stat_cols[0].text.strip()
                if conference_name not in conference_dict:
                    conference_dict.update([(conference_name, None)])
                    
                    conference_stats = [stat_col.text.strip() for stat_col in stat_cols]
                    conference_stats_writer.writerow(conference_stats)
                    
                    # this check is performed so that the conference names only get added to the
                    # conferences file once
                    if stat_type == stat_types[2]:
                        conference_info.append([conference_name])
            
            print('{num_conferences} conferences found.'.format(num_conferences=
                                                                len(conference_dict) - 1))
    
    conferences_file_name = FileUtils.get_scrape_file_name(year, division, 'conferences')
    conference_header = ['conference_name']
    with open(conferences_file_name, 'wb') as file:
        conferences_writer = unicodecsv.writer(file)
        conferences_writer.writerow(conference_header)
        conferences_writer.writerows(conference_info[:-1])
