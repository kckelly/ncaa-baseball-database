"""
File to scrape box scores. Creates 3 csvs, one each for hitting, pitching, and fielding. Uses the
ids acquired by GameInfo since there is a new contest ID in 2019 that does not work for getting
each box score.
"""
import os

import unicodecsv

import DataUtils
import Database
import FileUtils
import WebUtils

stat_types = ['hitting', 'pitching', 'fielding']
base_url = 'https://stats.ncaa.org/game/box_score/{game_id}?year_stat_category_id={stat_id}'
base_file_name = 'box_score_{stat_type}'


def get_box_scores(year, division):
    """
    Get all box scores for a given year and division. Creates 3 csvs, in the format box_score_{
    stat_type}.csv.
    @param year: the year to get games from
    @param division: the division the games were played at
    @return: None
    """
    ids = Database.get_year_info(year)
    
    games = DataUtils.get_games_from_game_info(year, division)
    
    for stat_type in stat_types:
        header = []
        box_score_file_name = FileUtils.get_file_name(year, division, base_file_name.format(
                stat_type=stat_type))
        
        game_ids = set()
        if os.path.exists(box_score_file_name):
            with open(box_score_file_name, 'rb') as box_score_file:
                box_score_reader = unicodecsv.DictReader(box_score_file)
                for box_score_line in box_score_reader:
                    game_ids.add(box_score_line['game_id'])
        
        with open(box_score_file_name, 'ab') as box_score_file:
            box_score_writer = unicodecsv.writer(box_score_file)
            
            for game in games:
                if game['game_id'] in game_ids:
                    continue
                
                box_score_url = base_url.format(game_id=game['game_id'],
                                                stat_id=ids[stat_type + '_id'])
                
                print('{num_games}: Getting {stat_type} box score for {game_id}...'
                      .format(num_games=len(game_ids),
                              stat_type=stat_type, game_id=game['game_id']), end='')
                page = WebUtils.get_page(box_score_url, 0.1, 10)
                
                box_score_tables = page.select('.mytable')[1:3]
                
                if not header and len(game_ids) == 0:
                    header = ['game_id', 'school_name', 'school_id']
                    [header.append(heading.text.strip()) for heading in box_score_tables[0]
                        .select_one('.grey_heading').select('th')]
                    header.insert(4, 'player_id')
                    box_score_writer.writerow(header)
                    
                game_ids.add(game['game_id'])
                
                box_score_lines = []
                for side, box_score_table in enumerate(box_score_tables):
                    for row in box_score_table.select('tr')[2:]:
                        cols = row.select('td')
                        
                        if side == 0:  # away
                            school_name = game['away_school_name']
                            school_id = game['away_school_id']
                        else:  # home
                            school_name = game['home_school_name']
                            school_id = game['home_school_id']
                        
                        box_score_line = [game['game_id'], school_name, school_id]
                        for col in cols:
                            box_score_line.append(col.text.strip())
                        try:
                            player_url = row.select_one('a').attrs.get('href')
                            player_id = WebUtils.get_player_id_from_url(player_url)
                        except AttributeError:
                            player_id = None
                        
                        box_score_line.insert(4, player_id)
                        box_score_lines.append(box_score_line)
                
                box_score_writer.writerows(box_score_lines)
                box_score_file.flush()
                print('{box_score_lines} players involved'.format(box_score_lines=len(
                        box_score_lines) - 2))
        print('{num_games} games total'.format(num_games=len(game_ids)))
