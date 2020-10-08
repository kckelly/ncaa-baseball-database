"""
This file puts all the game information into the game table.

@author: Kevin Kelly
"""
from datetime import datetime
import re

import unicodecsv

import Database
import FileUtils
from copiers import Rosters
from copiers import Schools


def copy_game_info(year, division):
    """
    Copy game information into the game table from this year and division.
    
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print('Copying games... ', end='')

    header = ['ncaa_id', 'away_team_id', 'home_team_id', 'date', 'location', 'attendance']

    database_schools = {school['name']: school['ncaa_id'] for school in Database.get_all_schools()}

    database_teams = {team['school_ncaa_id']: team['team_id'] for team in
                      Database.get_all_team_info() if team['year'] == year}

    database_games = {game['ncaa_id']: game for game in Database.get_all_game_info()}

    new_games = []

    new_schools = 0
    new_teams = 0

    game_info_file_name = FileUtils.get_scrape_file_name(year, division, 'game_info')
    with open(game_info_file_name, 'rb') as game_info_file:
        game_info_reader = unicodecsv.DictReader(game_info_file)
        for game in game_info_reader:
            ncaa_id = int(game['game_id'])
            if ncaa_id in database_games:
                continue
            name_changes = {'NYIT': 'New York Tech',
                            'Wheeling Jesuit': 'Wheeling',
                            'Cal St. LA': 'Cal State LA',
                            'California (PA)': 'Cal U (PA)',
                            'Robert Morris-Peoria': 'Roosevelt-Peoria'}
            if game['away_school_name'] in name_changes:
                game['away_school_name'] = name_changes[game['away_school_name']]
            elif game['home_school_name'] in name_changes:
                game['home_school_name'] = name_changes[game['home_school_name']]
            try:
                away_team_id = database_teams[int(game['away_school_id'])]
            except KeyError:
                # if there is no team for this school yet, we check if the school is in the database. If it is not,
                # then we need to create the school and team. If it is in the database, then we just create the team
                # using the school id.
                if game['away_school_name'] in database_schools:
                    away_team_id = Database.create_team(year, game['away_school_id'])
                    database_teams.update({int(game['away_school_id']): int(away_team_id)})
                    new_teams += 1
                else:
                    away_school_id = Schools.add_other_school(game['away_school_name'], game['away_school_id'])
                    database_schools.update({game['away_school_name']: int(game['away_school_id'])})
                    away_team_id = Database.create_team(year, game['away_school_id'])
                    database_teams.update({int(game['away_school_id']): int(away_team_id)})
                    new_schools += 1
                    new_teams += 1
            except ValueError:
                if game['away_school_name'] in database_schools:
                    game['away_school_id'] = database_schools[game['away_school_name']]
                    try:
                        away_team_id = database_teams[int(game['away_school_id'])]
                    except KeyError:
                        away_team_id = Database.create_team(year, game['away_school_id'])
                        database_teams.update({int(game['away_school_id']): int(away_team_id)})
                        new_teams += 1
                else:
                    game['away_school_id'], away_school_id = \
                        Schools.find_and_add_other_school(game['away_school_name'], game['away_team_sport_id'])
                    database_schools.update({game['away_school_name']: int(game['away_school_id'])})
                    away_team_id = Database.create_team(year, game['away_school_id'])
                    database_teams.update({int(game['away_school_id']): int(away_team_id)})
                    new_schools += 1
                    new_teams += 1
        
            try:
                home_team_id = database_teams[int(game['home_school_id'])]
            except KeyError:
                # if there is no team for this school yet, we check if the school is in the database. If it is not,
                # then we need to create the school and team. If it is in the database, then we just create the team
                # using the school id.
                if game['home_school_name'] in database_schools:
                    home_team_id = Database.create_team(year, game['home_school_id'])
                    database_teams.update({int(game['home_school_id']): int(home_team_id)})
                    new_teams += 1
                else:
                    home_school_id = Schools.add_other_school(game['home_school_name'], game['home_school_id'])
                    database_schools.update({game['home_school_name']: int(game['home_school_id'])})
                    home_team_id = Database.create_team(year, game['home_school_id'])
                    database_teams.update({int(game['home_school_id']): int(home_team_id)})
                    new_schools += 1
                    new_teams += 1
            except ValueError:
                if game['home_school_name'] in database_schools:
                    game['home_school_id'] = database_schools[game['home_school_name']]
                    try:
                        home_team_id = database_teams[int(game['home_school_id'])]
                    except KeyError:
                        home_team_id = Database.create_team(year, game['home_school_id'])
                        database_teams.update({int(game['home_school_id']): int(home_team_id)})
                        new_teams += 1
                else:
                    game['home_school_id'], home_school_id = \
                        Schools.find_and_add_other_school(game['home_school_name'], game['home_team_sport_id'])
                    database_schools.update({game['home_school_name']: int(game['home_school_id'])})
                    home_team_id = Database.create_team(year, game['home_school_id'])
                    database_teams.update({int(game['home_school_id']): int(home_team_id)})
                    new_schools += 1
                    new_teams += 1
            
            match = re.search(r'\d{2}/\d{2}/\d{4}', game['date'])
            date = datetime.strptime(match.group(), '%m/%d/%Y').date()
            
            location = game['location']
            
            attendance = game['attendance'].replace(',', '')
        
            new_games.append({'ncaa_id': ncaa_id,
                              'away_team_id': away_team_id,
                              'home_team_id': home_team_id,
                              'date': date,
                              'location': location,
                              'attendance': attendance})

    Database.copy_expert('game(ncaa_id, away_team_id, home_team_id, date, location, attendance)',
                         'game_info', header, new_games)

    print('{num_games} new games. {new_schools} schools added. {new_teams} teams created'.format(num_games=len(
        new_games), new_schools=new_schools, new_teams=new_teams))


def copy_game_innings(year, division):
    """
    Copy each inning of each game into the game_innings table.
    
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print('Copying innings... ', end='')
    database_schools = {school['name']: school['ncaa_id'] for school in Database.get_all_schools()}
    database_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    database_teams = {team['school_ncaa_id']: team['team_id'] for team in
                      Database.get_all_team_info() if team['year'] == year}
    
    database_innings = {(inning['game_id'], inning['team_id']): None for
                        inning in Database.get_all_innings()}
    
    new_innings = []
    inning_file_name = FileUtils.get_scrape_file_name(year, division, 'game_innings')
    with open(inning_file_name, 'rb') as inning_file:
        reader = unicodecsv.reader(inning_file)
        next(reader)  # skip header
        for line in reader:
            game_id = database_games[int(line[1])]
            try:
                team_id = database_teams[int(line[4])]
            except ValueError:
                name_changes = {'NYIT': 'New York Tech',
                                'Wheeling Jesuit': 'Wheeling',
                                'Cal St. LA': 'Cal State LA',
                                'California (PA)': 'Cal U (PA)',
                                'Robert Morris-Peoria': 'Roosevelt-Peoria'}
                if line[3] in name_changes:
                    line[3] = name_changes[line[3]]
                elif line[3] in name_changes:
                    line[3] = name_changes[line[3]]
                school_id = database_schools[line[3]]
                team_id = database_teams[school_id]
            if (game_id, team_id) in database_innings:
                continue

            inning_num = 1
            for inning in line[5:]:
                if inning == '':
                    continue
                new_innings.append({'game_id': game_id, 'team_id': team_id, 'inning': inning_num,
                                    'runs': inning})
                inning_num += 1
            
            database_innings.update({(game_id, team_id): None})
    
    header = ['game_id', 'team_id', 'inning', 'runs']
    Database.copy_expert('inning(game_id, team_id, inning, runs)', 'innings', header, new_innings)
    
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

    database_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}

    all_players = {player['ncaa_id']: player['player_id'] for player in Database.get_all_players()}

    database_rosters = {roster['ncaa_id']: roster['roster_id'] for roster in
                        Database.get_all_roster_info() if roster['year'] == year}

    all_players_by_name = {
        (roster['first_name'], roster['last_name'], roster['team_id']): roster['roster_id'] for
        roster in Database.get_all_roster_info() if roster['year'] == year}

    database_teams = {team['school_name']: team['team_id'] for team in Database.get_all_team_info()
                      if team['year'] == year}

    database_game_positions = {(game_position['game_id'], game_position['roster_id']): None for
                               game_position in Database.get_all_game_position_info()}

    box_score_file_name = FileUtils.get_scrape_file_name(year, division, 'box_score_fielding')

    new_positions = []

    no_names = 0
    new_players = 0
    new_rosters = 0

    unknown_schools = set()

    with open(box_score_file_name, 'rb') as box_score_file:
        reader = unicodecsv.DictReader(box_score_file)
        for line in reader:
            if line['Player'] == 'Totals':
                continue
            game_id = database_games[int(line['game_id'])]
        
            try:
                roster_id = database_rosters[int(line['player_id'])]
            except ValueError:
                name_changes = {'NYIT': 'New York Tech',
                                'Wheeling Jesuit': 'Wheeling',
                                'Cal St. LA': 'Cal State LA',
                                'California (PA)': 'Cal U (PA)',
                                'Robert Morris-Peoria': 'Roosevelt-Peoria'}
                if line['school_name'] in name_changes:
                    line['school_name'] = name_changes[line['school_name']]
                last_name = line['Player'].split(',', 1)[0].strip()
                if last_name == '':
                    no_names += 1
                    continue
                try:
                    first_name = line['Player'].split(',', 1)[1].strip()
                except IndexError:
                    first_name = 'N/A'
                try:
                    roster_id = all_players_by_name.get((first_name, last_name, database_teams[line['school_name']]))
                    if roster_id is None:
                        if line['player_id'] != '' and int(line['player_id']) in all_players:
                            roster_id = Rosters.create_roster(all_players[int(line['player_id'])],
                                                              database_teams[line['school_name']])
                            new_rosters += 1
                        else:
                            player_id, roster_id = \
                                Rosters.add_player_and_create_roster(first_name, last_name, line['player_id'],
                                                                     database_teams[line['school_name']])
                            all_players_by_name.update({(first_name, last_name,
                                                         database_teams[line['school_name']]): roster_id})
                            if line['player_id'] != '':
                                database_rosters.update({int(line['player_id']): roster_id})
                                all_players.update({int(line['player_id']): player_id})
                            new_players += 1
                            new_rosters += 1
                except KeyError:
                    unknown_schools.update({(line['school_name'], line['school_id'])})
                    continue
                except IndexError:
                    if line['player_id'] != '' and int(line['player_id']) in all_players:
                        roster_id = Rosters.create_roster(all_players[int(line['player_id'])],
                                                          database_teams[line['school_name']])
                        new_rosters += 1
                    else:
                        player_id, roster_id = \
                            Rosters.add_player_and_create_roster(first_name, last_name, line['player_id'],
                                                                 database_teams[line['school_name']])
                        all_players_by_name.update({(first_name, last_name,
                                                     database_teams[line['school_name']]): roster_id})
                        if line['player_id'] != '':
                            database_rosters.update({int(line['player_id']): roster_id})
                            all_players.update({int(line['player_id']): player_id})
                        new_players += 1
                        new_rosters += 1
            except KeyError:
                name_changes = {'NYIT': 'New York Tech',
                                'Wheeling Jesuit': 'Wheeling',
                                'Cal St. LA': 'Cal State LA',
                                'California (PA)': 'Cal U (PA)',
                                'Robert Morris-Peoria': 'Roosevelt-Peoria'}
                if line['school_name'] in name_changes:
                    line['school_name'] = name_changes[line['school_name']]
                last_name = line['Player'].split(',', 1)[0].strip()
                if last_name == '':
                    no_names += 1
                    continue
                try:
                    first_name = line['Player'].split(',', 1)[1].strip()
                except IndexError:
                    first_name = 'N/A'
                try:
                    roster_id = all_players_by_name.get((first_name, last_name, database_teams[line['school_name']]))
                    if roster_id is None:
                        if line['player_id'] != '' and int(line['player_id']) in all_players:
                            roster_id = Rosters.create_roster(all_players[int(line['player_id'])],
                                                              database_teams[line['school_name']])
                            database_rosters.update({int(line['player_id']): all_players[int(line['player_id'])]})
                            all_players_by_name.update({(first_name, last_name,
                                                         database_teams[line['school_name']]): roster_id})
                            new_rosters += 1
                        else:
                            player_id, roster_id = \
                                Rosters.add_player_and_create_roster(first_name, last_name, line['player_id'],
                                                                     database_teams[line['school_name']])
                            all_players_by_name.update({(first_name, last_name,
                                                         database_teams[line['school_name']]): roster_id})
                            if line['player_id'] != '':
                                database_rosters.update({int(line['player_id']): roster_id})
                                all_players.update({int(line['player_id']): player_id})
                            new_players += 1
                            new_rosters += 1
                except KeyError:
                    unknown_schools.update({(line['school_name'], line['school_id'])})
                    continue
                except IndexError:
                    if line['player_id'] != '' and int(line['player_id']) in all_players:
                        roster_id = Rosters.create_roster(all_players[int(line['player_id'])],
                                                          database_teams[line['school_name']])
                        database_rosters.update({int(line['player_id']): all_players[int(line['player_id'])]})
                        all_players_by_name.update({(first_name, last_name,
                                                     database_teams[line['school_name']]): roster_id})
                        new_rosters += 1
                    else:
                        player_id, roster_id = \
                            Rosters.add_player_and_create_roster(first_name, last_name, line['player_id'],
                                                                 database_teams[line['school_name']])
                        all_players_by_name.update({(first_name, last_name,
                                                     database_teams[line['school_name']]): roster_id})
                        if line['player_id'] != '':
                            database_rosters.update({int(line['player_id']): roster_id})
                            all_players.update({int(line['player_id']): player_id})
                        new_players += 1
                        new_rosters += 1
            if (game_id, roster_id) in database_game_positions:
                continue
            
            player_positions = []
            position_string = line['Pos'].lower()
            if position_string == '':
                player_positions.append('n/a')
            else:
                # Gets all positions a player played in a game by removing positions from the
                # position string one by one. For instance a position_string that looks like
                # 'prlf' will return ['pr', 'lf'].
                for position in positions:
                    position_string = re.subn(position, '', position_string)
                    if position_string[1] > 0:
                        # designated hitter is written as dp or designated player in some box scores
                        if position == 'dp':
                            player_positions.append('dh')
                        else:
                            player_positions.append(position)
                    position_string = position_string[0]  # gets the old position string without
                    # the position we just found
                    # if the position string is empty or contains just a slash all positions have
                    # been found
                    if position_string == '' or position_string == '/':
                        break
        
            for position in player_positions:
                new_positions.append({'game_id': game_id,
                                      'roster_id': roster_id,
                                      'position': position})
            database_game_positions.update({(game_id, roster_id): None})

    header = ['game_id', 'roster_id', 'position']
    Database.copy_expert('game_position(game_id, roster_id, position)', 'positions', header,
                         new_positions)

    print('{num_positions} position relations created. {new_players} players added. {new_rosters} roster relations '
          'created. {no_names} players with no name. {unknown_schools} unknown schools.'
          .format(num_positions=len(new_positions), new_players=new_players, new_rosters=new_rosters,
                  no_names=no_names, unknown_schools=len(unknown_schools)))


