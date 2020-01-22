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
stat_type = 'team_{stat_type}_totals'
stat_types = ['hitting', 'pitching', 'fielding']


def get_team_stats(year, division):
    """
    Scrape the team totals for hitting, pitching, and fielding into 3 separate csv files.
    Also creates another csv file containing just the names of the teams for that year and
    division.

    @param year: the year to scrape
    @param division: the division of the teams (1, 2, 3)
    @return: None
    """
    ids = Database.get_year_info(year)
    year_id = ids[0]
    team_info = []

    for stat_id in ids[1:]:
        print('Getting team {stat_type} stats for {year} division {division}... '
              .format(stat_type=stat_types[stat_id - ids[1]], year=year, division=division),
              end='')
        
        url = base_url.format(division=division, year_id=year_id, year_stat_id=stat_id)
        page = WebUtils.get_page(url, 0.5, 10)
        
        table = page.select_one('#stat_grid')
        table_header = table.select_one('tr', {'style': 'background: white;'})
        
        header = [th.text for th in table_header.select('th')]
        header.insert(1, 'school_id')
        
        team_dict = dict()
        stats = []
        
        for row in table.select('tr')[1:-1]:
            cols = row.select('td')
            
            # Some pages have duplicate teams, this check prevents duplicate stats from
            # being recorded
            if cols[0].text.strip() not in team_dict:
                team_name = cols[0].text.strip()
                team_dict.update([(team_name, None)])
                team_stats = []
                for col in cols:
                    team_stats.append(col.text.strip())
                
                # get school id
                try:
                    team_url = row.select_one('a').attrs.get('href')
                    school_id = WebUtils.get_school_id_from_url(team_url)
                    team_stats.insert(1, school_id)
                    if stat_id == ids[1]:
                        team_info.append([team_name, school_id])
                except AttributeError:
                    team_stats.insert(1, None)
                    
                stats.append(team_stats)

        # length - 1 since the list should include the national totals as well
        print('{num_teams} teams found.'.format(num_teams=len(stats) - 1))
        
        file_name = FileUtils.get_file_name(year, division, stat_type.format(
                stat_type=stat_types[stat_id - ids[1]]))
        with open(file_name, 'wb') as file:
            writer = unicodecsv.writer(file)
            writer.writerow(header)
            writer.writerows(stats)
        
    file_name = FileUtils.get_file_name(year, division, 'teams')
    with open(file_name, 'wb') as file:
        writer = unicodecsv.writer(file)
        writer.writerow(['team', 'school_id'])
        writer.writerows(team_info)
