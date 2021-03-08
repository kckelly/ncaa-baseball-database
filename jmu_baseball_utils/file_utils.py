"""
File containing multiple helper methods for the scraped csv data.
"""
import os
import pathlib

import unicodecsv
from dropbox import Dropbox

from jmu_baseball_utils import data_utils


def get_path(file_path: str) -> str:
    """
    Get the absolute file path starting with this package's home folder. Creates the path if it does not exist.
    
    :param file_path: the file path string
    :return: the specified file path appended to the absolute file path to this package's home folder
    """
    dir_path = pathlib.Path(__file__).parent.absolute()
    path = os.path.join(dir_path, file_path)
    
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path))
    return path


def get_num_file_lines(file_name: str) -> int:
    """
    Get the number of lines in a file.
    
    :param file_name: the name of the file
    :return: the number of lines in the file, or 0 if it does not exist
    """
    if os.path.exists(file_name):
        with open(file_name) as game_info_file:
            num_lines = sum(1 for row in game_info_file)
    else:
        num_lines = 0
    return num_lines


def get_year_info_file_name() -> str:
    """
    Get the year info file path.
    :return: the year info file path
    """
    return get_path('../jmu_baseball_utils/year_info.csv')


def get_school_id_file_name() -> str:
    """
    Get the school id file path.
    :return: the school id file path
    """
    return get_path('../scraped-data/school_ids.csv')


def get_logos_directory() -> str:
    """
    Get the directory of the logo images.
    :return: the path to the directory of the logo images
    """
    return get_path('../scraped-data/logos/')


def get_logos_csv_name() -> str:
    """
    Get the logos csv file path.
    :return: the path to the logos csv file
    """
    return '{logos_path}/logo_list.csv'.format(logos_path=get_logos_directory())


def get_scrape_file_name(year: int, division: int, stat_type: str) -> str:
    """
    Get a scrape file name for this data's year, division, and type.
    
    :param year: the year of this data
    :param division: the division of this data
    :param stat_type: the type of this data
    :return: a string in the form: "scraped-data/{year}/division_{division}/{type}.csv
    """
    path = get_path('../scraped-data/{year}/division_{division}/'.format(year=year,
                                                                         division=division))
    return '{path}/{type}.csv'.format(path=path, type=stat_type)


def get_hit_location_file_name(year: int, division: int, conference: str, school_name: str) -> str:
    """
    Get a hit location file name for this year, division, conference, and school name.
    
    :param year: the year of this data
    :param division: the division of this data
    :param conference: the conference the school was in that year
    :param school_name: the name of the school
    :return: the hit location file name
    """
    path = get_path('../hit_location_data/{year}/division_{division}/{conference}/'
                    .format(year=year, division=division,
                            conference=conference.lower().replace(' ', '_')))
    return '{path}/{team}_hit_locations.csv'.format(path=path, team=school_name.lower().replace(' ', '_'))


def get_hit_location_log_file_name(year: int, division: int, conference: str, school_name: str) -> str:
    """
    Get a hit location log file name for this year, division, conference, and school name.

    :param year: the year of this data
    :param division: the division of this data
    :param conference: the conference the school was in that year
    :param school_name: the name of the school
    :return: the hit location file name
    """
    path = get_path('../hit_location_data/{year}/division_{division}/{conference}/logs/'
                    .format(year=year, division=division,
                            conference=conference.lower().replace(' ', '_')))
    return '{path}/{team}_hit_location_log.csv'.format(path=path, team=school_name.lower().replace(' ', '_'))


def get_spray_chart_file_name(year: int, division: int, conference: str, school_name: str, first_name: str,
                              last_name: str) -> str:
    """
    Get a spray chart for the specified player in the specified year, division, conference, and school.
    
    :param year: the year of this data
    :param division: the division of this data
    :param conference: the conference the school was in that year
    :param school_name: the name of the school
    :param first_name: the first name of the player
    :param last_name: the last name of the player
    :return: the spray chart file name
    """
    path = get_path('../spray_charts/{year}/division_{division}/{conference}/{team}'
                    .format(year=year, division=division,
                            conference=conference.lower().replace(' ', '_'),
                            team=school_name.lower().replace(' ', '_')))
    return '{path}/{first_name}_{last_name}_spray_chart.png' \
        .format(path=path, first_name=first_name.lower().replace(' ', '_'),
                last_name=last_name.lower().replace(' ', '_'))


