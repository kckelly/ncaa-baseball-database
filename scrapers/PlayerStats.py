"""
File to scrape player stats for verification purposes later.

@author: Kevin Kelly
"""
import unicodecsv

import DataUtils
import Database
import FileUtils
import WebUtils


def get_player_stats(year, division):
    """
    Get each player's stat line for the specified year and division. Creates three csv files, in the
    format 'scraped-data/{year}/division_{}/player_{stat_type}_stats.csv'.
    
    :param year: the year to get the stats from
    :param division: the division the players play in
    :return: None
    """
    
    base_url = 'https://stats.ncaa.org/team/{school_id}/stats?id={' \
               'year_id}&year_stat_category_id={' \
               'stat_id}'
    
    base_file_name = 'player_{stat_type}_totals'
    
    stat_types = ['hitting', 'pitching', 'fielding']
    
    teams_list = DataUtils.get_schools(year, division)
    
    ids = Database.get_year_info(year)
    
    for stat_type in stat_types:
        header = []
        stat_file_name = base_file_name.format(stat_type=stat_type)
        player_stats_file_name = FileUtils.get_scrape_file_name(year, division, stat_file_name)
        
        with open(player_stats_file_name, 'wb') as player_stats_file:
            player_stats_writer = unicodecsv.writer(player_stats_file)
            
            for team in teams_list:
                print('Getting player {stat_type} stats for {school}... '
                      .format(stat_type=stat_type, school=team['school_name']), end='')
                
                player_stats_url = base_url.format(school_id=team['school_id'],
                                                   year_id=ids['year_id'],
                                                   stat_id=ids[stat_type + '_id'])
                
                page = WebUtils.get_page(player_stats_url, 0.1, 10)
                
                stat_table = page.select_one('#stat_grid')
                
                if not header:
                    stat_header = [col.text.strip() for col in stat_table.select('th')]
                    header = ['school_name', 'school_id'] + stat_header
                    header.insert(4, 'player_id')
                    player_stats_writer.writerow(header)
                
                stat_rows = stat_table.select('tr')
                
                for stat_row in stat_rows[1:]:
                    player_stats = [col.text.strip() for col in stat_row.select('td')]
                    player = [team['school_name'], team['school_id']] + player_stats
                    
                    try:
                        player_url = stat_row.select_one('a').attrs.get('href')
                        player_id = WebUtils.get_player_id_from_url(player_url)
                    except AttributeError:
                        player_id = None
                    player.insert(4, player_id)
                    
                    player_stats_writer.writerow(player)
                
                player_stats_file.flush()
                print('{} players found.'.format(len(stat_rows) - 3))
