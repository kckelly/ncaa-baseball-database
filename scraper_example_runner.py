"""
Main scraping file, if the methods in this file are kept in the same order they should always
work.

@author: Kevin Kelly
"""
import os
import time

from scrapers import box_scores
from scrapers import conference_stats
from scrapers import game_info
from scrapers import logos
from scrapers import play_by_play
from scrapers import player_stats
from scrapers import rosters
from scrapers import school_ids
from scrapers import team_info
from scrapers import team_stats


def main():
    """
    Run all scrapers. Creates various csv files as a side effect.
    
    :return: None
    """
    start = time.time()
    
    school_ids.get_school_ids()
    logos.get_all_logos()
    years = range(2012, 2021)
    divisions = [1]
    for year in years:
        for division in divisions:
            if year == 2012 and division != 1:
                continue
            if year == 2013 and division == 2:
                continue
            print('Year: {}, Division: {}'.format(year, division))
            start_time = time.time()
            conference_stats.get_conference_stats(year, division)
            team_stats.get_team_stats(year, division)  # must run before team info, rosters, and player stats
            team_info.get_team_info(year, division)
            rosters.get_rosters(year, division)
            player_stats.get_player_stats(year, division)
            game_info.get_game_info(year, division)  # must run before box scores and play by play
            box_scores.get_box_scores(year, division)
            play_by_play.get_play_by_play(year, division)
            end_time = time.time() - start_time
            print(f'{year} division {division}: {end_time / 60} minutes')
    total_time = time.time() - start
    print(f'total time: {total_time / 60} minutes')


if __name__ == '__main__':
    main()
