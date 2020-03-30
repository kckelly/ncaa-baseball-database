"""
Main scraping file, if the methods in this file are kept in the same order they should always
work.

@author: Kevin Kelly
"""
import os

from scrapers import BoxScores
from scrapers import ConferenceStats
from scrapers import GameInfo
from scrapers import Logos
from scrapers import PlayByPlay
from scrapers import PlayerStats
from scrapers import Rosters
from scrapers import SchoolIds
from scrapers import TeamInfo
from scrapers import TeamStats


def main():
    """
    Run all scrapers. Creates various csv files as a side effect.
    
    :return: None
    """
    if not os.path.exists('../scraped-data/'):
        os.makedirs('../scraped-data/')
    
    # SchoolIds.get_school_ids()
    # Logos.get_all_logos()
    years = range(2014, 2020)
    divisions = [1]
    for year in years:
        for division in divisions:
            print('Year: {}, Division: {}'.format(year, division))
            ConferenceStats.get_conference_stats(year, division)
            
            TeamStats.get_team_stats(year, division)  # must run before team info, rosters,
            # and player stats
            TeamInfo.get_team_info(year, division)
            Rosters.get_rosters(year, division)
            PlayerStats.get_player_stats(year, division)
            
            GameInfo.get_game_info(year, division)  # must run before box scores and play by play
            BoxScores.get_box_scores(year, division)
            PlayByPlay.get_play_by_play(year, division)


if __name__ == '__main__':
    main()
