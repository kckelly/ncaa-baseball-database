"""
This file copies the play by play to the database.
"""
import re

import unicodecsv

import Database
import FileUtils


def copy_play_by_play(year, division):
    """
    Copy play by play text from this year and division to the database.
    
    :param year: the year the games that the play by play describes were played in
    :param division: the division the games that the play by play describes were played at
    :return: None
    """
    print('Copying play by play... ', end='')
    
    all_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}

    current_pbp_games = {(pbp['game_id']): None for pbp in Database.get_all_play_by_play()}

    all_teams = {team['school_ncaa_id']: team['team_id'] for team in Database.get_all_team_info()
                 if team['year'] == year}
    
    pbp_file_name = FileUtils.get_scrape_file_name(year, division, 'play_by_play')
    new_pbp = []
    with open(pbp_file_name, 'rb') as pbp_file:
        reader = unicodecsv.DictReader(pbp_file)
        order = 0
        for line in reader:
            game_id = all_games[int(line['game_id'])]
            if game_id in current_pbp_games:
                continue
            if line['pbp_type'] == 'inning_summary' and line['side'] == 'home':
                order = 0
                continue
            team_id = all_teams[int(line['school_id'])]
            text = re.sub(r'\(.*\)', '', line['pbp_text'])
            try:
                pitches = re.search(r'\((.*)\)', line['pbp_text']).group(1)
                if not re.match(r'[0-3]-[0-2] ?[SFBK]*', pitches):
                    text += pitches
                    pitches = None
            except AttributeError:
                pitches = None
            if text == '' or text is None:
                continue
            new_pbp.append({'game_id': game_id, 'team_id': team_id, 'inning': line['inning'],
                            'ord': order, 'text': text, 'pitches': pitches})
            order += 1
        
    copy_file_name = FileUtils.get_copy_file_name('play_by_play')
    with open(copy_file_name, 'wb') as copy_file:
        writer = unicodecsv.DictWriter(copy_file, ['game_id', 'team_id', 'inning', 'ord', 'text',
                                                   'pitches'])
        writer.writeheader()
        writer.writerows(new_pbp)
        
    Database.copy_expert('play_by_play(game_id, team_id, inning, ord, text, pitches)',
                         copy_file_name)
    print('{num_lines} new play by play lines.'.format(num_lines=len(new_pbp)))
