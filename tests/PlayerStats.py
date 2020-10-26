"""
This file compares the player stats in the database with the ones scraped
directly from the ncaa stats website.
"""
import unicodecsv

import ncaadatabase
import FileUtils

base_file_name = 'player_{stat_type}_totals'
stat_types = ['hitting', 'pitching', 'fielding']


def compare_player_stats(year, division):
    """
    Compare player stats from the database to the scraped data from the ncaa
    stats website.
    :param year: the year of the stats
    :param division: the division of the stats
    :return:
    """
    error_map = {}
    team_map = {}
    errors = 0
    incorrect_ids = 0
    database_teams = {team['team_id']: {'ncaa_id': team['school_ncaa_id'],
                                        'school_name': team['school_name']} for team in
                      ncaadatabase.get_all_team_info()}
    all_rosters = {roster['roster_id']: {'team_id': roster['team_id'], 'ncaa_id': roster[
        'ncaa_id'], 'first_name': roster['first_name'], 'last_name': roster['last_name']}
                   for roster in ncaadatabase.get_all_roster_info() if roster['year'] == year}
    headers = {
        'hitting': ['AB', 'H', '2B', '3B', 'HR', 'BB', 'IBB', 'HBP', 'R', 'RBI', 'K', 'SF', 'SH',
                    'DP', 'SB', 'CS'],
        'pitching': ['App', 'GS', 'OrdAppeared', 'W', 'L', 'SV', 'IP', 'Pitches', 'BF', 'H', '2B-A',
                     '3B-A', 'HR-A', 'BB', 'IBB', 'HB', 'r', 'ER', 'Inh Run', 'Inh Run Score', 'FO',
                     'GO', 'K', 'KL', 'SF', 'SH', 'BK', 'WP', 'CG', 'SHO'],
        'fielding': ['PO', 'A', 'E', 'PB', 'CI', 'SBA', 'CSB', 'IDP', 'TP']
        }
    header_mappings = {
        'hitting': {'ab': 'AB', 'h': 'H', 'dbl': '2B', 'tpl': '3B', 'hr': 'HR', 'bb': 'BB',
                    'ibb': 'IBB', 'hbp': 'HBP', 'r': 'R', 'rbi': 'RBI', 'k': 'K', 'sf': 'SF',
                    'sh': 'SH', 'dp': 'DP', 'sb': 'SB', 'cs': 'CS'},
        'pitching': {'app': 'App', 'gs': 'GS', 'ord': 'OrdAppeared', 'w': 'W', 'l': 'L', 'sv': 'SV',
                     'ip': 'IP', 'p': 'Pitches', 'bf': 'BF', 'h': 'H', 'dbl': '2B-A', 'tpl': '3B-A',
                     'hr': 'HR-A', 'bb': 'BB', 'ibb': 'IBB', 'hbp': 'HB', 'r': 'r', 'er': 'ER',
                     'ir': 'Inh Run', 'irs': 'Inh Run Score', 'fo': 'FO', 'go': 'GO', 'k': 'K',
                     'kl': 'KL', 'sf': 'SF', 'sh': 'SH', 'bk': 'BK', 'wp': 'WP', 'cg': 'CG',
                     'sho': 'SHO'},
        'fielding': {'po': 'PO', 'a': 'A', 'e': 'E', 'pb': 'PB', 'ci': 'CI', 'sb': 'SBA',
                     'cs': 'CSB', 'dp': 'IDP', 'tp': 'TP'}}
    for stat_type in stat_types:
        database_stats = ncaadatabase.get_player_year_stats(year, division, stat_type)
        database_stats_dict = {}
        for row in database_stats:
            roster_info = all_rosters[row['roster_id']]
            team_id = roster_info['team_id']
            team = database_teams[team_id]
            new_row = {'school_name': team['school_name'],
                       'school_id': team['ncaa_id'],
                       'Player': roster_info['last_name'] + ', ' + roster_info['first_name'],
                       'player_id': roster_info['ncaa_id']}
            for heading, new_heading in header_mappings[stat_type].items():
                new_row.update({new_heading: row[heading]})
            database_stats_dict.update({roster_info['ncaa_id']: new_row})
        scraped_stats_name = FileUtils.get_scrape_file_name(year, division, base_file_name.format(
            stat_type=stat_type))
        with open(scraped_stats_name, 'rb') as scraped_stats:
            scrape_reader = unicodecsv.DictReader(scraped_stats)
            for number, row in enumerate(scrape_reader):
                if row['player_id'] == '' or row['Player'] == ',':
                    continue
                try:
                    player_database_stats = database_stats_dict[int(row['player_id'])]
                except KeyError:
                    incorrect_ids += 1
                    continue
                for stat in headers[stat_type]:
                    if stat not in row:
                        continue
                    if row[stat] == '':
                        row[stat] = '0'
                    if stat == 'IP':
                        None
                        '''if float(row[stat].replace(',', '')) != player_database_stats[stat]:
                            errors += 1
                            error_map.update({stat: error_map.get(stat, 0) + 1})
                            print('{}: Error: {} {} {} != {}'.format(number, row['Player'],
                                                                     stat,
                                                                     row[stat],
                                                                     player_database_stats[
                                                                     stat]))'''
                    else:
                        if player_database_stats[stat] is None or \
                                int(row[stat].replace(',', '')) < player_database_stats[stat]:
                            errors += 1
                            error_map.update({stat: error_map.get(stat, 0) + 1})
                            team_map.update({row['school_name']: team_map.get(row['school_name'],
                                                                              0) + 1})
                            '''print('{}: Error: {} {} {} {} != {}'.format(number, row['school_name'],
                                                                        row['Player'], stat,
                                                                        row[stat],
                                                                        player_database_stats[
                                                                            stat]))'''
    print('Errors: {}'.format(errors))
    print('Bad Ids: {}'.format(incorrect_ids))
    print({k: v for k, v in sorted(error_map.items(), key=lambda item: item[1], reverse=True)})
    print({k: v for k, v in sorted(team_map.items(), key=lambda item: item[1], reverse=True)})
    print(len(team_map))
