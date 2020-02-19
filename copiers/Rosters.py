"""
This file adds all players to the database and creates roster relations.
"""
import unicodecsv

import Database
import FileUtils


def copy_players(year, division):
    """
    Copy players from this year and division to the database.
    :param year: the year the players played at
    :param division: the divisions the players were in
    :return: None
    """
    print('Copying players... ', end='')
    
    all_players_by_id = {player['ncaa_id']: player['player_id'] for player in
                         Database.get_all_players()}
    
    players = []
    roster_file_name = FileUtils.get_scrape_file_name(year, division, 'rosters')
    with open(roster_file_name, 'rb') as roster_file:
        reader = unicodecsv.DictReader(roster_file)
        for line in reader:
            try:
                ncaa_id = int(line['player_id'])
            except ValueError:
                continue
            if ncaa_id in all_players_by_id:
                continue
            first_name = line['player_name'].split(',', 1)[1].strip()
            last_name = line['player_name'].split(',', 1)[0].strip()
            if (first_name, last_name) == ('', ''):
                continue
            if first_name == '':
                first_name = 'N/A'
            all_players_by_id.update({ncaa_id: None})  # necessary because of some silly duplicates
            players.append({'ncaa_id': ncaa_id, 'first_name': first_name, 'last_name': last_name})
    
    copy_file_name = FileUtils.get_copy_file_name('players')
    with open(copy_file_name, 'wb') as copy_file:
        writer = unicodecsv.DictWriter(copy_file, ['ncaa_id', 'first_name', 'last_name'])
        writer.writeheader()
        writer.writerows(players)
    
    Database.copy_expert('player(ncaa_id, first_name, last_name)', copy_file_name)
    
    print('{num_players} new players.'.format(num_players=len(players)))


def create_rosters(year, division):
    """
    Create roster relations for this year and division.
    :param year: the year of the players and teams
    :param division: the divisions the teams played at
    :return: None
    """
    print('Creating rosters... ', end='')
    
    all_players_by_id = {player['ncaa_id']: player['player_id'] for player in
                         Database.get_all_players()}
    year_teams_by_ncaa_id = {team['school_ncaa_id']: team['team_id'] for team in
                             Database.get_all_team_info() if team['year'] == year}
    all_roster_info = {(roster['team_id'], roster['player_id']): roster['ncaa_id'] for roster in
                       Database.get_all_roster_info()}
    player_class_map = {'fr': 'freshman', 'so': 'sophomore', 'jr': 'junior', 'sr': 'senior',
                        'n/a': 'n/a'}
    roster_rows = []
    roster_file_name = FileUtils.get_scrape_file_name(year, division, 'rosters')
    with open(roster_file_name, 'rb') as roster_file:
        reader = unicodecsv.DictReader(roster_file)
        for line in reader:
            try:
                player_id = all_players_by_id[int(line['player_id'])]
            except (KeyError, ValueError):
                continue
            team_id = year_teams_by_ncaa_id[int(line['school_id'])]
            if (team_id, player_id) in all_roster_info:
                continue
            all_roster_info.update({(team_id, player_id): None})
            player_school_year = player_class_map[line['class'].lower()]
            roster_rows.append({'team_id': team_id, 'player_id': player_id,
                                'class':   player_school_year})
    
    copy_file_name = FileUtils.get_copy_file_name('rosters')
    with open(copy_file_name, 'wb') as copy_file:
        writer = unicodecsv.DictWriter(copy_file, ['team_id', 'player_id', 'class'])
        writer.writeheader()
        writer.writerows(roster_rows)
    
    Database.copy_expert('roster(team_id, player_id, class)', copy_file_name)
    
    print('{num_players} new roster rows.'.format(num_players=len(roster_rows)))
