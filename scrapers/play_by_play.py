"""
File to scrape play by play text.

@author: Kevin Kelly
"""
import os

import unicodecsv

from jmu_baseball_utils import data_utils
from jmu_baseball_utils import file_utils
from jmu_baseball_utils import web_utils


def get_play_by_play(year: int, division: int) -> None:
    """
    Get play by play for the specified year and division. Creates a csv file called 'scraped-data/{
    year}/division_{}/play_by_play.csv'.
    
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    base_url = 'https://stats.ncaa.org/game/play_by_play/{game_id}'
    
    games = data_utils.get_games_from_game_info(year, division)
    game_ids = set()
    
    header = ['game_id', 'school_name', 'school_id', 'inning', 'pbp_type', 'side', 'pbp_text',
              'score_change']
    
    # if the play by play file already has data in it, we do not want to redo work we have already
    # done so we take all game urls from the old file and add it to game_ids so they will be skipped
    # if the file does not exist we start from the beginning
    play_by_play_file_name = file_utils.get_scrape_file_name(year, division, 'play_by_play')
    if os.path.exists(play_by_play_file_name):
        with open(play_by_play_file_name, 'rb') as play_by_play_file:
            play_by_play_reader = unicodecsv.DictReader(play_by_play_file)
            for play_by_play_line in play_by_play_reader:
                game_ids.add(play_by_play_line['game_id'])
    
    # write in append mode because we want to add on if the file already exists
    with open(play_by_play_file_name, 'ab') as play_by_play_file:
        play_by_play_writer = unicodecsv.DictWriter(play_by_play_file, header)
        
        if len(game_ids) == 0:
            play_by_play_writer.writeheader()
        
        for game in games:
            if game['game_id'] in game_ids:
                continue

            game_ids.add(game['game_id'])
            url = base_url.format(game_id=game['game_id'])
            
            print('{num_games}: Getting play by play for {game_id}...'
                  .format(num_games=len(game_ids), game_id=game['game_id']), end='')

            page = web_utils.get_page(url, 0.1, 10)
            
            innings = page.select('.mytable')[1:]
            
            game_pbp_lines = []

            for inning_num, inning in enumerate(innings):
                for pbp_line in inning.select('tr')[1:]:
        
                    pbp_cols = pbp_line.select('td')
        
                    away_pbp = pbp_cols[0].text.strip()
                    score_change = pbp_cols[1].text.strip()
                    home_pbp = pbp_cols[2].text.strip()
        
                    # this indicates this is an inning summary line
                    if away_pbp.startswith('R: '):
                        for side in ['away', 'home']:
                            summary = {heading: None for heading in header}
                
                            summary['game_id'] = game['game_id']
                            summary['school_name'] = game[side + '_school_name']
                            summary['school_id'] = game[side + '_school_id']
                            summary['inning'] = inning_num + 1
                            summary['side'] = side
                            summary['pbp_type'] = 'inning_summary'
                            if side == 'away':
                                summary['pbp_text'] = away_pbp
                            else:
                                summary['pbp_text'] = home_pbp
                            summary['score_change'] = score_change
                
                            game_pbp_lines.append(summary)
                    else:
                        pbp_line = {heading: None for heading in header}
                        pbp_line['game_id'] = game['game_id']
                        pbp_line['inning'] = inning_num + 1
                        pbp_line['pbp_type'] = 'play'
                        pbp_line['score_change'] = score_change
                        
                        if away_pbp == '':
                            pbp_line['school_name'] = game['home_school_name']
                            pbp_line['school_id'] = game['home_school_id']
                            pbp_line['side'] = 'home'
                            pbp_line['pbp_text'] = home_pbp
                        else:
                            pbp_line['school_name'] = game['away_school_name']
                            pbp_line['school_id'] = game['away_school_id']
                            pbp_line['side'] = 'away'
                            pbp_line['pbp_text'] = away_pbp

                        game_pbp_lines.append(pbp_line)

            play_by_play_writer.writerows(game_pbp_lines)
            play_by_play_file.flush()

            print('{num_lines} lines'.format(num_lines=len(game_pbp_lines)))
    
    print('{num_games} games total'.format(num_games=len(game_ids)))
