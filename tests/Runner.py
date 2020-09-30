"""
Runs all comparison tests.
"""
from tests import PlayerStats

years = range(2013, 2020)
divisions = [1]
for year in years:
    for division in divisions:
        print('Year: {year} Division: {division}'.format(year=year, division=division))
        PlayerStats.compare_player_stats(year, division)
