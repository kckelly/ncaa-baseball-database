"""
File to scrape game information. Needs to be separate from getting box scores since in years
since 2019 there is a contest id that is different from game ids.

@author: Kevin Kelly
"""
import os

import unicodecsv
from bs4 import NavigableString

from jmu_baseball_utils import data_utils
from jmu_baseball_utils import file_utils
from jmu_baseball_utils import web_utils


def get_game_info(year: int, division: int) -> None:
    """
    Get game information for each game in a year in a specified division. This information
    includes inning scores, umpires, attendance, etc. Creates two csv files, in the format
    'scraped-data/{year}/division_{}/game_info.csv' and 'scraped-data/{year}/division_{}/game_
    innings.csv'.
    
    :param year: the year to get games from
    :param division: the division the games were played at
    :return: None
    """
    base_url = 'https://stats.ncaa.org'
    
    games = data_utils.get_games_from_schedule(year, division)
    school_ids = data_utils.get_school_id_dict()
    
    game_info_header = ['game_url', 'contest_id', 'game_id', 'away_school_name', 'away_school_id',
                        'home_school_name', 'home_school_id', 'game_code', 'date', 'location', 'attendance',
                        'hp_official', '1b_official', '2b_official', '3b_official', 'weather',
                        'other']
    
    game_info_file_name = file_utils.get_scrape_file_name(year, division, 'game_info')
    game_ids = set()
    
    # If the game info file already has data in it, we do not want to redo work we have already
    # done so we take all game urls from the old file and add it to game_ids so they will be skipped.
    # If the file does not exist we start from the beginning
    file_exists = os.path.exists(game_info_file_name)
    if file_exists:
        with open(game_info_file_name, 'rb') as game_info_file:
            game_info_reader = unicodecsv.DictReader(game_info_file)
            for line in game_info_reader:
                game_ids.add(line['game_url'])
    
    # write in append mode because we want to add on if the files already exist
    innings_file_name = file_utils.get_scrape_file_name(year, division, 'game_innings')
    with open(innings_file_name, 'ab') as innings_file, \
            open(game_info_file_name, 'ab') as game_info_file:
        
        innings_writer = unicodecsv.writer(innings_file)
        
        info_writer = unicodecsv.DictWriter(game_info_file, game_info_header)
        
        # write headers if game_info file is empty
        if not file_exists:
            innings_writer.writerow(['url', 'game_id', 'side', 'school', 'school_id'])
            info_writer.writeheader()
        
        for game in games:
            game_url = base_url + game['game_url']
            
            if game_url in game_ids:
                continue

            if game['game_url'] is None or game['game_url'] == '':
                print('No link for game {date} {school_name} {opponent_name}'
                      .format(date=game['date'], school_name=game['school_name'],
                              opponent_name=game['opponent_string']))
                continue

            game_ids.add(game_url)

            print('{num_games}: Getting game info and innings for {game_id}... '.format(
                num_games=len(game_ids),
                game_id=web_utils.get_contest_id_from_url(game['game_url'])), end='')

            page = web_utils.get_page(game_url, 0.1, 10)
            if page.text == 'Box score not available' or 'We\'re sorry, but something went wrong (500)' in page.text:
                print('{url}: box score missing'.format(url=game['game_url']))
                continue
            game_id = page.select_one('#primary_nav_wrap').select_one('a').attrs.get('href')[16:]

            print('{date} {school_name} {opponent_name}'
                  .format(date=game['date'], school_name=game['school_name'],
                          opponent_name=game['opponent_string']))

            # innings
            innings = page.select_one('.mytable')
            away_innings = innings.select('tr')[1]
            home_innings = innings.select('tr')[2]
            
            away_school = away_innings.select_one('td').text.strip()
            
            if year > 2019:
                away_school = away_school.split('(')[0].strip()
            
            try:
                away_school_id = school_ids[away_school]
            except KeyError:
                away_school_id = None
            
            home_school = home_innings.select_one('td').text.strip()
            
            if year > 2019:
                home_school = home_school.split('(')[0].strip()
            
            try:
                home_school_id = school_ids[home_school]
            except KeyError:
                home_school_id = None

            away_runs = [inning.text for inning in away_innings.select('td')[1:-3]]
            home_runs = [inning.text for inning in home_innings.select('td')[1:-3]]

            innings_writer.writerow([game_url, game_id, 'away', away_school, away_school_id] +
                                    away_runs)
            innings_writer.writerow([game_url, game_id, 'home', home_school, home_school_id] +
                                    home_runs)

            # game info
            game_row = {heading: None for heading in game_info_header}
            game_row['game_url'] = game_url
            game_row['contest_id'] = web_utils.get_contest_id_from_url(game['game_url'])
            game_row['game_id'] = game_id
            game_row['away_school_name'] = away_school
            game_row['away_school_id'] = away_school_id
            game_row['home_school_name'] = home_school
            game_row['home_school_id'] = home_school_id

            game_tables = page.find_all('table', {"width": "50%", "align": "center", "class": None})
            other_info = game_tables[0]
            info_table = game_tables[1]
            officials_table = game_tables[2]

            other = []

            # other info
            for col in other_info.select('td'):
                if col.text.strip().startswith('Weather:'):
                    game_row['weather'] = col.text.strip()[9:]
                elif col.text.strip().startswith('Game:'):
                    game_row['game_code'] = col.text.strip()[6:]
                else:
                    other.append(col.text.strip())
            game_row['other'] = other
            
            # game info
            for col in info_table.select('td'):
                if col.text.strip() == 'Game Date:':
                    game_row['date'] = col.findNext('td').text.strip()
                elif col.text.strip() == 'Location:':
                    game_row['location'] = col.findNext('td').text.strip()
                elif col.text.strip() == 'Attendance:':
                    game_row['attendance'] = col.findNext('td').text.strip()
            
            # officials
            for col in officials_table.select('td'):
                if col.text.strip() == 'Officials:':
                    for line in col.findNext('td').contents:
                        if type(line) is NavigableString:
                            if line.strip().startswith('hp'):
                                game_row['hp_official'] = line.replace('hp:', '').strip()
                            elif line.strip().startswith('first'):
                                game_row['1b_official'] = line.replace('first:', '').strip()
                            elif line.strip().startswith('second'):
                                game_row['2b_official'] = line.replace('second:', '').strip()
                            elif line.strip().startswith('third'):
                                game_row['3b_official'] = line.replace('third:', '').strip()
            info_writer.writerow(game_row)

            innings_file.flush()
            game_info_file.flush()
    
    print('Total games: {num_games}'.format(num_games=len(game_ids)))
