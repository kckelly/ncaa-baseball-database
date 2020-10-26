"""
File to scrape team information, including stadiums, coaches, and schedules.

@author: Kevin Kelly
"""

import unicodecsv

import DataUtils
import ncaadatabase
import FileUtils
import WebUtils


def get_team_info(year, division):
    """
    Get team information about each team in the division that year. This includes stadiums,
    coaches, and schedules. Creates 4 csv files in scraped-data: team_info, stadiums, coaches,
    and schedules.

    :param year: the year to get team info
    :param division: the division the teams are in
    :return: None
    """
    base_url = 'https://stats.ncaa.org'
    
    ids = ncaadatabase.get_year_info(year)
    teams_list = DataUtils.get_schools(year, division)
    
    team_info_file_name = FileUtils.get_scrape_file_name(year, division, 'team_info')
    team_info_header = ['school_name', 'school_id', 'nickname', 'website']
    
    stadium_file_name = FileUtils.get_scrape_file_name(year, division, 'stadiums')
    stadium_header = ['school_name', 'school_id', 'stadium_name', 'capacity', 'year_built']
    
    coach_file_name = FileUtils.get_scrape_file_name(year, division, 'coaches')
    coach_header = ['school_name', 'school_id', 'coach_name', 'coach_id', 'alma_mater',
                    'year_graduated']
    
    schedule_file_name = FileUtils.get_scrape_file_name(year, division, 'schedules')
    schedule_header = ['school_name', 'school_id', 'opponent_string', 'opponent_id', 'date',
                       'score_string', 'game_url']
    
    with open(team_info_file_name, 'wb') as team_info_file, \
            open(stadium_file_name, 'wb') as stadium_file, \
            open(coach_file_name, 'wb') as coach_file, \
            open(schedule_file_name, 'wb') as schedule_file:
        
        team_info_writer = unicodecsv.DictWriter(team_info_file, team_info_header)
        team_info_writer.writeheader()
        
        stadium_writer = unicodecsv.DictWriter(stadium_file, stadium_header)
        stadium_writer.writeheader()
        
        coach_writer = unicodecsv.DictWriter(coach_file, coach_header)
        coach_writer.writeheader()
        
        schedule_writer = unicodecsv.DictWriter(schedule_file, schedule_header)
        schedule_writer.writeheader()
        
        for team in teams_list:
            team_url = base_url + '/team/{school_id}/{year_id}'.format(school_id=team['school_id'],
                                                                       year_id=ids['year_id'])
            print('Getting team information and schedules for {school_name}... '.format(
                school_name=team['school_name']), end='')
            page = WebUtils.get_page(team_url, 0.1, 10)

            # school website and nickname
            school_info = page.select_one('legend')
            school_nickname = school_info.text.replace(team['school_name'], '').split('(')[
                0].strip()
            try:
                school_website = school_info.select_one('a').attrs.get('href')
            except AttributeError:
                school_website = None
            team_info_writer.writerow({'school_name': team['school_name'],
                                       'school_id': team['school_id'],
                                       'nickname': school_nickname,
                                       'website': school_website})

            # stadium information
            stadium_info = page.select_one('#facility_div').select_one('fieldset').text.strip()
            stadium = {heading: None for heading in stadium_header}
            stadium['school_name'] = team['school_name']
            stadium['school_id'] = team['school_id']
            if stadium_info != 'Stadium':
                for line in stadium_info.split('\n'):
                    if line.startswith('Name'):
                        stadium['stadium_name'] = line[5:]
                    elif line.startswith('Capacity'):
                        stadium['capacity'] = line[9:]
                    elif line.startswith('Year Built'):
                        stadium['year_built'] = line[11:]
                    elif line.startswith('Primary Venue'):
                        break
            stadium_writer.writerow(stadium)

            # coach information
            coach = {heading: None for heading in coach_header}
            coach['school_name'] = team['school_name']
            coach['school_id'] = team['school_id']
            try:
                coach_info = page.select_one('#head_coaches_div').select('fieldset')[-1]
                if coach_info != 'Head Coach':
                    for line in coach_info.text.strip().split('\n'):
                        if line.startswith('Name'):
                            coach['coach_name'] = line[6:]
                            try:
                                coach_url = coach_info.select_one('a').attrs.get('href')
                                coach['coach_id'] = WebUtils.get_coach_id_from_url(coach_url)
                            except AttributeError:
                                coach['coach_id'] = None
                        elif line.startswith('Alma mater'):
                            if '-' in line:
                                year_index = line.rindex('-')
                                coach['alma_mater'] = line[12:year_index - 1]
                                coach['year_graduated'] = line[year_index + 2:]
                            else:
                                coach['alma_mater'] = line[12:]
            except:
                pass
            finally:
                coach_writer.writerow(coach)

            # team schedule
            schedule_table = page.select('table')[1]
            schedule_rows = schedule_table.select('tr')[2:]
            game_counter = 0
            if year > 2018:
                starting_index = 1
                step_amount = 2
            else:
                starting_index = 0
                step_amount = 1
            for schedule_row in schedule_rows[starting_index::step_amount]:
                if len(schedule_row.attrs) > 0 and \
                        schedule_row.attrs.get('class')[0] == 'grey_heading':
                    continue
                game_counter += 1
                game_details = schedule_row.select('td')
                game = {heading: None for heading in schedule_header}
                game['school_name'] = team['school_name']
                game['school_id'] = team['school_id']
                game['opponent_string'] = game_details[1].text.strip()
                try:
                    game['opponent_id'] = WebUtils.get_school_id_from_url(
                        game_details[1].select_one('a').attrs.get('href'))
                except AttributeError:
                    game['opponent_id'] = None
                game['date'] = game_details[0].text.strip()
                game['score_string'] = game_details[2].text.strip()
                try:
                    game['game_url'] = game_details[2].select_one('a').attrs.get('href')
                except AttributeError:
                    game['game_url'] = None
                schedule_writer.writerow(game)

            stadium_file.flush()
            coach_file.flush()
            schedule_file.flush()
            team_info_file.flush()
            print('{} games found.'.format(game_counter))
