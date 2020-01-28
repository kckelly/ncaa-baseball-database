"""
File containing many helper methods for interfacing with the web with bs4 and urllib.
"""
import sys

from bs4 import BeautifulSoup
import time
import requests


def get_page(url, sleep_time, try_limit):
    """
    Get a page with the specified url. If the requested page is not found, the method will try
    again until try_limit is reached, sleeping for sleep_time seconds in between each attempt.
    
    @param url: the url of the page to get
    @param sleep_time: the time to sleep in between attempts
    @param try_limit: the maximum number of attempts to connect
    @return: the page in a BeautifulSoup object with the parser set to 'html.parser'
    """
    for tries in range(0, try_limit):
        headers = {'User-Agent': 'Mozilla/5.0', 'Connection': 'close'}
        try:
            t0 = time.time()
            page = requests.get(url, headers=headers)
            print('{:.2f} seconds... '.format(time.time() - t0), end='')
            return BeautifulSoup(page.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print('\nFailed to connect to {url} trying again. Try {try_number}.'.
                  format(url=url, try_number=tries))
            if tries == try_limit - 1:
                print('Unable to connect to {url}'.format(url=url))
                print('\t' + str(e))
        time.sleep(sleep_time)
    sys.exit(1)


def get_school_id_from_url(url):
    """
    Get the school id from the url of a ncaa team.
    
    @param url: the team url
    @return: the school id of the team
    """
    return url.split('/')[2]


def get_coach_id_from_url(url):
    """
    Get the coach's id from their url.

    @param url: the coach's url
    @return: the coach's id
    """
    return url.split('/')[2].split('?')[0]


def get_player_id_from_url(url):
    """
    Get the player's id from their url.

    @param url: the player's url
    @return: the player's id
    """
    return url[url.rindex('=') + 1:]


def get_contest_id_from_url(url, year):
    """
    Get the game's id from its url.

    @param url: the game's url
    @param year: the year of the game the url came from
    @return: the game's id
    """
    if year < 2019:
        return url.split('?')[0].split('/')[3][:]
    else:
        return url.split('/')[2]
