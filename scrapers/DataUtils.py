"""
File containing helper methods for accessing scraped data to be used in other scrapers.
"""
import unicodecsv

import FileUtils


def get_school_id_dict():
    """
    Return a dict of school codes, use the school name to get the code for that school.
    
    @return: a dict of all school codes
    """
    file_name = 'scraped-data/school_ids.csv'
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return {row['school']: row['id'] for row in reader}


def get_teams(year, division):
    """
    Gets all teams in a division for the specified year.
    
    @param year: the year to get teams for
    @param division: the division of the teams
    @return: a list of teams in the division and year specified
    """
    file_name = FileUtils.get_file_name(year, division, 'teams')
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return [[row['team'], row['url']] for row in reader]


def get_games_from_schedule(year, division):
    """
    Gets all game urls in a division for the specified year.
    
    @param year: the year to get games for
    @param division: the division of the games
    @return: a list of games in the division and year specified
    """
    file_name = FileUtils.get_file_name(year, division, 'schedules')
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return [[row['school'], row['date'], row['opponent_school'], row['game_link']] for row in
                reader]
