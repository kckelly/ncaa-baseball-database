"""
Copies all umpire information into the umpire and game_umpire tables.

@author: Kevin Kelly
"""
import unicodecsv

import Database
import FileUtils


def copy_umpires(year, division):
    """
    Copy umpires from the game_info file in this year and division.
    
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print('Copying umpires... ', end='')
    database_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    
    database_umpires = {(umpire['first_name'], umpire['last_name']): umpire['id'] for
                        umpire in Database.get_all_umpires()}
    
    database_umpire_games = Database.get_all_game_umpires()
    
    game_info_file_name = FileUtils.get_scrape_file_name(year, division, 'game_info')
    
    new_umpires = []
    with open(game_info_file_name, 'rb') as game_info_file:
        reader = unicodecsv.DictReader(game_info_file)
        for game in reader:
            if database_games[int(game['game_id'])] in database_umpire_games:
                continue
            
            for ump_position in ['hp_official', '1b_official', '2b_official', '3b_official']:
                ump = game[ump_position]
                
                try:
                    ump_first_name = ump.split(' ', 1)[0]
                    ump_last_name = ump.split(' ', 1)[1].split('\\">')[0]
                except IndexError:
                    continue
                
                # TODO: Get umpires in lf and rf from game notes
                
                if (ump_first_name, ump_last_name) not in database_umpires:
                    new_umpires.append({'first_name': ump_first_name,
                                        'last_name': ump_last_name})
                    database_umpires.update({(ump_first_name, ump_last_name): None})
    
    header = ['first_name', 'last_name']
    Database.copy_expert('umpire(first_name, last_name)', 'umpires', header, new_umpires)
    
    print('{num_umpires} new umpires.'.format(num_umpires=len(new_umpires)))


def create_umpire_games(year, division):
    """
    Create the game to umpire relations in the game_umpire table.
    
    :param year: the year of the games
    :param division: the division the games were played at
    :return: None
    """
    print('Copying umpires... ', end='')
    database_games = {game['ncaa_id']: game['id'] for game in Database.get_all_game_info()}
    
    database_umpires = {(umpire['first_name'], umpire['last_name']): umpire['id'] for
                        umpire in Database.get_all_umpires()}
    
    database_umpire_games = Database.get_all_game_umpires()
    
    game_info_file_name = FileUtils.get_scrape_file_name(year, division, 'game_info')
    new_umpire_games = []
    with open(game_info_file_name, 'rb') as game_info_file:
        reader = unicodecsv.DictReader(game_info_file)
        
        for game in reader:
            game_id = database_games[int(game['game_id'])]
            if game_id in database_umpire_games:
                continue
            
            for ump_position in ['hp_official', '1b_official', '2b_official', '3b_official']:
                ump = game[ump_position]
                try:
                    ump_first_name = ump.split(' ', 1)[0]
                    ump_last_name = ump.split(' ', 1)[1].split('\\">')[0]
                except IndexError:
                    continue
                umpire_id = database_umpires[(ump_first_name, ump_last_name)]
                new_umpire_games.append({'game_id': game_id,
                                         'umpire_id': umpire_id,
                                         'position': ump_position.replace('_official', '')})
    
    header = ['game_id', 'umpire_id', 'position']
    Database.copy_expert('game_umpire(game_id, umpire_id, position)', 'game_umpires', header,
                         new_umpire_games)
    
    print('{num_umpires} new umpire games.'.format(num_umpires=len(new_umpire_games)))
