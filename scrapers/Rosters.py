"""
File for scraping rosters for each team. Necessary since not every player is on the team
statistics page.

@author: Kevin Kelly
"""
import unicodecsv

import DataUtils
import Database
import FileUtils
import WebUtils


def get_rosters(year, division):
    """
    Get all rosters for the given year and division. Creates a csv file called 'scraped-data/{
    year}/division_{}/rosters.csv'.
    
    :param year: the year to get rosters from
    :param division: the division of the teams
    :return: None
    """
    base_url = 'https://stats.ncaa.org'
    
    ids = Database.get_year_info(year)
    teams_list = DataUtils.get_schools(year, division)
    
    header = ['school_name', 'school_id', 'player_name', 'player_id', 'jersey_number', 'class']
    
    roster_file_name = FileUtils.get_scrape_file_name(year, division, 'rosters')
    with open(roster_file_name, 'wb') as roster_file:
        roster_writer = unicodecsv.DictWriter(roster_file, header)
        roster_writer.writeheader()
        
        for team in teams_list:
            print('Getting roster for {school}... '.format(school=team['school_name']), end='')
            roster_url = base_url + '/team/{school_id}/roster/{year_id}'.format(school_id=team[
                'school_id'], year_id=ids['year_id'])
    
            page = WebUtils.get_page(roster_url, 0.1, 10)
    
            roster_rows = page.select_one('tbody').select('tr')
    
            # get player info from each roster row and write to file
            for roster_row in roster_rows:
                roster_cols = roster_row.select('td')
        
                player = {heading: None for heading in header}
                player['school_name'] = team['school_name']
                player['school_id'] = team['school_id']
                player['player_name'] = roster_cols[1].text.strip()
        
                try:
                    player_url = roster_row.select_one('a').attrs.get('href')
                    player['player_id'] = WebUtils.get_player_id_from_url(player_url)
                except AttributeError:
                    player['player_id'] = None
        
                player['jersey_number'] = roster_cols[0].text.strip()
                player['class'] = roster_cols[3].text.strip()
        
                roster_writer.writerow(player)
    
            roster_file.flush()
            print('{} players found.'.format(len(roster_rows)))