def copy_box_score_lines(year, division):
    """
    Copy each box score type for this year and division into the corresponding stat line table in
    the database.
    
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    
    ncaa_stat_headers = {
        'hitting': ['ab', 'h', '2b', '3b', 'hr', 'bb', 'ibb', 'hbp', 'r', 'rbi', 'k', 'sf',
                    'sh', 'dp', 'sb', 'cs'],
        'pitching': ['app', 'gs', 'ordappeared', 'w', 'l', 'sv', 'ip', 'pitches', 'bf', 'h',
                     '2b-a', '3b-a', 'hr-a', 'bb', 'ibb', 'hb', 'r', 'er', 'inh run',
                     'inh run score', 'fo', 'go', 'so', 'kl', 'sfa', 'sha', 'bk', 'wp', 'cg',
                     'sho'],
        'fielding': ['po', 'a', 'e', 'pb', 'ci', 'sba', 'csb', 'idp', 'tp']}
    database_stat_headers = {
        'hitting': ['ab', 'h', 'dbl', 'tpl', 'hr', 'bb', 'ibb', 'hbp', 'r', 'rbi', 'k', 'sf',
                    'sh', 'dp', 'sb', 'cs'],
        'pitching': ['app', 'gs', 'ord', 'w', 'l', 'sv', 'ip', 'p', 'bf', 'h', 'dbl', 'tpl',
                     'hr', 'bb', 'ibb', 'hbp', 'r', 'er', 'ir', 'irs', 'fo', 'go', 'k', 'kl',
                     'sf', 'sh', 'bk', 'wp', 'cg', 'sho'],
        'fielding': ['po', 'a', 'e', 'pb', 'ci', 'sb', 'cs', 'dp', 'tp']}
    
    database_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    
    database_rosters = {roster['ncaa_id']: roster['roster_id'] for roster in
                        Database.get_all_roster_info() if roster['year'] == year}
    
    all_players_by_name = {
        (roster['first_name'], roster['last_name'], roster['team_id']): roster['roster_id'] for
        roster in Database.get_all_roster_info() if roster['year'] == year}
    
    database_teams = {team['school_name']: team['team_id'] for team in Database.get_all_team_info()
                      if team['year'] == year}
    
    for stat_type in ['hitting', 'pitching', 'fielding']:
        print('Copying {stat_type} box scores... '.format(stat_type=stat_type), end='')
    
        database_box_score_lines = {(line[0], line[1]): None for
                                    line in Database.get_all_box_score_lines(stat_type)}
    
        stat_file_name = 'box_score_' + stat_type
        box_score_file_name = FileUtils.get_scrape_file_name(year, division, stat_file_name)
    
        new_box_score_lines = []
    
        no_names = 0
        no_roster_id = 0
    
        unknown_schools = set()
    
        with open(box_score_file_name, 'rb') as box_score_file:
            reader = unicodecsv.DictReader(box_score_file)
            reader.fieldnames = [field.lower() for field in reader.fieldnames]
            for line in reader:
                if line['player'] == 'Totals':
                    continue
            
                game_id = database_games[int(line['game_id'])]
            
                try:
                    roster_id = database_rosters[int(line['player_id'])]
                except ValueError:
                    name_changes = {'NYIT': 'New York Tech',
                                    'Wheeling Jesuit': 'Wheeling',
                                    'Cal St. LA': 'Cal State LA',
                                    'California (PA)': 'Cal U (PA)',
                                    'Robert Morris-Peoria': 'Roosevelt-Peoria'}
                    if line['school_name'] in name_changes:
                        line['school_name'] = name_changes[line['school_name']]
                    last_name = line['player'].split(',', 1)[0].strip()
                    if last_name == '':
                        no_names += 1
                        continue
                    try:
                        first_name = line['player'].split(',', 1)[1].strip()
                    except IndexError:
                        first_name = 'N/A'
                    try:
                        roster_id = all_players_by_name.get(
                            (first_name, last_name, database_teams[line['school_name']]))
                        if roster_id is None:
                            no_roster_id += 1
                            continue
                    except KeyError:
                        unknown_schools.update({(line['school_name'], line['school_id'])})
                        continue
                except KeyError:
                    name_changes = {'NYIT': 'New York Tech',
                                    'Wheeling Jesuit': 'Wheeling',
                                    'Cal St. LA': 'Cal State LA',
                                    'California (PA)': 'Cal U (PA)',
                                    'Robert Morris-Peoria': 'Roosevelt-Peoria'}
                    if line['school_name'] in name_changes:
                        line['school_name'] = name_changes[line['school_name']]
                    last_name = line['player'].split(',', 1)[0].strip()
                    if last_name == '':
                        no_names += 1
                        continue
                    try:
                        first_name = line['player'].split(',', 1)[1].strip()
                    except IndexError:
                        first_name = 'N/A'
                    try:
                        roster_id = all_players_by_name.get(
                            (first_name, last_name, database_teams[line['school_name']]))
                        if roster_id is None:
                            no_roster_id += 1
                            continue
                    except KeyError:
                        unknown_schools.update({(line['school_name'], line['school_id'])})
                        continue
                
                if (game_id, roster_id) in database_box_score_lines:
                    continue
                
                player_stats = {heading: None for heading in database_stat_headers[stat_type]}
                player_stats.update({'game_id': game_id,
                                     'roster_id': roster_id})
                for i, stat in enumerate(ncaa_stat_headers[stat_type]):
                    try:
                        if line[stat] == '':
                            line[stat] = 0
                    except KeyError:
                        # not all years have the same statistics, if that stat was not kept for
                        # this box score then we just set the value of the statistic to None
                        player_stats[database_stat_headers[stat_type][i]] = None
                        continue
                    try:
                        player_stats[database_stat_headers[stat_type][i]] = int(line[stat])
                    except ValueError:
                        # sometimes stats have non-numerical characters like '-' and ',',
                        # we remove them with this regex if the previous cast results in a
                        # ValueError
                        player_stats[database_stat_headers[stat_type][i]] = re.sub(r'[^\d.]', '',
                                                                                   line[stat])
            
                new_box_score_lines.append(player_stats)
                database_box_score_lines.update({(game_id, roster_id): None})
    
        header = ['game_id', 'roster_id'] + database_stat_headers[stat_type]
        Database.copy_expert('{stat_type}_line(game_id, roster_id, {stat_headings})'.format(
            stat_type=stat_type, stat_headings=', '.join(database_stat_headers[stat_type])),
            'box_score_{stat_type}'.format(stat_type=stat_type), header, new_box_score_lines)
    
        print('{num_lines} new lines. {no_name} players with no name. {unknown_schools} unknown schools.'
              .format(num_lines=len(new_box_score_lines), no_name=no_names, unknown_schools=len(unknown_schools)))
