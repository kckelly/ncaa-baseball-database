"""
File to scrape player stats for verification purposes later.
"""
import unicodecsv

import DataUtils
import Database
import FileUtils
import WebUtils

base_url = 'https://stats.ncaa.org/team/{school_id}/stats?id={year_id}&year_stat_category_id={' \
           'stat_id}'
base_file_name = 'player_{stat_type}_totals'
stat_types = ['hitting', 'pitching', 'fielding']


def get_player_stats(year, division):
    """
    Get each player's stat line for the specified year and division.
    
    @param year: the year to get the stats from
    @param division: the division the players play in
    @return: None
    """
    teams_list = DataUtils.get_schools(year, division)
    ids = Database.get_year_info(year)
    header = []
    for stat_type in stat_types:
        
        player_stats_file_name = FileUtils.get_file_name(year, division,
                                                         base_file_name.format(stat_type=stat_type))
        with open(player_stats_file_name, 'wb') as player_stats_file:
            player_stats_writer = unicodecsv.writer(player_stats_file)
            
            for team in teams_list:
                print('Getting player {stat_type} stats for {school}... '
                      .format(stat_type=stat_type, school=team['school_name']), end='')
                player_stats_url = base_url.format(school_id=team['school_id'],
                                                   year_id=ids['year_id'],
                                                   stat_id=ids[stat_type + '_id'])
                
                page = WebUtils.get_page(player_stats_url, 0.1, 10)
                
                table = page.select_one('#stat_grid')
                
                if not header:
                    header = ['school_name', 'school_id'] + [col.text.strip()
                                                             for col in table.select('th')]
                    header.insert(4, 'player_id')
                    player_stats_writer.writerow(header)
                
                rows = table.select('tr')
                
                for row in rows[1:]:
                    player = [team['school_name'], team['school_id']] + \
                        [col.text.strip() for col in row.select('td')]
                    try:
                        player.insert(4, WebUtils.get_player_id_from_url(row.select_one(
                                'a').attrs.get('href')))
                    except AttributeError:
                        player.insert(4, None)
                    player_stats_writer.writerow(player)
            
                player_stats_file.flush()
                print('{} players found'.format(len(rows) - 3))
