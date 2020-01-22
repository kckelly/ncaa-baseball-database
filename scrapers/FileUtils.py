"""
File containing multiple helper methods for the scraped csv data.
"""
import os


def get_file_name(year, division, stat_type):
    """
    Get a file name for this data's year, division, and type.
    @param year: the year of this data
    @param division: the division of this data
    @param stat_type: the type of this data
    @return: a string in the form: "scraped-data/{year}/division_{division}/{type}.csv
    """
    path = 'scraped-data/{year}/division_{division}/'.format(year=year, division=division)
    if not os.path.exists(path):
        os.makedirs(path)
    return 'scraped-data/{year}/division_{division}/{type}.csv' \
        .format(year=year, division=division, type=stat_type)
