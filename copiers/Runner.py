"""
Main copy file, if the methods in this file are kept in the same order they
should always work.

@author: Kevin Kelly
"""

from copiers import Conferences, Schools, Stadiums, Coaches, Teams, Games, \
    DefaultValues, Umpires, Rosters, PlayByPlay
from ncaadatabase import NCAADatabase


def main():
    """
    Run all copiers. Creates various csv files as a side effect.

    :return: None
    """
    with NCAADatabase() as database:
        DefaultValues.insert_default_conferences(database)
        Schools.copy_schools(database)
        years = range(2012, 2020)
        divisions = [1, 2, 3]
        for year in years:
            for division in divisions:
                if year == 2012 and division != 1:
                    continue
                if year == 2013 and division == 2:
                    continue
                print('Year: {}, Division: {}'.format(year, division))
                Conferences.copy_conferences(database, year, division)
                Schools.add_nicknames_and_urls(database, year, division)
                Stadiums.copy_stadiums(database, year, division)
                Coaches.copy_coaches(database, year, division)
                Teams.create_teams(database, year, division)
                Rosters.copy_players(database, year, division)
                Rosters.create_rosters(database, year, division)
                Games.copy_game_info(database, year, division)
                Games.create_game_positions(database, year, division)
                Games.copy_game_innings(database, year, division)
                Games.copy_box_score_lines(database, year, division)
                Umpires.copy_umpires(database, year, division)
                Umpires.create_umpire_games(database, year, division)
                PlayByPlay.copy_play_by_play(database, year, division)


if __name__ == '__main__':
    main()
