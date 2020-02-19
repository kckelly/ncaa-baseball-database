"""
File to scrape from https://stats.ncaa.org/rankings/institution_trends and get each division's
team stats by year. Makes one file that is used to put team names into the database and
another that holds stats for verification purposes later.
"""
import unicodecsv

import Database
import FileUtils
import WebUtils

base_url = 'https://stats.ncaa.org/rankings/institution_trends?' \
           'division={division}&id={year_id}&year_stat_category_id={year_stat_id}'
base_file_name = 'team_{stat_type}_totals'
stat_types = ['hitting', 'pitching', 'fielding']


def get_team_stats(year, division):
    """
    Scrape the team totals for hitting, pitching, and fielding into 3 separate csv files.
    Also creates another csv file containing just the names of the teams for that year and
    division.

    :param year: the year to scrape
    :param division: the division of the teams (1, 2, 3)
    :return: None
    """
    ids = Database.get_year_info(year)
    year_id = ids['year_id']
    team_conference_info = []
    
    for stat_type in stat_types:
        team_stats_file_name = FileUtils.get_scrape_file_name(year, division, base_file_name.format(
                stat_type=stat_type))
        with open(team_stats_file_name, 'wb') as team_stats_file:
            team_stats_writer = unicodecsv.writer(team_stats_file)
        
            print('Getting team {stat_type} stats for {year} division {division}... '
                  .format(stat_type=stat_type, year=year, division=division),
                  end='')
            
            url = base_url.format(division=division, year_id=year_id, year_stat_id=ids[stat_type +
                                                                                       '_id'])
            page = WebUtils.get_page(url, 0.1, 10)
            
            table = page.select_one('#stat_grid')
            table_header = table.select_one('tr', {'style': 'background: white;'})
            
            header = [th.text for th in table_header.select('th')]
            header.insert(1, 'school_id')
            team_stats_writer.writerow(header)
            
            team_dict = dict()
            rows = table.select('tr')[1:-1]
            for row in rows:
                cols = row.select('td')
                
                # Some pages have duplicate teams, this check prevents duplicate stats from
                # being recorded
                team_name = cols[0].text.strip()
                if team_name not in team_dict:
                    team_dict.update([(team_name, None)])
                    team_stats = []
                    for col in cols:
                        team_stats.append(col.text.strip())
                    
                    # for whatever reason the conferences for some independent teams is set as
                    # the same as the team name, so we fix it here
                    if team_name == team_stats[1]:
                        team_stats[1] = 'Independent'
                        
                    # get school id
                    try:
                        team_url = row.select_one('a').attrs.get('href')
                        school_id = WebUtils.get_school_id_from_url(team_url)
                        team_stats.insert(1, school_id)
                        if stat_type == stat_types[2]:
                            team_conference_info.append([school_id, team_stats[2], team_name])
                    except AttributeError:
                        team_stats.insert(1, None)
                    
                    team_stats_writer.writerow(team_stats)
            
            print('{num_teams} teams found.'.format(num_teams=len(team_dict) - 1))
    
    schools_file_name = FileUtils.get_scrape_file_name(year, division, 'conference_teams')
    with open(schools_file_name, 'wb') as file:
        schools_writer = unicodecsv.writer(file)
        schools_writer.writerow(['school_id', 'conference_name', 'school_name'])
        schools_writer.writerows(team_conference_info)