def get_conference_name(year: int, division: int, school_name: str) -> str:
    """
    Get the conference name of this school in this year and division.
    
    :param year: the year
    :param division: the division the school is in
    :param school_name: the name of the school
    :return: the conference name
    """
    conference_teams_file_name = get_scrape_file_name(year, division, 'conference_teams')
    with open(conference_teams_file_name, 'rb') as conference_teams_file:
        reader = unicodecsv.DictReader(conference_teams_file)
        for team in reader:
            if team['school_name'] == school_name:
                conference_name = team['conference_name']
    if conference_name == '':
        print('team not found: {}'.format(school_name))
        exit(-1)
    return conference_name


def get_game_ids(year: int, division: int, school_name: str) -> set:
    """
    Get all game ids for this school in this year and division.
    
    :param year: the year
    :param division: the division the school is in
    :param school_name: the name of the school
    :return: a set of game ids
    """
    all_game_ids = set()
    schedule_file_name = get_scrape_file_name(year, division, 'game_info')
    with open(schedule_file_name, 'rb') as schedule_file:
        reader = unicodecsv.DictReader(schedule_file)
        for line in reader:
            if line['away_school_name'] == school_name or line['home_school_name'] == school_name:
                all_game_ids.add(line['game_id'])
    return all_game_ids


def get_roster(year: int, division: int, school_name: str) -> dict:
    """
    Get a school's roster for this year and division.
    
    :param year: the year
    :param division: the division the school is in
    :param school_name: the name of the school
    :return: a dict in this format: {player_id: {'first_name': first name, 'last_name': last name}}
    """
    roster = dict()
    roster_file_name = get_scrape_file_name(year, division, 'rosters')
    with open(roster_file_name, 'rb') as roster_file:
        reader = unicodecsv.DictReader(roster_file)
        for line in reader:
            if line['school_name'] == school_name:
                first_name, last_name, suffix = data_utils.split_name(line['Player'])
                roster.update({line['player_id']: {'first_name': first_name,
                                                   'last_name': last_name}})
    return roster


def get_school_schedule(year: int, division: int, school_name: str) -> list:
    """
    Get the schedule for this school in this year and division.
    
    :param year: the year
    :param division: the division the school is in
    :param school_name: the name of the school
    :return: a list of game info dicts
    """
    game_info = []
    game_info_file_name = get_scrape_file_name(year, division, 'game_info')
    with open(game_info_file_name, 'rb') as game_info_file:
        game_info_reader = unicodecsv.DictReader(game_info_file)
        for line in game_info_reader:
            if line['away_school_name'] == school_name or line['home_school_name'] == school_name:
                game_info.append(line)
    return game_info


def get_school_play_by_play(year: int, division: int, school_name: str) -> dict:
    """
    Get the play by play for this school in this year and division.
    
    :param year: the year
    :param division: the division the school is in
    :param school_name: the name of the school
    :return: a dict of play by play line lists in the format:
    {game_id: [[line_1_info], [line_2_info]...]}
    """
    play_by_play = {}
    game_ids = {game['game_id'] for game in get_school_schedule(year, division, school_name)}
    play_by_play_file_name = get_scrape_file_name(year, division, 'play_by_play')
    with open(play_by_play_file_name, 'rb') as play_by_play_file:
        play_by_play_reader = unicodecsv.DictReader(play_by_play_file)
        for line in play_by_play_reader:
            if line['game_id'] in game_ids:
                if line['game_id'] in play_by_play:
                    current_pbp = play_by_play[line['game_id']]
                    current_pbp.append(line)
                    play_by_play[line['game_id']] = current_pbp
                else:
                    play_by_play.update({line['game_id']: [line]})
    return play_by_play


def get_lineups(year: int, division: int, school_name: str) -> dict:
    """
    Get all lineups for each game this school played in this year and division. This means all players will be
    listed, even ones that did not start, and the list of players may not be in line up order.
    
    :param year: the year
    :param division: the division the school is in
    :param school_name: the name of the school
    :return: a dict of game lineups in the format:
    {game_id: {school_name: [{'first_name': first name, 'last_name': last_name, 'player_id': player id}, ...]}}
    """
    all_game_ids = get_game_ids(year, division, school_name)
    
    all_lineups = dict()
    box_score_file_name = get_scrape_file_name(year, division, 'box_score_hitting')
    with open(box_score_file_name, 'rb') as box_score_file:
        reader = unicodecsv.DictReader(box_score_file)
        for line in reader:
            if line['game_id'] in all_game_ids and line['Player'] != 'Totals':
                game_lineup = all_lineups.get(line['game_id'], {})
                team_lineup = game_lineup.get(line['school_name'], [])
                first_name, last_name, suffix = data_utils.split_name(line['Player'])
                team_lineup.append({'first_name': first_name, 'last_name': last_name,
                                    'player_id': line['player_id']})
                game_lineup.update({line['school_name']: team_lineup})
                all_lineups.update({line['game_id']: game_lineup})
    return all_lineups
