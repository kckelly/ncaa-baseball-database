"""
File for combining ids of conferences, schools, coaches, and stadiums to create yearly teams in
the database.

@author: Kevin Kelly
"""
import unicodecsv

import Database
import FileUtils


def create_teams(year, division):
    """
    Combine data from the conference, school, coach, and stadium tables to make team relations from
    the year and division specified. Uses the corresponding csvs in scraped-data to ensure the
    relations are correct.
    :param year: the year of the teams
    :param division: the division of the teams
    :return: None
    """
    print('Creating teams... ', end='')
    
    database_teams = {team['school_ncaa_id'] for team
                      in Database.get_all_team_info() if team['year'] == year}
    
    # These dict comprehensions make a mapping of either the name or ncaa_id of each item to the
    # id of that item stored in the database. For instance, database_conferences contains a
    # mapping of conference names to ids from the conference table, so to get the conference id for
    # any one conference you would write conference['conference_name'].
    database_conferences = {conference['name']: conference['id'] for conference
                            in Database.get_all_conferences() if conference['division'] == division}
    database_schools = {school['ncaa_id']: school['id'] for school
                        in Database.get_all_schools()}
    database_coaches = {coach['ncaa_id']: coach['id'] for coach
                        in Database.get_all_coaches()}
    database_stadiums = {stadium['name']: stadium['id'] for stadium
                         in Database.get_all_stadiums()}
    
    team_coaches = {}
    coach_file_name = FileUtils.get_scrape_file_name(year, division, 'coaches')
    with open(coach_file_name, 'rb') as coach_file:
        coach_reader = unicodecsv.DictReader(coach_file)
        for coach in coach_reader:
            team_coaches.update({int(coach['school_id']): int(coach['coach_id'])})
    
    team_stadiums = {}
    stadiums_file_name = FileUtils.get_scrape_file_name(year, division, 'stadiums')
    with open(stadiums_file_name, 'rb') as stadiums_file:
        stadiums_reader = unicodecsv.DictReader(stadiums_file)
        for stadium in stadiums_reader:
            team_stadiums.update({int(stadium['school_id']): stadium['stadium_name']})
    
    new_teams = []
    team_file_name = FileUtils.get_scrape_file_name(year, division, 'conference_teams')
    with open(team_file_name, 'rb') as team_file:
        team_reader = unicodecsv.DictReader(team_file)
        for team in team_reader:
            school_ncaa_id = int(team['school_id'])
            if school_ncaa_id not in database_teams:
                conference_id = database_conferences[team['conference_name']]
                school_id = database_schools[school_ncaa_id]
        
                if team_coaches[school_ncaa_id] != '':
                    coach_ncaa_id = team_coaches[school_ncaa_id]
                    coach_id = database_coaches[coach_ncaa_id]
                else:
                    coach_id = None
        
                if team_stadiums[school_ncaa_id] != '':
                    stadium_name = team_stadiums[school_ncaa_id]
                    stadium_id = database_stadiums[stadium_name]
                else:
                    stadium_id = None
        
                new_teams.append({'year': year,
                                  'conference_id': conference_id,
                                  'school_id': school_id,
                                  'coach_id': coach_id,
                                  'stadium_id': stadium_id})
    
    header = ['year', 'conference_id', 'school_id', 'coach_id', 'stadium_id']
    Database.copy_expert('team(year, conference_id, school_id, coach_id, stadium_id)',
                         'teams', header, new_teams)
    
    print('{num_teams} new teams.'.format(num_teams=len(new_teams)))
