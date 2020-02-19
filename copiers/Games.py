"""
This file puts all the game information into the game table.
"""
from datetime import datetime
import re

import unicodecsv

import Database
import FileUtils

header = ['ncaa_id', 'away_team_id', 'home_team_id', 'date', 'location', 'attendance']


def copy_game_info(year, division):
    """
    Copy game information into the game table from this year and division.
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print('Copying games... ', end='')
    
    all_teams = {(team['year'], team['school_ncaa_id']): team['team_id'] for team in
                 Database.get_all_team_info()}
    
    current_games = {game['ncaa_id']: game for game in Database.get_all_game_info()}
    
    new_games = []
    
    game_info_file_name = FileUtils.get_scrape_file_name(year, division, 'game_info')
    with open(game_info_file_name, 'rb') as game_info_file:
        game_info_reader = unicodecsv.DictReader(game_info_file)
        for game in game_info_reader:
            ncaa_id = int(game['game_id'])
            if ncaa_id in current_games:
                continue
            new_game = {heading: None for heading in header}
            new_game['ncaa_id'] = ncaa_id
            try:
                new_game['away_team_id'] = all_teams[(year, int(game['away_school_id']))]
            except KeyError:
                new_game['away_team_id'] = Database.create_team(year, game['away_school_id'])
                all_teams.update({(year, int(game['away_school_id'])): new_game['away_team_id']})
            try:
                new_game['home_team_id'] = all_teams[(year, int(game['home_school_id']))]
            except KeyError:
                new_game['home_team_id'] = Database.create_team(year, game['home_school_id'])
                all_teams.update({(year, int(game['home_school_id'])): new_game['home_team_id']})
            match = re.search(r'\d{2}/\d{2}/\d{4}', game['date'])
            new_game['date'] = datetime.strptime(match.group(), '%m/%d/%Y').date()
            new_game['location'] = game['location']
            new_game['attendance'] = game['attendance'].replace(',', '')
            new_games.append(new_game)
    
    copy_file_name = FileUtils.get_copy_file_name('game_info')
    with open(copy_file_name, 'wb') as copy_file:
        writer = unicodecsv.DictWriter(copy_file, header)
        writer.writeheader()
        writer.writerows(new_games)
    
    Database.copy_expert('game(ncaa_id, away_team_id, home_team_id, date, location, attendance)',
                         copy_file_name)
    
    print('{num_games} new games.'.format(num_games=len(new_games)))


def copy_game_innings(year, division):
    """
    Copy each inning of each game into the game_innings table.
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print('Copying innings... ', end='')
    
    all_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    all_teams = {team['school_ncaa_id']: team['team_id'] for team in Database.get_all_team_info()
                 if team['year'] == year}
    
    all_innings = {(inning['game_id'], inning['team_id']): None for
                   inning in Database.get_all_innings()}
    
    new_innings = []
    inning_file_name = FileUtils.get_scrape_file_name(year, division, 'game_innings')
    with open(inning_file_name, 'rb') as inning_file:
        reader = unicodecsv.reader(inning_file)
        next(reader)  # skip header
        for line in reader:
            game_id = all_games[int(line[1])]
            team_id = all_teams[int(line[4])]
            if (game_id, team_id) in all_innings:
                continue
            inning_num = 1
            for inning in line[5:]:
                if inning == '':
                    continue
                new_innings.append({'game_id': game_id, 'team_id': team_id, 'inning': inning_num,
                                    'runs':    inning})
                inning_num += 1
            all_innings.update({(game_id, team_id): None})
    
    copy_file_name = FileUtils.get_copy_file_name('innings')
    with open(copy_file_name, 'wb') as copy_file:
        writer = unicodecsv.DictWriter(copy_file, ['game_id', 'team_id', 'inning', 'runs'])
        writer.writeheader()
        writer.writerows(new_innings)
    
    Database.copy_expert('inning(game_id, team_id, inning, runs)', copy_file_name)
    print('{num_innings} new innings.'.format(num_innings=len(new_innings)))


