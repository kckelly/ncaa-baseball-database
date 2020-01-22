"""
File containing many helper methods for interfacing with the web with bs4 and urllib.
"""
import sys

from bs4 import BeautifulSoup
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


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
        time.sleep(sleep_time)
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            page = urlopen(req)
            return BeautifulSoup(page, 'html.parser')
        except HTTPError:
            print('\nFailed to connect to {url} trying again. Try {try_number}.'.
                  format(url=url, try_number=tries))
    print('\tUnable to connect to {url}'.format(url=url))
    sys.exit(1)
