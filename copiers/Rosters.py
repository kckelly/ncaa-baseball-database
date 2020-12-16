"""
This file adds all players to the database and creates roster relations.

@author: Kevin Kelly
"""
import unicodecsv

from jmu_baseball_utils import file_utils
from database_files.ncaa_database import NCAADatabase


def copy_players(database: NCAADatabase, year, division):
    """
    Copy players from this year and division to the database.
    
    :param database: the ncaa database
    :param year: the year the players played at
    :param division: the divisions the players were in
    :return: None
    """
    print('Copying players... ', end='')
    
    all_players_by_ncaa_id = {player['ncaa_id']: player['player_id'] for player in
                              database.get_all_players()}
    
    new_players = []
    roster_file_name = file_utils.get_scrape_file_name(year, division, 'rosters')
    with open(roster_file_name, 'rb') as roster_file:
        reader = unicodecsv.DictReader(roster_file)
        for line in reader:
            try:
                ncaa_id = int(line['player_id'])
            except ValueError:
                continue
            if ncaa_id in all_players_by_ncaa_id:
                continue
            
            # names are scraped in the format 'last_name, first_name'
            first_name = line['player_name'].split(',', 1)[1].strip()
            last_name = line['player_name'].split(',', 1)[0].strip()
            
            # some players have empty names, I chose to ignore them
            if last_name == '':
                continue
            
            # null values are not allowed for first names so if they have a last name I still add
            # them to the database and change their first name to 'N/A'
            if first_name == '':
                first_name = 'N/A'
            
            all_players_by_ncaa_id.update(
                {ncaa_id: None})  # necessary because of some silly duplicates
            
            new_players.append({'ncaa_id': ncaa_id,
                                'first_name': first_name,
                                'last_name': last_name})
    
    header = ['ncaa_id', 'first_name', 'last_name']
    database.copy_expert('player(ncaa_id, first_name, last_name)', 'players', header, new_players)
    
    print('{num_players} new players.'.format(num_players=len(new_players)))


def create_rosters(database: NCAADatabase, year, division):
    """
    Create roster relations for this year and division.
    
    :param database: the ncaa database
    :param year: the year of the players and teams
    :param division: the divisions the teams played at
    :return: None
    """
    print('Creating rosters... ', end='')
    
    all_players_by_ncaa_id = {player['ncaa_id']: player['player_id'] for player in
                              database.get_all_players()}
    
    # all teams from this year
    year_teams_by_ncaa_id = {team['school_ncaa_id']: team['team_id'] for team in
                             database.get_all_team_info() if team['year'] == year}
    year_teams_by_name = {team['school_name']: team['team_id'] for team in
                          database.get_all_team_info() if team['year'] == year}
    
    database_roster_rows = {(roster['team_id'], roster['player_id']): roster['ncaa_id'] for roster
                            in database.get_all_roster_info()}
    
    player_class_map = {'fr': 'freshman', 'so': 'sophomore', 'jr': 'junior', 'sr': 'senior',
                        'n/a': 'n/a'}
    new_roster_rows = []
    roster_file_name = file_utils.get_scrape_file_name(year, division, 'rosters')
    with open(roster_file_name, 'rb') as roster_file:
        reader = unicodecsv.DictReader(roster_file)
        for line in reader:
            try:
                player_ncaa_id = int(line['player_id'])
                player_id = all_players_by_ncaa_id[player_ncaa_id]
            except (KeyError, ValueError):
                continue
            try:
                team_id = year_teams_by_ncaa_id[int(line['school_id'])]
            except KeyError:
                team_id = year_teams_by_name[line['school_name']]
            
            # skip if the player is already in the database
            if (team_id, player_id) in database_roster_rows:
                continue
            
            database_roster_rows.update({(team_id, player_id): player_ncaa_id})
            
            player_class = player_class_map[line['class'].lower()]
            new_roster_rows.append({'team_id': team_id,
                                    'player_id': player_id,
                                    'class': player_class})
    
    header = ['team_id', 'player_id', 'class']
    database.copy_expert('roster(team_id, player_id, class)', 'rosters', header, new_roster_rows)
    
    print('{num_players} new roster rows.'.format(num_players=len(new_roster_rows)))


def add_player_and_create_roster(database: NCAADatabase, first_name, last_name, player_ncaa_id, team_id):
    """
    Add a player to the player table and create the corresponding row in the roster table.
    
    :param database: the ncaa database
    :param first_name: the first name of the player
    :param last_name: the last name of the player
    :param player_ncaa_id: the ncaa id of the player
    :param team_id: the team id of the team in the database
    :return: the player id and roster id of the added player
    """
    cursor = database.cursor
    
    if player_ncaa_id == '':
        player_ncaa_id = None
    
    cursor.execute('INSERT INTO player(ncaa_id, first_name, last_name) '
                   'VALUES(%s, %s, %s) '
                   'RETURNING id', (player_ncaa_id, first_name, last_name))
    player_id = cursor.fetchone()[0]
    
    roster_id = create_roster(database, player_id, team_id)
    return player_id, roster_id


def create_roster(database: NCAADatabase, player_id, team_id):
    """
    Create a row in the roster table for this player and team.
    
    :param database: the ncaa database
    :param player_id: the id of the player
    :param team_id: the id of the team
    :return: the roster id of the new roster row
    """
    
    cursor = database.cursor
    cursor.execute('INSERT INTO roster(team_id, player_id, class)'
                   'VALUES(%s, %s, %s) '
                   'RETURNING id', (team_id, player_id, 'n/a'))
    
    roster_id = cursor.fetchone()[0]
    return roster_id
