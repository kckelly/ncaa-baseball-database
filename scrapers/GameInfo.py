"""
File to scrape game information. Needs to be separate from getting box scores since in years
since 2019 there is a contest id that is different from game ids.
"""
import os

import unicodecsv
from bs4 import NavigableString

import DataUtils
import FileUtils
import WebUtils

base_url = 'https://stats.ncaa.org'


def get_game_info(year, division):
    """
    Get game information for each game in a year in a specified division. This information
    includes inning scores, umpires, attendance, etc.
    
    :param year: the year to get games from
    :param division: the division the games were played at
    :return: None
    """
    game_set = set()
    games = DataUtils.get_games_from_schedule(year, division)
    schools = DataUtils.get_school_id_dict()
    
    game_info_header = ['game_url', 'game_id', 'away_school_name', 'away_school_id',
                        'away_team_sport_id', 'home_school_name', 'home_school_id',
                        'home_team_sport_id', 'game_code', 'date', 'location', 'attendance',
                        'hp_official', '1b_official', '2b_official', '3b_official', 'weather',
                        'other']
    
    game_info_file_name = FileUtils.get_scrape_file_name(year, division, 'game_info')
    num_lines = FileUtils.get_num_file_lines(game_info_file_name)
    
    innings_file_name = FileUtils.get_scrape_file_name(year, division, 'game_innings')
    with open(innings_file_name, 'ab') as innings_file, open(game_info_file_name, 'ab') as \
            game_info_file:
        innings_writer = unicodecsv.writer(innings_file)
        info_writer = unicodecsv.DictWriter(game_info_file, game_info_header)
        
        # write headers if game_info file is empty
        if num_lines == 0:
            innings_writer.writerow(['url', 'game_id', 'side', 'school', 'school_id'])
            info_writer.writeheader()
        
        for game in games:
            if game['game_url'] in game_set:
                continue
            if game['game_url'] is None or game['game_url'] == '':
                print('No link for game {date} {school_name} {opponent_name}'
                      .format(date=game['date'], school_name=game['school_name'],
                              opponent_name=game['opponent_string']))
                continue
            game_set.add(game['game_url'])
            
            if len(game_set) < num_lines:
                continue
            
            game_url = base_url + game['game_url']
            
            print('{num_games}: Getting game info and innings for {game_id}... '.format(
                    num_games=len(game_set),
                    game_id=WebUtils.get_contest_id_from_url(game['game_url'], year)), end='')
            page = WebUtils.get_page(game_url, 0.1, 10)
            
            game_id = page.select_one('#primary_nav_wrap').select_one('a').attrs.get('href')[16:]
            
            print('{date} {school_name} {opponent_name}'
                  .format(date=game['date'], school_name=game['school_name'],
                          opponent_name=game['opponent_string']))
            
            # innings
            innings = page.select_one('.mytable')
            away_innings = innings.select('tr')[1]
            home_innings = innings.select('tr')[2]
            
            away_school = away_innings.select_one('td').text.strip()
            
            # This dict is for some of the errors in the game info pages, for some reason these
            # do not always match the school name the ncaa has
            name_changes = {'Incarnate Word': 'UIW', 'LIU Brooklyn': 'LIU',
                            'Coastal Caro.': 'Coastal Carolina', 'Loyola Marymount': 'LMU (CA)'}
            if away_school in name_changes:
                away_school = name_changes[away_school]
                
            try:
                away_school_id = schools[away_school]
            except KeyError:
                away_school_id = None
                
            home_school = home_innings.select_one('td').text.strip()
            if home_school in name_changes:
                home_school = name_changes[home_school]
                
            try:
                home_school_id = schools[home_school]
            except KeyError:
                home_school_id = None
                
            try:
                away_school_url = away_innings.select_one('a').attrs.get('href')
                away_team_sport_id = WebUtils.get_school_id_from_url(away_school_url)
            except AttributeError:
                away_team_sport_id = None
            try:
                home_school_url = home_innings.select_one('a').attrs.get('href')
                home_team_sport_id = WebUtils.get_school_id_from_url(home_school_url)
            except AttributeError:
                home_team_sport_id = None
            
            away_runs = [inning.text for inning in away_innings.select('td')[1:-3]]
            home_runs = [inning.text for inning in home_innings.select('td')[1:-3]]
            
            innings_writer.writerow([game_url, game_id, 'away', away_school, away_school_id] +
                                    away_runs)
            innings_writer.writerow([game_url, game_id, 'home', home_school, home_school_id] +
                                    home_runs)
            
            # game info
            game = {heading: None for heading in game_info_header}
            game['game_url'] = game_url
            game['game_id'] = game_id
            game['away_school'] = away_school
            game['away_school_id'] = away_school_id
            game['away_team_sport_id'] = away_team_sport_id
            game['home_school'] = home_school
            game['home_school_id'] = home_school_id
            game['home_team_sport_id'] = home_team_sport_id
            
            game_tables = page.find_all('table',
                                        {"width": "50%", "align": "center", "class": None})
            other_info = game_tables[0]
            info_table = game_tables[1]
            officials_table = game_tables[2]
            
            other = []
            
            # other info
            for col in other_info.select('td'):
                if col.text.strip().startswith('Weather:'):
                    game['weather'] = col.text.strip()[9:]
                elif col.text.strip().startswith('Game:'):
                    game['game_code'] = col.text.strip()[6:]
                else:
                    other.append(col.text.strip())
            game['other'] = other
            
            # game info
            for col in info_table.select('td'):
                if col.text.strip() == 'Game Date:':
                    game['date'] = col.findNext('td').text.strip()
                elif col.text.strip() == 'Location:':
                    game['location'] = col.findNext('td').text.strip()
                elif col.text.strip() == 'Attendance:':
                    game['attendance'] = col.findNext('td').text.strip()
            
            # officials
            for col in officials_table.select('td'):
                if col.text.strip() == 'Officials:':
                    for line in col.findNext('td').contents:
                        if type(line) is NavigableString:
                            if line.strip().startswith('hp'):
                                game['hp_official'] = line.replace('hp:', '').strip()
                            elif line.strip().startswith('first'):
                                game['1b_official'] = line.replace('first:', '').strip()
                            elif line.strip().startswith('second'):
                                game['2b_official'] = line.replace('second:', '').strip()
                            elif line.strip().startswith('third'):
                                game['3b_official'] = line.replace('third:', '').strip()
            info_writer.writerow(game)
            
            innings_file.flush()
            game_info_file.flush()
    
    print('Total games: {num_games}'.format(num_games=len(game_set)))
