"""
Main copy file, if the methods in this file are kept in the same order they
should always work.

@author: Kevin Kelly
"""

from copiers import Conferences, Schools, Stadiums, Coaches, Teams, Games, \
    DefaultValues, Umpires, Rosters, PlayByPlay


def main():
    """
    Run all copiers. Creates various csv files as a side effect.

    :return: None
    """
    DefaultValues.insert_default_conferences()
    Schools.copy_schools()
    years = range(2012, 2013)
    divisions = [1]
    
    for year in years:
        for division in divisions:
            print('Year: {}, Division: {}'.format(year, division))
            Conferences.copy_conferences(year, division)
            Schools.add_nicknames_and_urls(year, division)
            Stadiums.copy_stadiums(year, division)
            Coaches.copy_coaches(year, division)
            Teams.create_teams(year, division)
            Rosters.copy_players(year, division)
            Rosters.create_rosters(year, division)
            Games.copy_game_info(year, division)
            Games.create_game_positions(year, division)
            Games.copy_game_innings(year, division)
            Games.copy_box_score_lines(year, division)
            Umpires.copy_umpires(year, division)
            Umpires.create_umpire_games(year, division)
            PlayByPlay.copy_play_by_play(year, division)


if __name__ == '__main__':
    main()
