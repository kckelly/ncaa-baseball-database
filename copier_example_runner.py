"""
Main copy file, if the methods in this file are kept in the same order they
should always work.

@author: Kevin Kelly
"""

from copiers import conferences, schools, stadiums, coaches, teams, games, \
    default_values, umpires, rosters, play_by_play
from database_files.ncaa_database import NCAADatabase


def main():
    """
    Run all copiers. Creates various csv files as a side effect.

    :return: None
    """
    with NCAADatabase() as database:
        default_values.insert_default_conferences(database)
        schools.copy_schools(database)
        years = range(2012, 2021)
        divisions = [1]
        for year in years:
            for division in divisions:
                if year == 2012 and division != 1:
                    continue
                if year == 2013 and division == 2:
                    continue
                print('Year: {}, Division: {}'.format(year, division))
                conferences.copy_conferences(database, year, division)
                schools.add_nicknames_and_urls(database, year, division)
                stadiums.copy_stadiums(database, year, division)
                coaches.copy_coaches(database, year, division)
                teams.create_teams(database, year, division)
                rosters.copy_players(database, year, division)
                rosters.create_rosters(database, year, division)
                games.copy_game_info(database, year, division)
                games.create_game_positions(database, year, division)
                games.copy_game_innings(database, year, division)
                games.copy_box_score_lines(database, year, division)
                umpires.copy_umpires(database, year, division)
                umpires.create_umpire_games(database, year, division)
                play_by_play.copy_play_by_play(database, year, division)


if __name__ == '__main__':
    main()
