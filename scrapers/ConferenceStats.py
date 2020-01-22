"""
File to scrape from https://stats.ncaa.org/rankings/conference_trends and get each division's
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

    @param year: the year to scrape
    @param division: the division of the conferences (1, 2, 3)
    @return: None
    """
    ids = Database.get_year_info(year)
    year_id = ids[0]
    
    for stat_id in ids[1:]:
        print('Getting {stat_type} conference stats for {year} division {division}... '
              .format(stat_type=stat_types[stat_id - ids[1]], year=year, division=division),
              end='')
        
        url = base_url.format(division=division, year_id=year_id, year_stat_id=stat_id)
        page = WebUtils.get_page(url, 0.5, 10)
        
        stats_table = page.select_one('#stat_grid')
        table_header = stats_table.select_one('tr', {'style': 'background: white;'})
        
        header = [th.text for th in table_header.select('th')]
        
        conference_dict = dict()
        stats = []
        for row in stats_table.select('tr')[1:-1]:
            cols = row.select('td')
            
            # Some pages have duplicate conferences, this check prevents duplicate stats from
            # being recorded
            if cols[0].text.strip() not in conference_dict:
                conference_name = cols[0].text.strip()
                conference_dict.update([(conference_name, None)])
                conference_stats = []
                for col in cols:
                    conference_stats.append(col.text.strip())
                stats.append(conference_stats)
        
        # length - 1 since the list should include the national totals as well
        print('{num_conferences} conferences found.'.format(num_conferences=len(stats) - 1))
        
        stats_file_name = FileUtils.get_file_name(year, division, base_file_name.format(
                stat_type=stat_types[stat_id - ids[1]]))
        with open(stats_file_name, 'wb') as file:
            stats_writer = unicodecsv.writer(file)
            stats_writer.writerow(header)
            stats_writer.writerows(stats)
        
        conference_file_name = FileUtils.get_file_name(year, division, 'conferences')
        with open(conference_file_name, 'wb') as file:
            conference_writer = unicodecsv.writer(file)
            conference_writer.writerow(['conference'])
            conference_writer.writerows([[conference[0]] for conference in stats[:-1]])
