"""
File containing helper methods for accessing scraped data to be used in other scrapers.
"""
import unicodecsv

import FileUtils


def get_school_id_dict():
    """
    Return a dict of all school codes, use the school name to get the code for that school.
    
    @return: a dict of all school codes
    """
    file_name = 'scraped-data/school_ids.csv'
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return {row['school_name']: row['school_id'] for row in reader}


def get_schools(year, division):
    """
    Gets all schools in a division for the specified year.
    
    @param year: the year to get schools for
    @param division: the division of the schools
    @return: a list of team dicts in the division and year specified, the dicts contain two
    items, 'school_name' for school name and 'school_id' for school code
    """
    file_name = FileUtils.get_file_name(year, division, 'schools')
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return [{'school_name': row['school_name'], 'school_id': row['school_id']} for row in
                reader]


def get_games_from_schedule(year, division):
    """
    Gets all game schedule data in a division for the specified year.
    
    @param year: the year to get games for
    @param division: the division of the games
    @return: a list of game dicts in the division and year specified, the dicts contain four
    items, 'school_name' for school name, 'date' for the date of the game, 'opponent_string' for the
    opponent name and some other information (@ for away game and some others), and 'game_url for
    the url of the game
    """
    file_name = FileUtils.get_file_name(year, division, 'schedules')
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return [{'school_name':     row['school_name'],
                 'date':            row['date'],
                 'opponent_string': row['opponent_string'],
                 'game_url':        row['game_url']}
                for row in
                reader]


def get_games_from_game_info(year, division):
    """
    Gets all game information for each game in a division for the specified year.
    
    @param year: the year to get games for
    @param division: the division of the games
    @return a list of game dicts that contain game information for that game
    """
    game_info_file_name = FileUtils.get_file_name(year, division, 'game_info')
    with open(game_info_file_name, 'rb') as game_info_file:
        game_info_reader = unicodecsv.DictReader(game_info_file)
        return [game for game in game_info_reader]