def create_game_positions(year, division):
    """
    Create game to position relations for each player from each game in this year and division.
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print("Creating game positions... ", end='')
    
    positions = ['1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf', 'dh', 'dp', 'ph', 'pr', 'p', 'c']
    
    all_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    
    all_rosters = {roster['ncaa_id']: roster['roster_id'] for roster in
                   Database.get_all_roster_info() if roster['year'] == year}
    
    current_game_positions = {(game_position['game_id'], game_position['roster_id']): None for
                              game_position in Database.get_all_game_position_info()}
    
    box_score_file_name = FileUtils.get_scrape_file_name(year, division, 'box_score_fielding')
    
    all_positions = []
    
    players_with_bad_id = 0
    
    with open(box_score_file_name, 'rb') as box_score_file:
        reader = unicodecsv.DictReader(box_score_file)
        for line in reader:
            if line['Player'] == 'Totals':
                continue
            game_id = all_games[int(line['game_id'])]
            try:
                player_id = all_rosters[int(line['player_id'])]
            except ValueError:
                continue
            except KeyError:
                players_with_bad_id += 1
                continue
            if (game_id, player_id) in current_game_positions:
                continue
            player_positions = []
            position_string = line['Pos'].lower()
            if position_string == '':
                player_positions.append('n/a')
            else:
                for position in positions:
                    position_string = re.subn(position, '', position_string)
                    if position_string[1] > 0:
                        if position == 'dp':
                            player_positions.append('dh')
                        else:
                            player_positions.append(position)
                    position_string = position_string[0]
                    if position_string == '' or position_string == '/':
                        break
            for position in player_positions:
                all_positions.append({'game_id':  game_id, 'roster_id': player_id,
                                      'position': position})
            current_game_positions.update({(game_id, player_id): None})
    
    position_file_name = FileUtils.get_copy_file_name('positions')
    with open(position_file_name, 'wb') as position_file:
        writer = unicodecsv.DictWriter(position_file, ['game_id', 'roster_id', 'position'])
        writer.writeheader()
        writer.writerows(all_positions)
    
    Database.copy_expert('game_position(game_id, roster_id, position)', position_file_name)
    
    print('{num_positions} position relations created, {bad_ids} players with bad id.'.format(
            num_positions=len(all_positions), bad_ids=players_with_bad_id))


def copy_box_score_lines(year, division):
    """
    Copy each box score type for this year and division into the corresponding stat line table in
    the database.
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    
    ncaa_stat_headers = {
            'hitting':  ['ab', 'h', '2b', '3b', 'hr', 'bb', 'ibb', 'hbp', 'r', 'rbi', 'k', 'sf',
                         'sh', 'dp', 'sb', 'cs'],
            'pitching': ['app', 'gs', 'ordappeared', 'w', 'l', 'sv', 'ip', 'pitches', 'bf', 'h',
                         '2b-a', '3b-a', 'hr-a', 'bb', 'ibb', 'hb', 'r', 'er', 'inh run',
                         'inh run score', 'fo', 'go', 'so', 'kl', 'sfa', 'sha', 'bk', 'wp', 'cg',
                         'sho'],
            'fielding': ['po', 'a', 'e', 'pb', 'ci', 'sba', 'csb', 'idp', 'tp']}
    database_stat_headers = {
            'hitting':  ['ab', 'h', 'dbl', 'tpl', 'hr', 'bb', 'ibb', 'hbp', 'r', 'rbi', 'k', 'sf',
                         'sh', 'dp', 'sb', 'cs'],
            'pitching': ['app', 'gs', 'ord', 'w', 'l', 'sv', 'ip', 'p', 'bf', 'h', 'dbl', 'tpl',
                         'hr', 'bb', 'ibb', 'hbp', 'r', 'er', 'ir', 'irs', 'fo', 'go', 'k', 'kl',
                         'sf', 'sh', 'bk', 'wp', 'cg', 'sho'],
            'fielding': ['po', 'a', 'e', 'pb', 'ci', 'sb', 'cs', 'dp', 'tp']}
    
    all_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    
    all_rosters = {roster['ncaa_id']: roster['roster_id'] for roster in
                   Database.get_all_roster_info() if roster['year'] == year}
    
    for stat_type in ['hitting', 'pitching', 'fielding']:
        print('Copying {stat_type} box scores... '.format(stat_type=stat_type), end='')
        
        current_box_score_lines = {(line[0], line[1]): None for
                                   line in Database.get_all_box_score_lines(stat_type)}
        
        box_score_file_name = FileUtils.get_scrape_file_name(year, division, 'box_score_' +
                                                             stat_type)
        
        new_box_score_lines = []
        
        players_with_bad_id = 0
        
        with open(box_score_file_name, 'rb') as box_score_file:
            reader = unicodecsv.DictReader(box_score_file)
            reader.fieldnames = [field.lower() for field in reader.fieldnames]
            for line in reader:
                if line['player'] == 'Totals':
                    continue
                game_id = all_games[int(line['game_id'])]
                try:
                    player_id = all_rosters[int(line['player_id'])]
                except ValueError:
                    continue
                except KeyError:
                    players_with_bad_id += 1
                    continue
                if (game_id, player_id) in current_box_score_lines:
                    continue
                player_stats = {heading: None for heading in database_stat_headers[stat_type]}
                player_stats.update({'game_id':   game_id,
                                     'roster_id': player_id})
                for i, stat in enumerate(ncaa_stat_headers[stat_type]):
                    try:
                        if line[stat] == '':
                            line[stat] = 0
                    except KeyError:
                        player_stats[database_stat_headers[stat_type][i]] = None
                        continue
                    try:
                        player_stats[database_stat_headers[stat_type][i]] = int(line[stat])
                    except ValueError:
                        player_stats[database_stat_headers[stat_type][i]] = re.sub(r'[^\d.]', '',
                                                                                   line[stat])
                new_box_score_lines.append(player_stats)
                current_box_score_lines.update({(game_id, player_id): None})
        
        copy_file_name = FileUtils.get_copy_file_name('box_score_{stat_type}'
                                                      .format(stat_type=stat_type))
        with open(copy_file_name, 'wb') as copy_file:
            writer = unicodecsv.DictWriter(copy_file, ['game_id', 'roster_id'] +
                                           database_stat_headers[stat_type])
            writer.writeheader()
            writer.writerows(new_box_score_lines)
        
        Database.copy_expert('{stat_type}_line(game_id, roster_id, {stat_headings})'.format(
                stat_type=stat_type, stat_headings=', '.join(database_stat_headers[stat_type])),
                copy_file_name)
        print('{num_lines} new lines.'.format(num_lines=len(new_box_score_lines)))
