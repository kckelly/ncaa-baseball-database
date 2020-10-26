"""
File to scrape from https://stats.ncaa.org/rankings/institution_trends and get each division's
team stats by year. Creates one file that is used to put team names into the database and
another that holds stats for verification purposes later.

@author: Kevin Kelly
"""
import unicodecsv

import ncaadatabase
import FileUtils
import WebUtils


def get_team_stats(year, division):
    """
    Scrape the team totals for hitting, pitching, and fielding. Also creates another csv file
    containing just the names of the teams for that year and division. The three stat csv files
    are saved in the format 'scraped-data/{year}/division_{}/team_{stat_type}_stats.csv'.

    :param year: the year to scrape
    :param division: the division of the teams (1, 2, 3)
    :return: None
    """
    base_url = 'https://stats.ncaa.org/rankings/institution_trends?' \
               'division={division}&id={year_id}&year_stat_category_id={year_stat_id}'
    base_file_name = 'team_{stat_type}_totals'

    stat_types = ['hitting', 'pitching', 'fielding']

    ids = ncaadatabase.get_year_info(year)

    year_id = ids['year_id']

    team_conference_info = []  # used for the team name file

    for stat_type in stat_types:
        stat_file_name = base_file_name.format(stat_type=stat_type)
        team_stats_file_name = FileUtils.get_scrape_file_name(year, division, stat_file_name)
        with open(team_stats_file_name, 'wb') as team_stats_file:
            if year == 2016 and division == 3 and stat_type != 'hitting':
                print('2016 division 3 pitching and fielding totals are messed up on the ncaa '
                      'site, check if they work again manually\n {}'.format(url))
                continue
            if year == 2018 and division == 2 and stat_type == 'fielding':
                print('2018 division 2 fielding totals are messed up on the ncaa '
                      'site, check if they work again manually\n {}'.format(url))
                continue
            team_stats_writer = unicodecsv.writer(team_stats_file)
        
            print('Getting team {stat_type} stats for {year} division {division}... '
                  .format(stat_type=stat_type, year=year, division=division),
                  end='')
        
            url = base_url.format(division=division, year_id=year_id, year_stat_id=ids[stat_type +
                                                                                       '_id'])
            page = WebUtils.get_page(url, 0.1, 10)
        
            stat_table = page.select_one('#stat_grid')
            stat_table_header = stat_table.select_one('tr', {'style': 'background: white;'})
        
            header = [th.text for th in stat_table_header.select('th')]
            header.insert(1, 'school_id')
            team_stats_writer.writerow(header)
        
            team_dict = dict()
            stat_rows = stat_table.select('tr')[1:-1]
            for stat_row in stat_rows:
                stat_cols = stat_row.select('td')

                # Some pages have duplicate teams, this check prevents duplicate stats from
                # being recorded
                team_name = stat_cols[0].text.strip()
                if team_name == 'NYIT':
                    team_name = 'New York Tech'
                if team_name not in team_dict:
                    team_dict.update([(team_name, None)])

                    team_stats = [stat_col.text.strip() for stat_col in stat_cols]

                    # for whatever reason the conferences for some independent teams is set as
                    # the same as the team name, so we fix it here
                    if team_name == team_stats[1]:
                        team_stats[1] = 'Independent'

                    # get school id
                    try:
                        team_url = stat_row.select_one('a').attrs.get('href')
                        school_id = WebUtils.get_school_id_from_url(team_url)
                        if stat_type == stat_types[0]:
                            team_conference_info.append([school_id, team_stats[1], team_name])
                    except AttributeError:
                        school_id = None
                    team_stats.insert(1, school_id)
                    team_stats_writer.writerow(team_stats)
        
            print('{num_teams} teams found.'.format(num_teams=len(team_dict) - 1))

    schools_file_name = FileUtils.get_scrape_file_name(year, division, 'conference_teams')
    team_header = ['school_id', 'conference_name', 'school_name']
    with open(schools_file_name, 'wb') as file:
        schools_writer = unicodecsv.writer(file)
        schools_writer.writerow(team_header)
        schools_writer.writerows(team_conference_info)
