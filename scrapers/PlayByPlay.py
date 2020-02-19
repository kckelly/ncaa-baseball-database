"""
File to scrape play by play text.
"""
import os

import unicodecsv

import DataUtils
import FileUtils
import WebUtils

base_url = 'https://stats.ncaa.org/game/play_by_play/{game_id}'
header = ['game_id', 'school_name', 'school_id', 'inning', 'pbp_type', 'side', 'pbp_text',
          'score_change']

def get_play_by_play(year, division):
    """
    Get play by play for the specified year and division.
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    games = DataUtils.get_games_from_game_info(year, division)
    game_ids = set()
    
    play_by_play_file_name = FileUtils.get_scrape_file_name(year, division, 'play_by_play')
    if os.path.exists(play_by_play_file_name):
        with open(play_by_play_file_name, 'rb') as play_by_play_file:
            play_by_play_reader = unicodecsv.DictReader(play_by_play_file)
            for play_by_play_line in play_by_play_reader:
                game_ids.add(play_by_play_line['game_id'])
    
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
            
            page = WebUtils.get_page(url, 0.1, 10)
            
            innings = page.select('.mytable')[1:]
            
            game_pbp_lines = []
            
            for inning_num, inning in enumerate(innings):
                for line in inning.select('tr')[1:]:
                    cols = line.select('td')
                    away_pbp = cols[0].text.strip()
                    score_change = cols[1].text.strip()
                    home_pbp = cols[2].text.strip()
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
