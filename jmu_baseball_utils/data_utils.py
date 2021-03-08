"""
File containing helper methods for accessing scraped data to be used in other scrapers.
"""
from typing import Optional

import unicodecsv
from difflib import SequenceMatcher

from dropbox import Dropbox
from dropbox.files import FileMetadata
from strsimpy.jaro_winkler import JaroWinkler

from jmu_baseball_utils import file_utils

jaro_winkler = JaroWinkler()


def get_year_info(year: int) -> dict:
    """
    Get the ids for the year specified. PLEASE NOTE THAT THE YEAR INFO FILE THAT THIS FUNCTION GETS ITS DATA FROM
    MUST BE UPDATED ONCE A YEAR MANUALLY.

    :param year: the year to get the ids of
    :return: a dict containing the year_id, hitting_id, pitching_id, and fielding_id for that year, or an empty dict
    if the year is not in the file
    """
    file_name = file_utils.get_year_info_file_name()
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        for line in reader:
            if year == int(line['year']):
                return line
    return {}


def get_school_id_dict() -> dict:
    """
    Return a dict of all school codes, use the school name to get the code for that school.
    
    :return: a dict of all school codes in the format {school_name: school_id}
    """
    file_name = file_utils.get_school_id_file_name()
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return {row['school_name']: row['school_id'] for row in reader}


def get_schools(year: int, division: int) -> list:
    """
    Gets all schools in a division for the specified year.
    
    :param year: the year to get schools for
    :param division: the division of the schools
    :return: a list of team dicts in the division and year specified, the dicts contain two
    items, 'school_name' for school name and 'school_id' for school code
    """
    file_name = file_utils.get_scrape_file_name(year, division, 'conference_teams')
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return [{'school_name': row['school_name'], 'school_id': row['school_id']} for row in
                reader]


def get_games_from_schedule(year: int, division: int) -> list:
    """
    Gets all game schedule data in a division for the specified year.
    
    :param year: the year to get games for
    :param division: the division of the games
    :return: a list of game dicts in the division and year specified, the dicts contain four
    items, 'school_name' for school name, 'date' for the date of the game, 'opponent_string' for the
    opponent name and some other information (@ for away game and some others), and 'game_url for
    the url of the game
    """
    file_name = file_utils.get_scrape_file_name(year, division, 'schedules')
    with open(file_name, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return [{'school_name': row['school_name'],
                 'date': row['date'],
                 'opponent_string': row['opponent_string'],
                 'game_url': row['game_url']}
                for row in
                reader]


def get_games_from_game_info(year: int, division: int) -> list:
    """
    Gets all game information for each game in a division for the specified year.
    
    :param year: the year to get games for
    :param division: the division of the games
    :return a list of game dicts that contain game information for that game
    """
    game_info_file_name = file_utils.get_scrape_file_name(year, division, 'game_info')
    with open(game_info_file_name, 'rb') as game_info_file:
        game_info_reader = unicodecsv.DictReader(game_info_file)
        return [game for game in game_info_reader]


def get_player_id_from_name(pbp_name: str, player_dict: dict) -> (str, int, float):
    """
    Get the player id of the player with the name closest to the name found in the play by play. Uses SequenceMatcher to
    find the longest match between each player's name in the player_dict and pbp_name. If two players have the same
    match length, the JaroWinkler similarity function is used to determine which player is a better match. This
    method is not guaranteed to return the correct player.

    :param pbp_name: the player name extracted from a play by play string
    :param player_dict: a dict of players formatted like this: {player_id: {'first_name': first, 'last_name': last}}
    :return: a tuple of the player id of the best match, the length of that match, and the jaro winkler similarity,
    or (None, None, None) if no player matches this name at all (some pbp names are just jersey numbers)
    """
    length = 0
    found_roster_id = None
    found_player_name = None
    for roster_id in player_dict:
        name_dict = player_dict[roster_id]
        player_name = name_dict['first_name'].lower() + ' ' + name_dict['last_name'].lower()
        s = SequenceMatcher(a=pbp_name.lower(), b=player_name)
        match = s.find_longest_match(0, len(pbp_name.lower()), 0, len(player_name))
        new_length = match.size
        if new_length > length:
            found_roster_id = roster_id
            found_player_name = player_name
            length = new_length
        elif length != 0 and new_length == length:
            old_similarity = jaro_winkler.similarity(found_player_name, pbp_name.lower())
            new_similarity = jaro_winkler.similarity(player_name, pbp_name.lower())
            if new_similarity > old_similarity:
                found_roster_id = roster_id
                found_player_name = player_name
    if found_player_name is None:
        return None, None, None
    return found_roster_id, length, jaro_winkler.similarity(found_player_name, pbp_name.lower())


def split_name(name: str) -> tuple:
    """
    Split a player's name from the ncaa site. Names are usually in the format last_name, first_name. Sometimes they
    include a suffix either like this: suffix, last_name, first_name or like this: last_name, first_name suffix.
    :param name: the name of the player
    :return: a tuple of the player's name in this format: (first_name, last_name, suffix). If the player does not
    have a suffix, the suffix is set to None. If the player does not have a first name, it is set to 'N/A'.
    """
    first_name = name.split(',', 1)[1].strip()
    last_name = name.split(',', 1)[0].strip()
    suffixes = ['Jr.', 'II', 'III', 'IV', 'V']
    name_suffix = None
    for suffix in suffixes:
        if first_name.startswith(f'{suffix}, '):
            name_suffix = suffix.replace('.', '')
            first_name = first_name.replace(f'{suffix}, ', '')
        if last_name.endswith(f' {suffix}'):
            name_suffix = suffix.replace('.', '')
            last_name = last_name.replace(f' {suffix}', '')
    if last_name == '':
        return None, None, None
    if first_name == '':
        first_name = 'N/A'
    return first_name, last_name, name_suffix


def upload_data(dbx: Dropbox, file_path: str, data_type: str, file_name: str, year: int = None, division: int = None) \
        -> None:
    """
    Upload this file to a dropbox folder.

    :param dbx: the dropbox connection
    :param file_path: the path of the file to upload
    :param data_type: the type of data this is (scraped-data, spray_charts, hit_location_data, etc.)
    :param file_name: the name of the file to be created
    :param year: the year of this data. Note: year and division must both have values if they are to be used
    :param division: the division of this data. Note: year and division must both have values if they are to be used
    :return: None
    """
    with open(file_path, 'rb') as file:
        if year and division:
            dbx_file_name = f'/{data_type}/{year}/division_{division}/{file_name}'
        else:
            dbx_file_name = f'/{data_type}/{file_name}'
        print(f'Uploading to {dbx_file_name}... ', end='')
        dbx.files_upload(file.read(), dbx_file_name)
        print('complete')


def download_all_data(dbx: Dropbox, data_type: str) -> None:
    """
    Download all data from a dropbox folder.

    :param dbx: the dropbox connection
    :param data_type: the type of data this is (scraped-data, spray_charts, hit_location_data, etc.)
    :return: None
    """
    metadata = dbx.files_list_folder(f'/{data_type}', recursive=True)
    while metadata.has_more:
        entries = metadata.entries
        for entry in entries:
            if isinstance(entry, FileMetadata):
                print(f'Downloading to {entry.path_display}... ', end='')
                file_name = entry.name
                path = entry.path_display.replace(file_name, '')
                dbx.files_download_to_file(f'{file_utils.get_path(f"../{path}")}/{file_name}', entry.path_display)
                print('complete')
        metadata = dbx.files_list_folder_continue(metadata.cursor)
    print(f'Finished downloading all {data_type} files')
