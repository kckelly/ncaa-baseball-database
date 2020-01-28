"""
Main scraping file, if the methods in this file are kept in the same order they should always
work.

@author: Kevin Kelly
"""
import BoxScores
import ConferenceStats
import GameInfo
import Logos
import PlayByPlay
import PlayerStats
import Rosters
import SchoolIds
import TeamInfo
import TeamStats


def main():
    """
    Run all scrapers. Creates various csv files as a side effect.
    
    @return: None
    """
    SchoolIds.get_school_ids()
    Logos.get_all_logos()
    years = range(2012, 2020)
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
