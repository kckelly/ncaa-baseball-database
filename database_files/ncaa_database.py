"""
File containing the NCAADatabase class, which has numerous methods for contacting the postgres database.
"""
import os
import sys

import psycopg2
import unicodecsv

from jmu_baseball_utils import file_utils

DEFAULT_CONFERENCE_NAME = 'Other'


class NCAADatabase:
    """
    NCAADatabase class, to be used with a with statement.
    """
    
    def __enter__(self):
        """
        Connect to the database and return the database object with a connection generated by psycopg2.

        :return: the database object
        """
        try:
            self.connection = psycopg2.connect(user=os.getenv('NCAABaseballUser'),
                                               password=os.getenv('NCAABaseballPassword'),
                                               host='localhost',
                                               port=5432,
                                               database='ncaa_baseball')
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            return self
        except psycopg2.Error as error:
            print("Error while connecting to ncaa_baseball, make sure your environment variables are "
                  "set properly", error)
            sys.exit(1)
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the connection to the database.
        :return: None
        """
        self.connection.close()
    
    def get_year_info(self, year):
        """
        Get the ids for the year specified.
        
        :param year: the year to get the ids of
        :return: a dict containing the year_id, hitting_id, pitching_id, and fielding_id for that year
        """
        
        self.cursor.execute('SELECT year_id, hitting_id, pitching_id, fielding_id '
                            'FROM year_info '
                            'WHERE year={year}'.format(year=year))
        ids = list(self.cursor.fetchone())
        
        return {'year_id': ids[0], 'hitting_id': ids[1], 'pitching_id': ids[2], 'fielding_id': ids[3]}
    
    def get_default_conference_id(self):
        """
        Get the id of the default conference from the conference table.
        :return: the id of the default conference
        """
        
        self.cursor.execute('SELECT id '
                            'FROM conference '
                            'WHERE conference.name = %s;', [DEFAULT_CONFERENCE_NAME])
        conference_id = self.cursor.fetchone()[0]
        
        return conference_id
    
    def get_all_conferences(self):
        """
        Get all conferences from the database.
        
        :return: a list of conference dicts
        """
        
        self.cursor.execute('SELECT id, name, division '
                            'FROM conference;')
        conferences = []
        for row in self.cursor:
            conferences.append({'id': row[0], 'name': row[1], 'division': row[2]})
        
        return conferences
    
    def get_all_schools(self):
        """
        Get all schools from the database.
    
        :return: a list of school dicts
        """
        
        self.cursor.execute('SELECT id, ncaa_id, name, nickname, url '
                            'FROM school;')
        schools = []
        for row in self.cursor:
            schools.append({'id': row[0], 'ncaa_id': row[1], 'name': row[2], 'nickname': row[3],
                            'url': row[4]})
        
        return schools
    
    def get_all_stadiums(self):
        """
        Get all stadiums from the database.
        :return: a list of stadium dicts
        """
        
        self.cursor.execute('SELECT id, name '
                            'FROM stadium;')
        stadiums = []
        for row in self.cursor:
            stadiums.append({'id': row[0], 'name': row[1]})
        
        return stadiums
    
    def get_all_coaches(self):
        """
        Get all coaches from the database.
        :return: a list of coach dicts
        """
        
        self.cursor.execute('SELECT id, ncaa_id, first_name, last_name '
                            'FROM coach;')
        coaches = []
        for row in self.cursor:
            coaches.append({'id': row[0], 'ncaa_id': row[1], 'first_name': row[2], 'last_name': row[3]})
        
        return coaches
    
    def get_all_teams(self):
        """
        Get all teams from the database.
        :return: a list of team dicts
        """
        
        self.cursor.execute('SELECT id, year, conference_id, school_id, coach_id, stadium_id '
                            'FROM team;')
        teams = []
        for row in self.cursor:
            teams.append({'id': row[0], 'year': row[1], 'conference_id': row[2],
                          'school_id': row[3],
                          'coach_id': row[4], 'stadium_id': row[4]})
        
        return teams
    
    def get_all_team_info(self):
        """
        Gets all team information from the database, including conference info, school info,
        coach info, and stadium info.
        :return: a list of team information dicts
        """
        
        self.cursor.execute('SELECT team.id, team.year, '
                            '       conference.id, conference.name, conference.division, '
                            '       school.id, school.ncaa_id, school.name, school.nickname, school.url, '
                            '       coach.id, coach.ncaa_id, coach.first_name, coach.last_name, '
                            '           coach.alma_mater, coach.year_graduated, '
                            '       stadium.id, stadium.name, stadium.capacity, stadium.year_built '
                            'FROM team '
                            '    JOIN conference ON team.conference_id = conference.id '
                            '    JOIN school ON team.school_id = school.id '
                            '    LEFT JOIN coach ON team.coach_id = coach.id '
                            '    LEFT JOIN stadium ON team.stadium_id = stadium.id;')
        teams = []
        for row in self.cursor:
            teams.append({'team_id': row[0], 'year': row[1],
                          'conference_id': row[2], 'conference_name': row[3], 'division': row[4],
                          'school_id': row[5], 'school_ncaa_id': row[6],
                          'school_name': row[7],
                          'school_nickname': row[8], 'school_url': row[9],
                          'coach_id': row[10], 'coach_ncaa_id': row[11],
                          'coach_first_name': row[12],
                          'coach_last_name': row[11], 'coach_alma_mater': row[12],
                          'coach_year_graduated': row[13],
                          'stadium_id': row[14], 'stadium_name': row[15],
                          'stadium_capacity': row[16],
                          'stadium_year_built': row[17]})
        
        return teams
    
    def get_all_players(self):
        """
        Get all players from the database.
        :return: a list of player dicts
        """
        
        self.cursor.execute('SELECT id, ncaa_id, first_name, last_name '
                            'FROM player;')
        players = []
        for row in self.cursor:
            players.append({'player_id': row[0], 'ncaa_id': row[1], 'first_name': row[2],
                            'last_name': row[3]})
        
        return players
    
    def get_all_roster_info(self):
        """
        Get all roster information from the database, joins the player table.
        :return: A list of roster dicts
        """
        
        self.cursor.execute('SELECT roster.id, roster.team_id, roster.player_id, roster.class, '
                            'player.ncaa_id, player.first_name, player.last_name, team.year '
                            'FROM roster '
                            '    JOIN player ON roster.player_id = player.id '
                            '    JOIN team ON roster.team_id = team.id;')
        roster_rows = []
        for row in self.cursor:
            roster_rows.append({'roster_id': row[0], 'team_id': row[1], 'player_id': row[2],
                                'class': row[3], 'ncaa_id': row[4], 'first_name': row[5],
                                'last_name': row[6], 'year': row[7]})
        
        return roster_rows
    
    def get_year_roster_info(self, year):
        """
        Get all roster information for a given year from the database, joins the player table.
        :param year: the year of the roster rows
        :return: A list of roster dicts
        """
        
        self.cursor.execute('SELECT roster.id, roster.team_id, roster.player_id, roster.class, '
                            'player.ncaa_id, player.first_name, player.last_name, team.year '
                            'FROM roster '
                            '    JOIN player ON roster.player_id = player.id '
                            '    JOIN team ON roster.team_id = team.id '
                            'WHERE team.year = %s;', [year])
        roster_rows = []
        for row in self.cursor:
            roster_rows.append({'roster_id': row[0], 'team_id': row[1], 'player_id': row[2],
                                'class': row[3], 'ncaa_id': row[4], 'first_name': row[5],
                                'last_name': row[6], 'year': row[7]})
        
        return roster_rows
    
    def get_all_game_info(self):
        """
        Get all games in the game table.
        :return: a list of game dicts
        """
        
        self.cursor.execute('SELECT id, ncaa_id, away_team_id, home_team_id, date, location, attendance '
                            'FROM game;')
        games = []
        for row in self.cursor:
            games.append({'id': row[0], 'ncaa_id': row[1], 'away_team_id': row[2], 'home_team_id': row[3],
                          'date': row[4], 'location': row[5], 'attendance': row[6]})
        
        return games
    
    def get_all_innings(self):
        """
        Get all inning run totals in the database.
        :return: a list of inning dicts
        """
        
        self.cursor.execute('SELECT game_id, team_id, inning, runs '
                            'FROM inning')
        innings = []
        for row in self.cursor:
            innings.append({'game_id': row[0], 'team_id': row[1], 'inning': row[2], 'runs': row[3]})
        
        return innings
    
    def get_all_game_position_info(self):
        """
        Get all game position relations from the game_position table.
        :return: a list of game position dicts
        """
        
        self.cursor.execute('SELECT game_id, roster_id, position '
                            'FROM game_position;')
        game_positions = []
        for row in self.cursor:
            game_positions.append({'game_id': row[0], 'roster_id': row[1], 'position': row[2]})
        
        return game_positions
    
    def get_all_box_score_lines(self, stat_type):
        """
        Get all box score lines from the stat_type_line table of this stat type.
        :param stat_type: the stat type of this table (hitting, pitching, or fielding)
        :return: a list of box score line lists with game_id and roster_id in positions 0 and 1
        """
        
        self.cursor.execute('SELECT * '
                            'FROM {stat_type}_line'.format(stat_type=stat_type))
        box_score_lines = []
        for row in self.cursor:
            box_score_lines.append(row)
        
        return box_score_lines
    
    def get_all_umpires(self):
        """
        Get all umpires from the database.
        :return: a list of umpire dicts
        """
        
        self.cursor.execute('SELECT id, first_name, last_name '
                            'FROM umpire;')
        umpires = []
        for row in self.cursor:
            umpires.append({'id': row[0], 'first_name': row[1], 'last_name': row[2]})
        
        return umpires
    
    def get_all_game_umpires(self):
        """
        Get all game umpire relations from the database.
        :return: a dict of game ids to a dict of umpire ids corresponding to hp, 1b, 2b, 3b, lf, and rf
        """
        
        self.cursor.execute('SELECT game_id, umpire_id, position '
                            'FROM game_umpire;')
        
        game_umpires = {}
        for row in self.cursor:
            if row[0] not in game_umpires:
                game_umpires.update({row[0]: {'hp': None, '1b': None, '2b': None, '3b': None,
                                              'lf': None, 'rf': None}})
            game_umpires[row[0]][row[2]] = row[1]
        
        return game_umpires
    
    def get_all_play_by_play(self):
        """
        Get all play by play text and information from the database.
        :return: a list of play by play dicts
        """
        
        self.cursor.execute('SELECT game_id, team_id, inning, side, ord, text, pitches '
                            'FROM play_by_play;')
        pbp = []
        for row in self.cursor:
            pbp.append({'game_id': row[0], 'team_id': row[1], 'inning': row[2], 'side': row[3],
                        'ord': row[4], 'text': row[5], 'pitches': row[6]})
        
        return pbp
    
    def copy_expert(self, table_string, data_type, file_header, data):
        """
        Copy data to the database using a csv file as an intermediary.
        :param table_string: the table to copy to, including column names if applicable in the format
        table_name(column1, column2)
        :param data_type: the type of the data, such as 'conferences' or 'box_score_hitting' to create
        and copy
        :param file_header: the header of the csv file
        :param data: the data to copy that will be inserted into the csv file via a csv dictwriter.
        This data must be a list of dicts
        :return: None
        """
        
        copy_file_name = file_utils.get_copy_file_name(data_type)
        with open(copy_file_name, 'wb') as copy_file:
            writer = unicodecsv.DictWriter(copy_file, file_header)
            writer.writeheader()
            writer.writerows(data)
            copy_file.flush()
        
        self.cursor.copy_expert("COPY {table_string} from STDIN delimiter ',' NULL AS '' "
                                "CSV HEADER".format(table_string=table_string), open(copy_file_name))
        self.connection.commit()
    
    def add_school(self, school_name, school_ncaa_id=None):
        """
        Insert a school that is not already in the database, usually an NAIA school.
        :param school_name: the name of the school
        :param school_ncaa_id: the ncaa id of the school, defaults to None if not included
        :return: the id of the newly created school
        """
        self.cursor.execute('INSERT INTO school(ncaa_id, name) '
                            'VALUES(%s, %s) '
                            'RETURNING id;', [school_ncaa_id, school_name])
        school_id = self.cursor.fetchone()[0]
        
        self.connection.commit()
        
        return school_id
    
    def create_team(self, year, school_id):
        """
        Insert a team that is not already in the database, usually from a school that is NAIA.This
        method gives the team a generic conference called 'Other', which will be changed if a
        matching team is scraped and added later.
        :param year: the year of this team
        :param school_id: the id of the school
        :return: the id of the newly created team
        """
        self.cursor.execute('INSERT INTO team(year, conference_id, school_id) '
                            'VALUES(%s, %s, %s) '
                            'RETURNING id;', [year, self.get_default_conference_id(), school_id])
        team_id = self.cursor.fetchone()[0]
        
        self.connection.commit()
        
        return team_id
    
    def get_player_year_stats(self, year, division, stat_type):
        """
        Get player year total stats for the specified type.
        :param year: the year of the stats
        :param division: the division of the stats
        :param stat_type: the type of stats ('hitting', 'pitching', 'fielding')
        :return: an array of dicts, with the dicts being comprised of a mapping of the stat headers
        to the stat values, ordered by roster id in ascending order
        """
        
        headers = {'hitting': ['ab, ', 'h, ', 'dbl, ', 'tpl, ', 'hr, ', 'bb, ', 'ibb, ', 'hbp, ', 'r, ',
                               'rbi, ', 'k, ', 'sf, ', 'sh, ', 'dp, ', 'sb, ', 'cs'],
                   'pitching': ['app, ', 'gs, ', 'ord, ', 'w, ', 'l, ', 'sv, ', 'ip, ', 'p, ', 'bf, ',
                                'h, ', 'dbl, ', 'tpl, ', 'hr, ', 'bb, ', 'ibb, ', 'hbp, ', 'r, ',
                                'er, ', 'ir, ', 'irs, ', 'fo, ', 'go, ', 'k, ', 'kl, ', 'sf, ', 'sh, ',
                                'bk, ', 'wp, ', 'cg, ', 'sho'],
                   'fielding': ['po, ', 'a, ', 'e, ', 'pb, ', 'ci, ', 'sb, ', 'cs, ', 'dp, ', 'tp']}
        select_string = 'stats.'.join(headers[stat_type])
        self.cursor.execute('SELECT r.id, {select_string} '
                            'FROM player_year_totals_{stat_type}({year}, {division}) AS stats '
                            '   JOIN roster AS r ON r.id = stats.roster_id '
                            'ORDER BY r.id ASC'
                            .format(select_string=select_string, stat_type=stat_type, year=year,
                                    division=division))
        stat_rows = []
        for row in self.cursor:
            stats = {'roster_id': row[0]}
            for index, heading in enumerate(headers[stat_type]):
                stats[heading.replace(', ', '')] = row[1 + index]
            stat_rows.append(stats)
        
        return stat_rows
    
    def get_roster_id(self, year, division, first_name, last_name, school_name):
        """
        Get a player's roster id from their first name and last name. Could possibly return the wrong
        player, since names are not unique, but it is unlikely that two players with the same first
        name and last name would be on the same team.
        
        :param year: the year of the player
        :param division: the division the player played in
        :param first_name: the first name of the player
        :param last_name: the last name of the player
        :param school_name: the school the player played at
        :return: the player id of the player or None if the player is not found or if more than one
        player is found
        """
        
        self.cursor.execute('SELECT r.id '
                            'FROM roster AS r '
                            '  JOIN team AS t ON t.id = r.team_id '
                            '  JOIN player AS p ON p.id = r.player_id '
                            '  JOIN school AS s ON s.id = t.school_id '
                            '  JOIN conference AS c ON c.id = t.conference_id '
                            'WHERE p.first_name = %s '
                            '  AND p.last_name = %s '
                            '  AND t.year = %s '
                            '  AND c.division = %s '
                            '  AND s.name = %s;', [first_name, last_name, year, division, school_name])
        player_ids = self.cursor.fetchmany(2)
        
        if len(player_ids) != 1:
            return None
        return player_ids[0][0]
    
    def get_year_division_game_ids(self, year, division):
        """
        Get all game ids from this year and division.
        
        :param year: the year of the games
        :param division: the division of the games
        :return: a list of game ids
        """
        
        self.cursor.execute('SELECT game.id '
                            'FROM game '
                            '  JOIN team AS at ON at.id = game.away_team_id '
                            '  JOIN team AS ht ON ht.id = game.home_team_id '
                            '  JOIN conference AS ac ON ac.id = at.conference_id '
                            '  JOIN conference AS hc ON hc.id = ht.conference_id '
                            'WHERE at.year = %s '
                            '  AND (ac.division = %s '
                            '  OR hc.division = %s)'
                            'ORDER BY game.id', [year, division, division])
        return [row[0] for row in self.cursor]
    
    def get_year_division_play_by_play(self, year, division):
        """
        Get all play by play from this year and division.
        :param year: the year of the games
        :param division: the division of the games
        :return: a dict of game ids to play by play dicts: {game_id: [line_1_dict, line_2_dict, ... ]
        """
        
        self.cursor.execute('SELECT game_id, team_id, inning, side, ord, text, pitches '
                            'FROM play_by_play AS pbp '
                            '  JOIN game AS g ON g.id = pbp.game_id '
                            '  JOIN team AS ta ON ta.id = g.away_team_id '
                            '  JOIN team AS th ON th.id = g.home_team_id '
                            '  JOIN conference AS ca ON ca.id = ta.conference_id '
                            '  JOIN conference AS ch ON ch.id = th.conference_id '
                            'WHERE ta.year = %s '
                            '  AND (ca.division = %s OR ch.division = %s) '
                            'ORDER BY pbp.game_id, inning, side, ord', [year, division, division])
        
        pbp_lines = self.cursor.fetchall()
        
        pbp_dicts = {}
        
        previous_game_id = pbp_lines[0][0]
        current_game_pbp = []
        for line in pbp_lines:
            pbp_dict = {'team_id': line[1], 'inning': line[2], 'side': line[3], 'ord': line[4], 'text': line[5],
                        'pitches': line[6]}
            current_game_id = line[0]
            if current_game_id == previous_game_id:
                current_game_pbp.append(pbp_dict)
            else:
                pbp_dicts.update({previous_game_id: current_game_pbp})
                previous_game_id = current_game_id
                current_game_pbp = [pbp_dict]
        return pbp_dicts
    
    def get_school_id(self, school_name):
        """
        Get the school id for a school with this name. If this school name is not in the database, return None.
        
        :param school_name: the name of the school
        :return: the school id, or None if the name does not exist
        """
        self.cursor.execute('SELECT id '
                            'FROM school '
                            'WHERE name = %s', [school_name])
        school_id = self.cursor.fetchone()
        if school_id is None:
            return None
        return school_id[0]
    
    def get_team_id(self, year, school_id):
        """
        Get the team id for a specific year and school. Return None if this school id and year combo does not have a
        corresponding team.
        
        :param year: the year of the team
        :param school_id: the school id of the team
        :return: the team id of the year and school, None if the team does not exist
        """
        self.cursor.execute('SELECT id '
                            'FROM team '
                            'WHERE year = %s '
                            '  AND school_id = %s', [year, school_id])
        team_id = self.cursor.fetchone()
        if team_id is None:
            return None
        return team_id[0]
    
    def get_team_schedule(self, team_id):
        """
        Get the schedule for a specific team. Return None if the team does not exist or if there are no games for
        that team.
        
        :param team_id: the team id
        :return: a list of game ids, or None if the team does not exist or if the team played no games
        """
        self.cursor.execute('SELECT id '
                            'FROM game '
                            'WHERE away_team_id = %s '
                            '  OR home_team_id = %s', [team_id, team_id])
        games = self.cursor.fetchall()
        if games == []:
            return None
        game_ids = [game[0] for game in games]
        return game_ids
    
    def get_game_info(self, game_id):
        """
        Get game info for the specified game. Return None if there is no game with this game_id in the database.
        
        :param game_id: the game id of the game
        :return: a game info dict: {'date': game.date, 'away_team_id': game.away_team_id, 'home_team_id':
        game.home_team_id, 'location': game.location, 'attendance': game.attendance} or None if the game does not exist
        """
        
        self.cursor.execute('SELECT date, away_team_id, home_team_id, location, attendance '
                            'FROM game '
                            'WHERE id = %s', [game_id])
        game_info = self.cursor.fetchall()
        if game_info == []:
            return None
        game_info = game_info[0]
        return {'date': game_info[0], 'away_team_id': game_info[1], 'home_team_id': game_info[2],
                'location': game_info[3], 'attendance': game_info[4]}
    
    def get_game_score(self, game_id):
        """
        Get the final score of the specified game. Return None if there is no game with this game_id in the database.
        
        :param game_id: the game id of he game
        :return: a dict with the final score of the game:
        {'away': away_team_score, 'home': home_team_score} or None if the game does not exist
        """
        
        self.cursor.execute('SELECT sum(runs) '
                            'FROM inning AS i '
                            '  JOIN game AS g ON g.id = i.game_id '
                            'WHERE game_id = %s '
                            '  AND i.team_id = g.away_team_id', [game_id])
        away_score_info = self.cursor.fetchone()
        if away_score_info is None:
            return None
        away_score = away_score_info[0]
        
        self.cursor.execute('SELECT sum(runs) '
                            'FROM inning AS i '
                            '  JOIN game AS g ON g.id = i.game_id '
                            'WHERE game_id = %s '
                            '  AND i.team_id = g.home_team_id', [game_id])
        home_score = self.cursor.fetchone()[0]
        return {'away': away_score, 'home': home_score}
    
    def get_game_umpires(self, game_id):
        """
        Get the umpire ids and positions for the specified game. Returns a dict of the umpire ids or None if there
        were no umpires found or if the game does not exist.
        
        :param game_id: the id of the game
        :return: a dict of the umpire ids: {'hp': umpire.home_plate, '1b': umpire.first_base ...}
        or None if there were no umpires found or if the game does not exist
        """
        
        self.cursor.execute('SELECT umpire_id, position '
                            'FROM game_umpire '
                            'WHERE game_id = %s', [game_id])
        umpires = self.cursor.fetchall()
        if umpires == []:
            return None
        return {umpire[1]: umpire[0] for umpire in umpires}
    
    def get_game_starting_lineup(self, game_id, side):
        """
        Get the starting lineup for the specified side team for this game.
        
        :param game_id: the game id of the game
        :param side: the side(away or home) of the lineup
        :return: a list of player dicts in the order of the lineup for that game:
        [{'roster_id': roster_id, first_name': first_name, 'last_name': last_name}]
        """
        
        self.cursor.execute('SELECT game_id, roster_id, first_name, last_name '
                            'FROM hitting_line '
                            '  JOIN game ON game.id = hitting_line.game_id '
                            '  JOIN roster ON roster.id = hitting_line.roster_id '
                            '  JOIN player ON player.id = roster.player_id '
                            'WHERE game_id = %s '
                            '  AND roster.team_id = game.{}_team_id '
                            '  AND hitting_line.sub = FALSE '
                            'ORDER BY hitting_line.lineup_spot'.format(side), [game_id])
        lineup = []
        for row in self.cursor:
            lineup.append({'roster_id': row[1], 'first_name': row[2], 'last_name': row[3]})
        
        return lineup
    
    def get_game_subs(self, game_id, side):
        """
        Get all subs for the specified side team for this game.
        
        :param game_id: the game id of the game
        :param side: the side(away or home) of the lineup
        :return: a list of player dicts of each sub from the game, with their lineup spot and initial position:
        [{'roster_id': roster_id, 'first_name': first_name, 'last_name': last_name, 'lineup_spot': lineup_spot,
        'position': position}]
        """
        self.cursor.execute('SELECT game_id, hitting_line.roster_id, first_name, last_name, lineup_spot, position '
                            'FROM hitting_line '
                            '  JOIN game ON game.id = hitting_line.game_id '
                            '  JOIN roster ON roster.id = hitting_line.roster_id '
                            '  JOIN player ON player.id = roster.player_id '
                            '  JOIN game_position on game_position.game_id = game.id '
                            'WHERE game.id = %s '
                            '  AND team_id = game.{}_team_id '
                            '  AND sub = TRUE '
                            '  AND ord = 1 '
                            'ORDER BY lineup_spot'.format(side), [game_id])
        
        subs = []
        for row in self.cursor:
            subs.append({'roster_id': row[1], 'first_name': row[2], 'last_name': row[3], 'lineup_spot': row[4],
                         'position': row[5]})
        return subs
    
    def get_game_players(self, game_id, side):
        """
        Get the all players for the specified side team for this game.

        :param game_id: the game id of the game
        :param side: the side(away or home) of the lineup
        :return: a list of player dicts from the game:
        [{'roster_id': roster_id, 'first_name': first_name, 'last_name': last_name}]
        """
        
        self.cursor.execute('SELECT roster_id, first_name, last_name '
                            'FROM hitting_line '
                            '  JOIN game ON game.id = hitting_line.game_id '
                            '  JOIN roster ON roster.id = hitting_line.roster_id '
                            '  JOIN player ON player.id = roster.player_id '
                            'WHERE game_id = %s '
                            '  AND roster.team_id = game.{}_team_id'.format(side), [game_id])
        players = []
        for row in self.cursor:
            players.append({'roster_id': row[0], 'first_name': row[1], 'last_name': row[2]})
        
        return players
    
    def get_game_initial_positions(self, game_id, side):
        """
        Get the initial positions for all players on the specified side team for this game.

        :param game_id: the game id of the game
        :param side: the side(away or home) of the lineup
        :return: a dict of roster ids to positions: {roster id: position}
        """
        self.cursor.execute('SELECT gp.roster_id, gp.position '
                            'FROM game_position AS gp '
                            '  JOIN game AS g ON g.id = gp.game_id '
                            '  JOIN roster AS r ON r.id = gp.roster_id '
                            'WHERE gp.game_id = %s '
                            '  AND g.{}_team_id = r.team_id '
                            '  AND gp.ord = 1'
                            'ORDER BY gp.roster_id'.format(side), [game_id])
        player_positions = dict()
        for row in self.cursor.fetchall():
            player_positions.update({row[0]: row[1]})
        
        return player_positions
    
    def get_game_all_positions(self, game_id, side):
        """
        Get the positions for the specified side team for this game.

        :param game_id: the game id of the game
        :param side: the side(away or home) of the lineup
        :return: a dict of roster ids to position lists (in order of position change):
        {roster id: [position_1, position_2, ... ]
        """
        self.cursor.execute('SELECT gp.roster_id, gp.position '
                            'FROM game_position AS gp '
                            '  JOIN game AS g ON g.id = gp.game_id '
                            '  JOIN roster AS r ON r.id = gp.roster_id '
                            'WHERE gp.game_id = %s '
                            '  AND g.{}_team_id = r.team_id '
                            'ORDER BY gp.roster_id, gp.ord'.format(side), [game_id])
        player_positions = dict()
        for row in self.cursor.fetchall():
            if row[0] in player_positions:
                previous_positions = player_positions[row[0]]
                previous_positions.append(row[1])
                player_positions.update({row[0]: previous_positions})
            else:
                player_positions.update({row[0]: [row[1]]})
        
        return player_positions
    
    def get_game_pbp(self, game_id):
        """
        Get the play by play for the specified game.
        
        :param game_id: the game id of the game
        :return: a list of play by play dicts, in order by inning, side, then ord
        """
        
        self.cursor.execute('SELECT team_id, inning, side, ord, text, pitches '
                            'FROM play_by_play AS pbp '
                            'WHERE game_id = %s '
                            'ORDER BY inning, side, ord', [game_id])
        pbp = []
        for row in self.cursor:
            pbp.append({'team_id': row[0], 'inning': row[1], 'side': row[2],
                        'ord': row[3], 'text': row[4], 'pitches': row[5]})
        return pbp
