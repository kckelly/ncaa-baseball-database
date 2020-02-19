"""
File containing multiple helper methods for the scraped csv data.
"""
import os


def get_num_file_lines(file_name):
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


def get_scrape_file_name(year, division, stat_type):
    """
    Get a scrape file name for this data's year, division, and type.
    :param year: the year of this data
    :param division: the division of this data
    :param stat_type: the type of this data
    :return: a string in the form: "scraped-data/{year}/division_{division}/{type}.csv
    """
    path = '../scraped-data/{year}/division_{division}/'.format(year=year, division=division)
    if not os.path.exists(path):
        os.makedirs(path)
    return '{path}{type}.csv'.format(path=path, type=stat_type)


def get_copy_file_name(stat_type):
    """
    Get a file name for this data's year, division, and type. This file will be used to write the
    data into the database.
    :param stat_type: the type of this data
    :return: a string in the form: "copy-data/{type}.csv
    """
    path = '../copy-data/'
    if not os.path.exists(path):
        os.makedirs(path)
    return '{path}{type}.csv'.format(path=path, type=stat_type)
