"""
This file copies the play by play to the database.

@author: Kevin Kelly
"""
import re

import unicodecsv

from copiers import school_name_changes
from jmu_baseball_utils import file_utils
from database_files.ncaa_database import NCAADatabase


def copy_play_by_play(database: NCAADatabase, year, division):
    """
    Copy play by play text from this year and division to the database.
    
    :param database: the ncaa database
    :param year: the year the games that the play by play describes were played in
    :param division: the division the games that the play by play describes were played at
    :return: None
    """
    print('Copying play by play... ', end='')
    database_schools = {school['name']: school['ncaa_id'] for school in database.get_all_schools()}
    
    database_games = {game['ncaa_id']: game['id'] for game in database.get_all_game_info()}
    
    current_pbp_games = {(pbp['game_id']): None for pbp in database.get_all_play_by_play()}
    
    database_teams = {team['school_name']: team['team_id'] for team in
                      database.get_all_team_info() if team['year'] == year}
    
    pbp_file_name = file_utils.get_scrape_file_name(year, division, 'play_by_play')
    new_pbp = []
    with open(pbp_file_name, 'rb') as pbp_file:
        reader = unicodecsv.DictReader(pbp_file)
        order = 0
        away = True
        for line in reader:
            game_id = database_games[int(line['game_id'])]
            if game_id in current_pbp_games:
                continue

            if line['pbp_type'] == 'inning_summary':
                order = 0
                away = True
                continue

            # if this conditional is true we have reached the end of the inning, so we start the
            # count over
            if away and line['side'] == 'home':
                order = 0
                away = False

            if line['school_name'] in school_name_changes.school_name_changes:
                line['school_name'] = school_name_changes.school_name_changes[line['school_name']]

            try:
                team_id = database_teams[line['school_name']]
            except ValueError:
                school_id = database_schools[line['school_name']]
                team_id = database_teams[school_id]

            play = re.sub(r'\(.*\)', '', line['pbp_text'])

            try:
                pitches = re.search(r'\((.*)\)', line['pbp_text']).group(1)
                if not re.match(r'[0-3]-[0-2] ?[SFBK]*', pitches):
                    play += pitches
                    pitches = None
            except AttributeError:
                pitches = None
            
            if play == '' or play is None:
                continue

            new_pbp.append({'game_id': game_id,
                            'team_id': team_id,
                            'inning': line['inning'],
                            'side': line['side'],
                            'ord': order,
                            'text': play,
                            'pitches': pitches})
            order += 1
    
    header = ['game_id', 'team_id', 'inning', 'side', 'ord', 'text', 'pitches']
    database.copy_expert('play_by_play(game_id, team_id, inning, side, ord, text, pitches)',
                         'play_by_play', header, new_pbp)
    print('{num_lines} new play by play lines.'.format(num_lines=len(new_pbp)))
