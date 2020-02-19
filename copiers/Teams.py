"""
File for combining ids of conferences, schools, coaches, and stadiums to create yearly teams in
the database.
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
    
    current_teams = {team['school_ncaa_id'] for team
                     in Database.get_all_team_info() if team['year'] == year}
    
    # These dict comprehensions make a mapping of either the name or ncaa_id of each item to the
    # id of that item stored in the database. For instance, database_conferences contains a
    # mapping of conference names to ids from the conference table, to get the conference id for
    # any conference do conference['{conference_name'}].
    database_conferences = {conference['name']: conference['id'] for conference
                            in Database.get_all_conferences() if conference['division'] == division}
    database_schools = {school['ncaa_id']: school['id'] for school
                        in Database.get_all_schools()}
    database_coaches = {coach['ncaa_id']: coach['id'] for coach
                        in Database.get_all_coaches()}
    database_stadiums = {stadium['name']: stadium['id'] for stadium
                         in Database.get_all_stadiums()}
    
    coaches = {}
    coach_file_name = FileUtils.get_scrape_file_name(year, division, 'coaches')
    with open(coach_file_name, 'rb') as coach_file:
        coach_reader = unicodecsv.DictReader(coach_file)
        for coach in coach_reader:
            coaches.update({int(coach['school_id']): int(coach['coach_id'])})
            
    stadiums = {}
    stadiums_file_name = FileUtils.get_scrape_file_name(year, division, 'stadiums')
    with open(stadiums_file_name, 'rb') as stadiums_file:
        stadiums_reader = unicodecsv.DictReader(stadiums_file)
        for stadium in stadiums_reader:
            stadiums.update({int(stadium['school_id']): stadium['stadium_name']})
    
    team_relations = []
    team_file_name = FileUtils.get_scrape_file_name(year, division, 'conference_teams')
    with open(team_file_name, 'rb') as team_file:
        team_reader = unicodecsv.DictReader(team_file)
        for team in team_reader:
            school_ncaa_id = int(team['school_id'])
            if school_ncaa_id not in current_teams:
                team_conference_name = team['conference_name']
                conference_id = database_conferences[team_conference_name]
                school_id = database_schools[school_ncaa_id]
                if coaches[school_ncaa_id] != '':
                    coach_id = database_coaches[coaches[school_ncaa_id]]
                else:
                    coach_id = None
                if stadiums[school_ncaa_id] != '':
                    stadium_id = database_stadiums[stadiums[school_ncaa_id]]
                else:
                    stadium_id = None
                team_relations.append({'year': year, 'conference_id': conference_id,
                                       'school_id': school_id, 'coach_id': coach_id,
                                       'stadium_id': stadium_id})
    
    copy_team_file_name = FileUtils.get_copy_file_name('teams')
    with open(copy_team_file_name, 'wb') as copy_team_file:
        team_writer = unicodecsv.DictWriter(copy_team_file, ['year', 'conference_id',
                                                             'school_id', 'coach_id', 'stadium_id'])
        team_writer.writeheader()
        team_writer.writerows(team_relations)
        copy_team_file.flush()
    
    Database.copy_expert('team(year, conference_id, school_id, coach_id, stadium_id)',
                         copy_team_file_name)
    
    print('{num_teams} new teams.'.format(num_teams=len(team_relations)))
